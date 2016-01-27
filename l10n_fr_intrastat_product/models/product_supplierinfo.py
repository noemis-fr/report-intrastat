# -*- encoding: utf-8 -*-
##############################################################################
#
#    Report intrastat product module for OpenERP
#    Copyright (C) 2004-2009 Tiny SPRL (http://tiny.be)
#    Copyright (C) 2010-2014 Akretion (http://www.akretion.com)
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


class product_supplierinfo(orm.Model):
    _inherit = "product.supplierinfo"
    _columns = {
        'origin_country_id': fields.many2one(
            'res.country', 'Country of origin',
            help="Country of origin of the product "
            "(i.e. product 'made in ____') when purchased from this supplier. "
            "This field is used only when the equivalent field on the product "
            "form is empty."),
        }

    def _same_supplier_same_origin(self, cr, uid, ids):
        """Products from the same supplier should have the same origin"""
        for supplierinfo in self.browse(cr, uid, ids):
            country_origin_id = supplierinfo.origin_country_id.id
            # Search for same supplier and same product
            same_product_same_supplier_ids = self.search(
                cr, uid, [
                    ('product_id', '=', supplierinfo.product_id.id),
                    ('name', '=', supplierinfo.name.id)])
            # 'name' on product_supplierinfo is a many2one to res.partner
            for supplieri in self.browse(
                    cr, uid, same_product_same_supplier_ids):
                if country_origin_id != supplieri.origin_country_id.id:
                    raise orm.except_orm(
                        _('Error !'),
                        _("For a particular product, all supplier info "
                            "entries with the same supplier should have the "
                            "same country of origin. But, for product '%s' "
                            "with supplier '%s', there is one entry with "
                            "country of origin '%s' and another entry with "
                            "country of origin '%s'.")
                        % (supplieri.product_id.name,
                            supplieri.name.name,
                            supplierinfo.origin_country_id.name,
                            supplieri.origin_country_id.name))
        return True

    _constraints = [(
        _same_supplier_same_origin,
        "error msg in raise",
        ['origin_country_id', 'name', 'product_id']
        )]
