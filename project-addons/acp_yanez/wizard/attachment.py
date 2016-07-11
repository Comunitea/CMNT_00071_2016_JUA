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

class acp_yanez_import(osv.osv_memory):


    _name = "acp_yanez.import"

    _columns = {
        'name': fields.char('Descripción', required=True),
        'tipo': fields.selection(
                [('justificante', 'Justificante Transferencia'),('mandato', 'Mandato')],
                'Tipo', required=True),         
        'data': fields.binary('Documento', required=True),
        'data_fname': fields.char('Nombre'),        
    }

    def upload_file(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        print 'context****************'
        print context
        self.pool.get('acp_yanez.sale_attachment').create(cr, uid, vals={'data_fname':this.data_fname,'sale_id':context.get('active_id'),'name':this.name,'tipo':this.tipo,'data':this.data}, context=context)
        '''
        if this.overwrite:
            context = dict(context, overwrite=True)
        fileobj = TemporaryFile('w+')
        try:
            fileobj.write(base64.decodestring(this.data))
    
            # now we determine the file format
            fileobj.seek(0)
            first_line = fileobj.readline().strip().replace('"', '').replace(' ', '')
            fileformat = first_line.endswith("type,name,res_id,src,value") and 'csv' or 'po'
            fileobj.seek(0)
    
            tools.trans_load_data(cr, fileobj, fileformat, this.code, lang_name=this.name, context=context)
        finally:
            fileobj.close()
        '''            
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

