# -*- coding: utf-8 -*-
#__author__ = 'yenke'

from osv import fields, osv
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
import time


class fleet_rim(osv.osv):
    _name = "fleet.rim"
    _description = 'Rim of vehicle'
    _columns = {
        'name': fields.char("Name", size=64, required=True),
        'description': fields.text("Description"),
    }
    _sql_constraints = [('fleet_rim_name_unique', 'unique(name)', 'Rim name already exists')]


fleet_rim()


#class res_partner(osv.osv):
#    _name = "res.partner"
#    _inherit = 'res.partner'
#    _columns = {
#        'driver': fields.boolean('Is Driver', help="Check is partner is driver"),
#    }
#res_partner()


class fleet_consumption_card_type(osv.osv):
    _name = "fleet.consumption.card.type"
    _description = "Type of consumption card"
    _columns = {
        'name': fields.char("Name", size=64, required=True),
        'description': fields.text("Description"),
    }
    _sql_constraints = [
        ('fleet_consumption_card_type_name_unique', 'unique(name)', 'Consumption card type name already exists')]


fleet_consumption_card_type()


class fleet_consumption_card(osv.osv):
    def return_action_to_open(self, cr, uid, ids, context=None):
        """ This opens the xml view specified in xml_id for the current consumption card """
        if context is None:
            context = {}
        if context.get('xml_id'):
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'fleet_guce', context['xml_id'],
                                                                    context=context)
            res['context'] = context
            res['domain'] = [('consumption_card_id', '=', ids[0])]
            return res
        return False

    _name = "fleet.consumption.card"
    _description = "Consumption card for a vehicle"
    _columns = {
        'name': fields.char("Card Number", size=64, required=True),
        'security_code': fields.char("Security Code", size=64),
        'value': fields.float("Amount", help="Amount of a card"),
        'critical_balance': fields.float("Critical Balance",
                                         help="The critical balance is used to notify for new recharge of a card"),
        'balance': fields.float("Current balance", help="The current balance of a card"),
        'vendor_id': fields.many2one('res.partner', 'Supplier', domain="[('supplier','=',True)]"),
        'card_type_id': fields.many2one("fleet.consumption.card.type", "Card Type"),
        'active': fields.boolean("Is active", help='Check if card is activated'),
        'recharge_ids': fields.one2many("fleet.consumption.card.log.recharges", "consumption_card_id", "Recharges"),
        'log_fuel': fields.one2many("fleet.vehicle.log.fuel", 'consumption_card_id', 'Fuel Logs'),

    }
    _defaults = {
        'active': True,
    }

    def view_consumptions(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'fleet', 'fleet_vehicle_log_fuel_act')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        fuel_ids = self.pool.get('fleet.vehicle.log.fuel').search(cr, uid, [('consumption_card_id', 'in', ids)],
                                                                  context=context)
        result['domain'] = "[('id','in',[" + ','.join(map(str, fuel_ids)) + "])]"
        return result


fleet_consumption_card()


