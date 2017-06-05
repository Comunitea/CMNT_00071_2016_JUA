# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class acp_contrato_genera_servicio(osv.osv_memory):
    """ PGenera serviciog """

    _name = 'acp_contrato.genera_servicio'
    _description = 'Crear servicio'


    _columns = {
        'ano': fields.integer('Año', required=True  ),
        'mes': fields.selection([
                ('01', 'Enero'),
                ('02', 'Febrero'),
                ('03', 'Marzo'),
                ('04', 'Abril'),
                ('05', 'Mayo'),
                ('06', 'Junio'),
                ('07', 'Julio'),
                ('08', 'Agosto'),
                ('09', 'Septiembre'),
                ('10', 'Octubre'),
                ('11', 'Noviembre'),
                ('12', 'Diciembre'),
            ], 'Mes', select=True,required=True),
        'generar_facturas': fields.boolean('Generar facturas programadas'),
        'diario_id': fields.many2one('account.journal', 'Diario', select=True),
        'facturar_servicios': fields.boolean('Generar facturas servicios'),
        'generar_servicios': fields.boolean('Generar servicios'),
    }


    _defaults = {
        'ano': lambda *a: int(time.strftime("%Y", time.localtime())),
    }


    def action_cancel(self, cr, uid, ids, context=None):

        return {'type':'ir.actions.act_window_close'}





    def genera_servicio(self, cr, uid, ids, ano, mes, context=None):

        print '<<<<<<<<<<<<<<<<<  GENERA SERVICIOS'
        mod_obj = self.pool.get('ir.model.data')
        #pool = pooler.get_pool(cr.dbname)
        warning = {}
        if not ano or not mes:
            raise osv.except_osv('Error !' , 'Especifique año y mes')
            return {'type':'ir.actions.act_window_close'}
        contador = 0
        contador_opp = 0
        serv_obj = self.pool.get('acp_contrato.servicio')
        opp_obj = self.pool.get('crm.lead')
        serv_mat_obj = self.pool.get('acp_contrato.servicio_producto')

        # Se seleccionan los servicios programados que no esten dados de baja
        cr.execute("select acp_contrato_contrato.id AS id , acp_contrato_contrato.name, acp_contrato_programar_servicio.tipo_servicio_id AS tipo_servicio_id , \
                    acp_contrato_contrato.partner_id as cliente_id ,  acp_contrato_contrato.partner_direccion_id cliente_direccion_id ,  acp_contrato_contrato.partner_factura_id cliente_factura_id , \
                    acp_contrato_programar_servicio.contratado, \
                    lpad(acp_contrato_fechas_servicio.dia::varchar, 2, '0') as dia_servicio,(select copia_materiales from acp_contrato_tipo_servicio  where id = acp_contrato_programar_servicio.tipo_servicio_id) as carga_materiales, \
                    acp_contrato_programar_servicio.id as servicio_prog_id \
                    from acp_contrato_contrato \
                    INNER JOIN acp_contrato_programar_servicio \
                    on acp_contrato_contrato.id =  acp_contrato_programar_servicio.contrato_id \
                    INNER  join acp_contrato_fechas_servicio \
                    on acp_contrato_programar_servicio.id = acp_contrato_fechas_servicio.programacion_id \
                    and acp_contrato_fechas_servicio.mes = '"+ mes +"' \
                    and acp_contrato_contrato.state  not in ('open','cancel','done') ")

        for contrato in cr.dictfetchall():
            # No esta marcado la opcion de contratado se crea una oportunidad
            if contrato['contratado'] == False:
                # Se comprueba si está creada ya la oportunidad del contrato para el mes y año
                cr.execute("select count(*) AS total from crm_lead \
                    where mes = '"+ mes +"' and ano = '"+ str(ano) +"' and contrato_id = " + str(contrato['id']))
                total = cr.fetchone()[0]
                # Si no está creada se crea la oportunidad
                if total == 0:
                    cr.execute("select  sum(acp_contrato_servicio_producto_extra.cantidad*acp_contrato_servicio_producto_extra.importe) as total \
                                from acp_contrato_servicio, \
                                acp_contrato_servicio_producto_extra \
                                where acp_contrato_servicio.contrato_id = "+ str(contrato['id']) +" \
                                and acp_contrato_servicio_producto_extra.servicio_id = acp_contrato_servicio.id")

                    planned_revenue = cr.fetchone()[0]
                    sales_man = self.pool.get('res.partner').browse(cr, uid, contrato['cliente_id']).user_id.id
                    phone = self.pool.get('res.partner').browse(cr, uid, contrato['cliente_direccion_id']).phone
                    email = self.pool.get('res.partner').browse(cr, uid, contrato['cliente_direccion_id']).email

                    opp = {
                        'contrato_id': contrato['id'],
                        'fecha': '01/' + mes + '/' + str(ano),
                        'ano': ano,
                        'mes': mes,
                        'day_close': 0,
                        'day_open': 0,
                        'partner_id': contrato['cliente_id'],
                        'user_id': sales_man,
                        'company_id': self.pool.get('res.company')._company_default_get(cr, uid, 'crm.lead', context=None),
                        'priority': '3',
                        'state': 'draft',
                        'type': 'opportunity',
                        'description': 'Oportunidad de realizar un servicio no contratado para el contrato: ' + str(contrato['name']) + ', Mes: '+ mes + '/' + str(ano),
                        'optin': False,
                        'phone': phone,
                        'active': True,
                        'categ_id':self.pool.get('crm.case.categ').search(cr, uid, [('name','=', 'Servicios') ] , context=context)[0],
                        'name': contrato['name'] + '/'+ mes + '/' + str(ano),
                        'optout': False,
                        'email_from': email,
                        'probability':0,
                        'partner_address_id':contrato['cliente_direccion_id'],
                        #'planned_revenue': planned_revenue
                    }

                    opp_id = opp_obj.create(cr, uid, opp, context=context)
                    contador_opp = contador_opp + 1


            if contrato['contratado'] == True:
                # Comprueba si el tipo de servicio ya está creado para el contrato y mes/año
                cr.execute("select count(*) AS total\
                            from acp_contrato_servicio \
                            where acp_contrato_servicio.contrato_id = "+ str(contrato['id']) +" \
                              and acp_contrato_servicio.tipo_servicio = "+ str(contrato['tipo_servicio_id']) +" \
                              and acp_contrato_servicio.servicio_prog_id = "+ str(contrato['servicio_prog_id']) +" \
                              and to_char(acp_contrato_servicio.fecha,'MM/YYYY') = '"+ mes + '/' + str(ano)+"'")
                total = cr.fetchone()[0]
                # Recupera los datos del ultimo servicio
                cr.execute( "select id as id, fecha as ultima_fecha \
                             from acp_contrato_servicio \
                             where acp_contrato_servicio.contrato_id = "+ str(contrato['id']) +"  \
                               and acp_contrato_servicio.tipo_servicio = "+ str(contrato['tipo_servicio_id']) +" \
                               and fecha = (select max(fecha) AS total \
                                            from acp_contrato_servicio\
                                            where acp_contrato_servicio.contrato_id = "+ str(contrato['id']) +"  \
                                              and acp_contrato_servicio.tipo_servicio = "+ str(contrato['tipo_servicio_id']) +" \
                                              and acp_contrato_servicio.fecha < to_date('"+ mes + '/' + str(ano)+"','mm/yyyy'))")
                ultimo_servicio = cr.fetchone()
                if ultimo_servicio:
                    ultimo_servicio_id = ultimo_servicio[0]
                    ultima_fecha_servicio = ultimo_servicio[1]
                else:
                    ultimo_servicio_id = None
                    ultima_fecha_servicio = None

                if total == 0:

                    #esto es para evitar el errroe en los meses de febrero o que tengan 30 dias,
                    #cuando el dia de facturacion o servicio se establece a 31
                    try:
                        fecha_servicio = datetime.strptime((contrato['dia_servicio'] + '/' + mes + '/' + str(ano)).strip(), '%d/%m/%Y')
                    except ValueError:
                        try:
                            fecha_servicio = datetime.strptime((str((int(contrato['dia_servicio'])-1)) + '/' + mes + '/' + str(ano)).strip(), '%d/%m/%Y')
                        except ValueError:
                            try:
                                fecha_servicio = datetime.strptime((str((int(contrato['dia_servicio'])-2)) + '/' + mes + '/' + str(ano)).strip(), '%d/%m/%Y')
                            except ValueError:
                                fecha_servicio = datetime.strptime((str((int(contrato['dia_servicio'])-3)) + '/' + mes + '/' + str(ano)).strip(), '%d/%m/%Y')


                    serv = {
                        'contrato_id': contrato['id'],
                        'fecha': fecha_servicio,
                        'partner_id': contrato['cliente_id'],
                        'partner_direccion_id': contrato['cliente_direccion_id'],
                        'partner_factura_id': contrato['cliente_factura_id'],
                        'tipo_servicio' : contrato['tipo_servicio_id'],
                        'state' : 'open',
                        'servicio_prog_id': contrato['servicio_prog_id']
                        }

                    serv_id = serv_obj.create(cr, uid, serv, context=context)
                    contador = contador + 1


            print 'se han generado %s servicio y %s oportunidades'%(str(contador),str(contador_opp))
        return True

    def _prepara_facturas_programadas(self, cr, uid, ids, ano, mes, diario_id, context=None):
        if context is None:
            context = {}
        fact_obj = self.pool.get('acp_contrato.facturacion')
        fact_lin_obj = self.pool.get('acp_contrato.conceptos_factura')
        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        inv_line_obj = self.pool.get('account.invoice.line')
        ir_sequence_obj = self.pool.get('ir.sequence')


        result = []
        # Se seleccionan facturas programadas de los contratos que no estén dados de baja
        # y tengan configurado el mes
        import ipdb; ipdb.set_trace()
        cr.execute("select acp_contrato_contrato.id as contrato_id , acp_contrato_contrato.name,acp_contrato_contrato.partner_id as cliente_id ,\
                    acp_contrato_contrato.partner_direccion_id cliente_direccion_id,acp_contrato_facturacion.id as programa_id, \
                    acp_contrato_facturacion.name as facturacion_name,to_char(acp_contrato_fechas_facturacion.dia,'00') as dia_factura \
                    from acp_contrato_facturacion, \
                         acp_contrato_contrato, \
                         acp_contrato_fechas_facturacion \
                    where acp_contrato_facturacion.autofactura = True \
                      and acp_contrato_contrato.id = acp_contrato_facturacion.contrato_id \
                      and acp_contrato_contrato.state not in ('open','cancel','done') \
                      and acp_contrato_fechas_facturacion.facturacion_id = acp_contrato_facturacion.id \
                      and acp_contrato_fechas_facturacion.mes = '"+ mes +"'")
        for factprog in cr.dictfetchall():
            # Comprobamos si está creada la factura para el mes
            user = self.pool.get('res.users').browse(cr, uid, uid, context)
            cr.execute("select count(*) as total \
                        from account_invoice,account_invoice_line \
                        where account_invoice.type = 'out_invoice' \
                        and account_invoice_line.invoice_id = account_invoice.id \
                        and account_invoice_line.factprog_id =  "+ str(factprog['programa_id']) +" \
                        and to_char(account_invoice.date_invoice,'MM/YYYY') = '"+ mes + '/' + str(ano)+"'\
                        and account_invoice.company_id = " + str(user.company_id.id))
            total = cr.fetchone()[0]

            if total == 0:
                fiscal_position_id = self.pool.get('res.partner').browse(cr, uid, factprog['cliente_id']).property_account_position.id
                #Recuperamos las lineas a facturar
                fact_lin_ids = fact_lin_obj.search(cr, uid,[('facturacion_id','=',factprog['programa_id'])], context=context)
                inv_line = []
                for fact_lin in fact_lin_obj.browse(cr, uid, fact_lin_ids, context=context):
                    val = inv_line_obj.product_id_change(cr, uid, [], fact_lin.product_id.id,
                        False, partner_id=factprog['cliente_id'], fposition_id=fiscal_position_id)
                    res = val['value']

                    # determine and check income account
                    if not fact_lin.product_id :
                        prop = ir_property_obj.get(cr, uid,
                            'property_account_income_categ', 'product.category', context=context)
                        prop_id = prop and prop.id or False
                        account_id = fiscal_obj.map_account(cr, uid, fiscal_position_id or False, prop_id)
                        if not account_id:
                            raise osv.except_osv(_('Configuration Error!'),
                                    _('There is no income account defined as global property.'))
                        res['account_id'] = account_id
                    if not res.get('account_id'):
                        raise osv.except_osv(_('Configuration Error!'),
                                _('There is no income account defined for this product: "%s" (id:%d).') % \
                                 (fact_lin.name, fact_lin.product_id,))

                    # determine invoice amount
                    if (fact_lin.cantidad * fact_lin.importe) <= 0.00:
                        raise osv.except_osv(_('Incorrect Data'),
                            _('The value of Advance Amount must be positive.'))

                    inv_amount = (fact_lin.cantidad * fact_lin.importe)

                    if not res.get('name'):
                        #TODO: should find a way to call formatLang() from rml_parse
                        symbol = self.pool.get('res.partner').browse(cr, uid, factprog['cliente_id']).property_product_pricelist.currency_id.symbol
                        symbol_position = self.pool.get('res.partner').browse(cr, uid, factprog['cliente_id']).property_product_pricelist.currency_id.position
                        partner_lang = self.pool.get('res.partner').browse(cr, uid, factprog['cliente_id']).lang

                        if symbol_position == 'after':
                            symbol_order = (inv_amount, symbol)
                        else:
                            symbol_order = (symbol, inv_amount)
                        res['name'] = self._translate_advance(cr, uid, context=dict(context, lang=partner_lang)) % symbol_order

                    # determine taxes
                    if res.get('invoice_line_tax_id'):
                       res['invoice_line_tax_id'] = [(6, 0, res.get('invoice_line_tax_id'))]
                    else:
                       res['invoice_line_tax_id'] = False

                    d = ir_sequence_obj._interpolation_dict()
                    line_name = ir_sequence_obj._interpolate(fact_lin.name, d)

                    # create the invoice
                    inv_line_values = self._get_inv_line_values(cr, uid, ids, fact_lin, line_name, res, factprog, context=context)
                    inv_line.append((0,0,inv_line_values))
                if not inv_line:
                    continue
                #esto es para evitar el errroe en los meses de febrero o que tengan 30 dias,
                #cuando el dia de facturacion o servicio se establece a 31

                try:
                    date_invoice = datetime.strptime((factprog['dia_factura'] + '/' + mes + '/' + str(ano)).strip(), '%d/%m/%Y').date()
                except ValueError:
                    try:
                        date_invoice = datetime.strptime((str((int(factprog['dia_factura'])-1)) + '/' + mes + '/' + str(ano)).strip(), '%d/%m/%Y').date()
                    except ValueError:
                        try:
                            date_invoice = datetime.strptime((str((int(factprog['dia_factura'])-2)) + '/' + mes + '/' + str(ano)).strip(), '%d/%m/%Y').date()
                        except ValueError:
                            date_invoice = datetime.strptime((str((int(factprog['dia_factura'])-3)) + '/' + mes + '/' + str(ano)).strip(), '%d/%m/%Y').date()


                inv_values = {
                    'name': factprog['facturacion_name'],
                    'type': 'out_invoice',
                    'reference': False,
                    'account_id': self.pool.get('res.partner').browse(cr, uid, factprog['cliente_id']).property_account_receivable.id,
                    'partner_id': factprog['cliente_direccion_id'],
                    'invoice_line': inv_line,
                    'currency_id': self.pool.get('res.partner').browse(cr, uid, factprog['cliente_id']).property_product_pricelist.currency_id.id,
                    'comment': '',
                    'payment_term': self.pool.get('res.partner').browse(cr, uid, factprog['cliente_id']).property_payment_term.id,
                    'fiscal_position': fiscal_position_id,
                    'dft_contrato_id': factprog['contrato_id'],
                    'dft_factprog_id': factprog['programa_id'],
                    'date_invoice': date_invoice,
                    'journal_id': diario_id,
                }

                result.append((factprog['programa_id'], inv_values))
        return result

    def _get_inv_line_values(self, cr, uid, ids, fact_lin, line_name, res, factprog, context=None):
        res = {
            'name': line_name,
            'account_id': res['account_id'],
            'price_unit': fact_lin.importe,
            'quantity': fact_lin.cantidad,
            'discount': False,
            'uos_id': res.get('uos_id', False),
            'product_id': fact_lin.product_id.id,
            'invoice_line_tax_id': res.get('invoice_line_tax_id'),
            'contrato_id': factprog['contrato_id'],
            'factprog_id': factprog['programa_id'],
        }
        return res


    def _crea_facturas(self, cr, uid, inv_values, context=None):
        print "<<<<<<<<<<<<<<<<<<<<< FUNCION CREA FACTURA"
        inv_obj = self.pool.get('account.invoice')
        inv_id = inv_obj.create(cr, uid, inv_values, context=context)
        inv_obj.button_reset_taxes(cr, uid, [inv_id], context=context)
        return inv_id

    def genera_factura_programada(self, cr, uid, ids, ano, mes, diario_id, context=None):
        """ Crea las facturas programadas pendientes """
        print "<<<<<<<<<<<<<<<<<<<<< FACTURAS PROGRAMADAS >>>>>>>>>>>>>>>>>>>>>"
        inv_ids = []
        for factprog_id, inv_values in self._prepara_facturas_programadas(cr, uid, ids, ano, mes, diario_id, context=context):
            inv_ids.append(self._crea_facturas(cr, uid, inv_values, context=context))

        return True

    def action_genera(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        data = self.read(cr, uid, ids, [], context=context)[0]

        ano = data['ano']
        mes = data['mes']
        diario_id = data.get('diario_id',False) and data['diario_id'][0] or False
        genera_fact_prog = data['generar_facturas']
        genera_fact_serv = data['facturar_servicios']
        genera_servicio = data['generar_servicios']

        if genera_fact_prog:
            print "<<<<<<<<<<<<<<<<<<<<<  Genera Facturas Programadas"
            self.genera_factura_programada(cr,uid,ids,ano,mes,diario_id,context=None)

        if genera_servicio:
            print "<<<<<<<<<<<<<<<<<<<<<  Genera Servicios"
            self.genera_servicio(cr,uid,ids,ano,mes,context=None)

        return True

acp_contrato_genera_servicio()

#~ class acp_contrato_genera_factura_servicio(osv.osv_memory):
    #~ """ PGenera serviciog """
#~
    #~ _name = 'acp_contrato.generar_factura_servicio'
    #~ _description = 'Creacion factura de servicio'
    #~ _columns = {
        #~ 'agrupar': fields.selection([
                #~ ('contrato', 'Contrato'),
                #~ ('cliente', 'Cliente'),
                #~ ('servicio', 'Servicio'),
            #~ ], 'Agrupar facturar por', select=True, required=True),
        #~ 'diario_id': fields.many2one('account.journal', 'Diario', select=True, required=True),
        #~ 'fecha_factura': fields.date('Fecha Factura', required=True, select=True),
    #~ }
    #~ _defaults = {
        #~ 'agrupar': "contrato",
    #~ }
    #~
#~
    #~ def action_cancel(self, cr, uid, ids, context=None):
#~
        #~ return {'type':'ir.actions.act_window_close'}
#~
    #~ def _prepara_facturas_servicios(self, cr, uid, ids, agrupar, fecha_factura, diario_id,context=None):
        #~
        #~ if context is None:
            #~ context = {}
        #~ fact_obj = self.pool.get('acp_contrato.facturacion')
        #~ fact_lin_obj = self.pool.get('acp_contrato.conceptos_factura')
        #~ ir_property_obj = self.pool.get('ir.property')
        #~ fiscal_obj = self.pool.get('account.fiscal.position')
        #~ inv_line_obj = self.pool.get('account.invoice.line')
        #~ ir_sequence_obj = self.pool.get('ir.sequence')
#~
        #~ # Actualiza los datos de clientes en servicios si no los tiene indicados
        #~ # los actualiza segun el cliente de contrato
        #~ cr.execute("select distinct acp_contrato_servicio.id as servicio_id,acp_contrato_contrato.partner_id as cont_partner_id, \
                           #~ acp_contrato_contrato.partner_direccion_id as cont_partner_direccion_id,\
                           #~ acp_contrato_contrato.partner_factura_id as cont_partner_factura_id,\
                           #~ acp_contrato_servicio.partner_id as serv_partner_id, \
                           #~ acp_contrato_servicio.partner_direccion_id as serv_partner_direccion_id,\
                           #~ acp_contrato_servicio.partner_factura_id as serv_partner_factura_id\
                    #~ from acp_contrato_servicio_producto_extra,acp_contrato_servicio,acp_contrato_contrato \
                    #~ where acp_contrato_servicio_producto_extra.id in %s and\
                          #~ acp_contrato_servicio.id = acp_contrato_servicio_producto_extra.servicio_id  and\
                          #~ acp_contrato_contrato.id = acp_contrato_servicio.contrato_id ",(tuple(ids),))
#~
        #~ for check in cr.dictfetchall():
            #~ if not check['serv_partner_id']:
                #~ cr.execute('UPDATE acp_contrato_servicio \
                            #~ SET partner_id = %s, partner_direccion_id = %s, partner_factura_id = %s \
                            #~ WHERE id = %s',(check['cont_partner_id'],check['cont_partner_direccion_id'],check['cont_partner_factura_id'],check['servicio_id']))
#~
            #~ if not check['serv_partner_direccion_id']:
                #~ cr.execute('UPDATE acp_contrato_servicio \
                            #~ SET  partner_direccion_id = %s \
                            #~ WHERE id = %s',(check['cont_partner_direccion_id'],check['servicio_id']))
#~
            #~ if not check['serv_partner_factura_id']:
                #~ cr.execute('UPDATE acp_contrato_servicio \
                            #~ SET  partner_factura_id = %s \
                            #~ WHERE id = %s',(check['cont_partner_factura_id'],check['servicio_id']))
#~
#~
#~
        #~ result = []
        #~ # Se seleccionan facturas programadas de los contratos que no estén dados de baja
        #~ # y tengan configurado el mes
        #~ if agrupar== 'contrato':
            #~ agrupar_campo = "acp_contrato_servicio.contrato_id"
#~
        #~ if agrupar == 'cliente':
            #~ agrupar_campo = "acp_contrato_servicio.partner_factura_id"
#~
        #~ if agrupar == 'servicio':
            #~ agrupar_campo = "acp_contrato_servicio.servicio_id"
#~
#~
        #~ cr.execute("select acp_contrato_servicio.partner_factura_id as cliente_direccion_id, \
                            #~ "+ agrupar_campo +"  as id \
                    #~ from acp_contrato_servicio_producto_extra,acp_contrato_servicio,acp_contrato_contrato \
                    #~ where acp_contrato_servicio_producto_extra.id in %s and\
                          #~ acp_contrato_servicio.id = acp_contrato_servicio_producto_extra.servicio_id  and\
                          #~ acp_contrato_contrato.id = acp_contrato_servicio.contrato_id \
                    #~ group by acp_contrato_servicio.partner_factura_id, "+ agrupar_campo,(tuple(ids),))
        #~ for serv_fact in cr.dictfetchall():
            #~ # Datos de cabecera de factura
#~
            #~ cliente_factura_id = serv_fact['cliente_direccion_id']
#~
#~
#~
            #~ fiscal_position_id = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_account_position.id
#~
            #~ cr.execute("select acp_contrato_servicio_producto_extra.product_id as product_id, acp_contrato_servicio_producto_extra.cantidad as cantidad, \
                        #~ acp_contrato_servicio_producto_extra.importe as precio,acp_contrato_servicio_producto_extra.id as servicio_extra_id, \
                        #~ acp_contrato_servicio.id as servicio_id,acp_contrato_contrato.id as contrato_id \
                        #~ from acp_contrato_servicio_producto_extra,acp_contrato_servicio,acp_contrato_contrato \
                        #~ where acp_contrato_servicio_producto_extra.id in %s and\
                              #~ acp_contrato_servicio.id = acp_contrato_servicio_producto_extra.servicio_id  and\
                              #~ acp_contrato_contrato.id = acp_contrato_servicio.contrato_id and \
                              #~ " + agrupar_campo + "= %s",(tuple(ids),serv_fact['id'],))
            #~ inv_line = []
            #~ for serv_fact_lin in cr.dictfetchall():
                #~ # Datos de linea de factura
                #~ val = inv_line_obj.product_id_change(cr, uid, [], serv_fact_lin['product_id'],
                        #~ False, partner_id=cliente_factura_id, fposition_id=fiscal_position_id)
                #~ res = val['value']
#~
                #~ # determine and check income account
                #~ if not serv_fact_lin['product_id'] :
                    #~ prop = ir_property_obj.get(cr, uid,
                       #~ 'property_account_income_categ', 'product.category', context=context)
                    #~ prop_id = prop and prop.id or False
                    #~ account_id = fiscal_obj.map_account(cr, uid, fiscal_position_id or False, prop_id)
                    #~ if not account_id:
                        #~ raise osv.except_osv(_('Configuration Error!'),
                            #~ _('There is no income account defined as global property.'))
                    #~ res['account_id'] = account_id
#~
                #~ if not res.get('account_id'):
                    #~ raise osv.except_osv(_('Configuration Error!'),
                            #~ _('There is no income account defined for this product: "%s" (id:%d).') % \
                            #~ (fact_lin.name, fact_lin.product_id,))
#~
                #~ # determine invoice amount
                #~ if (serv_fact_lin['cantidad'] * serv_fact_lin['precio']) <= 0.00:
                        #~ raise osv.except_osv(_('Incorrect Data'),
                            #~ _('The value of Advance Amount must be positive.'))
#~
                #~ inv_amount =  (serv_fact_lin['cantidad'] * serv_fact_lin['precio'])
#~
                #~ if not res.get('name'):
                    #~ #TODO: should find a way to call formatLang() from rml_parse
                    #~ symbol = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_product_pricelist.currency_id.symbol
                    #~ symbol_position = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_product_pricelist.currency_id.position
                    #~ partner_lang = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).lang
                        #~
                    #~ if symbol_position == 'after':
                        #~ symbol_order = (inv_amount, symbol)
                    #~ else:
                        #~ symbol_order = (symbol, inv_amount)
                    #~ res['name'] = self._translate_advance(cr, uid, context=dict(context, lang=partner_lang)) % symbol_order
#~
                #~ # determine taxes
                #~ if res.get('invoice_line_tax_id'):
                    #~ res['invoice_line_tax_id'] = [(6, 0, res.get('invoice_line_tax_id'))]
                #~ else:
                    #~ res['invoice_line_tax_id'] = False
#~
#~
                #~
                #~ taxes = []
                #~ for tax in self.pool.get('acp_contrato.servicio_producto_extra').browse(cr, uid, serv_fact_lin['servicio_extra_id']):
                    #~ if tax.tax_id not in taxes:
                        #~ taxes.append(tax.tax_id.id)
#~
                #~ # create the invoice
                #~ inv_line_values = {
                    #~ 'name': res['name'],
                    #~ 'account_id': res['account_id'],
                    #~ 'price_unit': serv_fact_lin['precio'],
                    #~ 'quantity':  serv_fact_lin['cantidad'],
                    #~ 'discount': False,
                    #~ 'uos_id': res.get('uos_id', False),
                    #~ 'product_id':  serv_fact_lin['product_id'],
                    #~ 'invoice_line_tax_id': [(6, 0, taxes)],
                    #~ 'contrato_id': serv_fact_lin['contrato_id'],
                    #~ 'servicio_id': serv_fact_lin['servicio_id'],
                    #~ 'servicio_extra_id': serv_fact_lin['servicio_extra_id'],
                #~ }
                #~ inv_line.append((0,0,inv_line_values))
#~
            #~ inv_values = {
                #~ #'name': factprog['facturacion_name'],
                #~ 'type': 'out_invoice',
                #~ 'reference': False,
                #~ 'account_id': self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_account_receivable.id,
                #~ 'partner_id': cliente_factura_id,
                #~ 'invoice_line': inv_line,
                #~ 'currency_id': self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_product_pricelist.currency_id.id,
                #~ 'comment': '',
                #~ 'payment_term': self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_payment_term.id,
                #~ 'fiscal_position': fiscal_position_id,
                #~ 'date_invoice': fecha_factura,
                #~ 'journal_id': diario_id,
            #~ }
#~
            #~ result.append(( inv_values))
        #~ return result
#~
    #~ def action_create_invoice(self, cr, uid, ids, context=None):
        #~ genera_obj = self.pool.get('acp_contrato.genera_servicio')
        #~ mod_obj = self.pool.get('ir.model.data')
        #~ act_obj = self.pool.get('ir.actions.act_window')
        #~ if context is None:
            #~ context = {}
        #~
        #~ data = self.read(cr, uid, ids)[0]
        #~ """ Crea las facturas programadas pendientes """
        #~ inv_ids = []
        #~ for inv_values in self._prepara_facturas_servicios(cr,uid,context.get(('active_ids'), []),data['agrupar'],data['fecha_factura'],data['diario_id'][0],context=None):
            #~ inv_ids.append(genera_obj._crea_facturas(cr, uid, inv_values, context=context))
#~
#~
        #~ inv_line_obj = self.pool.get('account.invoice.line')
        #~ inv_line_ids = inv_line_obj.search(cr, uid,[('invoice_id','in',inv_ids)], context=context)
        #~ for inv_line in inv_line_obj.browse(cr, uid, inv_line_ids, context=context):
            #~ self.pool.get('acp_contrato.servicio_producto_extra').write(cr, uid, inv_line.servicio_extra_id.id, {'invoice_state': 'facturado'}, context=context)
        #~ return True
#~
#~ acp_contrato_genera_factura_servicio()

class acp_contrato_genera_factura_servicio(osv.osv_memory):
    """ PGenera serviciog """

    _name = 'acp_contrato.generar_factura_servicio'
    _description = 'Creacion factura de servicio'
    _columns = {
        'agrupar': fields.selection([
                ('contrato', 'Contrato'),
                ('cliente', 'Cliente'),
                ('servicio', 'Servicio'),
            ], 'Agrupar facturar por', select=True, required=True),
        'diario_id': fields.many2one('account.journal', 'Diario', select=True, required=True),
        'fecha_factura': fields.date('Fecha Factura', required=True, select=True),
    }
    _defaults = {
        'agrupar': "cliente",
    }


    def action_cancel(self, cr, uid, ids, context=None):

        return {'type':'ir.actions.act_window_close'}

    def _prepara_facturas_servicios(self, cr, uid, ids, agrupar, fecha_factura, diario_id,context=None):

        if context is None:
            context = {}
        fact_obj = self.pool.get('acp_contrato.facturacion')
        fact_lin_obj = self.pool.get('acp_contrato.conceptos_factura')
        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        inv_line_obj = self.pool.get('account.invoice.line')
        ir_sequence_obj = self.pool.get('ir.sequence')

        # Actualiza los datos de clientes en servicios si no los tiene indicados
        # los actualiza segun el cliente de contrato
        cr.execute("select distinct acp_contrato_servicio.id as servicio_id,acp_contrato_contrato.partner_id as cont_partner_id, \
                           acp_contrato_contrato.partner_direccion_id as cont_partner_direccion_id,\
                           acp_contrato_contrato.partner_factura_id as cont_partner_factura_id,\
                           acp_contrato_servicio.partner_id as serv_partner_id, \
                           acp_contrato_servicio.partner_direccion_id as serv_partner_direccion_id,\
                           acp_contrato_servicio.partner_factura_id as serv_partner_factura_id\
                    from acp_contrato_tarea_producto,acp_contrato_tarea,acp_contrato_servicio,acp_contrato_contrato \
                    where acp_contrato_tarea_producto.id in %s and\
                          acp_contrato_tarea.id = acp_contrato_tarea_producto.tarea_id and\
                          acp_contrato_servicio.id = acp_contrato_tarea.servicio_id  and\
                          acp_contrato_contrato.id = acp_contrato_servicio.contrato_id ",(tuple(ids),))

        for check in cr.dictfetchall():
            if not check['serv_partner_id']:
                cr.execute('UPDATE acp_contrato_servicio \
                            SET partner_id = %s, partner_direccion_id = %s, partner_factura_id = %s \
                            WHERE id = %s',(check['cont_partner_id'],check['cont_partner_direccion_id'],check['cont_partner_factura_id'],check['servicio_id']))

            if not check['serv_partner_direccion_id']:
                cr.execute('UPDATE acp_contrato_servicio \
                            SET  partner_direccion_id = %s \
                            WHERE id = %s',(check['cont_partner_direccion_id'],check['servicio_id']))

            if not check['serv_partner_factura_id']:
                cr.execute('UPDATE acp_contrato_servicio \
                            SET  partner_factura_id = %s \
                            WHERE id = %s',(check['cont_partner_factura_id'],check['servicio_id']))



        result = []
        # Se seleccionan facturas programadas de los contratos que no estén dados de baja
        # y tengan configurado el mes
        if agrupar== 'contrato':
            agrupar_campo = "acp_contrato_servicio.contrato_id"

        if agrupar == 'cliente':
            agrupar_campo = "acp_contrato_servicio.partner_factura_id"

        if agrupar == 'servicio':
            agrupar_campo = "acp_contrato_servicio.id"


        cr.execute("select acp_contrato_servicio.partner_factura_id as cliente_direccion_id, \
                            "+ agrupar_campo +"  as id \
                    from acp_contrato_tarea_producto,acp_contrato_tarea,acp_contrato_servicio,acp_contrato_contrato \
                    where acp_contrato_tarea_producto.id in %s and\
                          acp_contrato_tarea.id = acp_contrato_tarea_producto.tarea_id and\
                          acp_contrato_servicio.id = acp_contrato_tarea.servicio_id  and\
                          acp_contrato_contrato.id = acp_contrato_servicio.contrato_id \
                    group by acp_contrato_servicio.partner_factura_id, "+ agrupar_campo,(tuple(ids),))
        for serv_fact in cr.dictfetchall():
            # Datos de cabecera de factura

            cliente_factura_id = serv_fact['cliente_direccion_id']



            fiscal_position_id = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_account_position.id

            cr.execute("select acp_contrato_tarea_producto.product_id as product_id, acp_contrato_tarea_producto.cantidad as cantidad, \
                        acp_contrato_tarea_producto.importe as precio,acp_contrato_tarea_producto.id as tarea_producto_id, \
                        acp_contrato_tarea.id as tarea_id, acp_contrato_servicio.id as servicio_id,acp_contrato_contrato.id as contrato_id \
                        from acp_contrato_tarea_producto,acp_contrato_tarea,acp_contrato_servicio,acp_contrato_contrato \
                        where acp_contrato_tarea_producto.id in %s and\
                              acp_contrato_tarea.id = acp_contrato_tarea_producto.tarea_id and\
                              acp_contrato_servicio.id = acp_contrato_tarea.servicio_id  and\
                              acp_contrato_contrato.id = acp_contrato_servicio.contrato_id and \
                              " + agrupar_campo + "= %s",(tuple(ids),serv_fact['id'],))
            inv_line = []
            for serv_fact_lin in cr.dictfetchall():
                # Datos de linea de factura
                val = inv_line_obj.product_id_change(cr, uid, [], serv_fact_lin['product_id'],
                        False, partner_id=cliente_factura_id, fposition_id=fiscal_position_id)
                res = val['value']

                # determine and check income account
                if not serv_fact_lin['product_id'] :
                    prop = ir_property_obj.get(cr, uid,
                       'property_account_income_categ', 'product.category', context=context)
                    prop_id = prop and prop.id or False
                    account_id = fiscal_obj.map_account(cr, uid, fiscal_position_id or False, prop_id)
                    if not account_id:
                        raise osv.except_osv(_('Configuration Error!'),
                            _('There is no income account defined as global property.'))
                    res['account_id'] = account_id

                if not res.get('account_id'):
                    raise osv.except_osv(_('Configuration Error!'),
                            _('There is no income account defined for this product: "%s" (id:%d).') % \
                            (fact_lin.name, fact_lin.product_id,))

                # determine invoice amount
                if (serv_fact_lin['cantidad'] * serv_fact_lin['precio']) <= 0.00:
                        raise osv.except_osv(_('Incorrect Data'),
                            _('The value of Advance Amount must be positive.'))

                inv_amount =  (serv_fact_lin['cantidad'] * serv_fact_lin['precio'])

                if not res.get('name'):
                    #TODO: should find a way to call formatLang() from rml_parse
                    symbol = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_product_pricelist.currency_id.symbol
                    symbol_position = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_product_pricelist.currency_id.position
                    partner_lang = self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).lang

                    if symbol_position == 'after':
                        symbol_order = (inv_amount, symbol)
                    else:
                        symbol_order = (symbol, inv_amount)
                    res['name'] = self._translate_advance(cr, uid, context=dict(context, lang=partner_lang)) % symbol_order

                # determine taxes
                if res.get('invoice_line_tax_id'):
                    res['invoice_line_tax_id'] = [(6, 0, res.get('invoice_line_tax_id'))]
                else:
                    res['invoice_line_tax_id'] = False


                taxes = []
                for tax in self.pool.get('acp_contrato.tarea_producto').browse(cr, uid, serv_fact_lin['tarea_producto_id']):
                    if tax.tax_id not in taxes and tax.tax_id:
                        taxes.append(tax.tax_id.id)

                # create the invoice
                inv_line_values = {
                    'name': res['name'],
                    'account_id': res['account_id'],
                    'price_unit': serv_fact_lin['precio'],
                    'quantity':  serv_fact_lin['cantidad'],
                    'discount': False,
                    'uos_id': res.get('uos_id', False),
                    'product_id':  serv_fact_lin['product_id'],
                    'invoice_line_tax_id': [(6, 0, taxes)],
                    'contrato_id': serv_fact_lin['contrato_id'],
                    'servicio_id': serv_fact_lin['servicio_id'],
                    'tarea_id': serv_fact_lin['tarea_id'],
                    'tarea_producto_id': serv_fact_lin['tarea_producto_id'],
                }
                inv_line.append((0,0,inv_line_values))

            inv_values = {
                #'name': factprog['facturacion_name'],
                'type': 'out_invoice',
                'reference': False,
                'account_id': self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_account_receivable.id,
                'partner_id': cliente_factura_id,
                'invoice_line': inv_line,
                'currency_id': self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_product_pricelist.currency_id.id,
                'comment': '',
                'payment_term': self.pool.get('res.partner').browse(cr, uid, cliente_factura_id).property_payment_term.id,
                'fiscal_position': fiscal_position_id,
                'date_invoice': fecha_factura,
                'journal_id': diario_id,
            }

            result.append(( inv_values))
        return result

    def action_create_invoice(self, cr, uid, ids, context=None):
        genera_obj = self.pool.get('acp_contrato.genera_servicio')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0]
        """ Crea las facturas programadas pendientes """
        inv_ids = []
        for inv_values in self._prepara_facturas_servicios(cr,uid,context.get(('active_ids'), []),data['agrupar'],data['fecha_factura'],data['diario_id'][0],context=None):
            inv_ids.append(genera_obj._crea_facturas(cr, uid, inv_values, context=context))


        inv_line_obj = self.pool.get('account.invoice.line')
        inv_line_ids = inv_line_obj.search(cr, uid,[('invoice_id','in',inv_ids)], context=context)
        for inv_line in inv_line_obj.browse(cr, uid, inv_line_ids, context=context):
            self.pool.get('acp_contrato.tarea_producto').write(cr, uid, inv_line.tarea_producto_id.id, {'invoice_state': 'facturado'}, context=context)
        return self.open_invoices(cr, uid, ids, inv_ids, context=context)

    def open_invoices(self, cr, uid, ids, invoice_ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        try:
            search_view_id = mod_obj.get_object_reference(cr, uid, 'account', 'view_account_invoice_filter')[1]
        except ValueError:
            search_view_id = False
        try:
            form_view_id = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')[1]
        except ValueError:
            form_view_id = False

        return  {
            'domain': [('id', 'in', invoice_ids)],
            'name': 'Facturas de cliente',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'context': {'type': 'out_invoice'},
            'views': [(False, 'tree'), (form_view_id, 'form')],
            'search_view_id': search_view_id,
        }

acp_contrato_genera_factura_servicio()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
