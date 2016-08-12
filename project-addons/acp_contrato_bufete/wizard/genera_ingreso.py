# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class acp_contrato_genera_recibo(osv.osv_memory):
    """ Crea recibo de ventas a partir de un recibo de compras """

    _name = 'acp_contrato.genera_recibo'
    _description = 'Crea recibo de ventas a partir de un recibo de compras'


    _columns = {
        'voucher_id': fields.many2one('account.voucher', 'Recibo Compra', required=True),
        'incremento': fields.float('Incremento (%)', digits_compute= dp.get_precision('Discount'), required=True),
        'account_id':fields.many2one('account.account','Cuenta', required=True),
        'reference': fields.char('Ref #')
    }



    def action_cancel(self, cr, uid, ids, context=None):
        return {'type':'ir.actions.act_window_close'}

    def action_genera_recibo(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        data = self.read(cr, uid, ids, [], context=context)[0]

        voucher_id = data['voucher_id'][0]
        incremento = data['incremento']
        account_id = data['account_id'][0]
        reference = ''
        if data['reference']:
            reference = data['reference']

        ttype = 'sale'

        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        journal_obj = self.pool.get('account.journal')
        journal_ids = journal_obj.search(cr, uid,[('type', '=', ttype)], limit=1)
        journal_id = journal_obj.browse(cr,uid,journal_ids,context).id

        voucher_ids = voucher_obj.browse(cr,uid,voucher_id,context)
        for voucher in voucher_ids:
            if voucher.type in ('purchase','purchase_refund') and voucher.dft_contrato_id:
                new_voucher_id = voucher_obj.create(cr, uid, {'type': ttype,
                                                              'journal_id':journal_id,
                                                              'partner_id': voucher.dft_contrato_id.partner_id.id,
                                                              'dft_contrato_id': voucher.dft_contrato_id.id,
                                                              'dft_servicio_id': voucher.dft_servicio_id.id,
                                                              'account_id': voucher.dft_contrato_id.partner_id.property_account_receivable.id,
                                                              'reference': reference
                                                             }, context=context)
                if new_voucher_id:
                    for voucher_line in voucher_line_obj.browse(cr,uid,voucher_id,context):
                        new_voucher_line_id = voucher_line_obj.create(cr, uid, {'voucher_id':new_voucher_id,
                                                                                'name': voucher_line.name,
                                                                                'account_id': account_id,
                                                                                'contrato_id': voucher_line.contrato_id.id,
                                                                                'servicio': voucher_line.servicio_id.id,
                                                                                'amount': voucher_line.amount * (1+(incremento or 0.0)/100.0),
                                                                                'type': 'cr'
                                                                     }, context=context)

        # Abre la pantalla de recibos de ventas
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'account_voucher', 'view_sale_receipt_form')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recibos de Venta',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'type':'sale'}",
            'res_model': 'account.voucher',
            'nodestroy': True,
            'res_id': new_voucher_id,
            'target':'current',
            'view_id': [res_id],
            }


acp_contrato_genera_recibo()

