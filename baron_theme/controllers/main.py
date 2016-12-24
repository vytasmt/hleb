# -*- coding: utf-8 -*-

import openerp

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.web.controllers.main import Home
from openerp.addons.website.models.website import slug
from openerp.addons.website.controllers.main import Website
from openerp.addons.website_crm.controllers.main import contactus
from openerp.addons.website_sale.controllers.main import QueryURL
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import table_compute

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


def drop_suggested_products(products, line_len=4):
    suggested_products = []
    if products:
        if len(products) >= line_len:
            for a in range(0, len(products), line_len):
                suggested_products.append(products[a:a + line_len])
        else:
            suggested_products.append([])
            for product in products:
                suggested_products[0].append(product)
    return suggested_products


def get_pricelist():
    cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
    sale_order = context.get('sale_order')
    if sale_order:
        pricelist = sale_order.pricelist_id
    else:
        partner = pool['res.users'].browse(
            cr, SUPERUSER_ID, uid, context=context).partner_id
        pricelist = partner.property_product_pricelist
    return pricelist



class baron_website(Website):

    def get_pricelist(self):
        return get_pricelist()

    def get_attribute_value_ids(self, product, order=False):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        currency_obj = pool['res.currency']
        attribute_value_ids = []
        visible_attrs = set(l.attribute_id.id
                            for l in product.attribute_line_ids
                            if len(l.value_ids) > 1)
        if request.website.pricelist_id.id != context['pricelist']:
            website_currency_id = request.website.currency_id.id
            currency_id = self.get_pricelist().currency_id.id
            for p in product.product_variant_ids:
                price = currency_obj.compute(
                    cr, uid, website_currency_id, currency_id, p.lst_price)
                attribute_value_ids.append(
                    [p.id, [v.id for v in p.attribute_value_ids if v.attribute_id.id in visible_attrs], p.price, price])
        else:
            attribute_value_ids = [[p.id, [v.id for v in p.attribute_value_ids if v.attribute_id.id in visible_attrs], p.price, p.lst_price]
                                   for p in product.product_variant_ids]
        if order:
            attribute_value_ids = sorted(attribute_value_ids)
        return attribute_value_ids

    def get_product_template_with_context(self, product=None):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        product_tmpl = False
        if product:
            product_tmpl = pool.get('product.template').browse(cr, uid, [product.product_tmpl_id.id], context)
        return product_tmpl

    def round_value(self, value):
        res = 0
        if value:
            res = round(value, 2)
        return res

    def get_default_product_for_price(self, product):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        products = product.product_variant_ids.ids
        default_product = False
        if product.attribute_line_ids and product.attribute_line_ids[0].value_ids:
            attrs_vals = []
            for attr in product.attribute_line_ids:
                for val in attr.value_ids:
                    res_ids = pool.get('product.attribute.value').search(
                        cr, uid, [('id', 'in', val.ids)], order="sequence")
                    res = pool.get('product.attribute.value').browse(
                        cr, uid, res_ids)
                    attrs_vals.append(res[0])
            for product in product.product_variant_ids:
                if attrs_vals == product.attribute_value_ids.ids:
                    default_product = product
            if not default_product:
                value_ids = product.attribute_line_ids[0].value_ids.ids
                res_ids = pool.get('product.attribute.value').search(
                    cr, uid, [('id', 'in', value_ids)], order="sequence")
                res = pool.get('product.attribute.value').browse(
                    cr, uid, res_ids)
                for prod in res[0].product_ids:
                    if prod.id in products:
                        default_product = prod
                        break
        else:
            default_product = pool.get('product.product').browse(
                cr, uid, [sorted(products)[0]], context)
        return default_product

    def get_website_price(self, product, prices_data):
        if prices_data and product:
            for line in prices_data:
                if line[0] == product.id:
                    return line[2]
        return 0


    def format_lang(self, value):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        res = 1
        if value:
            digits = 2
            lang = 'ru_RU'
            lang_objs = pool.get('res.lang').search(cr,uid,[('code', '=', lang)])
            if not lang_objs:
                lang_objs = pool.get('res.lang').search(cr,uid,[('code', '=', 'en_EN')])
            lang_obj = pool.get('res.lang').browse(cr,uid,[lang_objs[0]])

            res = lang_obj.format('%.' + str(digits) + 'f', value, grouping=True)
        return res

    @http.route('/page/<page:page>', type='http', auth="public", website=True)
    def page(self, page, **opt):
        keep = QueryURL('/page')
        context = request.context

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(
                cr, uid, context['pricelist'], context)

        values = {
            'path': page,
            'keep': keep,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'pricelist': pricelist,
            'default_product': self.get_default_product_for_price,
            'format_lang': self.format_lang,
            'round': self.round_value,
            'get_website_price': self.get_website_price,
            'get_product_template_with_context': self.get_product_template_with_context,
        }
        # /page/website.XXX --> /page/XXX
        if page.startswith('website.'):
            return request.redirect('/page/' + page[8:], code=301)
        elif '.' not in page:
            page = 'website.%s' % page

        try:
            request.website.get_template(page)
        except ValueError, e:
            # page not found
            if request.website.is_publisher():
                page = 'website.page_404'
            else:
                return request.registry['ir.http']._handle_exception(e, 404)

        return request.render(page, values)


