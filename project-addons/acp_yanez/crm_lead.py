# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import tools
from openerp.osv import osv, fields

class crm_lead(osv.osv):


    _inherit  = "crm.lead"

    def _mail_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
       
        for lead in self.browse(cr, uid, ids, context):
            res[lead.id] = len(self.pool.get('mail.message').search(cr, uid, [('res_id','=',ids[0]),('model','=','crm.lead')]))
        return res

    def _get_mail_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
       
        for lead in self.browse(cr, uid, ids, context):
            res[lead.id] = self.pool.get('mail.message').search(cr, uid, [('res_id','=',ids[0]),('model','=','crm.lead')])
        return res

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
            
    _columns = {
        'mass_mailing_id': fields.many2one('mail.mass_mailing','Envio Masivo'),        
        'event_registration_id': fields.many2one('event.registration','Registro de Evento'),
        'event_id': fields.many2one('event.event','Evento'),        
        'contact_id':  fields.many2one('mail.mass_mailing.contact','Contacto'), 
        'company_id':fields.many2one('res.company', 'Company', required=False, readonly=False),
        'mail_ids': fields.function(_get_mail_ids, string='Emails', type='one2many',  relation='mail.message'),        
        'mail_count': fields.function(_mail_count, string='# of Sales Order', type='integer'),
        
    }

    _defaults = {
        'company_id': _get_default_company,
   }

    def action_mail_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'acp_yanez', 'acp_yanez_email_template_opportunity_mail')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict()
        ctx.update({
            'default_model': 'crm.lead',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

