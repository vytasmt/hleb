# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.osv import osv, orm, fields as ofields


class SaleOrder(models.Model):
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


class SaleOrderOld(osv.Model):
    _inherit = "sale.order"

    def _cart_qty(self, cr, uid, ids, field_name, arg, context=None):
        res = dict()
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = float(sum(l.product_uom_qty for l in (order.website_order_line or [])))
        return res

    _columns = {
        'cart_quantity': ofields.function(_cart_qty, type='float', string='Cart Quantity'),
    }


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    mod = fields.Boolean(default=False)
    old_pack = fields.Float(default=0)

