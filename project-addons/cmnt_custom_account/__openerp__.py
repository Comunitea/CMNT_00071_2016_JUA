# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Custom Account CMNT',
    'version': '8.0.0.0.0',
    'author': 'Comunitea ',
    "category": "CRM",
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account',
        'sale',
        'account_banking_sepa_direct_debit',
        'account_payment',
        'account_due_dates_str',
        'acp_contrato_bufete_report',
        'account_followup',
        'mail',
        'account_banking_sepadd_groupby_partner'
    ],
    'contributors': [
        "Comunitea ",
        "Javier Colmenero <javier@comunitea.com>"
    ],
    "data": [
        'data/mail_templates.xml',
        'data/ir_cron.xml',
        'views/payment_order_view.xml'
    ],
    "demo": [
    ],
    'test': [
    ],
    "installable": True
}
