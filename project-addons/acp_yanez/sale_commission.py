# # -*- coding: utf-8 -*-
# # -*- encoding: utf-8 -*-
# ##############################################################################
# #
# #    OpenERP, Open Source Management Solution
# #
# #    This program is free software: you can redistribute it and/or modify
# #    it under the terms of the GNU General Public License as published by
# #    the Free Software Foundation, either version 3 of the License, or
# #    (at your option) any later version.
# #
# #    This program is distributed in the hope that it will be useful,
# #    but WITHOUT ANY WARRANTY; without even the implied warranty of
# #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #    GNU General Public License for more details.
# #
# #    You should have received a copy of the GNU General Public License
# #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# #
# ##############################################################################

# from openerp.osv import fields, orm
# from openerp.tools.translate import _
# import datetime

# class res_partner_agent(orm.Model):
#     """
#         objeto de comportamiento many2many que relaciona agentes o
#         comerciales con partners
#     """
#     _inherit = "res.partner.agent"
#     _columns = {
#                 'date_from': fields.date('Desde Fecha'),                                                
#                 'date_to': fields.date('Hasta Fecha'),                    
#     }


# class sale_order(orm.Model):
#     """Modificamos las ventas para incluir el comportamiento de comisiones"""

#     _inherit = "sale.order"


#     def onchange_partner_id2(self, cr, uid, ids, date,part, early_payment_discount=False, payment_term=False,context=None):
#         """extend this event for delete early payment discount if it isn't valid to new partner or add new early payment discount"""
#         print 'onchange_partner_id22222222222222222222'        
#         sale_agent_ids = []        
#         res = self.onchange_partner_id(cr, uid, ids, part, {})
#         if not part:
#             res['value']['early_payment_discount'] = False
#             res['value']['sale_agent_ids'] = []            
#             return res

#         #CODIGO PARA EARLY PAYMENT DISCOUNT#
#         early_discs = []

#         if not early_payment_discount and res.get('value', False):
#             if not payment_term:
#                 early_discs = self.pool.get('account.partner.payment.term.early.discount').search(cr, uid, [('partner_id', '=', part), ('payment_term_id', '=', False)])
#                 if early_discs:
#                     res['value']['early_payment_discount'] = self.pool.get('account.partner.payment.term.early.discount').browse(cr, uid, early_discs[0]).early_payment_discount

#             if res['value'].get('payment_term', False):
#                 payment_term = res['value']['payment_term']

#             if payment_term or not early_discs:
#                 early_discs = self.pool.get('account.partner.payment.term.early.discount').search(cr, uid, [('partner_id', '=', part), ('payment_term_id', '=', payment_term)])
#                 if early_discs:
#                     res['value']['early_payment_discount'] = self.pool.get('account.partner.payment.term.early.discount').browse(cr, uid, early_discs[0]).early_payment_discount
#                 else:
#                     early_discs = self.pool.get('account.partner.payment.term.early.discount').search(cr, uid, [('partner_id', '=', False), ('payment_term_id', '=', payment_term)])
#                     if early_discs:
#                         res['value']['early_payment_discount'] = self.pool.get('account.partner.payment.term.early.discount').browse(cr, uid, early_discs[0]).early_payment_discount

#         #CODIGO PARA SALE COMMISSION#


#         sale_order_agent = self.pool.get('sale.order.agent')
         
#         if ids:

#             so_agent_ids = sale_order_agent.search(cr, uid, [('sale_id', 'in', ids)])
#             for  agent in so_agent_ids:
#                 sale_agent_ids.append((2, agent))
#         if res.get('value', False) and part:
#             date_order = date
#             date_order = datetime.datetime.strptime(date_order, '%Y-%m-%d %H:%M:%S').date()

#             partner = self.pool.get('res.partner').browse(cr, uid, part,context)
#             for partner_agent in partner.commission_ids:
#                 date_from = partner_agent.date_from and datetime.datetime.strptime(partner_agent.date_from, '%Y-%m-%d').date() or datetime.datetime.strptime('01011000', '%d%m%Y').date()
#                 date_to = partner_agent.date_to and datetime.datetime.strptime(partner_agent.date_to, '%Y-%m-%d').date() or datetime.datetime.strptime('01013000', '%d%m%Y').date()
#                 print 'date_order'
#                 print date_order
#                 print 'date_from'
#                 print date_from
#                 print 'date_to'
#                 print date_to
#                 if (date_order >= date_from ) and (date_order <= date_to):

#                     vals = {
#                         'agent_id': partner_agent.agent_id.id,
#                         'commission_id': partner_agent.commission_id.id,
#                     }
#                     if ids:
#                         for id in ids:
#                             vals['sale_id'] = id
    
#                     sale_agent_ids.append((0,0,vals))
#             if sale_agent_ids:
#                 res['value']['sale_agent_ids'] = sale_agent_ids
#             else:
#                 res['value']['sale_agent_ids'] = False
#         return res 
        
# class sale_order_line(orm.Model):
#     """
#         Modificamos las lineas ventas para incluir las comisiones en las
#         facturas creadas desde ventas
#     """
#     _inherit = "sale.order.line"
#     def product_id_change2(self, cr, uid, ids, pricelist, product, qty=0,
#                            uom=False, qty_uos=0, uos=False, name='',
#                            partner_id=False, lang=False, update_tax=True,
#                            date_order=False, packaging=False,
#                            fiscal_position=False,
#                            flag=False, warehouse_id=False, sale_agent_ids=False, context=None):
							   
#         order_agent_obj = self.pool.get("sale.order.agent")
#         res = super(sale_order_line, self).product_id_change_with_wh(
#             cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name,
#             partner_id, lang, update_tax, date_order, packaging,
#             fiscal_position, flag, warehouse_id, context)
#         if product:
#             list_agent_ids = []
#             product_obj = self.pool.get("product.product").browse(cr, uid,
#                                                                   product)
#             sale_line_agent = self.pool.get("sale.line.agent")
#             if ids:
#                 sale_line_agent.unlink(cr, uid, sale_line_agent.search(
#                     cr, uid, [('line_id', 'in', ids)]))
#                 res['value']['line_agent_ids'] = []
#             if not product_obj.commission_exent:
#                 order_agent_ids = []
#                 obj_list = []
#                 for agent in sale_agent_ids:
#                     if type(agent[-1]) == type(obj_list):
#                         obj_list += agent[-1]
#                     else:
#                         obj_list.append(agent[-1])
#                 for obj in obj_list:
#                     if not obj:
#                         continue
#                     if type(obj) == type({}):
#                         order_agent_ids.append(obj['agent_id'])
#                     else:
#                         order_agent_ids.append(order_agent_obj.browse(cr, uid, obj, context).agent_id.id)
#                 dic = {}
#                 for prod_record in product_obj.product_agent_ids:
#                     # no hay agentes especificados para la comisión:
#                     # se usan los agentes del pedido
#                     if not prod_record.agent_ids:
#                         for agent_id in order_agent_ids:
#                             if agent_id not in dic:
#                                 dic[agent_id] = prod_record.commission_id.id
#                     else:
#                         for agent_id in prod_record.agent_ids:
#                             #if agent_id.id in order_agent_ids:
#                             #Modificacion: siempre añadimos al agente
#                             dic[agent_id.id] = prod_record.commission_id.id
#                 for k in dic:
#                     line_agent_id = self._create_line_commission(cr, uid,
#                                                                  ids, k,
#                                                                  dic[k])
#                     list_agent_ids.append(int(line_agent_id))
#                 res['value']['line_agent_ids'] = list_agent_ids
#         return res        
# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

