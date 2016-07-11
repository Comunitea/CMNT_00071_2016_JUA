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

from openerp.osv import osv, fields, expression


class survey_survey(osv.osv):


    _inherit  = "survey.survey"
    _columns = {
               'event_ids': fields.many2many('event.event','event_survey_rel', id1='survey_id', id2='event_id', string='Eventos', readonly=True),
               }
               
               
class survey_mail_compose_message(osv.TransientModel):
    _inherit = 'survey.mail.compose.message'

    def default_get(self, cr, uid, fields, context=None):
        res = super(survey_mail_compose_message, self).default_get(cr, uid, fields, context=context)
        if context.get('active_model') == 'event.event' and context.get('active_ids'):
            partner_ids = []
            emails_list = []
            for event in self.pool.get('event.event').browse(cr, uid, context.get('active_ids'), context=context):
                for reg in event.registration_ids:
                    if reg.partner_id:
                        partner_ids.append(reg.partner_id.id)
                    else:
                        email = reg.name and "%s <%s>" % (reg.name, reg.email or "") or reg.email or None
                        if email and email not in emails_list:
                            emails_list.append(email)
                multi_email = "\n".join(emails_list)

            res.update({'partner_ids': list(set(partner_ids)), 'multi_email': multi_email})
        return res
    def send_mail(self, cr, uid, ids, context=None):
        res = super(survey_mail_compose_message, self).send_mail(cr, uid, ids, context=context)
        print 'contextcontextcontextcontextcontextcontextcontextcontextcontextcontextcontextcontextcontextcontext'
        print context
        if context.has_key('from_event') and context.has_key('default_event_id') and context.get('from_event'):
            smcm_obj=self.pool.get('survey.mail.compose.message')
            smcm=smcm_obj.browse(cr, uid, ids[0], context=context)
            survey_obj = self.pool.get('survey.survey')
            survey_obj.write(cr, uid, smcm.survey_id.id,{'event_ids':[[6, 0, [context.get('default_event_id')]]]}, context=context)
    
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

