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

import urllib
import urlparse

from openerp import tools
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields



class MailMail(osv.Model):

    _inherit = 'mail.mail'

    def _get_lopd_txt(self, cr, uid, context=None):

        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        return company.lopd_footer_msg or ''

    def _get_unsubscribe_url(self, cr, uid, mail, email_to, msg=None, context=None):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        url = urlparse.urljoin(
            base_url, 'mail/mailing/%(mailing_id)s/unsubscribe?%(params)s' % {
                'mailing_id': mail.mailing_id.id,
                'params': urllib.urlencode({'db': cr.dbname, 'res_id': mail.res_id, 'email': email_to})
            }
        )
        
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        msg_unsubscribe = company.unsubscribe_text or False
        u  = '</br><small><a href="%s">%s</a></small>' % (url, msg_unsubscribe or 'Haga Click aqui si no deseas recibir mas mensajes')
        
        lopd_text = self._get_lopd_txt(cr, uid,context=context)
        
        if lopd_text:
            u = lopd_text + u                   
       
        return u

    def send_get_email_dict_NO_USAR(self, cr, uid, mail, partner=None, context=None):
        res = super(MailMail, self).send_get_email_dict(cr, uid, mail, partner, context=context)
        print 'context SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS'  
        print context
        print 'tiene la llave'
        print context.has_key('active_model')
        if context.has_key('active_model'):
            print 'paso por unooooooooooooooooooooooo'
            if context.get('active_model',False)   == 'mail.mass_mailing':
                print 'paso por dossssssssssssssssssssssss'
                return res

        res['body'] = '<table width="100%" border="0" cellspacing="0" cellpadding="0"><tr ><td align="center">'+res['body'] +'</td></tr></table>'

        return res
class MassMailing(osv.Model):

    _inherit = 'mail.mass_mailing'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
        'company_id':fields.many2one('res.company', 'Company', required=False, readonly=False),
        'event_id':fields.many2one('event.event', 'Evento', required=False, readonly=False),
    }

    _defaults = {
        'company_id': _get_default_company,
   }

    def on_change_model_and_list(self, cr, uid, ids, mailing_model, list_ids, context=None):
        res =  super(MassMailing, self).on_change_model_and_list(cr, uid, ids, mailing_model, list_ids, context=context)  
        value = {}
        if context.has_key('from_event') and context.get('from_event'):
            res['value']['mailing_domain'] = context.get('default_mailing_domain')
        return res
        '''
        print 'contextcontextcontextcontextcontextcontextcontext'
        print context
        if mailing_model == 'mail.mass_mailing.contact':
            mailing_list_ids = set()
            for item in list_ids:
                if isinstance(item, (int, long)):
                    mailing_list_ids.add(item)
                elif len(item) == 3:
                    mailing_list_ids |= set(item[2])
            if mailing_list_ids:
                value['mailing_domain'] = "[('list_id', 'in', %s)]" % list(mailing_list_ids)
            else:
                value['mailing_domain'] = "[('list_id', '=', False)]"
        else:
            value['mailing_domain'] = False
        return {'value': value}
        '''        
    def send_mail(self, cr, uid, ids, context=None):
        res = super(MassMailing, self).send_mail(cr, uid, ids, context=context)
        for mailing in self.browse(cr, uid, ids, context=context):
            res_ids = self.get_recipients(cr, uid, mailing, context=context)
            if res_ids:
               if mailing.mailing_model == 'crm.lead':
                   for id_ in res_ids:
                       self.pool.get('crm.lead').write(cr, uid, id_, {'mass_mailing_id':mailing.id}, context=context)
               if mailing.mailing_model == 'res.partner':
                   for id_ in res_ids:
                       partner = self.pool.get('res.partner').browse(cr, uid, id_, context)
                       vals={'name':mailing.name + '-' + (partner.name or ''),
                             'mass_mailing_id':mailing.id,
                             'partner_id':id_,
                             'email_from': partner.email,
                             'phone': partner.phone,
                             'type':'opportunity'
                             }
                       self.pool.get('crm.lead').create(cr, uid, vals, context=context)
               if mailing.mailing_model == 'mail.mass_mailing.contact':
                   for id_ in res_ids:
                       contact = self.pool.get('mail.mass_mailing.contact').browse(cr, uid, id_, context)
                       vals={'name':mailing.name + '-' + (contact.name or ''),
                             'mass_mailing_id':mailing.id,
                             'contact_id':id_,
                             'email_from': contact.email,
                             'type':'opportunity'
                             }
                       self.pool.get('crm.lead').create(cr, uid,  vals, context=context)
        return res 

        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
