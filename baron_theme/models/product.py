# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.osv import expression, osv
import re
import random
from itertools import chain


class ProductTemplate(models.Model):
    _inherit = "product.template"

    description = fields.Html(u'Описание', translate=False)


class product_product(models.Model):
    _inherit = "product.product"

    description = fields.Html(u'Описание', translate=False)

    @api.multi
    def get_attributes_values(self):
        for product in self:
            # variant = ", ".join([v.name for v in product.attribute_value_ids])
            variant = ''
            for v in product.attribute_value_ids:
                variant += v.name
                for price_id in v.price_ids:
                    if price_id.product_tmpl_id.id == product.product_tmpl_id.id:
                        if price_id.pack_true:
                            variant += ''  #' x ' + ('%.2f' % price_id.pack_qty) + u" шт."
                variant += ', '
            product.attributes_values_string = variant and "(%s)" % (
                variant[:-2]) or ''

    @api.one
    def get_default_pack_qty(self):
        value_ids = self.env['product.attribute.value'].search([('id','in',self.attribute_value_ids.ids)],order='sequence')
        for variant_id in value_ids:
            for price_id in variant_id.price_ids:
                if price_id.product_tmpl_id.id == self.product_tmpl_id.id:
                    if price_id.pack_true:
                        return price_id.pack_qty
        return 1

    @api.one
    def get_uom_qty(self):
        uom_qty = 1
        for v in self.attribute_value_ids:
            for price_id in v.price_ids:
                if price_id.product_tmpl_id.id == self.product_tmpl_id.id:
                    if price_id.pack_true:
                        uom_qty = uom_qty * price_id.pack_qty
        uom_qty = uom_qty / self.uos_coeff
        return uom_qty

    attributes_values_string = fields.Char(
        string='Attributes values',
        compute=get_attributes_values)

    bestseller_id = fields.Many2one('bestseller.category', u'Категория хита продаж')
    bestseller_ids = fields.Many2many('bestseller.category', 'categ_product_rel', 'categ_id' , 'prod_id', u'Категория хита продаж')

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            ids = []
            if operator in positive_operators:
                ids = self.search(cr, user, [('default_code','=',name)]+ args, limit=limit, context=context)
                if not ids:
                    ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
                if not ids:
                    ids = self.search(cr, user, [('attribute_value_ids.name','ilike',name)]+ args, limit=limit, context=context)
            if not ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set(self.search(cr, user, args + [('default_code', operator, name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(ids)) if limit else False
                    ids.update(self.search(cr, user, args + [('name', operator, name), ('id', 'not in', list(ids))], limit=limit2, context=context))
                ids = list(ids)
            elif not ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                ids = self.search(cr, user, args + ['&', ('default_code', operator, name), ('name', operator, name)], limit=limit, context=context)
            if not ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('default_code','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

class bestseller_category(models.Model):
    _name = 'bestseller.category'
    _description = u"Категории Хитов Продаж"

    @api.multi
    def get_random_bestsellers(self):
        products = self.products_ids
        s = set(product for product in products if product.website_published == True)
        product_ids = random.sample(s, min(len(s), 4))
        return product_ids

    name = fields.Char(u"Название")
    product_ids = fields.One2many('product.product','bestseller_id', u'Продукция')
    products_ids = fields.Many2many('product.product', 'categ_product_rel', 'prod_id' , 'categ_id', u'Продукция')
    sequence = fields.Integer(u'Порядок')
    public = fields.Boolean(u'Опубликовано')

    _order = "sequence, id"


class product_temolate(models.Model):
    _inherit = "product.template"

    @api.one
    def on_inverse_bestseller(self):
        if self.bestseller:
            self.bestseller_bread = \
                True if self.bestseller == 'bread' else False
            self.bestseller_meat = \
                True if self.bestseller == 'meat' else False
        else:
            self.bestseller_bread = False
            self.bestseller_meat = False

    bestseller_bread = fields.Boolean(u"Хит продаж (выпечка)", default=False)
    bestseller_meat = fields.Boolean(u"Хит продаж (мясо)", default=False)
    bestseller = fields.Selection([
        ('bread', u'Выпечка'),
        ('meat', u'Мясо')], u"Хит продаж", inverse="on_inverse_bestseller")


# class ProductPricelist(models.Model):
#     _inherit = "product.pricelist"
#
#     @api.model
#     def _price_rule_get_multi(self, pricelist, products_by_qty_by_partner):
#         product_uom_obj = self.env['product.uom']
#         res = super(ProductPricelist, self)._price_rule_get_multi(pricelist, products_by_qty_by_partner)
#         products = map(lambda x: x[0], products_by_qty_by_partner)
#         is_product_template = products[0]._name == "product.template"
#         if is_product_template:
#             for rec in res:
#                 product = self.env['product.template'].sudo().browse(rec)
#                 res[rec] = (product_uom_obj._compute_price(product.uom_id.id, res[rec][0], product.uos_id.id),res[rec][1])
#         else:
#             for rec in res:
#                 product = self.env['product.product'].sudo().browse(rec)
#                 res[rec] = (product_uom_obj._compute_price(product.uom_id.id, res[rec][0], product.uos_id.id),res[rec][1])
#         return res
#