class acp_contrato_genera_factura(osv.osv_memory):
    """ Crea factura de ventas a partir de factura de compras """

    _name = 'acp_contrato.genera_factura'
    _description = 'Crea factura de ventas a partir de factura de compras'


    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Factura Compra', required=True),
        'incremento': fields.float('Incremento (%)', digits_compute= dp.get_precision('Discount'), required=True),
    }

    def _prepara_facturas(self, cr, uid, ids, invoice_id, incremento, context=None):
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')

        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        inv_line_obj = self.pool.get('account.invoice.line')
        ir_sequence_obj = self.pool.get('ir.sequence')
        ttype = 'sale'
        journal_obj = self.pool.get('account.journal')
        journal_ids = journal_obj.search(cr, uid,[('type', '=', ttype)], limit=1)
        journal_id = journal_obj.browse(cr,uid,journal_ids,context).id


        result = []
        for invoice in invoice_obj.browse(cr, uid, invoice_id):
                cliente_id = invoice.dft_contrato_id.partner_factura_id.id
                fiscal_position_id = self.pool.get('res.partner').browse(cr, uid, cliente_id).property_account_position.id
                invoice_line_ids = invoice_line_obj.search(cr, uid,[('invoice_id','=',invoice_id)], context=context)
                #Recuperamos las lineas a facturar
                inv_line = []
                for fact_lin in invoice_line_obj.browse(cr, uid, invoice_line_ids, context=context):
                    val = invoice_line_obj.product_id_change(cr, uid, [], fact_lin.product_id.id,
                        False, partner_id=cliente_id, fposition_id=fiscal_position_id)
                    res = val['value']
                    # recupera la cuenta de ventas del producto
                    if not fact_lin.product_id :
                        prop = ir_property_obj.get(cr, uid,
                            'property_account_income_categ', 'product.category', context=context)
                        prop_id = prop and prop.id or False
                        account_id = fiscal_obj.map_account(cr, uid, fiscal_position_id or False, prop_id)
                        if not account_id:
                            raise osv.except_osv(_('Configuration Error!'),
                                    _('There is no income account defined as global property.'))
                        res['account_id'] = account_id
                    if not res.get('account_id'):
                        raise osv.except_osv(_('Configuration Error!'),
                                _('There is no income account defined for this product: "%s" (id:%d).') % \
                                 (fact_lin.name, fact_lin.product_id,))
                    quantity = fact_lin.quantity
                    price_unit = fact_lin.price_unit * (1+(incremento or 0.0)/100.0)

                    # determina el importe de la factura
                    if (quantity * price_unit) <= 0.00:
                        raise osv.except_osv(_('Incorrect Data'),
                            _('The value of Advance Amount must be positive.'))

                    inv_amount = (quantity * price_unit)

                    if not res.get('name'):
                        #TODO: should find a way to call formatLang() from rml_parse
                        symbol = self.pool.get('res.partner').browse(cr, uid, cliente_id).property_product_pricelist.currency_id.symbol
                        symbol_position = self.pool.get('res.partner').browse(cr, uid, cliente_id).property_product_pricelist.currency_id.position
                        partner_lang = self.pool.get('res.partner').browse(cr, uid, cliente_id).lang

                        if symbol_position == 'after':
                            symbol_order = (inv_amount, symbol)
                        else:
                            symbol_order = (symbol, inv_amount)
                        res['name'] = self._translate_advance(cr, uid, context=dict(context, lang=partner_lang)) % symbol_order

                    # Impuestos
                    if res.get('invoice_line_tax_id'):
                       res['invoice_line_tax_id'] = [(6, 0, res.get('invoice_line_tax_id'))]
                    else:
                       res['invoice_line_tax_id'] = False

                    d = ir_sequence_obj._interpolation_dict()
                    line_name = ir_sequence_obj._interpolate(fact_lin.name, d)

                    # lineas de la factura
                    inv_line_values = {
                        'name': line_name,
                        'account_id': res['account_id'],
                        'price_unit': price_unit,
                        'quantity': quantity,
                        'discount': False,
                        'uos_id': res.get('uos_id', False),
                        'product_id': fact_lin.product_id.id,
                        'invoice_line_tax_id': res.get('invoice_line_tax_id'),
                        'contrato_id': fact_lin.contrato_id.id,
                        'servicio_id': fact_lin.servicio_id.id,
                    }
                    inv_line.append((0,0,inv_line_values))

                # campos de la factura
                inv_values = {
                    'name': invoice.name,
                    'type': 'out_invoice',
                    'reference': invoice.reference,
                    'account_id': self.pool.get('res.partner').browse(cr, uid, cliente_id).property_account_receivable.id,
                    'partner_id': cliente_id,
                    'invoice_line': inv_line,
                    'currency_id': self.pool.get('res.partner').browse(cr, uid, cliente_id).property_product_pricelist.currency_id.id,
                    'comment': False,
                    'origin': invoice.number,
                    'payment_term': self.pool.get('res.partner').browse(cr, uid, cliente_id).property_payment_term.id,
                    'fiscal_position': fiscal_position_id,
                    'dft_contrato_id': invoice.dft_contrato_id.id,
                    'journal_id': journal_id,
                    'message_follower_ids': False,
                    'message_ids': False,
                    'company_id': self.pool.get('res.company')._company_default_get(cr, uid, context=None),
                    'date_invoice': datetime.today().strftime('%Y-%m-%d'),
                }

                result.append((inv_values))
        return result

    def _crea_facturas(self, cr, uid, inv_values, context=None):
        inv_obj = self.pool.get('account.invoice')
        inv_id = inv_obj.create(cr, uid, inv_values, context=context)
        inv_obj.button_reset_taxes(cr, uid, [inv_id], context=context)
        return inv_id

    def action_genera_factura(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        data = self.read(cr, uid, ids, [], context=context)[0]
        invoice_id = data['invoice_id'][0]
        incremento = data['incremento']

        inv_values = self._prepara_facturas(cr, uid, ids, invoice_id,incremento, context=None)
        new_invoice_id = self._crea_facturas(cr, uid, inv_values[0], context=context)

        # Abre la pantalla de facturas
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas de Cliente',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'type':'out_invoice'}",
            'res_model': 'account.invoice',
            'nodestroy': True,
            'res_id': new_invoice_id,
            'target':'current',
            'view_id': [res_id],
            }

acp_contrato_genera_factura()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
