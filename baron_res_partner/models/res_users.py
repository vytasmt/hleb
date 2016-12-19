# -*- coding: utf-8 -*-

from openerp import models, osv


class res_users(models.Model):
    _inherit = 'res.users'

    def copy(self, cr, uid, id, default=None, context=None):

        partner = self.browse(cr, uid, id, context=context).partner_id
        pricelist = partner.property_product_pricelist.id or False
        res = super(res_users, self).copy(cr, uid, id, default, context=context)
        new_partner = self.browse(cr, uid, res, context=context).partner_id
        new_partner.property_product_pricelist = pricelist
        return res
