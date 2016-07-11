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
import time


class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'
    '''
    def _get_templates(self, cr, uid, context=None):
        print '_get_templates'
        if context is None:
            context = {}
        model = False
        email_template_obj = self.pool.get('email.template')
        message_id = context.get('default_parent_id', context.get('message_id', context.get('active_id')))

        if context.get('default_composition_mode') == 'reply' and message_id:
            message_data = self.pool.get('mail.message').browse(cr, uid, message_id, context=context)
            if message_data:
                model = message_data.model
        else:
            model = context.get('default_model', context.get('active_model'))
            
        cmpn_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        record_ids = email_template_obj.search(cr, uid, [('model', '=', model),'|',('company_id', '=', cmpn_id),('company_id', '=', False)], context=context)
        #record_ids = email_template_obj.search(cr, uid, [('model', '=', model)], context=context)
        print email_template_obj.name_get(cr, uid, record_ids, context) + [(False, '')]
        return email_template_obj.name_get(cr, uid, record_ids, context) + [(False, '')]

    _columns = {
        # incredible hack of the day: size=-1 means we want an int db column instead of an str one
        'template_id': fields.selection(_get_templates, 'Template', size=-1),
    }
    '''


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

