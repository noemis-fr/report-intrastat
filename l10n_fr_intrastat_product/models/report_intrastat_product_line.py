# -*- encoding: utf-8 -*-
##############################################################################
#
#    Report intrastat product module for OpenERP
#    Copyright (C) 2009-2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
import logging
from lxml import etree

logger = logging.getLogger(__name__)


class report_intrastat_product_line(orm.Model):
    _name = "report.intrastat.product.line"
    _description = "Intrastat Product Lines"
    _order = 'id'

    _columns = {
        'parent_id': fields.many2one('report.intrastat.product', 'Intrastat product ref', ondelete='cascade', readonly=True),
        'company_id': fields.related('parent_id', 'company_id', type='many2one', relation='res.company', string="Company", readonly=True),
        'type': fields.related('parent_id', 'type', type='char', string="Type", readonly=True),
        'company_currency_id': fields.related('company_id', 'currency_id', type='many2one', relation='res.currency', string="Company currency", readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice ref', readonly=True),
        'quantity': fields.char('Quantity', size=10),
        'source_uom_id': fields.many2one('product.uom', 'Source UoM', readonly=True),
        'intrastat_uom_id': fields.many2one('product.uom', 'Intrastat UoM'),
        'partner_country_id': fields.many2one('res.country', 'Partner country'),
        'partner_country_code': fields.related('partner_country_id', 'code', type='char', relation='res.country', string='Partner country', readonly=True),
        'intrastat_code': fields.char('Intrastat code', size=9),
        'intrastat_code_id': fields.many2one('report.intrastat.code', 'Intrastat code (not used in XML)'),
        # Weight should be an integer... but I want to be able to display nothing in
        # tree view when the value is False (if weight is an integer, a False value would
        # be displayed as 0), that's why weight is a char !
        'weight': fields.char('Weight', size=10),
        'amount_company_currency': fields.integer('Fiscal value in company currency',
            required=True,
            help="Amount in company currency to write in the declaration. Amount in company currency = amount in invoice currency converted to company currency with the rate of the invoice date and rounded at 0 digits"),
        'amount_invoice_currency': fields.float('Fiscal value in invoice currency',
            digits_compute=dp.get_precision('Account'), readonly=True,
            help="Amount in invoice currency = amount of product value in invoice currency + amount of accessory cost in invoice currency (not rounded)"),
        'amount_accessory_cost_inv_cur': fields.float(
            'Amount of accessory costs in invoice currency',
            digits_compute=dp.get_precision('Account'), readonly=True,
            help="Amount of accessory costs in invoice currency = total amount of accessory costs of the invoice broken down into each product line at the pro-rata of the value"),
        'amount_product_value_inv_cur': fields.float(
            'Amount of product value in invoice currency',
            digits_compute=dp.get_precision('Account'), readonly=True,
            help="Amount of product value in invoice currency ; it is the amount of the invoice line or group of invoice lines."),
        'invoice_currency_id': fields.many2one('res.currency', "Invoice currency", readonly=True),
        'product_country_origin_id': fields.many2one('res.country', 'Product country of origin'),
        'product_country_origin_code': fields.related('product_country_origin_id', 'code', type='char', relation='res.country', string='Product country of origin', readonly=True),
        'transport': fields.selection([
            (1, '1. Transport maritime'),
            (2, '2. Transport par chemin de fer'),
            (3, '3. Transport par route'),
            (4, '4. Transport par air'),
            (5, '5. Envois postaux'),
            (7, '7. Installations de transport fixes'),
            (8, '8. Transport par navigation intérieure'),
            (9, '9. Propulsion propre')
            ], 'Type of transport'),
        'department': fields.char('Department', size=2),
        'intrastat_type_id': fields.many2one('report.intrastat.type', 'Intrastat type'),
        'is_vat_required': fields.related('intrastat_type_id', 'is_vat_required', type='boolean', relation='report.intrastat.type', string='Is Partner VAT required ?', readonly=True),
        # Is fiscal_only is not fields.related because, if obligation_level = simplified, is_fiscal_only is always true
        'is_fiscal_only': fields.boolean('Is fiscal only?', readonly=True),
        'procedure_code': fields.char('Procedure code', size=2),
        'transaction_code': fields.char('Transaction code', size=2),
        'partner_vat': fields.char('Partner VAT', size=32),
        'partner_id': fields.many2one('res.partner', 'Partner name'),
    }

    def _integer_check(self, cr, uid, ids):
        for values in self.read(cr, uid, ids, ['weight', 'quantity']):
            if values['weight'] and not values['weight'].isdigit():
                raise orm.except_orm(_('Error :'), _('Weight must be an integer.'))
            if values['quantity'] and not values['quantity'].isdigit():
                raise orm.except_orm(_('Error :'), _('Quantity must be an integer.'))
        return True

    def _code_check(self, cr, uid, ids):
        for lines in self.read(cr, uid, ids, ['procedure_code', 'transaction_code']):
            self.pool.get('report.intrastat.type').real_code_check(lines)
        return True

    _constraints = [
        (_code_check, "Error msg in raise", ['procedure_code', 'transaction_code']),
        (_integer_check, "Error msg in raise", ['weight', 'quantity']),
    ]


    def partner_on_change(self, cr, uid, ids, partner_id=False, context=None):
        return self.pool['report.intrastat.common'].partner_on_change(
            cr, uid, ids, partner_id, context=context)

    def intrastat_code_on_change(
            self, cr, uid, ids, intrastat_code_id=False, context=None):
        result = {}
        result['value'] = {}
        if intrastat_code_id:
            intrastat_code = self.pool['report.intrastat.code'].browse(
                cr, uid, intrastat_code_id, context=context)
            if intrastat_code.intrastat_uom_id:
                result['value'].update({
                    'intrastat_code': intrastat_code.intrastat_code,
                    'intrastat_uom_id': intrastat_code.intrastat_uom_id.id,
                    })
            else:
                result['value'].update({
                    'intrastat_code': intrastat_code.intrastat_code,
                    'intrastat_uom_id': False,
                    })
        return result

    def intrastat_type_on_change(
            self, cr, uid, ids, intrastat_type_id=False, type=False,
            obligation_level=False, context=None):
        result = {}
        result['value'] = {}
        if obligation_level == 'simplified':
            result['value'].update({'is_fiscal_only': True})
        if intrastat_type_id:
            intrastat_type = self.pool['report.intrastat.type'].read(
                cr, uid, intrastat_type_id, [
                    'procedure_code', 'transaction_code',
                    'is_fiscal_only', 'is_vat_required',
                    ], context=context)
            result['value'].update({'procedure_code': intrastat_type['procedure_code'], 'transaction_code': intrastat_type['transaction_code'], 'is_vat_required': intrastat_type['is_vat_required']})
            if obligation_level == 'detailed':
                result['value'].update({'is_fiscal_only': intrastat_type['is_fiscal_only']})

        if result['value'].get('is_fiscal_only', False):
            result['value'].update({
                'quantity': False,
                'source_uom_id': False,
                'intrastat_uom_id': False,
                'partner_country_id': False,
                'intrastat_code': False,
                'intrastat_code_id': False,
                'weight': False,
                'product_country_origin_id': False,
                'transport': False,
                'department': False
            })
        #print "intrastat_type_on_change res=", result
        return result
