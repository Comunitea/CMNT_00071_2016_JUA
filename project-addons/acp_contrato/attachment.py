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

    def _get_contrato_id2(self, cr, uid, ids, context=None):
        cr.execute("""SELECT DISTINCT ir.id FROM ir_attachment ir 
                                    WHERE ir.res_model='acp_contrato.mail_pop' and ir.res_id = ANY(%s)""", (list(ids),))
        return [i[0] for i in cr.fetchall()]

        
    def _get_contrato_id(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        contrato_obj = self.pool.get('acp_contrato.contrato')
        mail_pop_obj = self.pool.get('acp_contrato.mail_pop')
        servicio_obj = self.pool.get('acp_contrato.servicio')
        tarea_obj = self.pool.get('acp_contrato.tarea')
        for rec in self.browse(cr, uid, ids, context=context):

            result[rec.id] = False
            if rec.res_model == 'acp_contrato.contrato':
                result[rec.id] = (contrato_obj.browse(cr, uid, rec.res_id, context=context).id,contrato_obj.browse(cr, uid, rec.res_id, context=context).name)
            if rec.res_model == 'acp_contrato.mail_pop':
                if mail_pop_obj.browse(cr, uid, rec.res_id, context=context).contrato_id:
                    result[rec.id] = (mail_pop_obj.browse(cr, uid, rec.res_id, context=context).contrato_id.id,mail_pop_obj.browse(cr, uid, rec.res_id, context=context).contrato_id.name)
            if rec.res_model == 'acp_contrato.servicio':
                if servicio_obj.browse(cr, uid, rec.res_id, context=context).contrato_id:
                    result[rec.id] = (servicio_obj.browse(cr, uid, rec.res_id, context=context).contrato_id.id,servicio_obj.browse(cr, uid, rec.res_id, context=context).contrato_id.name)

            if rec.res_model == 'acp_contrato.tarea':
                if tarea_obj.browse(cr, uid, rec.res_id, context=context).contrato_id:
                    result[rec.id] = (tarea_obj.browse(cr, uid, rec.res_id, context=context).contrato_id.id,tarea_obj.browse(cr, uid, rec.res_id, context=context).contrato_id.name)
               
            
        return result
                
    _columns = {
        'contrato_id': fields.function(_get_contrato_id,method=True,type='many2one',relation='acp_contrato.contrato', string="Contrato",            
               store={
                'ir.attachment': (lambda self, cr, uid, ids, c={}: ids, ['res_model'], 10),
                'acp_contrato.mail_pop': (_get_contrato_id2, ['contrato_id'], 10),
            })
    }

   

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

