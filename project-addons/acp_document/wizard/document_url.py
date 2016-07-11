# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
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
from openerp.osv import fields, orm, osv

try:
    # Python 3
    from urllib import parse as urlparse
except:
    from urlparse import urlparse



class ir_attachment(osv.osv):
    _inherit = 'ir.attachment'
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
        'tipo_documento': fields.selection(
                [('justificante', 'Justificante Transferencia'),('mandato', 'Mandato')],
                'Tipo de documento', required=False),        
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
     }      
   
   
acp_document_category()
