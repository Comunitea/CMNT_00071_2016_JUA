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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp





class mail_alias(osv.osv):
    _inherit = "mail.alias"

    def _get_alias_domain(self, cr, uid, ids, name, args, context=None):

        if context is None:
            context = {}        
        userid = context.get('uid',uid)
        ir_config_parameter = self.pool.get("ir.config_parameter")
        #domain = ir_config_parameter.get_param(cr, uid, "mail.catchall.domain", context=context)
        domain = self.pool.get('res.users').browse(cr, uid, userid, context=context).company_id.email_domain       
        print 'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
        print domain
        return dict.fromkeys(ids, domain or "")

        _columns = {

        'alias_domain': fields.function(_get_alias_domain, string="Alias domain", type='char', size=None),
        }

mail_alias()    

class res_company(osv.osv):
    _inherit = "res.company"

    _columns = {
        'email_domain': fields.char('Dominio', required=False)
             }

res_company()    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

