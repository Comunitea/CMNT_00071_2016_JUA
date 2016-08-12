# -*- coding: utf-8 -*-

import pytz
import re
import time
import openerp
import openerp.service.report
import uuid
import collections
import babel.dates
from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta
from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from openerp import api
from openerp import tools, SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.http import request
from operator import itemgetter

import logging
_logger = logging.getLogger(__name__)


class acp_contrato_alarm_manager(osv.AbstractModel):
    _name = 'acp_contrato.alarm_manager'

    def get_next_potential_limit_alarm(self, cr, uid, seconds, notif=True, mail=True, partner_id=None, context=None):
        res = {}
        base_request = """
                    SELECT
                        cal.id,
                        cal.fecha_limite - interval '1' minute  * calcul_delta.max_delta AS first_alarm,
                        cal.fecha_limite - interval '1' minute  * calcul_delta.min_delta as last_alarm,
                        cal.fecha_limite as first_event_date,
                        cal.fecha_limite last_event_date,
                        calcul_delta.min_delta,
                        calcul_delta.max_delta
                    FROM
                        acp_contrato_tarea AS cal
                        RIGHT JOIN
                            (
                                SELECT
                                    rel.acp_contrato_tarea_id, max(alarm.duration_minutes) AS max_delta,min(alarm.duration_minutes) AS min_delta
                                FROM
                                    acp_contrato_alarm_calendar_event_rel AS rel
                                        LEFT JOIN acp_contrato_alarm AS alarm ON alarm.id = rel.acp_contrato_alarm_id
                                WHERE alarm.type in %s
                                GROUP BY rel.acp_contrato_tarea_id
                            ) AS calcul_delta ON calcul_delta.acp_contrato_tarea_id = cal.id
             """

        #filter_user = """
        #        RIGHT JOIN calendar_event_res_partner_rel AS part_rel ON part_rel.calendar_event_id = cal.id
        #            AND part_rel.res_partner_id = %s
        #"""

        #Add filter on type
        type_to_read = ()
        if notif:
            type_to_read += ('notification',)
        if mail:
            type_to_read += ('email',)

        tuple_params = (type_to_read,)

        # ADD FILTER ON PARTNER_ID
        #if partner_id:
        #    base_request += filter_user
        #    tuple_params += (partner_id, )

        #Add filter on hours
        tuple_params += (seconds,)

        cr.execute("""SELECT *
                        FROM ( %s WHERE cal.state = 'open' ) AS ALL_EVENTS
                       WHERE ALL_EVENTS.first_alarm < (now() at time zone 'utc' + interval '%%s' second )
                         AND ALL_EVENTS.last_event_date > (now() at time zone 'utc')
                   """ % base_request, tuple_params)

        for tarea_id, first_alarm, last_alarm, first_meeting, last_meeting, min_duration, max_duration in cr.fetchall():
            res[tarea_id] = {
                'event_id': tarea_id,
                'first_alarm': first_alarm,
                'last_alarm': last_alarm,
                'first_meeting': first_meeting,
                'last_meeting': last_meeting,
                'min_duration': min_duration,
                'max_duration': max_duration
            }

        return res

    def do_check_alarm_for_one_date(self, cr, uid, one_date, event, event_maxdelta, in_the_next_X_seconds, after=False, notif=True, mail=True, missing=False, context=None):
        # one_date: date of the event to check (not the same that in the event browse if recurrent)
        # event: Event browse record
        # event_maxdelta: biggest duration from alarms for this event
        # in_the_next_X_seconds: looking in the future (in seconds)
        # after: if not False: will return alert if after this date (date as string - todo: change in master)
        # missing: if not False: will return alert even if we are too late
        # notif: Looking for type notification
        # mail: looking for type email

        res = []

        # TODO: replace notif and email in master by alarm_type + remove event_maxdelta and if using it
        alarm_type = []
        if notif:
            alarm_type.append('notification')
        if mail:
            alarm_type.append('email')

        if one_date - timedelta(minutes=(missing and 0 or event_maxdelta)) < datetime.now() + timedelta(seconds=in_the_next_X_seconds):  # if an alarm is possible for this date
            for alarm in event.alarm_ids:
                if alarm.type in alarm_type and \
                    one_date - timedelta(minutes=(missing and 0 or alarm.duration_minutes)) < datetime.now() + timedelta(seconds=in_the_next_X_seconds) and \
                        (not after or one_date - timedelta(minutes=alarm.duration_minutes) > openerp.fields.Datetime.from_string(after)):
                        alert = {
                            'alarm_id': alarm.id,
                            'tarea_id': event.id,
                            'notify_at': one_date - timedelta(minutes=alarm.duration_minutes),
                        }
                        res.append(alert)
        return res

    def get_next_mail(self, cr, uid, context=None):
        now = openerp.fields.Datetime.to_string(datetime.now())

        icp = self.pool['ir.config_parameter']
        last_notif_mail = icp.get_param(cr, SUPERUSER_ID, 'acp_contrato.last_notif_mail', default=False) or now

        try:
            cron = self.pool['ir.model.data'].get_object(cr, uid, 'acp_contrato', 'ir_cron_scheduler_task_alarm', context=context)
        except ValueError:
            _logger.error("Cron for " + self._name + " can not be identified !")
            return False

        interval_to_second = {
            "weeks": 7 * 24 * 60 * 60,
            "days": 24 * 60 * 60,
            "hours": 60 * 60,
            "minutes": 60,
            "seconds": 1
        }

        if cron.interval_type not in interval_to_second.keys():
            _logger.error("Cron delay can not be computed !")
            return False

        cron_interval = cron.interval_number * interval_to_second[cron.interval_type]

        all_events = self.get_next_potential_limit_alarm(cr, uid, cron_interval, notif=False, context=context)

        for curEvent in self.pool.get('acp_contrato.tarea').browse(cr, uid, all_events.keys(), context=context):
            max_delta = all_events[curEvent.id]['max_duration']


            in_date_format = datetime.strptime(curEvent.fecha_limite, DEFAULT_SERVER_DATETIME_FORMAT)
            last_found = self.do_check_alarm_for_one_date(cr, uid, in_date_format, curEvent, max_delta, 0, after=last_notif_mail, notif=False, missing=True, context=context)
            for alert in last_found:
                self.do_mail_reminder(cr, uid, alert, context=context)
        icp.set_param(cr, SUPERUSER_ID, 'acp_contrato.last_notif_mail', now)



    def do_mail_reminder(self, cr, uid, alert, context=None):
        if context is None:
            context = {}
        res = False

        tarea = self.pool['acp_contrato.tarea'].browse(cr, uid, alert['tarea_id'], context=context)
        alarm = self.pool['acp_contrato.alarm'].browse(cr, uid, alert['alarm_id'], context=context)

        if alarm.type == 'email':
            res = self.pool['acp_contrato.tarea']._send_mail(
                cr,
                uid,
                [tarea.id],
                email_from=tarea.user_id.partner_id.email,###############################################################33/*   OJO SI ES EL ADMINI N FUNCIONA*/
                template_xmlid='acp_contrato_template_task_reminder',
                force=True,
                context=context
            )

        return res

    def do_notif_reminder(self, cr, uid, alert, context=None):
        alarm = self.pool['acp_contrato.alarm'].browse(cr, uid, alert['alarm_id'], context=context)
        tarea = self.pool['acp_contrato.tarea'].browse(cr, uid, alert['tarea_id'], context=context)

        if alarm.type == 'notification':
            message = event.display_time

            delta = alert['notify_at'] - datetime.now()
            delta = delta.seconds + delta.days * 3600 * 24

            return {
                'tarea_id': tarea.id,
                'title': tarea.name,
                'message': message,
                'timer': delta,
                'notify_at': alert['notify_at'].strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            }


