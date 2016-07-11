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
    'name': 'Reports Gestion de Contratos (Bufetes de Abogados)',
    'version': '1.0',
    'category': 'Generic Modules/Jasper Reports',
    'description':  """

Informes personalizados:
=================================================
    * Presupuesto/Pedido Venta (Expedientes)
    * Factura Venta (Expedientes)

Acciones después de la instalación del módulo
=================================================

Una vez instalado el modulo, hay que cargar manualmente el archivo jrxml de cada informe:
    1. Ir a Configuración > Técnico > Jasper Reports > Jasper Reports
    2. Seleccionar Informe Jasper Report y editar
    3. En archivos añadir y seleccionar el informe correspondiente que se encuentra en acp_contrato_bufete_repot/report:
        * Presupuesto/Pedido Venta (Expedientes) (acp_sale_order_expbu_jasper) > acp_sale_order_expbu_jasper.jrxml
        * Factura Venta (Expedientes) (acp_invoice_expbu_jasper) > acp_invoice_expbu_jasper.jrxml y acp_invoice_vencimiento_expbu_jasper.jrxml
    4. Marcar casilla predeterminado


    """,
    'author': 'InfoAcp',
    'website': 'http://www.infoacp.es',
    'depends': ['jasper_reports','acp_contrato_bufete'],
    'init_xml': [],
    'data': [
        'acp_contrato_bufete_report.xml',
        'company_view.xml',
        'wizard/acp_contrato_bufete_report_wizard.xml',
        'data/data.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
