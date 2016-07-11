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


class res_company(osv.osv):
    _inherit = "res.company"
  

    _columns = {

        'lopd_footer_msg': fields.text('Mensaje LOPD', help="Aparecera en el pie de todas las capagnas de email." ),
        'unsubscribe_text': fields.text('Mensaje para "cancelar suscripción"' ),        
        'condiciones_generales' : fields.many2one('ir.attachment', 'Condiciones Generales', help="Documento de condiciones generales"),
        'normas_internas' : fields.many2one('ir.attachment', 'Normas Internas', help="Documento de normas internas"),        
        'mandato' : fields.many2one('ir.attachment', 'Mandato (CORE)', help="Documento de Mandato"),                
        'mandato_empresa' : fields.many2one('ir.attachment', 'Mandato (B2B)', help="Documento de Mandato"),                        
        'mail_depart_template' : fields.many2one('email.template', 'Plantilla de email cambio de estado', help="Plantilla de email para informar del cambio de estado de un pedido"),        
        'mail_confirm_template' : fields.many2one('email.template', 'Plantilla de email de confirmacion', help="Plantilla de email para de confirmación de pedido"),        
        'mail_survey_template' : fields.many2one('email.template', 'Plantilla de email para encuestas', help="Plantilla de email para enviar la encuesta al cliente"),        
        'survey' : fields.many2one('survey.survey', 'Encuesta', help="Encuesta que se envia al cliente cuando se rechaza un presupuesto"),                
        
       
      }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

