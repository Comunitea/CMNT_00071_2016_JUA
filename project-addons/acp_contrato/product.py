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

from openerp.osv import fields, osv

from datetime import datetime
#import netsvc
import time
from openerp.tools.translate import _

#----------------------------------------------------------
# Sale Order
#----------------------------------------------------------
class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'mantenimiento_product_id': fields.many2one('product.product', 'Servicio Mantenimiento', help="Este es el producto que se factura cuando se hace un mantenimiento de este equipo",domain="[('type','=','service'),('sale_ok', '=', True)]", required=False),
        'tipo_producto': fields.many2one('acp_contrato.tipo_producto', 'Tipo de Producto', help="El tipo de producto añade campos adicionales al numero de serie del producto"),
        'perioricidad_servicio': fields.selection([
                     ('mensual','Mensual'),
                     ('trimestral','Trimestral'),
                     ('semestral','Semestral'),
                     ('anual','Anual'),
                      ], 'Periodicidad Matenimiento',  select=True, help="Periodicidad que se utilizará para la programación de servicios de matenimiento"),
        'tipo_servicio': fields.many2one('acp_contrato.tipo_servicio', 'Tipo Servicio', select=True,required=False, help="Tipo de Servicio asociado al matenimiento del producto"),
  }
product_template()


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    def onchange_product_id(self, cr, uid, ids, product, context=None):
        print "**********  CAMBIO TIPO DE PRODUCTO *************"
        if not product:
             return {'value': {'tipo_producto': False}}

        product_rec = self.pool.get('product.product').browse(cr, uid, product, context=context)


        val = {
            'tipo_producto': product_rec.tipo_producto and product_rec.tipo_producto.id or False,
            'tipo_producto_n': product_rec.tipo_producto and product_rec.tipo_producto.name or False,
        }
        return {'value': val}

    _columns = {
        'tipo_producto': fields.related('product_id', 'tipo_producto', type='many2one', relation='acp_contrato.tipo_producto', string="Tipo de Producto", readonly="1"),
        'tipo_producto_n': fields.char(string="Tipo de Producto Nombre", size=64),
        'fecha_garantia': fields.date('Fecha fin garantía'),
    }

stock_production_lot()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
