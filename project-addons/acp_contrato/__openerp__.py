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
    'name': 'Gestion de Contratos',
    'version': '1.0',
    'category': 'Generic Modules/Sales & Purchases',
    'description':  """
Gestión de contratos/expedientes
==================================
Esta aplicación permite gestionar contratos/expedientes, generar uno o varios servicios por contratos/expedientes y dar seguimiento detallado a cada uno de los servicios.


Caracteriaticas
------------------------------------------------------

*.Integración con el módulo de notas, permite crear notas colaborativas desde las actividades.

*.Asignación de actividades: se pueden asignar actividades a otros empleadoa, el sistema le notificará con un correo cuando la actividad se ha Finalizado.

*.Cree actividades de “especial atención” para que cualquier usuario pueda verlas y no se pase nada por alto.

*.Cree contactos para los contratos/expedientes.

*.Asigne operarios a los servicios.

*.Calendario de actividades pendientes.

*.Imputación de facturas compras/gastos.

*.Imputación de facturas de venta.


Integración con compras / ventas y contabilidad
------------------------------------------------------

Desde un expediente o servicio puede generar presupuesto de compras / Ventas, asignar coste e asociar facturas de venta para poder obtener la rentabilidad de cada expediente

    """,
    'author': 'InfoAcp',
    'website': 'http://www.infoacp.es',
    'depends': ['jasper_reports',
                'web_m2x_options',
                'sale',
                'purchase',
                'account',
                'base_vat',
                'crm',
                'base_location',
                'l10n_es_toponyms',
                'l10n_es_partner',
                'hr_contract',
                'acp_document',
                'mail',
                'sale_commission' # Por el contexto del order line
                ],
    'init_xml': [],
    'data': [
        'data/acp_contrato_sequence.xml',
        'security/contrato_security.xml',
        'wizard/repercute_cost_wzd_view.xml',
        'acp_contrato.xml',
        'product_view.xml',
        'partner_view.xml',
        'res_users_view.xml',
        'sale_order_view.xml',
        'purchase_order_view.xml',
        'account_invoice_view.xml',
        'purchase_view.xml',
        'wizard/wizard_genera_servicio.xml',
        'wizard/wizard_refactura.xml',
        'workflow/workflow.xml',
        'hr_view.xml',
        'attachment_view.xml',
        'acp_contrato_cron.xml',
        'acp_contrato_portal.xml',
        'security/contrato_rules.xml',
        'data/data.xml',
        'data/acp_contrato_cron_data.xml',
        'security/ir.model.access.csv',


    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
