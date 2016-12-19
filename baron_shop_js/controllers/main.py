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

class baron_shop(website_sale):

    @http.route(['/shop/cart/update_baron'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_baron(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        order = request.website.sale_get_order(force_create=1)
        if not line_id:
            line_id = pool['sale.order.line'].search(cr,SUPERUSER_ID,[('order_id','=',order.id),('product_id','=',int(product_id))])
            if len(line_id) > 0:
                line_id = line_id[0]
        else:
            line_id = int(line_id)
        set_qty = float(set_qty) if set_qty else None
        add_qty = float(add_qty) if add_qty else None
        value = request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_id), line_id=line_id, add_qty=add_qty, set_qty=set_qty)
        if not display:
            return None
        value['cart_quantity'] = order.cart_quantity
        value['website_sale.total'] = request.website._render("website_sale.total", {
                'website_sale_order': request.website.sale_get_order()
            })
        return value

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        category_obj = pool['product.public.category']
        template_obj = pool['product.template']

        context.update(active_id=product.id)

        if category:
            category = category_obj.browse(cr, uid, int(category), context=context)

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int,v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        category_ids = category_obj.search(cr, uid, [], context=context)
        category_list = category_obj.name_get(cr, uid, category_ids, context=context)
        category_list = sorted(category_list, key=lambda category: category[1])

        pricelist = self.get_pricelist()

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

        if not context.get('pricelist'):
            context['pricelist'] = int(self.get_pricelist())
            product = template_obj.browse(cr, uid, int(product), context=context)

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
            'get_attribute_value_ids': self.get_attribute_value_ids
        }
        return request.website.render("website_sale.product", values)

    def checkout_form_save(self, checkout):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        order = request.website.sale_get_order(force_create=1, context=context)

        orm_partner = registry.get('res.partner')
        orm_user = registry.get('res.users')
        order_obj = request.registry.get('sale.order')

        partner_lang = request.lang if request.lang in [lang.code for lang in request.website.language_ids] else None

        billing_info = {}
        if partner_lang:
            billing_info['lang'] = partner_lang
        billing_info.update(self.checkout_parse('billing', checkout, True))

        # set partner_id
        partner_id = None
        if request.uid != request.website.user_id.id:
            partner_id = orm_user.browse(cr, SUPERUSER_ID, uid, context=context).partner_id.id
        elif order.partner_id:
            user_ids = request.registry['res.users'].search(cr, SUPERUSER_ID,
                [("partner_id", "=", order.partner_id.id)], context=dict(context or {}, active_test=False))
            if not user_ids or request.website.user_id.id not in user_ids:
                partner_id = order.partner_id.id
            else:
                # check for partners with given email in db if user is not registered
                email_matching_partners = request.env['res.partner'].sudo().search([('email', '=', checkout['email'])])
                if email_matching_partners:
                    partner_id = email_matching_partners[0].id

        # save partner informations
        if partner_id and request.website.partner_id.id != partner_id:
            orm_partner.write(cr, SUPERUSER_ID, [partner_id], billing_info, context=context)
        else:
            # create partner
            partner_id = orm_partner.create(cr, SUPERUSER_ID, billing_info, context=context)

        # create a new shipping partner
        if checkout.get('shipping_id') == -1:
            shipping_info = {}
            if partner_lang:
                shipping_info['lang'] = partner_lang
            shipping_info.update(self.checkout_parse('shipping', checkout, True))
            shipping_info['type'] = 'delivery'
            shipping_info['parent_id'] = partner_id
            checkout['shipping_id'] = orm_partner.create(cr, SUPERUSER_ID, shipping_info, context)

        order_info = {
            'partner_id': partner_id,
            'message_follower_ids': [(4, partner_id), (3, request.website.partner_id.id)],
            'partner_invoice_id': partner_id,
        }
        order_info.update(order_obj.onchange_partner_id(cr, SUPERUSER_ID, [], partner_id, context=context)['value'])
        address_change = order_obj.onchange_delivery_id(cr, SUPERUSER_ID, [], order.company_id.id, partner_id,
                                                        checkout.get('shipping_id'), None, context=context)['value']
        order_info.update(address_change)
        if address_change.get('fiscal_position'):
            fiscal_update = order_obj.onchange_fiscal_position(cr, SUPERUSER_ID, [], address_change['fiscal_position'],
                                                               [(4, l.id) for l in order.order_line], context=None)['value']
            order_info.update(fiscal_update)

        order_info.pop('user_id')
        order_info.update(partner_shipping_id=checkout.get('shipping_id') or partner_id)

        order_obj.write(cr, SUPERUSER_ID, [order.id], order_info, context=context)


class CountactusExt(contactus):

    def create_lead(self, request, values, kwargs):
        cr, context = request.cr, request.context
        lead_ids = request.env['crm.lead'].sudo().search([('email_from', '=', values['email_from'])])
        lead = None
        if lead_ids:
            lead = lead_ids[0]
            new_values = {}
            for field_name, field_value in values.items():
                if field_value and (getattr(lead, field_name) != field_value):
                    new_values[field_name] = field_value
                elif field_name not in ['user_id']:
                    new_values[field_name] = getattr(lead, field_name)
            old_desctiption = getattr(lead, 'description')
            if old_desctiption:
                new_values['description'] = '{0} \n{1}'.format(old_desctiption, values.get('description'))
            else:
                new_values['description'] = values.get('description')
            lead.sudo().write(new_values)
            return lead
        else:
            return super(CountactusExt, self).create_lead(request, values, kwargs)