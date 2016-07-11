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
import openerp.addons.decimal_precision as dp
#from mx import DateTime
#import netsvc
import time
from openerp.tools.translate import _
from openerp import tools

class account_move_line(osv.osv):
    _inherit = 'account.move.line'


    def _get_forma_pago(self,cr, uid,ids,fields,arg,context):
        x={}      
        for record in self.browse(cr, uid, ids):
            sql='''select payment_mode_id from account_invoice
                   where move_id=%s limit 1'''%(record.move_id.id)
            cr.execute(sql)    
            res = cr.fetchall()
            if len(res) >0:
                x[record.id] =  res[0][0]
            else:    
                x[record.id] =  False
        return x

    _columns = {
        'forma_pago' : fields.function(_get_forma_pago,method=True,type='many2one',relation='payment.mode', string="Modo de pago"),
    }
     
account_move_line()


class account_invoice(osv.osv):
    _inherit = 'account.invoice'


    _columns = {
        #'line_sum_id' : fields.one2many('account.invoice.line.sum','invoice_id','Lineas',copy=False),
        
    }
    
class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    def _producto(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))


        for line in self.browse(cr, uid, ids, context):
            if line.product_id:
                res[line.id] = line.product_id.product_tmpl_id.name
            else:
                res[line.id] = ''
        return res


    _columns = {
        'product_template_name': fields.function(_producto, string="Producto", type='char'),        
        
    }    
'''    
class account_invoice_line_line_sum(osv.osv):
    _name = "account.invoice.line.sum"
    _description = "Account Invoice Line Sums"
    _auto = False
    #_rec_name = 'date'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'name': fields.char('Producto', readonly=True), 
        'invoice_id': fields.many2one('account.invoice','Factura', readonly=True),
        'product_tmpl_id': fields.many2one('product.template','Producto', readonly=True),
        'qty': fields.float('Cantidad', readonly=True),
        'subtotal': fields.float('Subtotal', readonly=True),
    }
    _order = 'id'

 

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, 'account_invoice_line_sum')
        cr.execute("""create or replace view account_invoice_line_sum as(
                      SELECT min(account_invoice_line.id) as id,
                             account_invoice_line.company_id, 
                             coalesce(
                                      coalesce(
                                              (select value from ir_translation where res_id =product_template.id and name = 'product.template,name' and lang='es_ES' and type='model'),product_template.name),account_invoice_line.name) as name,
                             invoice_id,  
                             product_tmpl_id ,
                             1.0 qty,
                             sum((quantity*price_unit)-(quantity*price_unit*discount/100)) subtotal
                      FROM account_invoice_line
                           left join product_product on (account_invoice_line.product_id = product_product.id)
                           left join product_template on (product_product.product_tmpl_id = product_template.id)
                      group by 
                           account_invoice_line.company_id,     
                           coalesce(
                                   coalesce(
                                            (select value from ir_translation where res_id =product_template.id and name = 'product.template,name' and lang='es_ES' and type='model'),product_template.name),account_invoice_line.name),
                           invoice_id,  
                           product_tmpl_id order by id
                           ) 
            """ )
'''
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
