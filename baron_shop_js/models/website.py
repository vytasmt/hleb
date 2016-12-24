# -*- coding: utf-8 -*-

from openerp import api
from openerp import models
from openerp.http import request
from fractions import Fraction as FR
from openerp import tools, SUPERUSER_ID


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
        res = self.subnumber(self.env['product.uom'].sudo().browse(uos_id).name)
        return res

    @api.model
    def subnumber(self, inp):
        s = "".join([x for x in inp if x in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "/", ".", ",", "-"]]).replace(",",".")
        try:
            res = FR(s)
            return float(res) if int(res) != float(res) else int(res)
        except:
            return 1
