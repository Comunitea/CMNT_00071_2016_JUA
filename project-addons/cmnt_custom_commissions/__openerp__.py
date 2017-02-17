# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Custom commissions CMNT',
    'version': '8.0.0.0.0',
    'author': 'Comunitea ',
    "category": "CRM",
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale_commission',
        'acp_yanez',
        'acp_contrato',
    ],
    'contributors': [
        "Comunitea ",
        "Javier Colmenero <javier@comunitea.com>"
    ],
    "data": [
        "security/commission_security.xml",
        'security/ir.model.access.csv',
        'views/commission_plan_view.xml',
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
        'views/sale_view.xml',
        'views/acp_contrato_view.xml',
        'views/settlement_view.xml',
    ],
    "installable": True
}
