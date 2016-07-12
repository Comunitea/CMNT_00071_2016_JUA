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
#from datetime import datetime
#import netsvc
import time
from openerp.tools.translate import _


class payment_mode(osv.osv):
    _inherit = 'payment.mode'
    _columns = {
        'visible_online' : fields.boolean('Visible para pago online?'),
        'terms_ids': fields.many2many('account.payment.term','account_payment_term_rel','payment_mode_id', 'term_id', 'Plazos de Pago'),        
        'tipo_documento': fields.selection(
                [('justificante', 'Justificante Transferencia'),('mandato', 'Mandato')],
                'Tipo de documento requerido', required=False, help="Tipo de documento Requerido para validar el presupuesto online"),         
        'guardar': fields.selection(
                [('presupuesto', 'Presupuesto'),('cliente', 'Cliente')],
                'Guardar cocumento en', required=False, help="Indica el modelo de datos donde debe validarse si el documento existe. \n  \
                                                                                Tambien será el modelo donde se guarde el documento.  "), 
         'acquirer_id':fields.many2one('payment.acquirer', 'Pasarela de pago  Online',required=False),                                                                                        
    }
     
payment_mode()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
