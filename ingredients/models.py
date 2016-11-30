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
            val = self.env['product.attribute.value'].browse(int(kwargs['value_id']))[0]
            prod = self.env['product.product'].browse(int(kwargs['prod_id']))[0]
            res['prod_ingred'] = prod.ingredients
            res['val_ingred'] = val.ingredients
        if kwargs.get('value_name', False):
            val = self.env['product.attribute.value'].search([('name', '=', kwargs['value_name'].strip())])[0]
            prod = self.env['product.product'].browse(int(kwargs['prod_id']))[0]
            if len(val):
                res['prod_ingred'] = prod.ingredients
                res['val_ingred'] = val.ingredients
        return res


class ProductProduct(models.Model):
    _inherit = 'product.template'

    ingredients = fields.Text(string="Состав", default = 'Состав не определен')
