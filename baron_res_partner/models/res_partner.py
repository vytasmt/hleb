# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from pprint import pprint

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _opportunity_meeting_phonecall_count(self, cr, uid, ids, field_name, arg, context=None):
        result = super(res_partner, self)._opportunity_meeting_phonecall_count(cr, uid, ids, field_name, arg, context)
        for partner_id, value_dict in result.items():
            partner_obj = self.browse(cr, uid, [partner_id], context)
            if partner_obj.is_company:
                childs_ids = self.pool.get('res.partner').search(cr, uid, \
                    [('id', 'child_of', partner_id),('id','!=', partner_id)], context=context)
                childs_obj = self.pool.get('res.partner').browse(cr, uid, childs_ids)
                for partner in childs_obj:
                    #result[partner_obj.id]['phonecall_count'] += len(partner.phonecall_ids)
                    result[partner_obj.id]['meeting_count'] += len(partner.meeting_ids)
        return result

    def _phonecall_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        for partner in self.browse(cr, uid, ids, context):
            operator = 'child_of' if partner.is_company else '='
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('id', operator, partner.id)], context=context)
            partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_ids)
            for obj in partner_obj:
                res[partner.id] += len(obj.phonecall_ids)
        return res


    def schedule_meeting(self, cr, uid, ids, context=None):
        partner_ids = list(ids)
        partner_ids.append(self.pool.get('res.users').browse(cr, uid, uid).partner_id.id)
        for partner_id in ids:
            partner_obj = self.browse(cr, uid, [partner_id], context)
            if partner_obj.is_company:
                childs_ids = self.pool.get('res.partner').search(cr, uid, \
                    [('id', 'child_of', partner_id),('id','!=', partner_id)], context=context)
                childs_obj = self.pool.get('res.partner').browse(cr, uid, childs_ids)
                ids += [p.id for p in childs_obj]
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'calendar', 'action_calendar_event', context)
        res['context'] = {
            'search_default_partner_ids': list(ids),
            'default_partner_ids': partner_ids,
        }
        return res

    def _sale_order_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        try:
            for partner in self.browse(cr, uid, ids, context):
                res[partner.id] = len(partner.sale_order_ids)
                if partner.is_company:
                    childs_ids = self.pool.get('res.partner').search(cr, uid, \
                        [('id', 'child_of', partner.id),('id','!=', partner.id)], context=context)
                    childs_obj = self.pool.get('res.partner').browse(cr, uid, childs_ids)
                    for contact in childs_obj:
                        res[partner.id] += len(contact.sale_order_ids)
        except:
            pass
        return res

    def _journal_item_count(self, cr, uid, ids, field_name, arg, context=None):
        result = dict(map(lambda x: (x, {'journal_item_count': 0, 'contracts_count': 0}), ids))
        MoveLine = self.pool('account.move.line')
        AnalyticAccount = self.pool('account.analytic.account')
        for partner_id in ids:
            partner_obj = self.browse(cr, uid, [partner_id], context)
            operator = 'child_of' if partner_obj.is_company else '='
            result[partner_id]['journal_item_count'] = MoveLine.search_count(
                cr, uid, [('partner_id', operator, partner_id)], context=context)
            result[partner_id]['contracts_count'] = AnalyticAccount.search_count(
                cr,uid, [('partner_id', operator, partner_id)], context=context)
        return result

    def _count_template(self, cr, uid, ids, field_name, arg, context=None, model_name=None):
        result = dict(map(lambda x: (x, 0), ids))
        model_obj = self.pool[model_name]
        for partner_id in ids:
            partner_obj = self.browse(cr, uid, [partner_id], context)
            operator = 'child_of' if partner_obj.is_company else '='
            result[partner_id] = model_obj.search_count(cr, uid, [('partner_id', operator, partner_id)])
        return result

    def _claim_count(self, cr, uid, ids, field_name, arg, context=None):
        return self._count_template(cr, uid, ids, field_name, arg, context, 'crm.claim')

    def _issue_count(self, cr, uid, ids, field_name, arg, context=None):
        return self._count_template(cr, uid, ids, field_name, arg, context, 'project.issue')

    def _task_count(self, cr, uid, ids, field_name, arg, context=None):
        return self._count_template(cr, uid, ids, field_name, arg, context, 'project.task')

    _columns = {
        'opportunity_count': fields.function(_opportunity_meeting_phonecall_count, string="Opportunity", type='integer', multi='opp_meet'),
        'meeting_count': fields.function(_opportunity_meeting_phonecall_count, string="# Meetings", type='integer', multi='opp_meet'),
        'phonecall_count': fields.function(_phonecall_count, string="Phonecalls", type="integer"),
        'sale_order_count': fields.function(_sale_order_count, string='# of Sales Order', type='integer'),
        'contracts_count': fields.function(_journal_item_count, string="Contracts", type='integer', multi="invoice_journal"),
        'journal_item_count': fields.function(_journal_item_count, string="Journal Items", type="integer", multi="invoice_journal"),
        'claim_count': fields.function(_claim_count, string='# Claims', type='integer'),
        'issue_count': fields.function(_issue_count, string='# Issues', type='integer'),
        'task_count': fields.function(_task_count, string='# Tasks', type='integer'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default['property_product_pricelist'] = self.browse(cr, uid, id, context=context).property_product_pricelist.id
        return super(res_partner, self).copy(cr, uid, id, default, context=context)
