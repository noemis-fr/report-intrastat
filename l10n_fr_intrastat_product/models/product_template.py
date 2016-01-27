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


class product_template(orm.Model):
    _inherit = "product.template"
    _columns = {
        'intrastat_id': fields.many2one(
            'report.intrastat.code', 'Intrastat code',
            help="Code from the Harmonised System. Nomenclature is "
            "available from the World Customs Organisation, see "
            "http://www.wcoomd.org/. Some countries have made their own "
            "extensions to this nomenclature."),
        'country_id': fields.many2one(
            'res.country', 'Country of origin',
            help="Country of origin of the product i.e. product "
            "'made in ____'. If you have different countries of origin "
            "depending on the supplier from which you purchased the product, "
            "leave this field empty and use the equivalent field on the "
            "'product supplier info' form."),
        # This field should be called origin_country_id, but it's named
        # country_id to keep "compatibility with OpenERP users that used
        # the "report_intrastat" module
        }