class fleet_consumption_card_log_recharges(osv.osv):
    _name = 'fleet.consumption.card.log.recharges'
    _description = 'Recharges for cards'
    _rec_name = 'order_ref'
    _order = 'id desc'
    _columns = {
        'loader_id': fields.many2one('res.users', 'Loader', ),
        'value': fields.float("Value", help="Value of a recharge"),
        'old_value': fields.float("Old Value", help="Value of the card before the recharge"),
        'consumption_card_id': fields.many2one("fleet.consumption.card", "Consumption Card"),
        'recharge_date': fields.datetime("Recharge Date", help="Date when the recharge has been realized"),
        'description': fields.text("Description"),
        'order_ref': fields.char("Recharge Order Reference", size=64, required=True),
        'attachment_ids': fields.many2many("ir.attachment", "fleet_consumption_card_recharge_attachment_rel",
                                           "attachment_id", "recharge_id", "Attachments"),
    }
    _defaults = {
        'recharge_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'loader_id': lambda obj, cr, uid, context: uid,
    }

    def create(self, cr, uid, value, context=None):
        if 'consumption_card_id' in value:
            consumption_card_pool = self.pool.get('fleet.consumption.card')
            consumption_card_obj = consumption_card_pool.browse(cr, uid, value['consumption_card_id'], context=context)
            if 'old_value' not in value:
                value['old_value'] = consumption_card_obj.balance
            consumption_card_pool.write(cr, uid, consumption_card_obj.id,
                                        {'balance': consumption_card_obj.balance + value['value']})
            return super(fleet_consumption_card_log_recharges, self).create(cr, uid, value, context=context)

    def on_change_consumption_card(self, cr, uid, ids, consumption_card_id, context=None):
        if not consumption_card_id:
            return {}
        consumption_card = self.pool.get('fleet.consumption.card').browse(cr, uid, consumption_card_id, context=context)
        return {
            'value': {
                'old_value': consumption_card.balance,
            }
        }

    def write(self, cr, uid, ids, value, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if 'consumption_card_id' in value and record.consumption_card_id.id == value['consumption_card_id']:
                value['old_value'] = record.old_value
            consumption_card = self.pool.get('fleet.consumption.card').browse(cr, uid, record.consumption_card_id.id,
                                                                              context=context)
            self.pool.get('fleet.consumption.card').write(cr, uid, consumption_card.id, {
                'balance': consumption_card.balance - record.value + value['value']})
        recharge_id = super(fleet_consumption_card_log_recharges, self).write(cr, uid, ids, value, context=context)
        return True


fleet_consumption_card_log_recharges()


class fleet_vehicle(osv.osv):
    def return_action_to_open_view(self, cr, uid, ids, context=None):
        """ This opens the xml view specified in xml_id for the current vehicle """
        if context is None:
            context = {}
        if context.get('xml_id'):
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'fleet_guce', context['xml_id'],
                                                                    context=context)
            res['context'] = context
            res['context'].update({'default_vehicle_id': ids[0]})
            res['domain'] = [('vehicle_id', '=', ids[0])]
            return res
        return False

    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'
    _description = 'Information on a vehicle'
    _columns = {
        'tire_size': fields.float("Tire Size"),
        'rim_id': fields.many2one("fleet.rim", "Rim Type"),
        'tank_capacity': fields.float("Tank Capacity"),
        'consumption': fields.float("Consumption per 100 km"),
        'sale_date': fields.date("Sale Date", help="Date when the vehicle has been sold"),
        'sale_amount': fields.float("Sale Amount", help="Sale Amount for the vehicle"),
        'consumption_card_id': fields.many2one('fleet.consumption.card', 'Consumption Card'),
        'consumption_card_ids': fields.many2many("fleet.consumption.card", "vehicle_consumption_card_rel", 'vehicle_id',
                                                 'consumption_card_id', "Consumption cards"),
        'log_moves': fields.one2many('fleet.vehicle.log.moves', 'vehicle_id', 'Moves Logs'),
        'log_incidents': fields.one2many('fleet.vehicle.log.incidents', 'vehicle_id', 'Incidents Logs'),
        'attachment_ids': fields.many2many("ir.attachment", "fleet_vehicle_attachment_rel", "attachment_id",
                                           "vehicle_id", "Attachments"),
        'log_costs': fields.one2many('fleet.vehicle.cost', 'vehicle_id', 'Costs Log'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'log_moves': [],
            'log_incidents': [],
            'log_costs': [],
        })
        return super(fleet_vehicle, self).copy(cr, uid, id, default, context=context)


fleet_vehicle()


