# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale
import sys
import platform

if platform.system() != 'Linux':
    sys.setdefaultencoding('utf-8')

_logger = logging.getLogger(__name__)
 

class SantanderController(http.Controller):
    _return_url = '/payment/santander/return'
    _cancel_url = '/payment/santander/cancel'
    _exception_url = '/payment/santander/error'
    _reject_url = '/payment/santander/reject'

    @http.route([
        '/payment/santander/return',
        '/payment/santander/cancel',
        '/payment/santander/error',
        '/payment/santander/reject',
    ], type='http', auth='none')
    def santander_return(self, **post):
        print 'SantanderController SantanderControllerSantanderControllerSantanderControllerSantanderControllerSantanderControllerSantanderControllerSantanderControllerSantanderControllerSantanderController' 
        """ Santander."""
        _logger.info('Santander: entering form_feedback with post data %s',
                     pprint.pformat(post))
        if post:
            if post.get('RESULT', '99') == '00':
                print 'OKOKOKOKOKOK'                
                request.registry['payment.transaction'].form_feedback(
                    request.cr, SUPERUSER_ID, post, 'santander',
                    context=request.context)
                return self._get_ok_msg(**post)
            else:
                print 'ERRRRORORORORORO'
                return self._get_error_msg(**post)
            
    def _get_ok_msg(self,**post):       
        return '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> \
        <html xmlns="http://www.w3.org/1999/xhtml"> \
        <head> \
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> \
        <title>Documento sin título</title> \
        <style type="text/css"> \
        #contenedor { \
        width: 550px; \
        margin: 0 auto; \
        } \
        p, h1, h2{ \
        color: #666; \
        font-family: "PT Sans Narrow",sans-serif; \
        text-align: center; \
        } \
        p{ \
        color: #666; \
        font-size: 12px; \
        line-height: 18px; \
        } \
        h1{ \
        color: #666; \
        font-size: 22px; \
        line-height: 28px; \
        text-align: center; \
        } \
        h2{ \
        color: #666; \
        font-size: 18px; \
        line-height: 24px; \
        text-align: center; \
        } \
        input[type="submit"] { \
        display: inline-block; \
        border: 1px solid rgba(0, 0, 0, 0.4); \
        color: #4C4C4C; \
        padding: 3px 12px; \
        font-size: 13px; \
        text-align: center; \
        background-color: #E3E3E3; \
        background-image: linear-gradient(to bottom, #EFEFEF, #D8D8D8); \
        border-radius: 3px; \
        box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.1), 0px 1px 1px rgba(255, 255, 255, 0.8) inset; \
        text-shadow: 0px 1px 1px rgba(255, 255, 255, 0.5); \
        outline: medium none; \
        line-height: normal; \
        </style> \
        </head> \
        <body> \
        <div id="contenedor"> \
        <p></p> \
        <center> \
        <img src="http://erp.jbi.es/web/binary/company_logo?db=TEST&amp;company=1" width="180" height="62" /> \
        <h1>Pago realizado correctamente \
        </h1> \
        <p> \
        <form action="http://erp.jbi.es/web" method="post"> \
        <input type="submit" name="button" id="button" value="Regresar al portal de cliente" /> \
        </form> \
        </p> \
        <p>&nbsp;</p> \
        <p>&nbsp;</p> \
        </center> \
        </div> \
        </body> \
        </html>'
    def _get_error_msg(self,**post):       
        return '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> \
               <html xmlns="http://www.w3.org/1999/xhtml"> \
               <head> \
               <meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> \
               <title>Documento sin título</title> \
               <style type="text/css"> \
               #contenedor { \
               width: 550px; \
               margin: 0 auto; \
               } \
               p, h1, h2{ \
               color: #666; \
               font-family: "PT Sans Narrow",sans-serif; \
               text-align: center; \
               } \
               p{ \
               color: #666; \
               font-size: 12px; \
               line-height: 18px; \
               } \
               h1{ \
               color: red; \
               font-size: 22px; \
               line-height: 28px; \
               text-align: center; \
               } \
               h2{ \
               color: #666; \
               font-size: 18px; \
               line-height: 24px; \
               text-align: center; \
               } \
               input[type="submit"] { \
               display: inline-block; \
               border: 1px solid rgba(0, 0, 0, 0.4); \
               color: #4C4C4C; \
               padding: 3px 12px; \
               font-size: 13px; \
               text-align: center; \
               background-color: #E3E3E3; \
               background-image: linear-gradient(to bottom, #EFEFEF, #D8D8D8); \
               border-radius: 3px; \
               box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.1), 0px 1px 1px rgba(255, 255, 255, 0.8) inset; \
               text-shadow: 0px 1px 1px rgba(255, 255, 255, 0.5); \
               outline: medium none; \
               line-height: normal; \
               </style> \
               </head> \
               <body> \
               <div id="contenedor"> \
               <p></p> \
               <center> \
               <img src="http://erp.jbi.es/web/binary/company_logo?db=TEST&amp;company=1" width="180" height="62" /> \
               <h1>Ha habido un error al procesar el pago \
               </h1> \
               <h2>Pongase en contacto con su entidad</h2> \
               <p>CODIGO DE ERROR: '+post.pop('RESULT', '-1')+'</p> \
               <p>MENSAJE DE ERROR: '+post.pop('MESSAGE', 'Error desconocido')+'</p> \
               <p> \
               <form action="http://erp.jbi.es/web" method="post"> \
               <input type="submit" name="button" id="button" value="Regresar al portal de cliente" /> \
               </form> \
               </p> \
               <p>&nbsp;</p> \
               <p>&nbsp;</p> \
               </center> \
               </div> \
               </body> \
               </html>'
