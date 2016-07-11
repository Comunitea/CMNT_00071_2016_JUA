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

from openerp.osv import fields, osv

#from mx import DateTime
#import netsvc
import time
from openerp.tools.translate import _


class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _event_registration_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        # The current user may not have access rights for sale orders
        try:
            for partner in self.browse(cr, uid, ids, context):
                res[partner.id] = len(partner.event_registration_ids)
        except:
            pass
        return res    

    def _mail_message_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        # The current user may not have access rights for sale orders
        try:
            for partner in self.browse(cr, uid, ids, context):
                res[partner.id] = len(partner.mail_message_ids)
        except:
            pass
        return res    
               
    def _mass_mail_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
       
        for partner in self.browse(cr, uid, ids, context):
            res[partner.id] = len(self.pool.get('mail.mail.statistics').search(cr, uid, [('res_id','=',ids[0]),('mass_mailing_id','!=',False)]))
        return res

    def _get_mass_mail_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
       
        for partner in self.browse(cr, uid, ids, context):
            res[partner.id] = self.pool.get('mail.mail.statistics').search(cr, uid, [('res_id','=',ids[0]),('mass_mailing_id','!=',False)])
        return res

    def _attachment_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
       
        for c in self.browse(cr, uid, ids, context):
            res[c.id] = len(self.pool.get('ir.attachment').search(cr, uid, [('res_id','=',ids[0]),('res_model','=','res.partner')]))
        return res

    def _get_attachment_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
       
        for c in self.browse(cr, uid, ids, context):
            res[c.id] = self.pool.get('ir.attachment').search(cr, uid, [('res_id','=',ids[0]),('res_model','=','res.partner')])
        return res
        
    _columns = {	    
        #'lead' : fields.boolean('Cliente Potencial'),
        'mandato_text' : fields.text('Mandato'),  
        'condiciones_especiales' : fields.text('Condiciones Especiales'), 
        'origen_cliente_id' : fields.many2one('acp_yanez.origen_cliente', 'Origen Cliente', help="Origenes de Clientes"),
        'crm_tracking_campaign' : fields.many2one('crm.tracking.campaign', 'Campaign', help="Campañas de Marketing"),
        'department' : fields.char('Deparamento', size=120, select=True,  help="Departamento"),
        'event_registration_ids': fields.one2many('event.registration','partner_id','Asistencias Eventos'),
        'event_registration_count': fields.function(_event_registration_count, string='# Asistencias', type='integer'),
        'mail_message_ids': fields.many2many('mail.message','mail_message_res_partner_rel','res_partner_id', 'mail_message_id', 'Message'),
        'mail_message_count': fields.function(_mail_message_count, string='# Mensajes', type='integer'),
        'suscrito_revistaonline' : fields.boolean('Revista Online'),
        'suscrito_revistafisica' : fields.boolean('Revista Fisica'),
        'suscrito_conferencia' : fields.boolean('Conferencia'),
        'suscrito_curso' : fields.boolean('Cursos'),
        'mass_mail_ids': fields.function(_get_mass_mail_ids, string='Envios Masivos', type='one2many',  relation='mail.mail.statistics'),        
        'mass_mail_count': fields.function(_mass_mail_count, string='# of Sales Order', type='integer'),
        'attachment_ids': fields.function(_get_attachment_ids, string='Documentos', type='one2many',  relation='ir.attachment'),        
        'attachment_count': fields.function(_attachment_count, string='# Documentos', type='integer'),
        
     }

    _defaults = {
        'customer': False,
        #'lead': True,
        'country_id': 69
    }    
  

     
res_partner()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

