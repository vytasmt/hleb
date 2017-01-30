# -*- coding: utf-8 -*-

from openerp import api
from openerp import models
from openerp.http import request
from fractions import Fraction as FR
from openerp import tools, SUPERUSER_ID
import decimal
import re


class BaronWebsite(models.Model):
    _name = 'baron_website_tools'

    @api.model
    def product_have_quantity(self, product):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        for rec in product.attribute_line_ids:
            if all(rec.value_ids.mapped('pack_true')):
                return True
        return False

    @api.model
    def product_get_quantity(self, product):
        uos_id = product.uos_id.id
        uom_id = product.uom_id.id
        res = {'uos_coeff': '','styles': '','factor': '', 'uos_name': False,'uom_name': False,'uos_qty': False, 'uom_qty': False, 'cof': False}
        res['list_price'] = product.list_price
        res['styles'] = ', '.join(self.env['product.style'].sudo().browse(product.website_style_ids.ids).mapped('html_class'))
        res['mult'] = 1
        res['variant_price'] = res['list_price']
        uom = self.env['product.uom'].sudo().browse(uom_id)
        res['uom_name'] = re.sub(re.compile(u'[0-9/ ]'), '', uom.name.encode('utf8').decode('utf8'))
        if uos_id:
            uos = self.env['product.uom'].sudo().browse(uos_id)
            res['mult'] = self.get_multiplier(product)
            res['uos_qty'] = self.subnumber(uos.name)
            res['uom_qty'] = self.subnumber(uom.name)
            res['variant_uos'] = decimal.Decimal(res['uos_qty'] * res['mult'])
            res['factor'] = product.uos_id.factor
            res['uos_coeff'] = product.uos_coeff or 1
            res['variant_price'] = round(decimal.Decimal(res['mult']*res['list_price']/res['uos_coeff']),1)
            res['uos_name'] = re.sub(re.compile(u'[0-9/ ]'), '',  uos.name.encode('utf8').decode('utf8'))
            if uos.uom_type == 'smaller':
                res['cof'] = float(product.uos_coeff)
            elif uos.uom_type == 'bigger':
                res['cof'] = product.uos_coeff
            else:
                res['cof'] = 1
            return res
        return res

    @api.model
    def convert_price(self, price):
        return ("%.02f" % price).replace('.', ',')

    def get_multiplier(self, product):
        res = 1
        if product._model._name == 'product.template':
            return res
        for v in product.attribute_value_ids:
            for price_id in v.price_ids:
                if price_id.product_tmpl_id.id == product.product_tmpl_id.id:
                    if price_id.pack_true:
                        res *= price_id.pack_qty
        return res

    @api.model
    def variant_data(self, product, variant):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        partner = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).partner_id
        pricelist = partner.property_product_pricelist.id
        vals = {'variant_qty': False, 'variant_uos': False}
        # vals['variant_qty'] = self.subnumber(variant.name)
        # vals['variant_uos'] = ""
        # if len(product.product_variant_ids):
        #     for prod_prod in product.product_variant_ids:
        #         price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], prod_prod.id, 1.0, partner.id, context)[pricelist]
        #         vals['id'] = prod_prod.id
        #         vals['price'] = price
        return vals

    @staticmethod
    def subnumber(inp):
        s = "".join([x for x in inp if x in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "/", ".", ",", "-"]]).replace(",",".")
        try:
            res = FR(s)
            return float(res) if int(res) != float(res) else int(res)
        except:
            return 1
