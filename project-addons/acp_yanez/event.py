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


from datetime import timedelta

import pytz

from openerp import models, fields, api, _
from openerp.exceptions import Warning

class event_event(models.Model):


    _inherit  = "event.event"

    materia = fields.Html(string='Description', oldname='note', translate=True,
        readonly=False, states={'done': [('readonly', True)]})
    conferenciantes_ids = fields.Many2many('res.partner', string='Conferenciantes')
    colaborador = fields.Many2one('res.partner', string='Colaborador')
    curso_type = fields.Selection([
            ('executive', 'Executive'),
            ('iniciación', 'Iniciación'),
        ], string='Tipo de Curso')
    duracion = fields.Char( string='Duración')
    ubicacion2 = fields.Char( string='Ubicación2')    

    def envio_masivo(self,cr,uid,ids,context=None):
        event_obj=self.pool.get('event.event')
        event=event_obj.browse(cr, uid, ids[0], context=context)

        registration_ids  = [r.id for r in event.registration_ids]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Envio Masivo',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'from_event':True,'default_name':event.name,'default_event_id':ids[0],'default_mailing_model':'event.registration','default_mailing_domain':[['id', 'in', registration_ids]]},
            'res_model': 'mail.mass_mailing',
            'nodestroy': True,
            'target':'current', 
            }
 
    def envio_encuesta(self,cr,uid,ids,context=None):
        event_obj=self.pool.get('event.event')
        event=event_obj.browse(cr, uid, ids[0], context=context)

        registration_ids  = [r.id for r in event.registration_ids]

        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'survey', 'email_template_survey')[1]
        except ValueError:
            template_id = False


        return {
            'type': 'ir.actions.act_window',
            'name': 'Envio Encuesta',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'from_event':True,'default_public':'email_public_link','default_use_template': True,'default_template_id': template_id,'default_event_id':ids[0]},
            'res_model': 'survey.mail.compose.message',
            'nodestroy': True,
            'target':'new', 
            }
 
 
 
class event_registration(models.Model):


    _inherit  = "event.registration"
    _mail_mass_mailing = _('Registros de Eventos')
    muestra_interes =  fields.Boolean(string='Muestra Interes',copy=False)
    solicita_presupuesto =  fields.Boolean(string='Solicita Presupuesto',copy=False)
    crm_lead_id = fields.Many2one('crm.lead', string='Oportunidad', 
        required=False, readonly=False,copy=False)
    crm_lead_company_name = fields.Char(related='crm_lead_id.company_id.name', store=False, readonly=True, copy=False,string='Compañia de la oportunidad')
    def new_so(self,cr,uid,ids,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedido de Venta',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'sale.order',
            'nodestroy': True,
            'target':'current',	
            }

    def create_lead_wizard(self, cr, uid, ids, context=None):
                    
        ctx = dict()


        '''
        ctx.update({
            'default_trabajar_festivos': self.browse(cr, uid, ids, context=context)[0].trabajar_festivos            
        })
        '''        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'acp_yanez.wizard_create_lead',
            'target': 'new',
            'context': ctx,
        } 
        



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

