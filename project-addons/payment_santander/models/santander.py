# -*- coding: utf-8 -*-
from hashlib import sha1
import logging
import urlparse
import datetime
from openerp import models, fields, api, _
from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.tools.float_utils import float_compare
_logger = logging.getLogger(__name__)


class Acquirersantander(models.Model):
    _inherit = 'payment.acquirer'

    def _get_santander_urls(self, environment):
        """ santander URLs
        """
        if environment == 'prod':
            return {
                'santander_form_url':
                'https://hpp.santanderelavontpvvirtual.es/pay',
            }
        else:
            return {
                'santander_form_url':
                'https://hpp.prueba.santanderelavontpvvirtual.es/pay',
            }

    @api.model
    def _get_providers(self):
        print '_get_providers_get_providers_get_providers_get_providers_get_providers_get_providers'
        
        providers = super(Acquirersantander, self)._get_providers()
        providers.append(['santander', 'santander'])
        print 'providers'
        print providers
        return providers

    santander_account = fields.Char('Account',
                                      required_if_provider='santander')
    santander_currency = fields.Char('Currency',
                                       required_if_provider='santander')
    santander_merchant_id = fields.Char('merchant ID',
                                          required_if_provider='santander')
    santander_secret_key  = fields.Char('Secreto',
                                          required_if_provider='santander') 
    santander_auto_settle_flag = fields.Char('Aauto settle flag',
                                          required_if_provider='santander')                                          
    santander_url_ok = fields.Char('URL OK')
    santander_url_ko = fields.Char('URL KO')

    def _santander_generate_digital_sign(self,type, acquirer,time_stamp,merchant_id,reference,amount,cur,secret,                                                  result=False,
                                                  message=False,
                                                  pasref=False,
                                                  authcode=False,
												  order_id=False):
        """ Generate the shasign for incoming or outgoing communications.
        :param browse acquirer: the payment.acquirer browse record. It should
                                have a shakey in shaky out
        :param string inout: 'in' (encoding) or 'out' (decoding).
        :param dict values: transaction values

        :return string: shasign
        """
        assert acquirer.provider == 'santander'

        '''
        def get_value(key):
            if values.get(key):
                return values[key]
            return ''

        if inout == 'out':
            keys = ['Ds_Amount',
                    'Ds_Order',
                    'Ds_MerchantCode',
                    'Ds_Currency',
                    'Ds_Response']
        else:
            keys = ['Ds_Merchant_Amount',
                    'Ds_Merchant_Order',
                    'Ds_Merchant_MerchantCode',
                    'Ds_Merchant_Currency',
                    'Ds_Merchant_TransactionType',
                    'Ds_Merchant_MerchantURL']
        sign = ''.join('%s' % (get_value(k)) for k in keys)
        # Add the pre-shared secret key at the end of the signature
        sign = sign + acquirer.santander_secret_key
        if isinstance(sign, str):
            sign = urlparse.parse_qsl(sign)
        shasign = sha1(sign).hexdigest().upper()
        '''
        if type == 'in':
            clave1 = sha1(str(time_stamp) + '.' + str(merchant_id) + '.' + str(reference) + '.' + str(amount) + '.' + str(cur))
            clave2 = sha1(str(clave1.hexdigest()) + '.' + str(secret))
            print str(clave2.hexdigest())
            return str(clave2.hexdigest())
        if type == 'out':
            clave1 = sha1(str(time_stamp) + '.' + str(merchant_id) + '.' + str(order_id) + '.' + str(result) + '.' + str(message) + '.' + str(pasref) + '.' + str(authcode))
            clave2 = sha1(str(clave1.hexdigest()) + '.' + str(secret))
            print str(clave2.hexdigest())
            return str(clave2.hexdigest())

    @api.model
    def santander_form_generate_values(self, id, partner_values, tx_values):
        print 'santander_form_generate_values santander_form_generate_values santander_form_generate_values'
        print 'tx_values'
        print tx_values
        acquirer = self.browse(id)
        santander_tx_values = dict(tx_values)
        
        '''
        MERCHANT_ID"
<input type="hidden" name="ORDER_ID" value="ID de pedido único">
<input type="hidden" name="ACCOUNT" value="nombre de subcuenta">
<input type="hidden" name="AMOUNT" value="importe">
<input type="hidden" name="CURRENCY" value="código de divisa">
<input type="hidden" name="TIMESTAMP" value="aaaammddhhmmss">
<input type="hidden" name="SHA1HASH" value="cadena de 40 caracteres">
<input type="hidden" name="AUTO_SETTLE_FLAG" value="1 o 0">
<input type="submit" value="Haz clic aquí para comprar">
        '''     
        time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        cur = 'EUR'
        santander_tx_values.update({

            'MERCHANT_ID': acquirer.santander_merchant_id ,                                                    
            'ORDER_ID':  tx_values['reference']+'$'+time_stamp ,                                        
            'ACCOUNT': acquirer.santander_account ,                                
            'AMOUNT': int(tx_values['amount'] * 100),                
            'CURRENCY': cur ,                
            'TIMESTAMP': time_stamp ,
            'AUTO_SETTLE_FLAG' :acquirer.santander_auto_settle_flag ,    
            'MERCHANT_RESPONSE_URL': 'http://erp.jbi.es/payment/santander/return'
        })                    
                    
        '''                    
            'Ds_Merchant_Amount': int(tx_values['amount'] * 100),
            'Ds_Merchant_Currency': acquirer.santander_currency or '978',
            'Ds_Merchant_Order': (
                tx_values['reference'] and tx_values['reference'][:12] or
                False),
            'Ds_Merchant_MerchantCode': (
                acquirer.santander_merchant_code and
                acquirer.santander_merchant_code[:9]),
            'Ds_Merchant_Terminal': acquirer.santander_terminal or '1',
            'Ds_Merchant_TransactionType': (
                acquirer.santander_transaction_type or '0'),
            'Ds_Merchant_Titular': (
                acquirer.santander_merchant_titular[:60] and
                acquirer.santander_merchant_titular[:60]),
            'Ds_Merchant_MerchantName': (
                acquirer.santander_merchant_name and
                acquirer.santander_merchant_name[:25]),
            'Ds_Merchant_MerchantURL': (
                acquirer.santander_merchant_url and
                acquirer.santander_merchant_url[:250] or ''),
            'Ds_Merchant_MerchantData': acquirer.santander_merchant_data or '',
            'Ds_Merchant_ProductDescription': (
                self._product_description(tx_values['reference']) or
                acquirer.santander_merchant_description and
                acquirer.santander_merchant_description[:125]),
            'Ds_Merchant_ConsumerLanguage': (
                acquirer.santander_merchant_lang or '001'),
            'Ds_Merchant_UrlOK': acquirer.santander_url_ok or '',
            'Ds_Merchant_UrlKO': acquirer.santander_url_ko or '',
            'Ds_Merchant_PayMethods': acquirer.santander_pay_method or 'T',
        '''               

        #TIMESTAMP.MERCHANT_ID.ORDER_ID.AMOUNT.CURRENCY
        santander_tx_values['SHA1HASH'] = (
            self._santander_generate_digital_sign('in',acquirer,
                                                  time_stamp,
                                                  acquirer.santander_merchant_id,
                                                  tx_values['reference']+'$'+time_stamp ,
                                                  int((tx_values['amount'] * 100)),
                                                  cur,
                                                  acquirer.santander_secret_key
            ))
        return partner_values, santander_tx_values

    @api.multi
    def santander_get_form_action_url(self):
        return self._get_santander_urls(self.environment)['santander_form_url']

    def _product_description(self, order_ref):
        sale_order = self.env['sale.order'].search([('name', '=', order_ref)])
        res = ''
        if sale_order:
            description = '|'.join(x.name for x in sale_order.order_line)
            res = description[:125]
        return res


