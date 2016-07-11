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


from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.charset import Charset
from email.header import Header
from email.utils import formatdate, make_msgid, COMMASPACE, getaddresses, formataddr
from email import Encoders
import logging
import re
import smtplib
import threading

from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.tools import html2text
import openerp.tools as tools
#from openerp.addons.base.ir import ir_mail_server

# ustr was originally from tools.misc.
# it is moved to loglevels until we refactor tools.
from openerp.loglevels import ustr

_logger = logging.getLogger(__name__)
_test_logger = logging.getLogger('openerp.tests')


class ir_mail_server(osv.osv):
    _inherit = "ir.mail_server"

    _columns = {
        'company_id':fields.many2one('res.company', 'Company', required=False, readonly=False),
    }


    _defaults = {
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.company')._company_default_get(cr, uid,
                                            'email.template', context=c),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

