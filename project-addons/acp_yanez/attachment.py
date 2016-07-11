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

import base64
from tempfile import TemporaryFile

from openerp import tools
from openerp.osv import osv, fields

class ir_attachment(osv.osv):


    _inherit  = "ir.attachment"
    
    def _type_selection(self, cr, uid, context=None):
        res = super(ir_attachment, self)._type_selection(cr, uid, context=context) 
        res.append(('justificante', 'Justificante Transferencia'))
        res.append(('mandato', 'Mandato'))
        res.append(('notificacion_procesal', 'Notificación procesal'))
        res.append(('poderes', 'Poderes'))
        res.append(('modelo_plantilla','Modelos y Plantillas'))
        res.append(('informe','Informes'))
        res.append(('doc_extrajudicial','Documentación Extrajudicial'))
        res.append(('doc_probatoria','Documentación Probatoria Judicial'))
        res.append(('doc_notariales','Documentos Notariales'))
        res.append(('doc_procesales','Documentos Procesales'))
        res.append(('editorial_ja','Editorial J&A'))
        res.append(('biblioteca_ja','Biblioteca J&A'))

        
        return res
        
        
    _columns = {
        'tipo_documento': fields.selection(_type_selection,'Tipo de documento', required=False),        
        'nprotocolo': fields.char('Nº Protocolo', required=False), 
        'notario': fields.char('Notario', required=False), 
        'procurador': fields.many2one('res.partner', 'Procurador'),
    }

   

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