class fleet_vehicle_log_fuel(osv.Model):
    def on_change_value(self, cr, uid, ids, liter, price_per_liter, amount, context=None):
        liter = float(liter)
        price_per_liter = float(price_per_liter)
        amount = float(amount)
        if amount > 0 and price_per_liter > 0 and round(amount / price_per_liter, 2) != liter:
            return {'value': {'liter': round(amount / price_per_liter, 2), }}
        else:
            return {}

    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        if not vehicle_id:
            return {}
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        odometer_unit = vehicle.odometer_unit
        driver = vehicle.driver_id.id
        return {
            'value': {
                'odometer_unit': odometer_unit,
                'purchaser_id': driver,
                'consumption_card_id': vehicle.consumption_card_id.id,
                'vendor_id': vehicle.consumption_card_id.vendor_id.id,
            },
            'domain': {
                'consumption_card_id': [('id', '=', vehicle.consumption_card_id.id)],
                #'consumption_card_id': [('id', 'in', vehicle.consumption_card_ids)],
                # The second parameter is required if vehicle cant admit multiple consumption cards
            }

        }

    def _check_positive_value(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.amount <= 0 or record.price_per_liter <= 0:
                return False
            if record.amount < record.price_per_liter:
                return False
        return True

    _name = 'fleet.vehicle.log.fuel'
    _inherit = 'fleet.vehicle.log.fuel'
    _columns = {
        'consumption_card_id': fields.many2one("fleet.consumption.card", "Consumption Card"),
        'payment_mode': fields.selection([('card', 'By consumption card'), ('cash', 'Cash')], 'Payment Mode',
                                         help='Payment mode for fuel consumption', required=True),
        'attachment_ids': fields.many2many("ir.attachment", "fleet_vehicle_log_fuel_attachment_rel", "attachment_id",
                                           "fuel_id", "Attachments"),
    }
    _defaults = {
        'payment_mode': 'cash',
    }
    _constraints = [
        (_check_positive_value,
         _('\nTotal amount and price per liter must be positive.\nTotal amount must be higher than price per liter'),
         ['Total amount', 'Price per liter']),
    ]

    def create(self, cr, uid, value, context=None):
        if value['payment_mode'] == 'card':
            consumption_card_pool = self.pool.get('fleet.consumption.card')
            consumption_card = consumption_card_pool.browse(cr, uid, value['consumption_card_id'], context=context)
            if consumption_card.balance >= value['amount']:
                consumption_card_pool.write(cr, uid, consumption_card.id,
                                            {'balance': consumption_card.balance - value['amount']})
            else:
                raise except_orm(_('Operation not allowed!'), _('Consumption card balance can''t support operation.'))
        else:
            value['consumption_card_id'] = None
        return super(fleet_vehicle_log_fuel, self).create(cr, uid, value, context=context)

        #def write(self, cr, uid, ids, value, context=None):
        #    for record in self.browse(cr, uid, ids, context=context):
        #        if record.payment_mode != value['payment_mode']
        #        if record.consumption_card_id.id != value['consumption_card_id']:
        #            return


fleet_vehicle_log_fuel()


class fleet_move_type(osv.osv):
    _name = 'fleet.move.type'
    _description = 'Moves types related to vehicles'
    _columns = {
        'name': fields.char("Name", size=64, required=True),
        'description': fields.text("Description"),
    }
    _sql_constraints = [('fleet_move_type_name_unique', 'unique(name)', 'Move type name already exists')]


fleet_move_type()


class fleet_passenger(osv.osv):
    _name = 'fleet.passenger'
    _description = 'Passengers for moves'
    _columns = {
        'name': fields.char("Name", size=64, required=True),
        'identity_card_number': fields.char("Identity Card Number", size=35),
    }
    _sql_constraints = [('fleet_passenger_name_unique', 'unique(name)', 'Passenger name already exists')]


fleet_passenger()


class fleet_vehicle_log_moves(osv.osv):
    def _move_name_get_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.vehicle_id.name + ' / ' + str(record.id)
        return res

    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        if not vehicle_id:
            return {}
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        odometer_unit = vehicle.odometer_unit
        driver = vehicle.driver_id.id
        return {
            'value': {
                'odometer_unit': odometer_unit,
                'odometer_back_unit': odometer_unit,
                'driver_id': driver,
            }
        }


    def _get_odometer_back(self, cr, uid, ids, odometer_back_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.odometer_back_id:
                res[record.id] = record.odometer_back_id.value
        return res

    def _set_odometer_back(self, cr, uid, id, name, value, args=None, context=None):
        if value:
            this = self.browse(cr, uid, id, context=context)
            date = this.back_date if not this.back_date else fields.date.context_today(self, cr, uid, context=context)
            vehicle_id = this.vehicle_id.id
            data = {'value': value, 'date': date, 'vehicle_id': vehicle_id}
            odometer_back_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
            self.write(cr, uid, id, {'odometer_back_id': odometer_back_id})
            return odometer_back_id

    def _get_odometer(self, cr, uid, ids, odometer_back_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.odometer_id:
                res[record.id] = record.odometer_id.value
        return res

    def _set_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if value:
            this = self.browse(cr, uid, id, context=context)
            date = this.departure_date if not this.departure_date else fields.date.context_today(self, cr, uid,
                                                                                                 context=context)
            vehicle_id = this.vehicle_id.id
            data = {'value': value, 'date': date, 'vehicle_id': vehicle_id}
            odometer_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
            self.write(cr, uid, id, {'odometer_id': odometer_id})
            return odometer_id

    _name = 'fleet.vehicle.log.moves'
    _order = 'id desc'
    _description = 'Moves for vehicles'
    _columns = {
        'name': fields.function(_move_name_get_fnc, type="char", string='Name', store=True),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle', required=True),
        'move_order_ref': fields.char("Order Reference", size=64),
        'driver_id': fields.many2one("res.partner", "Driver", required=True),
        'object': fields.char("Object", size=64),
        'date': fields.datetime("Date", help="Date of logging record"),
        'move_type_id': fields.many2one("fleet.move.type", "Move Type", required=True),
        'estimated_departure_date': fields.datetime("Estimated Departure Date", required=True),
        'departure_date': fields.datetime("Departure Date"),
        'departure_place': fields.char("Departure Place", size=64),
        'arrival_place': fields.char("Destination Place", size=64),
        'back_date': fields.datetime("Back Date"),
        'odometer_id': fields.many2one('fleet.vehicle.odometer', 'Odometer'),
        'odometer': fields.function(_get_odometer, fnct_inv=_set_odometer, type='float', string='Odometer Value',
                                    help='Odometer measure of the vehicle at the moment of this log'),
        'odometer_unit': fields.related('vehicle_id', 'odometer_unit', type="char", string="Unit", readonly=True),
        'notes': fields.text('Notes'),
        'other_passenger_ids': fields.many2many("fleet.passenger", "move_passenger_rel", "move_id", "passenger_id",
                                                "Other Passengers"),
        'passenger_ids': fields.many2many("res.partner", "move_partner_rel", "move_id", "partner_id", "Passengers",
                                          domain="[('employee','=',True)]"),
        'state': fields.selection([
                                      ('draft', 'Draft'),
                                      ('confirmed', 'Confirmed'),
                                      ('done', 'Done')
                                  ], "State", readonly=True),
        'consumption_card_ids': fields.many2many("fleet.consumption.card", "move_consumption_card_rel", "move_id",
                                                 "consumption_card_id", "Consumption Cards"),
        'odometer_back_id': fields.many2one('fleet.vehicle.odometer', 'Odometer'),
        'odometer_back': fields.function(_get_odometer_back, fnct_inv=_set_odometer_back, type='float',
                                         string='Odometer Value',
                                         help='Odometer measure of the vehicle at the moment of this log'),
        'odometer_back_unit': fields.related('vehicle_id', 'odometer_unit', type="char", string="Unit", readonly=True),
        'attachment_ids': fields.many2many("ir.attachment", "fleet_vehicle_log_moves_attachment_rel", "attachment_id",
                                           "move_id", "Attachments"),
    }
    _defaults = {
        'state': 'draft',
        'estimated_departure_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def create(self, cr, uid, value, context=None):
        value['date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        return super(fleet_vehicle_log_moves, self).create(cr, uid, value, context=context)

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def action_confirmed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True


fleet_vehicle_log_moves()


class fleet_vehicle_log_incidents(osv.osv):
    def _incident_name_get_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.vehicle_id.name + ' / ' + str(record.id)
        return res

    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        if not vehicle_id:
            return {}
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        odometer_unit = vehicle.odometer_unit
        driver = vehicle.driver_id.id
        return {
            'value': {
                'odometer_unit': odometer_unit,
                'purchaser_id': driver,
            }
        }

    def _get_odometer(self, cr, uid, ids, odometer_back_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.odometer_id:
                res[record.id] = record.odometer_id.value
        return res

    def _set_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if value:
            this = self.browse(cr, uid, id, context=context)
            date = this.date if not this.date else fields.date.context_today(self, cr, uid, context=context)
            vehicle_id = this.vehicle_id.id
            data = {'value': value, 'date': date, 'vehicle_id': vehicle_id}
            odometer_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
            self.write(cr, uid, id, {'odometer_id': odometer_id})
            return odometer_id

    _name = 'fleet.vehicle.log.incidents'
    _order = 'id desc'
    _description = 'Incident logs for vehicles'
    _columns = {
        'name': fields.function(_incident_name_get_fnc, type="char", string='Name', store=True),
        'state': fields.selection([
                                      ('draft', 'Draft'),
                                      ('confirmed', 'Confirmed'),
                                      ('done', 'Done')
                                  ], "State", readonly=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'note': fields.text("Notes"),
        'date': fields.datetime("Date"),
        'odometer_id': fields.many2one('fleet.vehicle.odometer', 'Odometer'),
        'odometer': fields.function(_get_odometer, fnct_inv=_set_odometer, type='float', string='Odometer Value',
                                    help='Odometer measure of the vehicle at the moment of this log'),
        'odometer_unit': fields.related('vehicle_id', 'odometer_unit', type="char", string="Unit", readonly=True),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle', required=True),
        'attachment_ids': fields.many2many("ir.attachment", "fleet_vehicle_log_incidents_attachment_rel",
                                           "attachment_id", "incident_id", "Attachments"),

    }
    _defaults = {
        'state': 'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
    }

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def action_confirmed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True


fleet_vehicle_log_incidents()


class fleet_vehicle_log_services(osv.osv):
    _name = 'fleet.vehicle.log.services'
    _inherit = 'fleet.vehicle.log.services'
    _columns = {
        'incident_id': fields.many2one('fleet.vehicle.log.incidents', 'Incident'),
        'attachment_ids': fields.many2many("ir.attachment", "fleet_vehicle_log_services_attachment_rel",
                                           "attachment_id", "service_id", "Attachments"),
    }


fleet_vehicle_log_services()


class fleet_vehicle_log_moves_needs(osv.osv):
    def return_action_to_open_view(self, cr, uid, ids, context=None):
        """ This opens the xml view specified in xml_id for the current vehicle """
        if context is None:
            context = {}
        if context.get('xml_id'):
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'fleet_guce', context['xml_id'],
                                                                    context=context)
            res['context'] = context
            res['target'] = "new"
            res['res_id'] = context['res_id']
            res['view_mode'] = 'form'
            res['view_type'] = 'form'
            return res
        return False

    def view_move_form(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0], context=context)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'fleet_guce', 'fleet_vehicle_log_moves_form')
        id_view = res and res[1] or False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Planned Move'),
            'res_model': 'fleet.vehicle.log.moves',
            'res_id': this.move_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': id_view,
            'target': 'new',
            'nodestroy': True,
        }

    def _needs_name_get_fnc(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            name = record.need_date + ' / ' + record.user_id.name
            res[record.id] = name
        return res

    def _check_return_date(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.return_date <= record.departure_date:
                return False
        return True

    def _check_departure_date(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.departure_date < record.need_date:
                return False
        return True

    _name = 'fleet.vehicle.log.moves.needs'
    _order = 'id desc'
    _description = 'Moves needs logs'
    _columns = {
        'name': fields.function(_needs_name_get_fnc, type="text", string="Name", store=True),
        'need_date': fields.datetime("Need Date", readonly=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'note': fields.text("Notes"),
        'state': fields.selection([
                                      ('draft', 'Draft'),
                                      ('submitted', 'Submitted'),
                                      ('answered', 'Answered')
                                  ], "State", readonly=True),
        'destination': fields.char("Destination", size=64, required=True),
        'departure_date': fields.datetime("Estimated Departure Date", required=True),
        'return_date': fields.datetime("Estimated Return Date", required=True),
        'seats': fields.integer('Seats Number', help='Number of seats needed', required=True),
        'attachment_ids': fields.many2many("ir.attachment", "fleet_vehicle_log_needs_attachment_rel", "attachment_id",
                                           "need_id", "Attachments"),
        'answer_decision': fields.selection([('yes', 'Yes'), ('no', 'No')], 'Decision'),
        'answer_notes': fields.text("Notes"),
        'answerer': fields.many2one('res.users', 'Answerer', readonly=True),
        'answer_date': fields.datetime('Answer Date'),
        'move_id': fields.many2one('fleet.vehicle.log.moves', 'Move'),

    }
    _defaults = {
        'state': 'draft',
        'need_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'departure_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
        'seats': 1,
    }

    _constraints = [
        (_check_return_date,
         _('\nInvalid estimated return date.'), [_('Estimated Return Date')]),
        (_check_departure_date,
         _('\nInvalid estimated departure date.'), [_('Estimated Departure Date')]),
    ]

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def action_answered(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'answered'}, context=context)
        return True

    def action_submitted(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'submitted'})
        return True


fleet_vehicle_log_moves_needs()


class fleet_vehicle_assignment(osv.osv):
    def create(self, cr, uid, value, context=None):
        if 'driver_id' in value:
            ids = []
            if 'old_driver_id' not in value:
                value['old_driver_id'] = self.pool.get('fleet.vehicle').browse(cr, uid, value['vehicle_id'],
                                                                               context=context).driver_id.id
            if value['driver_id'] != value['old_driver_id']:
                assignment_id = super(fleet_vehicle_assignment, self).create(cr, uid, value, context=context)
                ids.append(value['vehicle_id'])
                self.pool.get('fleet.vehicle').write(cr, uid, ids, {'driver_id': value['driver_id']}, context=context)
                return assignment_id

    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        if not vehicle_id:
            return {}
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        return {
            'value': {
                'old_driver_id': vehicle.driver_id.id,
            }
        }

    def write(self, cr, uid, ids, value, context=None):
        if 'driver_id' in value:
            vehicle_ids = []
            if 'old_driver_id' not in value:
                value['old_driver_id'] = self.pool.get('fleet.vehicle').browse(cr, uid, value['vehicle_id'],
                                                                               context=context).driver_id.id
            if value['driver_id'] != value['old_driver_id']:
                vehicle_ids.append(value['vehicle_id'])
                assignment_id = super(fleet_vehicle_assignment, self).write(cr, uid, ids, value, context=context)
                self.pool.get('fleet.vehicle').write(cr, uid, vehicle_ids, {'driver_id': value['driver_id']},
                                                     context=context)
        return True

    def _assignment_name_get_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            name = record.vehicle_id.name + ' / ' + record.driver_id.name
            res[record.id] = name
        return res

    _name = 'fleet.vehicle.assignment'
    _order = 'id desc'
    _description = 'Assignment of drivers to vehicles'
    _columns = {
        'name': fields.function(_assignment_name_get_fnc, type="char", string='Name', store=True),
        'assignment_date': fields.datetime("Assignment Date"),
        'vehicle_id': fields.many2one("fleet.vehicle", "Vehicle", required=True),
        'driver_id': fields.many2one('res.partner', 'New Driver', required=True),
        'old_driver_id': fields.many2one('res.partner', 'Old Driver', readonly=True),
        'note': fields.text('Notes'),
    }
    _defaults = {
        'assignment_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }


fleet_vehicle_assignment()
