#coding: utf-8
from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

class product_attribute_value(osv.osv):
    _inherit = "product.attribute.value"

    def get_value_from_price_pack_true(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, 0)
        if not context.get('active_id'):
            return result

        for obj in self.browse(cr, uid, ids, context=context):
            for price_id in obj.price_ids:
                if price_id.product_tmpl_id.id == context.get('active_id'):
                    result[obj.id] = price_id.pack_true
                    break
        return result

    def get_value_from_price_multiple_pack_qty(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, 0)
        if not context.get('active_id'):
            return result

        for obj in self.browse(cr, uid, ids, context=context):
            for price_id in obj.price_ids:
                if price_id.product_tmpl_id.id == context.get('active_id'):
                    result[obj.id] = price_id.pack_qty
                    break
        return result

    def set_price_in_pack_true(self, cr, uid, id, name, value, args, context=None):
        if context is None:
            context = {}
        if 'active_id' not in context:
            return None
        p_obj = self.pool['product.attribute.price']
        p_ids = p_obj.search(cr, uid, [('value_id', '=', id), ('product_tmpl_id', '=', context['active_id'])], context=context)
        if p_ids:
            p_obj.write(cr, uid, p_ids, {'pack_true': value}, context=context)
        else:
            p_obj.create(cr, uid, {
                    'product_tmpl_id': context['active_id'],
                    'value_id': id,
                    'pack_true': value,
                }, context=context)

    def set_price_in_line_pack_qty(self, cr, uid, id, name, value, args, context=None):
        if context is None:
            context = {}
        if 'active_id' not in context:
            return None
        p_obj = self.pool['product.attribute.price']
        p_ids = p_obj.search(cr, uid, [('value_id', '=', id), ('product_tmpl_id', '=', context['active_id'])], context=context)
        if p_ids:
            p_obj.write(cr, uid, p_ids, {'pack_qty': value}, context=context)
        else:
            p_obj.create(cr, uid, {
                    'product_tmpl_id': context['active_id'],
                    'value_id': id,
                    'pack_qty': value,
                }, context=context)
    
    _columns = {
        'pack_true': fields.function(get_value_from_price_pack_true, type='boolean', string='Package',
            fnct_inv=set_price_in_pack_true,),
        'pack_qty': fields.function(get_value_from_price_multiple_pack_qty, type='float', string='Quantity in package',
            fnct_inv=set_price_in_line_pack_qty,
            digits_compute=dp.get_precision('Product Price'),)
    }
