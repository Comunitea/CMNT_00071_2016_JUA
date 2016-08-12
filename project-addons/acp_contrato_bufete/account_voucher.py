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

import time
from lxml import etree

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
import openerp


class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
        'dft_contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', readonly=False,required=False),
        'dft_servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', readonly=False,required=False),
       }

    def action_genera_recibo(self,cr,uid,ids,context=None):
        ctx = dict()
        ctx.update({
            'default_voucher_id': self.browse(cr, uid, ids).id,
            'default_reference': self.browse(cr, uid, ids).reference,
        })

        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'acp_contrato_bufete', 'view_genera_recibo_bu')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generar Recibo Ventas',
            'view_type': 'form',
            'view_mode': 'form',
            'context': ctx,
            'res_model': 'acp_contrato.genera_recibo',
            'target':'new',
            'view_id': [res_id],
            }

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'
    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', readonly=False,required=False),
        'servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', readonly=False,required=False),
       }

    _defaults = {
      'contrato_id' : lambda self, cr, uid, context : context['contrato_id'] if context and 'contrato_id' in context else None,
      'servicio_id' : lambda self, cr, uid, context : context['servicio_id'] if context and 'servicio_id' in context else None,
         }

    def open_voucher_sale(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        voucher_id = self.browse(cr, uid, ids, context=context)[0].voucher_id.id
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
            'res_id': voucher_id,
            'target':'current',
            'view_id': [res_id],
            }

    def open_voucher_purchase(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        voucher_id = self.browse(cr, uid, ids, context=context)[0].voucher_id.id
        res = mod_obj.get_object_reference(cr, uid, 'account_voucher', 'view_purchase_receipt_form')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recibos de Compra',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'type':'purchase'}",
            'res_model': 'account.voucher',
            'nodestroy': True,
            'res_id': voucher_id,
            'target':'current',
            'view_id': [res_id],
            }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
