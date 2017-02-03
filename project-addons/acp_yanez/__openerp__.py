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
    'name': 'ACP Yanez',
    'version': '1.0',
    'category': 'Customer Relationship Management',
    'description':  """

Descripcion pendiente

    """,
    'author': 'InfoAcp',
    'website': 'http://www.infoacp.es',
    'depends': ['portal',
                'sale','crm','stock',
                'event','marketing',
                'marketing_campaign',
                'mass_mailing',
                'account_payment_sale',
                'survey_crm',
                'sale_early_payment_discount',
                'website_sale',
                'acp_document'],
    'init_xml': [],
    'data': [  
         
        'wizard/select_payment_term.xml',
        'wizard/select_payment_mode.xml',        
        'res_company_view.xml',
        'calendar_view.xml'  ,       
        'crm_lead_view.xml',
        'mail_message_view.xml',
        'mass_mail_view.xml',        
        'sale_view.xml',
        'partner_view.xml',        
        'payment_mode_view.xml',        
        'payment_term_view.xml', 
        'event_view.xml',        
        'attachment_view.xml',     
        'wizard/attachment_view.xml',
        'wizard/create_lead.xml',
        # 'sale_commission_view.xml',   
        'security/security.xml',
        'yanez_invoice_view.xml',
        'account_view.xml',
        'survey.xml',
        'security/ir.model.access.csv',        


      
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
