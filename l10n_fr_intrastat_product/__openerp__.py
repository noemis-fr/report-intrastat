# -*- encoding: utf-8 -*-
##############################################################################
#
#    Report intrastat product module for OpenERP
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


{
    'name': 'France Intrastat Product',
    'version': '1.1',
    'category': 'Localisation/Report Intrastat',
    'license': 'AGPL-3',
    'summary': 'Module for Intrastat product reporting (DEB) for France',
    'description': """This module adds support for the "Déclaration d'Echange de Biens" (DEB).

More information about the DEB is available on this official web page : http://www.douane.gouv.fr/page.asp?id=322

Please contact Alexis de Lattre from Akretion <alexis.delattre@akretion.com> for any help or question about this module.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['intrastat_base', 'sale_stock', 'purchase'],
    'data': [
        'security/intrastat_product_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/email_template.xml',
        'views/account_invoice_view.xml',
        'views/product_category_view.xml',
        'views/product_product_view.xml',
        'views/product_supplierinfo_view.xml',
        'views/product_template_view.xml',
        'views/product_uom_view.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_location_view.xml',
        'views/report_intrastat_code_view.xml',
        'views/report_intrastat_product_view.xml',
        'views/report_intrastat_type_view.xml',
        'views/menu.xml',
    ],
    'demo': [
        'intrastat_demo.xml',
    ],
    'installable': True,
}
