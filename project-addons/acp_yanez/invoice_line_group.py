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

from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'line_group_ids' : fields.one2many('acp_yanez.invoice_line_group','invoice_id','Lineas',copy=False),
    }
    
class invoice_line_group(osv.osv):
    _name = "acp_yanez.invoice_line_group"
    _auto = False
    #_rec_name = 'order_id'

    def _taxs(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        _tax_pool = self.pool.get('account.tax')

        for _obj in self.browse(cr, uid, ids, context=context):
            if _obj.tax_array:
                _taxes = _tax_pool.search(cr, uid, [('id', 'in', eval(_obj.tax_array)), ], context=context)
            else:
                _taxes = False
            res[_obj.id] =_taxes
        return res

    def _taxs_print(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        _tax_pool = self.pool.get('account.tax')

        for _obj in self.browse(cr, uid, ids, context=context):
            if _obj.tax_array:
                _taxes = ''
                for t in _tax_pool.browse(cr, uid, eval(_obj.tax_array), context=context):
                    _taxes = _taxes + t.name + ' '
            else:
                _taxes = ''
            res[_obj.id] =_taxes
        return res
        
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Factura', readonly=True),
        'template_id': fields.many2one('product.template', 'Producto', readonly=True),                
        'name': fields.text('Descripción', readonly=True),        
        'tax_array': fields.char('Tax Array', readonly=True),        
        'tax_ids': fields.function(_taxs, string="Impuestos", type="many2many", relation='account.tax'),
        'tax_print': fields.function(_taxs_print, string="Impuestos", type="char"),        
        'total': fields.float('Subtotal', digits_compute= dp.get_precision('Product Price'), readonly=True),
    }
    #_order = 'order_id desc, id '


    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW acp_yanez_invoice_line_group as (
                         SELECT Min(account_invoice_line.id) AS id,
                                account_invoice_line.company_id,
                                invoice_id,
                                product_template.id AS template_id,
                            CASE
                                WHEN product_template.id IS NOT NULL THEN                                
                                   (SELECT String_agg(l.NAME, Chr(10)) AS _list
                                    FROM
                                      (SELECT l1.NAME,
                                              l1.invoice_id,
                                              l1.id
                                       FROM account_invoice_line AS l1
                                       LEFT OUTER JOIN product_product p1 ON (l1.product_id = p1.id)
                                       LEFT OUTER JOIN product_template t1 ON (p1.product_tmpl_id = t1.id)
                                       WHERE l1.invoice_id = account_invoice_line.invoice_id
                                         AND t1.id = product_template.id
                                         AND coalesce(
                                                        (SELECT array_agg(tax_id)
                                                         FROM account_invoice_line_tax
                                                         WHERE account_invoice_line_tax.invoice_line_id = l1.id),'{-99}'::integer[]) = coalesce(tax_array,'{-99}'::integer[])
                                       ORDER BY invoice_id DESC, id) AS l) 
                                ELSE
                                   (SELECT String_agg(l.NAME, Chr(10)) AS _list
                                    FROM
                                      (SELECT l1.NAME,
                                              l1.invoice_id,
                                              l1.id
                                       FROM account_invoice_line AS l1
                                       WHERE l1.invoice_id = account_invoice_line.invoice_id
                                         AND l1.product_id IS NULL
                                         AND coalesce(
                                                        (SELECT array_agg(tax_id)
                                                         FROM account_invoice_line_tax
                                                         WHERE account_invoice_line_tax.invoice_line_id = l1.id),'{-99}'::integer[]) = coalesce(tax_array,'{-99}'::integer[])
                                       ORDER BY invoice_id DESC, id) AS l) 
                            END AS NAME,                       
                                tax_array,
                                Sum(price_subtotal) AS total
                         FROM
                           (SELECT id,
                                   company_id,
                                   invoice_id,
                                   product_id,
                                   price_subtotal, 
                              (SELECT array_agg(tax_id)
                               FROM account_invoice_line_tax
                               WHERE account_invoice_line_tax.invoice_line_id = account_invoice_line.id) AS tax_array
                            FROM account_invoice_line) AS account_invoice_line
                         LEFT OUTER JOIN product_product ON (account_invoice_line.product_id = product_product.id)
                         LEFT OUTER JOIN product_template ON (product_product.product_tmpl_id = product_template.id)
                         GROUP BY account_invoice_line.company_id, invoice_id, tax_array, product_template.id,
                           (SELECT array_agg(tax_id)
                            FROM account_invoice_line_tax
                            WHERE account_invoice_line_tax.invoice_line_id = account_invoice_line.id)
                         ORDER BY invoice_id DESC,
                                  id
                                 )""" )
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