class Txsantander(models.Model):
    _inherit = 'payment.transaction'

    santander_txnid = fields.Char('Transaction ID')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _santander_form_get_tx_from_data(self, data):
      
        print 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU'
        print 'data'
        print data
        """ Given a data dict coming from santander, verify it and
        find the related transaction record. """
        reference = data.get('ORDER_ID', '')
        amount = data.get('AMOUNT', '')
        time_stamp = data.get('TIMESTAMP', '')
        authcode = data.get('AUTHCODE')
        result = data.get('RESULT')
        message = data.get('MESSAGE')
        pasref = data.get('PASREF')
        shasign = data.get('SHA1HASH')
		
        if not reference or not authcode or not shasign:
            error_msg = 'santander: received data with missing reference' \
                ' (%s) or authcode (%s) or shashign (%s)' % (reference,
                                                           authcode, shasign)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        _reference = reference[0:reference.find('$')]
        print '_reference'
        print _reference
        tx = self.search([('reference', '=', _reference)])
        if not tx or len(tx) > 1:
            error_msg = 'santander: received data for reference %s' % (_reference)
            if not tx:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        # verify shasign
        acquirer = tx.acquirer_id
        print 'acquirer'
        print acquirer

        shasign_check = acquirer._santander_generate_digital_sign(
                                                  'out',
                                                  acquirer,
                                                  time_stamp,
                                                  acquirer.santander_merchant_id,
                                                  reference,
                                                  amount,
                                                  acquirer.santander_currency,
                                                  acquirer.santander_secret_key,
                                                  result,
                                                  message,
                                                  pasref,
                                                  authcode,
                                                  reference
                                                  )
        if shasign_check.upper() != shasign.upper():
            error_msg = 'santander: invalid shasign, received %s, computed %s,' \
                ' for data %s' % (shasign, shasign_check, data)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx

    @api.model
    def _santander_form_get_invalid_parameters(self, tx, data):
        print 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
        invalid_parameters = []

        if (tx.acquirer_reference and
                data.get('ORDER_ID')) != tx.acquirer_reference:
            invalid_parameters.append(
                ('Transaction Id', data.get('ORDER_ID'),
                 tx.acquirer_reference))
        # check what is buyed
        if (float_compare(float(data.get('AMOUNT', '0.0')) / 100,
                          tx.amount, 2) != 0):
            invalid_parameters.append(('Amount', data.get('AMOUNT'),
                                       '%.2f' % tx.amount))
        return invalid_parameters

    @api.model
    def _santander_form_validate(self, tx, data):
        print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        status_code = data.get('RESULT', '29999')
        print 'status_code'
        print status_code 

        if (status_code == '00'):
            tx.write({
                'state': 'done',
                'santander_txnid': data.get('AUTHCODE'),
                'state_message': _('Ok: %s') % data.get('MESSAGE'),
            })
            email_act = tx.sale_order_id.action_quotation_send()
            # send the email
            print 'email_act.get(context)'
            print email_act.get('context')
            print 'email_act'
            print email_act
            if email_act and email_act.get('context'):
                self.send_mail(email_act['context'])
            print 'ESTADO CORRECTO okokokokokokokokok'
            return True
        if (status_code >= 101) and (status_code <= 202):
            # 'Payment error: code: %s.'
            tx.write({
                'state': 'pending',
                'santander_txnid': data.get('AUTHCODE'),
                'state_message': _('Error: %s') % data.get('Ds_Response'),
            })
            return True
        if (status_code == 912) and (status_code == 9912):
            # 'Payment error: bank unavailable.'
            tx.write({
                'state': 'cancel',
                'santander_txnid': data.get('AUTHCODE'),
                'state_message': (_('Bank Error: %s')
                                  % data.get('Ds_Response')),
            })
            return True
        else:
            error = 'santander: feedback error'
            _logger.info(error)
            tx.write({
                'state': 'error',
                'santander_txnid': data.get('AUTHCODE'),
                'state_message': error,
            })
            return False

    def send_mail(self, email_ctx):
        print 'HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH'
        composer_values = {}
        template = self.env.ref('sale.email_template_edi_sale', False)
        if not template:
            print 'NO HAY PLANTILLA'		
            return True
        email_ctx['default_template_id'] = template.id
        composer_id = self.env['mail.compose.message'].with_context(
            email_ctx).create(composer_values)
        composer_id.with_context(email_ctx).send_mail()
        print 'EMAIL ENVIADO'
