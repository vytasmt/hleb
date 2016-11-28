# -*- coding: utf-8 -*-

import logging
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    ingredients = fields.Char(string="Состав", default = 'Состав не определен')

    @api.model
    def pyth_met(self, *args, **kwargs):
        res = {'ingredients': ''}
        if kwargs.get('value_id', False):
            val = self.env['product.attribute.value'].browse(int(kwargs.get('value_id', False)))
            res['ingredients'] = val.ingredients
        return res


class ProductProduct(models.Model):
    _inherit = 'product.template'

    ingredients = fields.Text(string="Состав", default = 'Состав не определен')
