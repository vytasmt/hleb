# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
import random

class sale_order(models.Model):
    _inherit = "sale.order"

    cart_uos_qty = fields.Float()

    @api.multi
    def _cart_accessories(self):
        for order in self:
            s = set(j.id for l in (order.website_order_line or [])
                    for j in (l.product_id.accessory_product_ids or []) if j.website_published == True)
            s -= set(l.product_id.id for l in order.order_line)
            product_ids = s
            return self.env['product.product'].browse(product_ids)
