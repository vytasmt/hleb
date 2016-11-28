# -*- coding: utf-8 -*-

import logging
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    ingredients = fields.Char(string="Состав", default = 'Состав не определен')

    @api.model
    def pyth_met(self):
        return 'aaaa'
