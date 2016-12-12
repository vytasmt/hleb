# -*- coding: utf-8 -*-

import logging
from openerp import models, fields, api
from openerp import http

_logger = logging.getLogger(__name__)


class Property(models.Model):
    _name = 'property'

    name = fields.Char(string=u"Наименование", required=True)
    caption = fields.Char(string=u"Заголовок", required=True)
    description = fields.Html(string=u"Описание", default="")


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    property_id = fields.Many2one('property')


class ProductProduct(models.Model):
    _inherit = 'product.template'

    property_id = fields.Many2one('property')
