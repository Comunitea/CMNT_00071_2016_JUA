# -*- coding: utf-8 -*-
import base64
import pytz
import re
import time
from openerp import netsvc
import openerp
import openerp.service.report
import uuid
import collections
import babel.dates
from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta, date
from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from openerp import api
from openerp import tools, SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.http import request
from operator import itemgetter
import sys
import logging
_logger = logging.getLogger(__name__)


class acp_contrato_bufete_report_scheduler(osv.AbstractModel):
    _name = 'acp_contrato_bufete_report.scheduler'
    _description = "Envio de informes diarios"


    def run(self, cr, uid, context=None):
        _logger.info('########################################################' )
        _logger.info('########################################################' )        
        _logger.info('              GENERACION DE INFORMES DIARIOS' )
        _logger.info('########################################################' )
        _logger.info('########################################################' )                
        now = openerp.fields.Datetime.to_string(datetime.now())
        today = date.today().strftime('%Y/%m/%d')      
        data_pool = self.pool['ir.model.data']
        mailmess_pool = self.pool['mail.message']
        mail_pool = self.pool['mail.mail']
        template_pool = self.pool['email.template']        
        mail_compose_message_pool = self.pool['mail.compose.message']        
        attachment_obj = self.pool.get('ir.attachment')
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        fields = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc',  'reply_to', 'mail_server_id','model','auto_delete']
        ##############################
        #informe horas letrado diario
        ##############################
 
        _logger.info('############################################' )        
        _logger.info(' informe horas letrado diario' )
        _logger.info('############################################' )
        try:
            mod_obj = self.pool.get('acp_contrato.bufete.horas_letrado.wizard')
            inf_dir_leatrado_id = mod_obj.create(cr, uid, {'abogado_id': False,'fecha_desde':today,'fecha_hasta':today}, context=context)
            dummy, template_id = data_pool.get_object_reference(cr, uid, 'acp_contrato_bufete_report', 'acp_contrato_report_template_horas_letrado')
            template= template_pool.generate_email_batch(cr, uid, template_id, [inf_dir_leatrado_id], fields=fields, context=context)
            logo = self.pool.get('res.partner').browse(cr, uid, 1, context=context).company_id.logo
            report_service = 'report.' + 'acp_contrato_bu_horas_letrado_jasper'
            service = netsvc.LocalService(report_service)
            (result, format) = service.create(cr, uid, [inf_dir_leatrado_id], 
                              {
                                'model': 'acp_contrato.bufete.horas_letrado.wizard',
                                'parameters': {
                                               'FECHA_DESDE': today,
                                               'FECHA_HASTA': today,
                                               'LOGO': logo
                               }
                     }, context=context)
            result = base64.b64encode(result)
            file_name = 'Horas-Letrado.pdf'
            attachment_id = attachment_obj.create(cr, uid,
                    {
                        'name': file_name,
                        'datas': result,
                        'datas_fname': file_name,
                        'res_model': 'acp_contrato.bufete.horas_letrado.wizard',
                        'res_id': inf_dir_leatrado_id,
                        'type': 'binary'
                    }, context=context)
            mail_values = {
                'subject': template[inf_dir_leatrado_id]['subject'],
                'body_html':  template[inf_dir_leatrado_id]['body_html'],
                'body':  template[inf_dir_leatrado_id]['body_html'],
                #'parent_id': wizard.parent_id and wizard.parent_id.id,
                #'partner_ids':  template[inf_dir_leatrado_id]['partner_ids'],
                'attachment_ids': [(6, 0, [attachment_id])],
                'email_from': template[inf_dir_leatrado_id]['email_from'],
                'email_to': template[inf_dir_leatrado_id]['email_to'],                
                'auto_delete':template[inf_dir_leatrado_id]['auto_delete'],
            }                     
            mail_id = self.pool['mail.mail'].create(cr, uid, mail_values, context=context)
            mail_pool.send(cr, uid, [mail_id], context=context)
        except:
            _logger.error( "ERROR ENVIADO INFORME HORAS LETRADO")
            _logger.error( sys.exc_info())
            _logger.error( "FIN INFORME ERROR")
            
        _logger.info('############################################' )        
        _logger.info(' informe horas iguala' )
        _logger.info('############################################' )
        try:
        #if 1==1:
            mod_obj = self.pool.get('acp_contrato.bufete.igualas.wizard')
            partner_obj = self.pool.get('res.partner')
            
            cr.execute("""select distinct id 
                          from res_partner
                          where 
                              id in (
                                  select partner_id 
                                  from acp_contrato_contrato 
                                  where baja=False and 
                                  state in ('exception','confirmed') and
                                  tipo_contrato = 
                                          (select res_id 
                                          from ir_model_data 
                                          where model = 'acp_contrato.tipo_contrato' and 
                                          module = 'acp_contrato_bufete' and 
                                          name = 'iguala'))""")
            for partner in cr.fetchall(): 

                partner_id = partner[0]

                wiz_id = mod_obj.create(cr, uid, {'partner_id': partner_id,'fecha_desde':today,'fecha_hasta':today}, context=context)
                wiz = mod_obj.browse(cr, uid,wiz_id, context=context)
                (data,report_id,fecha_desde_c,fecha_hasta_c,logo) = wiz.action_print( print_report=False, context = context)
                cr.commit()

                cr.execute("""select count(*) 
                              from acp_contrato_bufete_igualas_report
                               where report_id = '%s' """ % (report_id,))


                
                if cr.fetchall()[0][0] > 0:

                    dummy, template_id = data_pool.get_object_reference(cr, uid, 'acp_contrato_bufete_report', 'acp_contrato_report_template_horas_iguala')
                    template= template_pool.generate_email_batch(cr, uid, template_id, [wiz_id], fields=fields, context=context)
                    #logo = self.pool.get('res.partner').browse(cr, uid, 1, context=context).company_id.logo
                    report_service = 'report.' + 'acp_contrato_bu_igualas_jasper'
                    service = netsvc.LocalService(report_service)
                    (result, format) = service.create(cr, uid, [wiz_id], 
                                  {
                                    'model': 'acp_contrato.bufete.igualas.wizard',
                                    'form': data,                                    
                                    'parameters': {
                                                   'REPORT_ID': report_id,
                                                   'LOGO': logo
                                   }
                             }, context=context)
                    result = base64.b64encode(result)
                    file_name = 'Horas-Iguala.pdf'
                    attachment_id = attachment_obj.create(cr, uid,
                            {
                            'name': file_name,
                            'datas': result,
                            'datas_fname': file_name,
                            'res_model': 'acp_contrato.bufete.igualas.report',
                            'res_id': wiz_id,
                            'type': 'binary'
                        }, context=context)
                    part = partner_obj.browse(cr, uid,partner_id)

                    #7 lauralima
                    #8 inma juares
                    #6 yanez
                    #502
                    mail_values = {
                        'subject': template[wiz_id]['subject']+' ' + part.name,
                        'body_html':  template[wiz_id]['body_html'],
                        'body':  template[wiz_id]['body_html'],
                        #'parent_id': wizard.parent_id and wizard.parent_id.id,
                        'partner_ids':  [(6, 0, [partner_id,7,8,6,502])],#[partner_id],
                        #'recipient_ids':  [(6, 0, [17])],#[partner_id],                    
                        'attachment_ids': [(6, 0, [attachment_id])],
                        'email_from': template[wiz_id]['email_from'],
                        #'email_to': template[inf_dir_leatrado_id]['email_to'],                
                        'auto_delete':False,#template[wiz_id]['auto_delete'],
                    }                     
                    mail_id = self.pool['mail.mail'].create(cr, uid, mail_values, context=context)
                    mail_pool.send(cr, uid, [mail_id], context=context)
        except:
            _logger.error( "ERROR ENVIADO INFORME HORAS IGUALA")
            _logger.error( sys.exc_info())
            _logger.error( "FIN INFORME ERROR")
        
        
        
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
acp_contrato_bufete_report_scheduler()    
