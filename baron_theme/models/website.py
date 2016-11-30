# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.addons.website_sale.controllers.main import QueryURL
import random


class website(models.Model):
    _inherit = "website"

    def get_bestsellers(self):
        categs = self.env['bestseller.category'].search([])
        res = {}
        if categs:
            for categ in categs:
                if categ.public:
                    categ_products = categ.get_random_bestsellers()
                    if categ_products:
                        res[categ.name] = categ.get_random_bestsellers()
            return res
        else:
            return False
