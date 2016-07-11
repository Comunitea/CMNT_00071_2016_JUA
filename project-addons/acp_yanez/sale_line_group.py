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

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'line_group_ids' : fields.one2many('acp_yanez.sale_order_line_group','order_id','Lineas',copy=False),
    }
    
class sale_order_line_group(osv.osv):
    _name = "acp_yanez.sale_order_line_group"
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
        'order_id': fields.many2one('sale.order', 'Pedido', readonly=True),
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
        cr.execute("""CREATE or REPLACE VIEW acp_yanez_sale_order_line_group as (

                         SELECT Min(sale_order_line.id) AS id,
                                sale_order_line.company_id,
                                order_id,
                                product_template.id AS template_id,
                           (SELECT String_agg(l.NAME, Chr(10)) AS _list
                            FROM
                              (SELECT l1.NAME,
                                      l1.order_id,
                                      l1.id
                               FROM sale_order_line AS l1
                               LEFT OUTER JOIN product_product p1 ON (l1.product_id = p1.id)
                               LEFT OUTER JOIN product_template t1 ON (p1.product_tmpl_id = t1.id)
                               WHERE l1.order_id = sale_order_line.order_id
                                 AND t1.id = product_template.id
                                 AND coalesce(
                                                (SELECT array_agg(tax_id)
                                                 FROM sale_order_tax
                                                 WHERE sale_order_tax.order_line_id = l1.id),'{-99}'::integer[]) = coalesce(tax_array,'{-99}'::integer[])
                               ORDER BY order_id DESC, id) AS l) AS NAME,
                                tax_array,
                                Sum((price_unit * product_uom_qty) * (1 - (discount / 100))) AS total
                         FROM
                           (SELECT id,
                                   company_id,
                                   order_id,
                                   product_id,
                                   price_unit,
                                   product_uom_qty,
                                   discount,
                              (SELECT array_agg(tax_id)
                               FROM sale_order_tax
                               WHERE sale_order_tax.order_line_id = sale_order_line.id) AS tax_array
                            FROM sale_order_line) AS sale_order_line
                         LEFT OUTER JOIN product_product ON (sale_order_line.product_id = product_product.id)
                         LEFT OUTER JOIN product_template ON (product_product.product_tmpl_id = product_template.id)
                         GROUP BY sale_order_line.company_id, order_id, tax_array, product_template.id,
                           (SELECT array_agg(tax_id)
                            FROM sale_order_tax
                            WHERE sale_order_tax.order_line_id = sale_order_line.id)
                         ORDER BY order_id DESC,
                                  id
            )""" )
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
