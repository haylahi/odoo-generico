# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright :
#        (c) 2015 VMCloud Solution (http://vmcloudsolution.pe)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _


class pos_order(osv.osv):
    _name = 'pos.order'
    _inherit = 'pos.order'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        if context and context.get('show_recibo', True):
            for value in self.browse(cr, uid, ids, context=context):
                res.append([value.id, "%s" % (value.pos_reference)])
            return res
        result = super(pos_order, self).name_get(cr, uid, ids, context=context)
        return result

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=None):
        if context and context.get('show_recibo', True):
            domain = [('pos_reference', operator, name)]
            search_ids = super(pos_order, self).search(cr, uid, domain + args, context=context, limit=limit)
            res = self.name_get(cr, uid, search_ids, context=context)
            return res
        return super(pos_order, self).search(cr, uid, args=args, context=context, limit=limit)

    def _payment_fields(self, cr, uid, ui_paymentline, context=None):
        res = super(pos_order, self)._payment_fields(cr, uid, ui_paymentline, context=context)
        res['gift_voucher_serial'] = ui_paymentline.get('gift_voucher_serial', False) or ''
        res['gift_voucher_validate'] = ui_paymentline.get('gift_voucher_validate', False) or False
        res['gift_voucher_spent'] = ui_paymentline.get('gift_voucher_spent', 0)
        return res

    def add_payment(self, cr, uid, order_id, data, context=None):
        res = super(pos_order, self).add_payment(cr, uid, order_id, data, context=context)
        print 'evugor:add_payment000', data
        if data.get('gift_voucher_validate', False):
            print 'evugor:add_payment'
            gift_obj = self.pool.get('pos.gift.voucher')
            absl_obj = self.pool.get('account.bank.statement.line')
            gift_id = gift_obj.get_voucher_ids(cr, uid, data.get('gift_voucher_serial'), context=context)
            if not gift_id:
                raise osv.except_osv('Error', _('The gift voucher:') + data.get('gift_voucher_serial') + _(' is invalid or has already redeemed.'))
            absl_obj.write(cr, uid, res, {'gift_voucher_id': gift_id[0] if gift_id else 0})
            gift_voucher = gift_obj.browse(cr, uid, gift_id, context=context)
            print 'evugor:add_payment222', data.get('gift_voucher_spent')
            gift_obj.write(cr, uid, gift_id, {'total_available': gift_voucher.total_available-data.get('gift_voucher_spent'),
                                              'order_ids': [(4, order_id)],})
            gift_obj.set_redeemed(cr, uid, gift_id, context=context)
        return res