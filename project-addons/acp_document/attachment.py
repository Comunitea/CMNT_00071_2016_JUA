# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Infoacp (http://www.infoacp.es)
#                       Alejandro Cano <alejandro.cano@infoacp.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import base64
from tempfile import TemporaryFile

from openerp import tools
from openerp.osv import fields, orm, osv
try:
    # Python 3
    from urllib import parse as urlparse
except:
    from urlparse import urlparse


class ir_attachment(osv.osv):


    _inherit  = "ir.attachment"
    
    def _type_selection(self, cr, uid, context=None):
        
        return []
        #sobreescribir para devolver los valores deseados
        #return [('justificante', 'Justificante Transferencia'), ('mandato', 'Mandato')]
        

    def _name_get_modelname(self, cr, uid, ids, object, method, context):
        data = {}
        for attachment in self.browse(cr, uid, ids, context=context):
            model_object = attachment.res_model
            if model_object :
                model_id = self.pool['ir.model'].search(cr, uid, [('model','=',model_object)], context=context)

                if model_id:
                    
                    data[attachment.id] = self.pool['ir.model'].browse(cr, uid, model_id[0], context=context).name
                else:
                    data[attachment.id] = False
        return data
    _columns = {
        'category_id': fields.many2many('acp_document.category', 'acp_document_category_rel', 'doc_id', 'category_id', 'Categorias'),
        'model_name': fields.function(_name_get_modelname, type='char', string='Modelo', store=True),
        'tipo_documento': fields.selection(_type_selection,'Tipo de documento', required=False),         
        #'tipo_dedocumento': fields.many2one('acp_document.tipo_documento', 'Tipo de documento', select=True),        
        'fecha_recepcion': fields.date('Fecha recepción', required=False), 
        'fecha_devolucion': fields.date('Fecha devolución', required=False), 
        'original': fields.boolean('¿Original?', required=False), 
        'devuelto': fields.boolean('¿Se devolvió al cliente?', required=False), 
        'firmado': fields.boolean('Versión firmada', required=False), 
        'definitivo': fields.boolean('Versión definitiva', required=False), 
        'ubicacion': fields.char('Ubicación', required=False), 
                
    }
    
    def write(self, cr, uid, ids, vals, context=None):
 
        if context is None:
            context = {}

        if vals.has_key('datas_fname') and vals.has_key('type'):
            if vals.get('type') == 'binary':
                if not vals.get('name',False):
                    vals['name'] = vals.get('datas_fname')        
        return super(ir_attachment, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid,  vals, context=None):
 
        if context is None:
            context = {}
            
        if vals.has_key('datas_fname') and vals.has_key('type'):
            if vals.get('type') == 'binary':
                if not vals.get('name',False):
                    vals['name'] = vals.get('datas_fname')


        return super(ir_attachment, self).create(cr, uid,  vals, context=context)

            
ir_attachment()



class acp_document_category(osv.osv):
    _name = "acp_document.category"
    _description = "Categorias de archivos"
    _columns = {
        
        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),                   
     }      
   
   
acp_document_category()
'''
class acp_document_tipo_documento(osv.osv):
    _name = "acp_document.tipo_documento"
    _description = "tipos de documento"
    _columns = {
        
        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),           
    }    
    _defaults = {
        'active': 1,
    }
    
    _sql_constraints = [
        ('unique_origen_cliente', 'unique(name)', 'nombre debe ser unico !'),
        
    ]
acp_document_tipo_documento() 
'''
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

