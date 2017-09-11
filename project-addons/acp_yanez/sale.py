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

from datetime import datetime, timedelta,date
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow
import urlparse
import uuid
import logging
from openerp import tools

_logger = logging.getLogger(__name__)

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _meeting_count2(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        # The current user may not have access rights for sale orders
        try:
            for order in self.browse(cr, uid, ids, context):
                res[order.id] = len(order.meeting_ids)
        except:
            pass
        return res 

    def _meeting_count(self, cr, uid, ids, field_name, arg, context=None):
        Event = self.pool['calendar.event']
        return {
            order_id: Event.search_count(cr,uid, [('sale_order_id', '=', order_id)], context=context)
            for order_id in ids
        }        
    def _data_get_cg(self, cr, uid, ids, name, arg, context=None):
        ira = self.pool['ir.attachment'] 
        if context is None:
            context = {}
        result = {}
        bin_size = context.get('bin_size')
        attch_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.condiciones_generales 
        if attch_id :
           attch_id = attch_id.id
        else:
            for sale in self.browse(cr, uid, ids, context=context):  
                result[sale.id] = False
            return result    

        for sale in self.browse(cr, uid, ids, context=context):
            attach = ira.browse(cr, 1, attch_id, context=context)
            if attach.store_fname:
                result[sale.id] = attach._file_read( attach.store_fname, bin_size)
            else:
                result[sale.id] = attach.db_datas
        return result

    def _data_get_cg_n(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}		
        for sale in self.browse(cr, uid, ids, context=context):
            result[sale.id] = 'Condiciones Generales.pdf'
        return result
        
    def _data_get_ni(self, cr, uid, ids, name, arg, context=None):
        ira = self.pool['ir.attachment'] 
        if context is None:
            context = {}
        result = {}
        bin_size = context.get('bin_size')
        attch_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.normas_internas 
        if attch_id :
           attch_id = attch_id.id
        else:
            for sale in self.browse(cr, uid, ids, context=context):  
                result[sale.id] = False
            return result         
        for sale in self.browse(cr, uid, ids, context=context):
            attach = ira.browse(cr, 1, attch_id, context=context)
            if attach.store_fname:
                result[sale.id] = attach._file_read( attach.store_fname, bin_size)
            else:
                result[sale.id] = attach.db_datas
        return result

    def _data_get_ni_n(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}		
        for sale in self.browse(cr, uid, ids, context=context):
            result[sale.id] = 'Normas Internas.pdf'
        return result  
    def _data_get_m(self, cr, uid, ids, name, arg, context=None):
        ira = self.pool['ir.attachment'] 
        if context is None:
            context = {}
        result = {}
        bin_size = context.get('bin_size')
        attch_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.mandato 
        if attch_id :
           attch_id = attch_id.id
        else:
            for sale in self.browse(cr, uid, ids, context=context):  
                result[sale.id] = False
            return result            
        for sale in self.browse(cr, uid, ids, context=context):
            attach = ira.browse(cr, 1, attch_id, context=context)
            if attach.store_fname:
                result[sale.id] = attach._file_read( attach.store_fname, bin_size)
            else:
                result[sale.id] = attach.db_datas
        return result

    def _data_get_m_n(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}		
        for sale in self.browse(cr, uid, ids, context=context):
            result[sale.id] = 'Mandato.pdf'
        return result     
        
    def _data_get_m_empresa(self, cr, uid, ids, name, arg, context=None):
        ira = self.pool['ir.attachment'] 
        if context is None:
            context = {}
        result = {}
        bin_size = context.get('bin_size')
        attch_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.mandato_empresa
        if attch_id :
           attch_id = attch_id.id
        else:
            for sale in self.browse(cr, uid, ids, context=context):  
                result[sale.id] = False
            return result            
        for sale in self.browse(cr, uid, ids, context=context):
            attach = ira.browse(cr, 1, attch_id, context=context)
            if attach.store_fname:
                result[sale.id] = attach._file_read( attach.store_fname, bin_size)
            else:
                result[sale.id] = attach.db_datas
        return result

    def _data_get_m_empresa_n(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}		
        for sale in self.browse(cr, uid, ids, context=context):
            result[sale.id] = 'Mandato.pdf'
        return result
        


    _columns = {
        'comment': fields.text('Notas Internas', translate=True, help="Notas Internas",readonly=True, states={'draft': [('readonly', False)]}),
        'department_user_id': fields.many2one('res.users', 'Responsable Departamento', select=True,readonly=True, states={'draft': [('readonly', False)]}),
        'expense_provision': fields.float('Provision Gastos', digits_compute= dp.get_precision('Provision Gastos'),readonly=True, states={'draft': [('readonly', False)]}),
        'ok_terms_conditions' : fields.boolean('Acepta Terminos y Condiciones',readonly=True, states={'draft': [('readonly', False)],'sent': [('readonly', False)]},copy=False),
        'meeting_count': fields.function(_meeting_count, string="# Agenda", type='integer'),
        'condiciones_generales': fields.function(_data_get_cg, string='File Content', type="binary", nodrop=True),        
        'condiciones_generales_n': fields.function(_data_get_cg_n, string='File Content', type="char" ),   
        'normas_internas': fields.function(_data_get_ni, string='File Content', type="binary", nodrop=True),        
        'normas_internas_n': fields.function(_data_get_ni_n, string='File Content', type="char" ), 
        'mandato': fields.function(_data_get_m, string='File Content', type="binary", nodrop=True),        
        'mandato_n': fields.function(_data_get_m_n, string='File Content', type="char" ), 
        'mandato_empresa': fields.function(_data_get_m_empresa, string='File Content', type="binary", nodrop=True),        
        'mandato_empresa_n': fields.function(_data_get_m_empresa_n, string='File Content', type="char" ), 

        'is_company' : fields.related('partner_id','is_company',type='boolean',string='Es una empresa'),        
        'payment_mode_id2': fields.many2one('payment.mode', 'Modo de Pago',readonly=True, states={'draft': [('readonly', False)],'sent': [('readonly', False)]} ,copy=False),                
        'payment_term2': fields.many2one('account.payment.term', 'Plazo de Pago' ,readonly=True, states={'draft': [('readonly', False)],'sent': [('readonly', False)]},copy=False),                        
        'desglose_id' : fields.one2many('acp_yanez.sale_order_desglose','sale_id','Desglose',copy=False),
        'adjunto_id' : fields.one2many('acp_yanez.sale_attachment','sale_id','Adjuntos',domain=[('active', '=', True)],copy=False),        
        'dummy_mostrar_adjuntos' : fields.boolean('mostrar adjuntos' , copy=False),        
        'dummy_mostrar_desglose' : fields.boolean('mostrar adjuntos' , copy=False),        
        'ready_to_pay' : fields.boolean('Listo para pagar' , copy=False),        
        'etapa' : fields.integer('Etapa' , copy=False),        
        'tipo_documento' : fields.related('payment_mode_id2', 'tipo_documento', type='char', string='Tipo de documento',copy=False),
        'fecha_confirmacion' : fields.date('Fecha Confirmación', copy=False),
        
        
    }

    _defaults = {
               'etapa':1,
              }
    def etapa1_siguiente(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'etapa':2})
        return True
        
    def etapa2_anterior(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'etapa':1})
        return True        
    def etapa2_siguiente(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'etapa':3})
        return True

    def etapa3_anterior(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'etapa':2})
        return True        
    def etapa3_siguiente(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'etapa':4})
        return True

    def etapa4_anterior(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'etapa':3})
        return True        
    def etapa4_siguiente(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'etapa':5})
        return True        

    def etapa5_anterior(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'etapa':4})
        return True        
    def etapa5_siguiente(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'etapa':6})
        return True

    def etapa6_anterior(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'etapa':5})
        return True        

        
    def ok_terms(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'ok_terms_conditions':True})
        return True
    def open_wizard_import(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None: context = {}
        # generic error checking
        if not ids: return False
        if not isinstance(ids, list): ids = [ids]
    

        res = mod_obj.get_object_reference(cr, uid, 'acp_yanez', 'view_acp_yanez_import')
        res_id = res and res[1] or False,        
        return {
            'name': 'Seleccionar Plazo de Pago',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'acp_yanez.import',
            #'res_id': wizard_id,
            'type': 'ir.actions.act_window',
            'view_id': [res_id],
            'target': 'new',
            'context': context,
        }
        
            
    def open_wizard_payment_mode(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        mode_obj = self.pool.get('payment.mode')
        if context is None: context = {}
        # generic error checking
        if not ids: return False
        if not isinstance(ids, list): ids = [ids]
    
        wizard_id = self.pool.get('acp_yanez.select_payment_mode').create(cr, uid, vals={'sale_id':ids[0]}, context=context)
        mode_ids = mode_obj.search(cr,uid,[('visible_online','=',True)],context=context)
        for mode_id in mode_ids:
            self.pool.get('acp_yanez.select_payment_mode_l').create(cr, uid, vals={'wiz_id':wizard_id,'mode_id':mode_id}, context=context)

        res = mod_obj.get_object_reference(cr, uid, 'acp_yanez', 'acp_yanez_view_select_payment_mode')
        res_id = res and res[1] or False,        
        return {
            'name': 'Seleccionar Plazo de Pago',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'acp_yanez.select_payment_mode',
            'res_id': wizard_id,
            'type': 'ir.actions.act_window',
            'view_id': [res_id],
            'target': 'new',
            'context': context,
        }
    def open_wizard_payment_term(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        term_obj = self.pool.get('account.payment.term')
        order_obj = self.pool.get('sale.order')
        if context is None: context = {}
        print 'context'
        print context
        # generic error checking
        if not ids: return False
        if not isinstance(ids, list): ids = [ids]
        order = order_obj.browse(cr, uid, ids[0], context=context)
        
        wizard_id = self.pool.get('acp_yanez.select_payment_term').create(cr, uid, vals={'sale_id':ids[0]}, context=context)
        for term in self.browse(cr, uid, ids, context=context).payment_mode_id2.terms_ids:
            if term.importe_minimo < order.amount_total:
                self.pool.get('acp_yanez.select_payment_term_l').create(cr, uid, vals={'wiz_id':wizard_id,'term_id':term.id}, context=context)



        res = mod_obj.get_object_reference(cr, uid, 'acp_yanez', 'acp_yanez_view_select_payment_term')
        res_id = res and res[1] or False,        
        return {
            'name': 'Seleccionar Plazo de Pago',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'acp_yanez.select_payment_term',
            'res_id': wizard_id,
            'type': 'ir.actions.act_window',
            'view_id': [res_id],
            'target': 'new',
            'context': context,
        }
  

    def action_button_confirm(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
        #Envio de notificacion
        self.send_mail_confirm(cr, uid, ids) 
        self.write(cr, uid, ids, {'etapa':999,'fecha_confirmacion':date.today().strftime('%Y-%m-%d')})
        return res        
        
    def action_button_confirm_portal(self, cr, uid, ids, context=None):
        res_obj = self.pool.get('res.partner')
        ir_obj = self.pool.get('ir.attachment')
        ir_sale_obj = self.pool.get('acp_yanez.sale_attachment')
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        
        for o in self.browse(cr, uid, ids):
            if not o.payment_mode_id2:
                raise osv.except_osv(_('Warning!'), _("Debe selecionar un modo de pago.")) 
            if not o.payment_term2:
                raise osv.except_osv(_('Warning!'), _("Debe selecionar un plazo de pago.")) 
            if not o.ok_terms_conditions:
                raise osv.except_osv(_('Warning!'), _("Debe aceptar los Terminos y Condiciones.")) 
            #Comprobamos que están los documentos
            if o.payment_mode_id2.tipo_documento:
                if o.payment_mode_id2.guardar == 'cliente':
                    #buscamos en el cliente por si ya esta subido con anterioridad
                    _ids = ir_obj.search(cr, uid,[('tipo_documento','=',o.payment_mode_id2.tipo_documento),('res_model','=','res.partner'),('res_id','=',o.partner_id.id)] ,context=context)
                    if len(_ids) == 0:
                        #si no , buscamso en el pedido por si se acaba de subir el documento
                        _ids = ir_sale_obj.search(cr, uid,[('active','=',True),('tipo','=',o.payment_mode_id2.tipo_documento),('sale_id','=',o.id)] ,context=context)
                        if len(_ids) == 0:                        
                            raise osv.except_osv(_('Warning!'), "Debe adjuntar la siguente documentacion para poder aceptar el presupuesto: %s"%(o.payment_mode_id2.tipo_documento,)) 
                else:
                    #buscamos en el pedido por si ya esta subido con anterioridad o lo ha subido un administrador diretamente 
                    _ids = ir_obj.search(cr, uid,[('tipo_documento','=',o.payment_mode_id2.tipo_documento),('res_model','=','sale.order'),('res_id','=',o.id)] ,context=context)
                    if len(_ids) == 0:
                        #si no , buscamso en el pedido por si se acaba de subir el documento
                        _ids = ir_sale_obj.search(cr, uid,[('active','=',True),('tipo','=',o.payment_mode_id2.tipo_documento),('sale_id','=',o.id)] ,context=context)
                        if len(_ids) == 0:                        
                            raise osv.except_osv(_('Warning!'), "Debe adjuntar la siguente documentacion para poder aceptar el presupuesto: %s"%(o.payment_mode_id2.tipo_documento,)) 
            #vamos a subir los documentos a su modelo correspondiente , insertamso en ir_attachment
            if o.payment_mode_id2.tipo_documento:
                for adjunto in o.adjunto_id:
                    if adjunto.tipo == o.payment_mode_id2.tipo_documento:
                        if o.payment_mode_id2.guardar == 'cliente':
                            #adjuntamos al cliente
                            ir_obj.create(cr, uid,{'tipo_documento':adjunto.tipo,'datas_fname':adjunto.data_fname,'res_model':'res.partner','res_id': o.partner_id.id,'db_datas':adjunto.data,'name':adjunto.data_fname,'type':'binary'},context=context)
                        else:
                            #adjuntamos al presupuesto
                            ir_obj.create(cr, uid,{'tipo_documento':adjunto.tipo,'datas_fname':adjunto.data_fname,'res_model':'sale.order','res_id': o.id,'db_datas':adjunto.data,'name':adjunto.data_fname,'type':'binary'},context=context)
            #copiamo el plazo de pago y el modo de pago
            o.write({'payment_mode_id':o.payment_mode_id2.id,'payment_term':o.payment_term2.id})
        #Envio de notificacion
        self.send_mail_confirm(cr, uid, ids)             
        self.signal_workflow(cr, uid, ids, 'order_confirm')
        self.write(cr, uid, ids, {'etapa':999,'fecha_confirmacion':date.today().strftime('%Y-%m-%d')})
        return True    

    def action_button_confirm_portal_pay(self, cr, uid, ids, context=None):
        res_obj = self.pool.get('res.partner')
        ir_obj = self.pool.get('ir.attachment')
        ir_sale_obj = self.pool.get('acp_yanez.sale_attachment')
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        
        for o in self.browse(cr, uid, ids):
            if o.ready_to_pay:
                raise osv.except_osv(_('Warning!'), _("Realice el pago para poder continuar con el proceso.")) 
            if not o.payment_mode_id2:
                raise osv.except_osv(_('Warning!'), _("Debe selecionar un modo de pago.")) 
            if not o.payment_term2:
                raise osv.except_osv(_('Warning!'), _("Debe selecionar un plazo de pago.")) 
            if not o.ok_terms_conditions:
                raise osv.except_osv(_('Warning!'), _("Debe aceptar los Terminos y Condiciones.")) 
            #Comprobamos que están los documentos
            if o.payment_mode_id2.tipo_documento:
                if o.payment_mode_id2.guardar == 'cliente':
                    #buscamos en el cliente por si ya esta subido con anterioridad
                    _ids = ir_obj.search(cr, uid,[('tipo_documento','=',o.payment_mode_id2.tipo_documento),('res_model','=','res.partner'),('res_id','=',o.partner_id.id)] ,context=context)
                    if len(_ids) == 0:
                        #si no , buscamso en el pedido por si se acaba de subir el documento
                        _ids = ir_sale_obj.search(cr, uid,[('active','=',True),('tipo','=',o.payment_mode_id2.tipo_documento),('sale_id','=',o.id)] ,context=context)
                        if len(_ids) == 0:                        
                            raise osv.except_osv(_('Warning!'), "Debe adjuntar la siguente documentacion para poder aceptar el presupuesto: %s"%(o.payment_mode_id2.tipo_documento,)) 
                else:
                    #buscamos en el pedido por si ya esta subido con anterioridad o lo ha subido un administrador diretamente 
                    _ids = ir_obj.search(cr, uid,[('tipo_documento','=',o.payment_mode_id2.tipo_documento),('res_model','=','sale.order'),('res_id','=',o.id)] ,context=context)
                    if len(_ids) == 0:
                        #si no , buscamso en el pedido por si se acaba de subir el documento
                        _ids = ir_sale_obj.search(cr, uid,[('active','=',True),('tipo','=',o.payment_mode_id2.tipo_documento),('sale_id','=',o.id)] ,context=context)
                        if len(_ids) == 0:                        
                            raise osv.except_osv(_('Warning!'), "Debe adjuntar la siguente documentacion para poder aceptar el presupuesto: %s"%(o.payment_mode_id2.tipo_documento,)) 
            #vamos a subir los documentos a su modelo correspondiente , insertamso en ir_attachment
            if o.payment_mode_id2.tipo_documento:
                for adjunto in o.adjunto_id:
                    if adjunto.tipo == o.payment_mode_id2.tipo_documento:
                        if o.payment_mode_id2.guardar == 'cliente':
                            #adjuntamos al cliente
                            ir_obj.create(cr, uid,{'tipo_documento':adjunto.tipo,'datas_fname':adjunto.data_fname,'res_model':'res.partner','res_id': o.partner_id.id,'db_datas':adjunto.data,'name':adjunto.data_fname,'type':'binary'},context=context)
                        else:
                            #adjuntamos al presupuesto
                            ir_obj.create(cr, uid,{'tipo_documento':adjunto.tipo,'datas_fname':adjunto.data_fname,'res_model':'sale.order','res_id': o.id,'db_datas':adjunto.data,'name':adjunto.data_fname,'type':'binary'},context=context)
            #copiamo el plazo de pago y el modo de pago
            o.write({'payment_mode_id':o.payment_mode_id2.id,'payment_term':o.payment_term2.id,'ready_to_pay':True})
        #Envio de notificacion
        #self.send_mail_confirm(cr, uid, ids)             
        #self.signal_workflow(cr, uid, ids, 'order_confirm')
        return True  
    def send_mail_depart(self, cr, uid, ids, context=None):
        email_template_obj = self.pool.get('email.template')
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        if company.mail_depart_template:
            template_ids = company.mail_depart_template.id
        else:
            return True
        #_logger.info('Template_id: ',template_ids)
        if template_ids:    	
            for o in self.browse(cr, uid, ids):
                values = email_template_obj.generate_email(cr, uid, template_ids, ids[0], context=context)
                values['res_id'] = o.id
                values['notification'] = True
                mail_mail_obj = self.pool.get('mail.mail')
                msg_id = mail_mail_obj.create(cr, uid, values, context=context)
                if msg_id:
                    mail_mail_obj.send(cr, uid, [msg_id], context=context) 
        return True 

    def send_mail_confirm(self, cr, uid, ids, context=None):
        email_template_obj = self.pool.get('email.template')
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        if company.mail_confirm_template:
            template_ids = company.mail_confirm_template.id
        else:
            return True
        #_logger.info('Template_id: ',template_ids)
        if template_ids:    	
            for o in self.browse(cr, uid, ids):
                values = email_template_obj.generate_email(cr, uid, template_ids, ids[0], context=context)
                values['res_id'] = o.id
                values['notification'] = True
                mail_mail_obj = self.pool.get('mail.mail')
                msg_id = mail_mail_obj.create(cr, uid, values, context=context)
                if msg_id:
                    mail_mail_obj.send(cr, uid, [msg_id], context=context) 
                    
        return True          

    def send_mail_survey_cancel(self, cr, uid, ids, context=None):
        """ Proceso que envia cuestionario cuando se ha desestimado un presupuesto"""
        if context is None:
            context = {}

        survey_obj = self.pool.get('survey.survey')
        #survey_ids = survey_obj.search(cr, uid, [('title','=','Encuesta Presupuestos Desestimados')]) 
        email_template_obj = self.pool.get('email.template')
       
        #template_ids = email_template_obj.search(cr, uid, [('name','=','Encuesta Presupuestos Desestimados')])     
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        if company.mail_survey_template:
            template_ids = company.mail_survey_template.id
        else:
            return True   
        if company.survey:
            survey_ids = company.survey.id
        else:
            return True                   
            
        survey_response_obj = self.pool.get('survey.user_input')
        mail_mail_obj = self.pool.get('mail.mail')
        try:
            model, anonymous_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'portal', 'group_anonymous')
        except ValueError:
            anonymous_id = None

        if not survey_ids:
            raise osv.except_osv(_('Warning!'), _("No está definida la encuesta Encuesta Presupuestos Desestimados.")) 
        survey_name = survey_obj.browse(cr, uid, survey_ids, context=context).title
        survey_arg = ""            

        if not template_ids :
            raise osv.except_osv(_('Warning!'), _("No está definida la plantilla de correo Encuesta Presupuestos Desestimados."))                        


        def create_response_and_send_mail(wizard, token, partner_id, email,res_id):
            """ Crear un correo por los destinatarios y reemplazar __URL__ por vínculo con testigo de identificación """

            url_public = survey_obj._get_public_url(cr, uid, survey_obj.browse(cr, uid, survey_ids, context=context).id, survey_name, survey_arg, context=context)
            url = urlparse.urlparse(url_public[1]).path[1:]

            if token:
                url = url + '/' + token

            # post the message
            values = {
                'model': 'sale.order',
                'res_id': res_id,
                'subject': wizard.subject,
                'body': wizard.body_html.replace("__URL__", url),
                'body_html': wizard.body_html.replace("__URL__", url),
                'parent_id': None,
                'partner_ids': partner_id and [(4, partner_id)] or None,
                'notified_partner_ids': partner_id and [(4, partner_id)] or None,
                'attachment_ids': wizard.attachment_ids or None,
                'email_from': wizard.email_from or None,
                'email_to': email,
                'notification': True
            }
            mail_id = mail_mail_obj.create(cr, uid, values, context=context)
            mail_mail_obj.send(cr, uid, [mail_id], context=context)

        def create_token(partner_id, email):
            if context.get("survey_resent_token"):
                response_ids = survey_response_obj.search(cr, uid, [('survey_id', '=', survey_obj.browse(cr, uid, survey_ids, context=context).id), ('state', 'in', ['new', 'skip']), '|', ('partner_id', '=', partner_id), ('email', '=', email)], context=context)
                if response_ids:
                    return survey_response_obj.read(cr, uid, response_ids, ['token'], context=context)[0]['token']

            token = uuid.uuid4().__str__()
            # create response with token
            survey_response_obj.create(cr, uid, {
                'survey_id': survey_obj.browse(cr, uid, survey_ids, context=context).id,
                'date_create': datetime.now(),
                'type': 'link',
                'state': 'new',
                'token': token,
                'partner_id': partner_id,
                'email': email})
            return token

        for o in self.browse(cr, uid, ids):                
            for wizard in email_template_obj.browse(cr, uid, template_ids, context=context):
                # check if __URL__ is in the text
                if wizard.body_html.find("__URL__") < 0:
                    raise osv.except_osv(_('Warning!'), _("The content of the text don't contain '__URL__'. \
                        __URL__ is automaticaly converted into the special url of the survey."))

                token = create_token(o.partner_id.id, o.partner_id.email)
                create_response_and_send_mail(wizard, token,  o.partner_id.id, o.partner_id.email,o.id)                      
    


                                                                 
    def action_wait(self, cr, uid, ids, context=None):
        context = context or {}
        res_partner_obj = self.pool.get('res.partner')
        res = super(sale_order, self).action_wait(cr, uid, ids, context=context)
        for o in self.browse(cr, uid, ids):
            # Cambia de cliente potencial a cliente cuando se confirma el presupuesto
            #if o.partner_id.lead:
            #	res_partner_obj.write(cr, uid, [o.partner_id.id], {'customer': True, 'lead': False})
            
            #Envio de notificacion
            self.send_mail_depart(cr, uid, ids)   

        return res


    def action_cancel(self, cr, uid, ids, context=None):
               
        if context is None:
            context = {}
        res = super(sale_order, self).action_cancel(cr, uid, ids, context=context)
        #Envio de notificacion
        self.send_mail_depart(cr, uid, ids)
        return res  

    def action_button_cancel_portal(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        res = super(sale_order, self).action_cancel(cr, uid, ids, context=context)
        #Envio de notificacion
        self.send_mail_depart(cr, uid, ids)
        #Envio de encuesta al cliente 
        self.send_mail_survey_cancel(cr, uid, ids)       
        return res  

    def action_make_meeting(self, cr, uid, ids, context=None):
        """        
        """
        partner_ids = []
        order = self.browse(cr, uid, ids[0], context)
        if order.partner_id:
            partner_ids.append(order.partner_id.id)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'calendar', 'action_calendar_event', context)
        res['context'] = {
            'default_sale_order_id': order.id,
            'default_partner_ids': partner_ids,
            'default_user_id': uid,
        }
        return res                  

sale_order()


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"


    def _producto(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))


        for line in self.browse(cr, 1, ids, context):
            res[line.id] = line.product_id.product_tmpl_id.name

        return res 
        
    _columns = {
        'orign_term_id': fields.many2one('account.payment.term', 'Plazo de Pago Relacionado' ),                                
        'product_template_name': fields.function(_producto, string="Producto", type='char'),
        }
sale_order_line()

'''
class sale_order_line_sum(osv.osv):
    _name = "sale.order.line.sum"
    _description = "Sales Orders Line Sums"
    _auto = False
    #_rec_name = 'date'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'name': fields.char('Producto', readonly=True), 
        'order_id': fields.many2one('sale.order','Pedido', readonly=True),
        'product_tmpl_id': fields.many2one('product.template','Producto', readonly=True),
        'qty': fields.float('Cantidad', readonly=True),
        'subtotal': fields.float('Subtotal', readonly=True),
    }
    _order = 'id'

 

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, 'sale_order_line_sum')
        cr.execute("""create or replace view sale_order_line_sum as(
                      SELECT min(sale_order_line.id) as id,
                             sale_order_line.company_id, 
                             coalesce(
                                      coalesce(
                                              (select value from ir_translation where res_id =product_template.id and name = 'product.template,name' and lang='es_ES' and type='model'),product_template.name),sale_order_line.name) as name,
                             order_id,  
                             product_tmpl_id ,
                             1.0 qty,
                             sum((product_uom_qty*price_unit)-(product_uom_qty*price_unit*discount/100)) subtotal
                      FROM sale_order_line
                           left join product_product on (sale_order_line.product_id = product_product.id)
                           left join product_template on (product_product.product_tmpl_id = product_template.id)
                      group by 
                           sale_order_line.company_id,     
                           coalesce(
                                   coalesce(
                                            (select value from ir_translation where res_id =product_template.id and name = 'product.template,name' and lang='es_ES' and type='model'),product_template.name),sale_order_line.name),
                           order_id,  
                           product_tmpl_id order by id) 
            """ )
'''
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
