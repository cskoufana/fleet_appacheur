# -*- encoding="utf-8" -*-
#__author__ = 'yenke'

from openerp.tools.translate import _
from openerp.osv import fields, orm, osv
import time


class guce_fleet_consumption_card_recharge(osv.osv_memory):
    _name = 'guce.fleet.consumption.card.recharge'
    _columns = {
        'order_ref': fields.char("Recharge Order Reference", size=64, required=True),
        'value': fields.float("Value", help="Value for the recharge"),
        'description': fields.text("Description"),
    }

    def action_validate(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)
        recharge_pool = self.pool.get('fleet.consumption.card.log.recharges')
        recharge_pool.create(cr, uid, {
            'value': wizard.value,
            'consumption_card_id': context.get('active_ids', [])[0],
            'description': wizard.description,
            'order_ref': wizard.order_ref,
        }, context=context)
        return {'type': 'ir.actions.act_window_close'}


guce_fleet_consumption_card_recharge()


class guce_fleet_need_answer(osv.osv_memory):
    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        if not vehicle_id:
            return {}
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        driver = vehicle.driver_id.id
        return {
            'value': {
                'driver_id': driver,
            }
        }

    _name = 'guce.fleet.need.answer'
    _columns = {
        'decision': fields.selection([('yes', 'Yes'), ('no', 'No')], 'Decision', required=True),
        'notes': fields.text("Notes"),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),
        'move_order_ref': fields.char("Order Reference", size=64),
        'driver_id': fields.many2one("res.partner", "Driver"),
        'object': fields.char("Object", size=64),
        'move_type_id': fields.many2one("fleet.move.type", "Move Type"),
        'departure_date': fields.datetime("Departure Date"),
        'departure_place': fields.char("Departure Place", size=64),
        'arrival_place': fields.char("Destination Place", size=64),
        'description': fields.text("Description"),
        'other_passenger_ids': fields.many2many("fleet.passenger", "move_passenger_rel", "move_id", "passenger_id",
                                                "Other Passengers"),
        'passenger_ids': fields.many2many("res.partner", "move_partner_rel", "move_id", "partner_id", "Passengers",
                                          domain="[('employee','=',True)]"),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(guce_fleet_need_answer, self).default_get(cr, uid, fields, context=context)
        active_id = context.get('active_id', False)
        move_need = self.pool.get('fleet.vehicle.log.moves.needs').browse(cr, uid, active_id, context=context)
        if move_need:
            res['arrival_place'] = move_need.destination,
            res['departure_date'] = move_need.departure_date,
            res['description'] = move_need.note or '',
        return res

    def action_validate(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)
        value = {
            'vehicle_id': wizard.vehicle_id.id,
            'move_order_ref': wizard.move_order_ref,
            'driver_id': wizard.driver_id.id,
            'object': wizard.object,
            'move_type_id': wizard.move_type_id.id,
            'departure_date': wizard.departure_date,
            'departure_place': wizard.departure_place,
            'arrival_place': wizard.arrival_place,
            'notes': wizard.description or '',
        }

        self.pool.get('fleet.vehicle.log.moves.needs').write(cr, uid, context.get('active_ids', [])[0], {
            'answer_decision': wizard.decision,
            'answer_notes': wizard.notes,
            'answer_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'answerer': uid,
            'state': 'answered',
            'move_id': self.pool.get('fleet.vehicle.log.moves').create(cr, uid, value, context=context) if wizard.decision == 'yes' else None
        }, context=context)
        return {'type': 'ir.actions.act_window_close'}


guce_fleet_need_answer()


class fleet_vehicle_log_moves_confirm(osv.osv_memory):
    def _check_odometer_not_null(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.odometer and record.odometer <= 0:
                return False
        return True

    _name = 'fleet.vehicle.log.moves.confirm'
    _columns = {
        'departure_date': fields.datetime("Effective Departure Date"),
        'odometer': fields.float('Odometer Value',
                                 help='Odometer measure of the vehicle at the moment of this log'),
        'odometer_unit': fields.char("Unit", readonly=True),
    }
    _defaults = {
        'departure_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    _constraints = [
        (_check_odometer_not_null,
         _('\nOdometer Value can''t be null.'), [_('Odometer Value')]),
    ]

    def default_get(self, cr, uid, fields, context=None):
        res = super(fleet_vehicle_log_moves_confirm, self).default_get(cr, uid, fields, context=context)
        active_id = context.get('active_id', False)
        move = self.pool.get('fleet.vehicle.log.moves').browse(cr, uid, active_id, context=context)
        if move:
            res['odometer_unit'] = move.odometer_unit,
        return res

    def action_validate(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)
        move = self.pool.get('fleet.vehicle.log.moves').browse(cr, uid, context.get('active_id', False),
                                                               context=context)
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, {
            'date': fields.date.context_today(self, cr, uid, context=context),
            'vehicle_id': move.vehicle_id.id,
            'value': wizard.odometer,
        }, context=context)
        self.pool.get('fleet.vehicle.log.moves').write(cr, uid, context.get('active_id', False), {
            'departure_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'odometer_id': odometer_id,
            'state': 'confirmed',
        }, context=context)
        return {'type': 'ir.actions.act_window_close'}


fleet_vehicle_log_moves_confirm()
