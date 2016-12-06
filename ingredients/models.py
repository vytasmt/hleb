# -*- coding: utf-8 -*-

import logging
from openerp import models, fields, api
from openerp import http

_logger = logging.getLogger(__name__)


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    ingredients = fields.Char(string=u"Состав", default=u'Состав не определен')


class ProductProduct(models.Model):
    _inherit = 'product.template'

    ingredients = fields.Text(string=u"Состав", default=u'Состав не определен')
