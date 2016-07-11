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



class acp_contrato_refacturar_gasto(osv.osv_memory):
    """ PGenera serviciog """

    _name = 'acp_contrato.refacturar_gasto'
    _description = 'Creacion factura de venta desde facturas de compra'
    _columns = {
        'agrupar': fields.selection([
                ('contrato', 'Contrato'),
                ('cliente', 'Cliente'),
            ], 'Agrupar facturar por', select=True, required=True),
        'diario_id': fields.many2one('account.journal', 'Diario', select=True, required=True), 
        'fecha_factura': fields.date('Fecha Factura', required=True, select=True),
    }
    _defaults = {
        'agrupar': "cliente",
    }
    

    def action_cancel(self, cr, uid, ids, context=None):

        return {'type':'ir.actions.act_window_close'}

    def _prepara_facturas_servicios(self, cr, uid, ids, agrupar, fecha_factura, diario_id,context=None):
        
        if context is None:
            context = {}


        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        inv_line_obj = self.pool.get('account.invoice.line')
        ir_sequence_obj = self.pool.get('ir.sequence')
        inv_obj = self.pool.get('account.invoice')
        result = []
        # Se seleccionan facturas de venta aprocesar
        if agrupar== 'contrato':
            agrupar_campo = "acp_contrato_contrato.id"

        if agrupar == 'cliente':
            agrupar_campo = "acp_contrato_contrato.partner_factura_id"



        cr.execute("select acp_contrato_contrato.partner_factura_id as cliente_direccion_id, \
                            "+ agrupar_campo +"  as id \
                    from account_invoice_line,acp_contrato_contrato \
                    where account_invoice_line.id in %s and \
                          acp_contrato_contrato.id = account_invoice_line.contrato_id \
                    group by acp_contrato_contrato.partner_factura_id, "+ agrupar_campo,(tuple(ids),))
        for serv_fact in cr.dictfetchall():
            # Datos de cabecera de factura
            cliente_factura_id = serv_fact['cliente_direccion_id']

            fiscal_position_id = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_account_position.id 

            cr.execute("select account_invoice_line.product_id as product_id, account_invoice_line.quantity as cantidad, \
                        account_invoice_line.price_unit as precio,account_invoice_line.tarea_id as tarea_id, \
                        account_invoice_line.servicio_id as servicio_id,account_invoice_line.contrato_id as contrato_id, \
                        account_invoice_line.id as linea_factura_id \
                        from account_invoice_line,acp_contrato_contrato \
                        where account_invoice_line.id in %s and \
                              acp_contrato_contrato.id = account_invoice_line.contrato_id and\
                              " + agrupar_campo + "= %s",(tuple(ids),serv_fact['id'],))
            inv_line = []
            for serv_fact_lin in cr.dictfetchall():
                # Datos de linea de factura  
                invoice_line = inv_line_obj.browse(cr, uid,serv_fact_lin['linea_factura_id'], context=context)  
                val = inv_line_obj.product_id_change(cr, uid, [], serv_fact_lin['product_id'],
                        False, partner_id=cliente_factura_id, fposition_id=fiscal_position_id)
                res = val['value']                  

                # determine and check income account
                if not serv_fact_lin['product_id'] :
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

                # determine invoice amount
                if (serv_fact_lin['cantidad'] * serv_fact_lin['precio']) <= 0.00:
                        raise osv.except_osv(_('Incorrect Data'),
                            _('The value of Advance Amount must be positive.'))

                inv_amount =  (serv_fact_lin['cantidad'] * serv_fact_lin['precio'])

                if not res.get('name'):
                    #TODO: should find a way to call formatLang() from rml_parse
                    symbol = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id, context=context).property_product_pricelist.currency_id.symbol
                    symbol_position = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id, context=context).property_product_pricelist.currency_id.position                        
                    partner_lang = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id, context=context).lang
                        
                    if symbol_position == 'after':
                        symbol_order = (inv_amount, symbol)
                    else:
                        symbol_order = (symbol, inv_amount)
                    res['name'] = self._translate_advance(cr, uid, context=dict(context, lang=partner_lang)) % symbol_order

                # determine taxes
                if res.get('invoice_line_tax_id'):
                    res['invoice_line_tax_id'] = [(6, 0, res.get('invoice_line_tax_id'))]
                else:
                    res['invoice_line_tax_id'] = False 


                

                # create the invoice
                inv_line_values = {
                    'name': res['name'],
                    'account_id': res['account_id'],
                    'price_unit': res['price_unit'],
                    'quantity':  serv_fact_lin['cantidad'],
                    'discount': False,
                    'origin' : invoice_line.invoice_id.number,
                    'linea_de_fac_original' : invoice_line.id,
                    'uos_id': res.get('uos_id', False),
                    'product_id':  serv_fact_lin['product_id'],
                    'invoice_line_tax_id': res['invoice_line_tax_id'] ,
                    'contrato_id': serv_fact_lin['contrato_id'],
                    'servicio_id': serv_fact_lin['servicio_id'],
                    'tarea_id': serv_fact_lin['tarea_id'],
                    'invoice_id': False

                }
                inv_line.append(inv_line_values)

            inv_values = {
                'type': 'out_invoice',
                'reference': False,
                'account_id': self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_account_receivable.id,
                'partner_id': cliente_factura_id,
                #'invoice_line': inv_line,
                'currency_id': self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_product_pricelist.currency_id.id,
                'comment': '',
                'payment_term': self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_payment_term.id,
                'fiscal_position': fiscal_position_id,                      
                'date_invoice': fecha_factura,
                'journal_id': diario_id,
            }
            inv_id = inv_obj.create(cr, uid, inv_values, context=context)
            for inv_lin in inv_line:
                inv_lin['invoice_id']=inv_id 
                new_inv_line_id = inv_line_obj.create(cr, uid, inv_lin, context=context)
                inv_line_obj.write(cr, uid, inv_lin['linea_de_fac_original'], {'sale_invoice_line_id': new_inv_line_id}, context=context)   
            result.append( inv_id)                                         
        return result           

    def action_create_invoice(self, cr, uid, ids, context=None):
        genera_obj = self.pool.get('acp_contrato.genera_servicio')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if context is None:
            context = {}
        
        data = self.read(cr, uid, ids)[0]
        inv_ids = self._prepara_facturas_servicios(cr,uid,context.get(('active_ids'), []),data['agrupar'],data['fecha_factura'],data['diario_id'][0],context=context)
        return self.open_invoices(cr, uid, ids, inv_ids, context=context)   

    def open_invoices(self, cr, uid, ids, invoice_ids, context=None):

        mod_obj = self.pool.get('ir.model.data')
        try:
            search_view_id = mod_obj.get_object_reference(cr, uid, 'account', 'view_account_invoice_filter')[1]
        except ValueError:
            search_view_id = False
        try:
            form_view_id = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')[1]
        except ValueError:
            form_view_id = False

        return  {
            'domain': [('id', 'in', invoice_ids)],
            'name': 'Facturas de cliente',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'context': {'type': 'out_invoice'},            
            'views': [(False, 'tree'), (form_view_id, 'form')],
            'search_view_id': search_view_id,
        }


acp_contrato_refacturar_gasto()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
