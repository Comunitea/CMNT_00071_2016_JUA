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


import logging
import time

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import openerp.addons.product.product

_logger = logging.getLogger(__name__)

class event_event(osv.osv):
    _inherit  = "event.event"

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result
    
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    _columns = {
        'image': fields.binary("Image"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'event.event': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            }),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Smal-sized image", type="binary", multi="_get_image",
            store={
                'event.event': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            }),
        'mass_mail_ids': fields.one2many('mail.mass_mailing', 'event_id','Envios masivos'),
        'survey_ids': fields.many2many('survey.survey', 'event_survey_rel',id1='event_id', id2='survey_id', string='Encuestas', readonly=True),
         
    }
    
    def create(self, cr, uid, values, context=None):
        calendar = self.pool.get('calendar.event')
        event_type = self.pool.get('event.type')
        res =  super(event_event, self).create(cr, uid, values, context=context)    
        if values.get('type',False):
            user_id = event_type.browse(cr, uid, values.get('type',False) , context=context).user_id and event_type.browse(cr, uid, values.get('type',False) , context=context).user_id.id or False
            name  = values.get('name',False)
            date_begin  = values.get('date_begin',False)
            date_end  = values.get('date_end',False)
            location = values.get('ubicacion2','')
            vals={
                  'user_id': user_id,
                  'name': name,
                  'start_datetime':date_begin,
                  'stop_datetime':date_end,                   
                  'event_id': res,
                  'location':location,
                  }
                 
            calendar.create(cr, uid, vals, context=context)    
        

        return res

    def write(self, cr, uid, ids, values, context=None):
        calendar = self.pool.get('calendar.event')
        res =  super(event_event, self).write(cr, uid, ids, values, context=context)
        for event in self.browse( cr, uid, ids,  context=context):
            user_id = event.type and event.type.user_id and event.type.user_id.id
            name  = event.name
            date_begin  = event.date_begin
            date_end  = event.date_end
            location = event.ubicacion2 or ''
         
            vals={
                  'user_id': user_id,
                  'name': name,
                  'start_datetime':date_begin,
                  'stop_datetime':date_end, 
                  'location':location       ,           
                  }
       
            calendar_event = calendar.search( cr, uid, [('event_id','=',event.id)],  context=context)
            if len(calendar_event) > 0:
                calendar.write(cr, uid, calendar_event[0],vals, context=context)    
        

        return res

class event_type(osv.osv):
    _inherit  = "event.type"

    _columns = {
        'user_id': fields.many2one('res.users','Usuario',help='Usado para generar una entrada en el calendário'),       
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

