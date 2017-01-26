# -*- coding: utf-8 -*-

import logging
from openerp import models, fields, api
from openerp import http

_logger = logging.getLogger(__name__)


class Property(models.Model):
    _name = 'hlebproperty'

    name = fields.Char(string=u"Наименование", required=True)
    caption = fields.Char(string=u"Заголовок", required=True)
    description = fields.Html(string=u"Описание", default="")


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    hlebproperty_id = fields.Many2one('hlebproperty', string=u"Свойство")


class ProductProduct(models.Model):
    _inherit = 'product.template'

    hlebproperty_id = fields.Many2one('hlebproperty', string=u"Свойство")