class baron_website_sale(website_sale):

    def get_attribute_value_ids(self, product, order=False):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        if not context.get('pricelist'):
            context['pricelist'] = int(self.get_pricelist())

        currency_obj = pool['res.currency']
        attribute_value_ids = []
        visible_attrs = set(l.attribute_id.id
                                for l in product.attribute_line_ids
                                if len(l.value_ids) > 0)
        if request.website.pricelist_id.id != context['pricelist']:
            website_currency_id = request.website.currency_id.id
            currency_id = self.get_pricelist().currency_id.id
            for p in product.product_variant_ids:
                price = currency_obj.compute(cr, uid, website_currency_id, currency_id, p.lst_price)
                attribute_value_ids.append([p.id, [v.id for v in p.attribute_value_ids if v.attribute_id.id in visible_attrs], p.price, price])
        else:
            attribute_value_ids = [[p.id, [v.id for v in p.attribute_value_ids if v.attribute_id.id in visible_attrs], p.price, p.lst_price]
                for p in product.product_variant_ids]

        if order:
            attribute_value_ids = sorted(attribute_value_ids)
        return attribute_value_ids

    def get_default_product_for_price(self, product):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        products = product.product_variant_ids.ids
        default_product = False
        if product.attribute_line_ids and product.attribute_line_ids[0].value_ids:
            attrs_vals = []
            for attr in product.attribute_line_ids:
                for val in attr.value_ids:
                    res_ids = pool.get('product.attribute.value').search(
                        cr, uid, [('id', 'in', val.ids)], order="sequence")
                    res = pool.get('product.attribute.value').browse(
                        cr, uid, res_ids)
                    attrs_vals.append(res[0])
            for product in product.product_variant_ids:
                if attrs_vals == product.attribute_value_ids.ids:
                    default_product = product
            if not default_product:
                value_ids = product.attribute_line_ids[0].value_ids.ids
                res_ids = pool.get('product.attribute.value').search(
                    cr, uid, [('id', 'in', value_ids)], order="sequence")
                res = pool.get('product.attribute.value').browse(
                    cr, uid, res_ids)
                for prod in res[0].product_ids:
                    if prod.id in products:
                        default_product = prod
                        break
        else:
            default_product = pool.get('product.product').browse(
                cr, uid, [sorted(products)[0]], context)
        return default_product

    def get_website_price(self, product, prices_data):
        if prices_data and product:
            for line in prices_data:
                if line[0] == product.id:
                    return line[2]
        return 0

    def format_lang(self, value):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        res = 1
        if value:
            digits = 2
            lang = 'ru_RU'
            lang_objs = pool.get('res.lang').search(cr,uid,[('code', '=', lang)])
            if not lang_objs:
                lang_objs = pool.get('res.lang').search(cr,uid,[('code', '=', 'en_EN')])
            lang_obj = pool.get('res.lang').browse(cr,uid,[lang_objs[0]])

            res = lang_obj.format('%.' + str(digits) + 'f', value, grouping=True)
        return res

    def round_value(self, value):
        res = 0
        if value:
            res = round(value, 2)
        return res

    def get_minimal_order_price(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        groups = pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context).group_baron
        if groups:
            minimal_order_price = min(groups, key=lambda g: g.minimal_order_price).minimal_order_price
        else:
            minimal_order_price = 0
        return minimal_order_price

    def checkout_parse(self, address_type, data, remove_prefix=False):
        values = super(baron_website_sale, self).checkout_parse(address_type, data, remove_prefix)

        if isinstance(data, dict) and data.get('delivery_period_id'):
            values['delivery_period_id'] = int(data['delivery_period_id'])
        if isinstance(data, dict) and data.get('comment'):
            values['comment'] = data['comment']
        return values

    def checkout_values(self, data=None):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        values = super(baron_website_sale, self).checkout_values(data)
        delivery_periods = False
        groups = pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context).group_baron

        for group in groups:
            if not delivery_periods:
                delivery_periods = group.delivery_period_ids
            else:
                delivery_periods += group.delivery_period_ids
        values['delivery_periods'] = delivery_periods
        return values

    def checkout_form_save(self, checkout):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        super(baron_website_sale, self).checkout_form_save(checkout)
        order = request.website.sale_get_order(force_create=1, context=context)
        order_obj = request.registry.get('sale.order')
        period_obj = registry.get("delivery.period")
        note = order_obj.browse(cr, SUPERUSER_ID, order.id, context=context).note
        if not note:
            note = ""
        changed = False
        if checkout.get("comment"):
            note += checkout['comment']
            changed = True
        if checkout.get("delivery_period_id"):
            if changed:
                note += "\n"
            note += u"Период доставки: " + \
                period_obj.browse(cr, SUPERUSER_ID, checkout["delivery_period_id"], context).name + u". "
            changed = True
        if changed:
            order_info = {
                'note': note,
            }
            order_obj.write(cr, SUPERUSER_ID, [order.id], order_info, context=context)

    def get_product_template_with_context(self, product=None):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        product_tmpl = False
        if not context.get('pricelist'):
            context['pricelist'] = int(self.get_pricelist())
        if product:
            product_tmpl = pool.get('product.template').browse(cr, uid, [product.product_tmpl_id.id], context)
        return product_tmpl

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        order = request.website.sale_get_order()
        if order:
            from_currency = pool.get('product.price.type')._get_field_currency(
                cr, uid, 'list_price', context)
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: pool['res.currency']._compute(
                cr, uid, from_currency, to_currency, price, context=context)
        else:
            compute_currency = lambda price: price

        keep = QueryURL('/shop')

        values = {
            'order': order,
            'keep': keep,
            'compute_currency': compute_currency,
            'suggested_products': [],
            'drop_suggested_products': drop_suggested_products,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'pricelist': self.get_pricelist(),
            'default_product': self.get_default_product_for_price,
            'format_lang': self.format_lang,
            'round': self.round_value,
            'minimal_order_price': self.get_minimal_order_price(),
            'get_product_template_with_context': self.get_product_template_with_context,
            'get_website_price': self.get_website_price,
        }
        if order:
            _order = order
            if not context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
                values['suggested_products'] = _order._cart_accessories()

        return request.website.render("website_sale.cart", values)

    @http.route(['/shop',
                 '/shop/page/<int:page>',
                 '/shop/category/<model("product.public.category"):category>',
                 '/shop/category/<model("product.public.category"):category>/page/<int:page>'
                 ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        domain = request.website.sale_product_domain()
        if search:
            for srch in search.split(" "):
                domain += ['|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                           ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]
        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        keep = QueryURL('/shop', category=category and int(category),
                        search=search, attrib=attrib_list)

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(
                cr, uid, context['pricelist'], context)

        product_obj = pool.get('product.template')

        url = "/shop"
        product_count = product_obj.search_count(
            cr, uid, domain, context=context)
        if search:
            post["search"] = search
        if category:
            category = pool['product.public.category'].browse(
                cr, uid, int(category), context=context)
            url = "/shop/category/%s" % slug(category)
        pager = request.website.pager(
            url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
        product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager[
                                         'offset'], order='website_published desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        category_obj = pool['product.public.category']
        category_ids = category_obj.search(
            cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, [], context=context)
        attributes = attributes_obj.browse(
            cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(
            cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(
            cr, uid, from_currency, to_currency, price, context=context)

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'bins': table_compute().process(products),
            'rows': PPR,
            'styles': styles,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib', i) for i in attribs]),
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'default_product': self.get_default_product_for_price,
            'format_lang': self.format_lang,
            'round': self.round_value,
            'get_website_price': self.get_website_price,
        }
        return request.website.render("website_sale.products", values)

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        category_obj = pool['product.public.category']
        template_obj = pool['product.template']

        context.update(active_id=product.id)

        if category:
            category = category_obj.browse(
                cr, uid, int(category), context=context)

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        keep = QueryURL('/shop', category=category and category.id,
                        search=search, attrib=attrib_list)

        category_ids = category_obj.search(cr, uid, [], context=context)
        category_list = category_obj.name_get(
            cr, uid, category_ids, context=context)
        category_list = sorted(category_list, key=lambda category: category[1])

        pricelist = self.get_pricelist()

        from_currency = pool.get('product.price.type')._get_field_currency(
            cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(
            cr, uid, from_currency, to_currency, price, context=context)

        if not context.get('pricelist'):
            context['pricelist'] = int(self.get_pricelist())
            product = template_obj.browse(
                cr, uid, int(product), context=context)

        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'category_list': category_list,
            'main_object': product,
            'product': product,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'default_product': self.get_default_product_for_price,
            'format_lang': self.format_lang,
            'round': self.round_value,
            'get_website_price': self.get_website_price,
        }
        return request.website.render("website_sale.product", values)


    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        value = super(baron_website_sale, self).cart_update_json(product_id, line_id, add_qty, set_qty, display)
        value['baron_theme.minimal_total_alert'] = request.website._render(
            "baron_theme.minimal_total_alert", {
                'website_sale_order': request.website.sale_get_order(),
                'minimal_order_price': self.get_minimal_order_price(),
                'format_lang': self.format_lang,
            }
        )
        return value

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        product = registry.get('product.product').browse(cr, uid, int(product_id))
        add_uos_qty = float(add_qty)
        set_uos_qty = float(set_qty)
        # for v in product.attribute_value_ids:
        #     for price_id in v.price_ids:
        #         if price_id.product_tmpl_id.id == product.product_tmpl_id.id:
        #             if price_id.pack_true:
        #                 add_uos_qty = add_uos_qty * price_id.pack_qty
        #                 set_uos_qty = set_uos_qty * price_id.pack_qty
        res = super(baron_website_sale, self).cart_update(product_id, add_uos_qty, set_uos_qty, **kw)
        back_to_product_href = "/shop/product/" + slug(product.product_tmpl_id)
        return request.redirect(back_to_product_href)

    @http.route('/shop/properties', type='json', auth="public", website=True)
    def pyth_met(self, *args, **kwargs):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        res = {'properties': ''}
        if kwargs.get('value_id', False):
            val = registry.get('product.attribute.value').browse(cr, uid, int(kwargs['value_id']))[0]
            prod = registry.get('product.product').browse(cr, uid, int(kwargs['prod_id']))[0]
            if prod.property_id:
                res['prod_property'] = prod.property_id.description
                res['prod_property_caption'] = prod.property_id.caption
            else:
                res['prod_property'] = ''
                res['prod_property_caption'] = ''
            if val.property_id:
                res['val_property'] = val.property_id.description
                res['val_property_caption'] = val.property_id.caption
            else:
                res['val_property'] = ''
                res['val_property_caption'] = ''
        if kwargs.get('value_name', False):
            val_id = registry.get('product.attribute.value').search(cr, uid, [('name', '=', kwargs['value_name'].strip())])[0]
            val = registry.get('product.attribute.value').browse(cr, uid, val_id)
            prod = registry.get('product.product').browse(cr, uid, int(kwargs['prod_id']))[0]
            if len(val):
                if prod.property_id:
                    res['prod_property'] = prod.property_id.description
                    res['prod_property_caption'] = prod.property_id.caption
                else:
                    res['prod_property'] = ''
                    res['prod_property_caption'] = ''
                if val.property_id:
                    res['val_property'] = val.property_id.description
                    res['val_property_caption'] = val.property_id.caption
                else:
                    res['val_property'] = ''
                    res['val_property_caption'] = ''
        return res