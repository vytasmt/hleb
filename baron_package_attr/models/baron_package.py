#coding: utf-8
from openerp import models, fields, api, _

class product_attribute_value(models.Model):
    _inherit = "product.attribute.value"

    @api.one
    @api.constrains('pack_true','pack_qty')
    def _check_qty(self):
        if self.pack_true and self.pack_qty <= 0:
            raise Warning(_('Quantity in pack can not be less than 0!'))

    pack_true = fields.Boolean(string='Package')
    pack_qty = fields.Float(string='Quantity in package')


class product_attribute_price(models.Model):
    _inherit = "product.attribute.price"

    pack_true = fields.Boolean(string='Package')
    pack_qty = fields.Float(string='Quantity in package')


class product_product(models.Model):
    _inherit = "product.product"

    # @api.one
    # def get_real_price(self):
    #     #to get 100% right ordering
    #     value_ids = self.env['product.attribute.value'].search([('id','in',self.attribute_value_ids.ids)],order='sequence')
    #     price = self.list_price
    #
    #     if 'uom' in self.env.context:
    #         uom = self.uos_id or self.uom_id
    #         price = self.env['product.uom']._compute_price(from_uom_id=
    #                 uom.id, price=self.list_price, to_uom_id=self.env.context['uom'])
    #
    #     for variant_id in value_ids:
    #         for price_id in variant_id.price_ids:
    #             if price_id.product_tmpl_id.id == self.product_tmpl_id.id:
    #                 price = (price+price_id.price_plus)*(1+price_id.price_multiple/100)
    #                 if price_id.pack_true:
    #                     price = price * price_id.pack_qty
    #
    #
    #     self.lst_price = price


    lst_price = fields.Float(compute='get_real_price')