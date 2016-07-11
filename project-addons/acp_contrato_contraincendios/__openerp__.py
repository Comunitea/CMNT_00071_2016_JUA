# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Gestion de Contratos (Empresas Contraincendios)',
    'version': '1.0',
    'category': 'Generic Modules/Sales & Purchases',
    'description':  """
Gestión de contratos de mantenimiento para empresas contraincendios
===================================================================
Añade los campos necesários para la gestion de los contratos de mantenimiento de empresas contraincendios


Caracteriaticas
------------------------------------------------------

*.



    """,
    'author': 'InfoAcp',
    'website': 'http://www.infoacp.es',
    'depends': ['acp_contrato'],
    'init_xml': [],
    'data': [
        'data.xml',
        'acp_contrato.xml',
        'product_view.xml',
        'res_company_view.xml' ,
        'report_invoice.xml',       
        'hr_view.xml', 

    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