class acp_contrato_alarm(osv.Model):
    _name = 'acp_contrato.alarm'
    _description = 'Event alarm'

    def _get_duration(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for alarm in self.browse(cr, uid, ids, context=context):
            if alarm.interval == "minutes":
                res[alarm.id] = alarm.duration
            elif alarm.interval == "hours":
                res[alarm.id] = alarm.duration * 60
            elif alarm.interval == "days":
                res[alarm.id] = alarm.duration * 60 * 24
            else:
                res[alarm.id] = 0
        return res

    _columns = {
        'name': fields.char('Name', required=True),
        'type': fields.selection([('notification', 'Notification'), ('email', 'Email')], 'Type', required=True),
        'duration': fields.integer('Amount', required=True),
        'interval': fields.selection([('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days')], 'Unit', required=True),
        'duration_minutes': fields.function(_get_duration, type='integer', string='duration_minutes', store=True),
    }

    _defaults = {
        'type': 'notification',
        'duration': 1,
        'interval': 'hours',
    }

    def _update_cron(self, cr, uid, context=None):
        try:
            cron = self.pool['ir.model.data'].get_object(
                cr, uid, 'acp_contrato', 'ir_cron_scheduler_task_alarm', context=context)
        except ValueError:
            return False
        return cron.toggle(model=self._name, domain=[('type', '=', 'email')])

    def create(self, cr, uid, values, context=None):
        res = super(acp_contrato_alarm, self).create(cr, uid, values, context=context)

        self._update_cron(cr, uid, context=context)

        return res

    def write(self, cr, uid, ids, values, context=None):
        res = super(acp_contrato_alarm, self).write(cr, uid, ids, values, context=context)

        self._update_cron(cr, uid, context=context)

        return res

    def unlink(self, cr, uid, ids, context=None):
        res = super(acp_contrato_alarm, self).unlink(cr, uid, ids, context=context)

        self._update_cron(cr, uid, context=context)

        return res

'''
class ir_values(osv.Model):
    _inherit = 'ir.values'

    def set(self, cr, uid, key, key2, name, models, value, replace=True, isobject=False, meta=False, preserve_user=False, company=False):
        new_model = []
        for data in models:
            if type(data) in (list, tuple):
                new_model.append((data[0], calendar_id2real_id(data[1])))
            else:
                new_model.append(data)
        return super(ir_values, self).set(cr, uid, key, key2, name, new_model,
                                          value, replace, isobject, meta, preserve_user, company)

    def get(self, cr, uid, key, key2, models, meta=False, context=None, res_id_req=False, without_user=True, key2_req=True):
        if context is None:
            context = {}
        new_model = []
        for data in models:
            if type(data) in (list, tuple):
                new_model.append((data[0], calendar_id2real_id(data[1])))
            else:
                new_model.append(data)
        return super(ir_values, self).get(cr, uid, key, key2, new_model,
                                          meta, context, res_id_req, without_user, key2_req)


class ir_model(osv.Model):

    _inherit = 'ir.model'

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        new_ids = isinstance(ids, (basestring, int, long)) and [ids] or ids
        if context is None:
            context = {}
        data = super(ir_model, self).read(cr, uid, new_ids, fields=fields, context=context, load=load)
        if data:
            for val in data:
                val['id'] = calendar_id2real_id(val['id'])
        return isinstance(ids, (basestring, int, long)) and data[0] or data


original_exp_report = openerp.service.report.exp_report


def exp_report(db, uid, object, ids, data=None, context=None):
    """
    Export Report
    """
    if object == 'printscreen.list':
        original_exp_report(db, uid, object, ids, data, context)
    new_ids = []
    for id in ids:
        new_ids.append(calendar_id2real_id(id))
    if data.get('id', False):
        data['id'] = calendar_id2real_id(data['id'])
    return original_exp_report(db, uid, object, new_ids, data, context)


openerp.service.report.exp_report = exp_report


class calendar_event_type(osv.Model):
    _name = 'calendar.event.type'
    _description = 'Meeting Type'
    _columns = {
        'name': fields.char('Name', required=True, translate=True),
    }

'''
