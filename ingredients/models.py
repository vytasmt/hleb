# -*- coding: utf-8 -*-

import logging
from openerp import models, fields

_logger = logging.getLogger(__name__)


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    ingredients = fields.Char(string="Состав", default = 'Состав не определен')
