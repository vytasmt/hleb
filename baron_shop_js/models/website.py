# -*- coding: utf-8 -*-

from openerp import api
from openerp import models
from openerp.http import request


class BaronWebsite(models.Model):
    _name = 'baron_website_tools'

    @api.model
    def product_have_quantity(self, product):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        for rec in product.attribute_line_ids:
            if all(rec.value_ids.mapped('pack_true')):
                return True
        return False
