# -*- coding: utf-8 -*-

from openerp import api
from openerp import models
from openerp.http import request
from fractions import Fraction as FR
from openerp import tools, SUPERUSER_ID
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
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        uos_id = product.uos_id.id
        res = {}
        if uos_id:
            uos = self.env['product.uom'].sudo().browse(uos_id)
            res['qty'] = self.subnumber(uos.name)
            res['uos_name'] = re.sub(re.compile(u'[0-9/ ]'), '',  uos.name.encode('utf8').decode('utf8'))
            res['styles'] = ', '.join(self.env['product.style'].sudo().browse(product.website_style_ids.ids).mapped('html_class'))
            if uos.uom_type == 'smaller':
                res['cof'] = 1/float(product.uos_coeff)
            elif uos.uom_type == 'bigger':
                res['cof'] = product.uos_coeff
            else:
                res['cof'] = 1
            return res
        return {'styles': ''}

    @api.model
    def variant_data(self, variant):
        res = {}
        # if len(variant.value_ids):
        #     for var in variant.value_ids:
        #         vals = {'name': var.name, 'price_multiple': var.price_multiple}
        #         res['id'] = var.id
        #         res['data'] = vals
        return res


    @api.model
    def subnumber(self, inp):
        s = "".join([x for x in inp if x in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "/", ".", ",", "-"]]).replace(",",".")
        try:
            res = FR(s)
            return float(res) if int(res) != float(res) else int(res)
        except:
            return 1
