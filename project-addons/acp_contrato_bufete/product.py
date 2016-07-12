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
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta


#----------------------------------------------------------
# Sale Order
#----------------------------------------------------------
class product_template(osv.osv):
    _inherit = 'product.template'


    _columns = {
        'computar_en_expedientes': fields.boolean('Computa en expedientes', required=False,help="Si esta marcado este producto computará para el cáculo 'Total Facturado' en contratos"),
              }  
    _defaults = {
        'computar_en_expedientes': True
    } 



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
