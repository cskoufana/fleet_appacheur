#__author__ = 'yenke'

import time
from openerp.report import report_sxw


class vehicle(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(vehicle, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})


report_sxw.report_sxw('report.fleet.vehicle', 'fleet.vehicle', 'addons/fleet_guce/report/vehicle.rml', parser=vehicle)


class fleet_vehicle_log_moves(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fleet_vehicle_log_moves, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time})


report_sxw.report_sxw('report.fleet.vehicle.log.moves', 'fleet.vehicle',
                      'addons/fleet_guce/report/vehicle_log_moves.rml', parser=fleet_vehicle_log_moves)


class fleet_vehicle_log_incidents(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fleet_vehicle_log_incidents, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time})


report_sxw.report_sxw('report.fleet.vehicle.log.incidents', 'fleet.vehicle',
                      'addons/fleet_guce/report/vehicle_log_incidents.rml', parser=fleet_vehicle_log_incidents)


class fleet_vehicle_log_services(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fleet_vehicle_log_services, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time})


report_sxw.report_sxw('report.fleet.vehicle.log.services', 'fleet.vehicle',
                      'addons/fleet_guce/report/vehicle_log_services.rml', parser=fleet_vehicle_log_services)


class fleet_vehicle_log_costs(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fleet_vehicle_log_costs, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time})


report_sxw.report_sxw('report.fleet.vehicle.log.costs', 'fleet.vehicle',
                      'addons/fleet_guce/report/vehicle_og_costs.rml', parser=fleet_vehicle_log_costs)


class fleet_vehicle_log_fuel(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fleet_vehicle_log_fuel, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time})


report_sxw.report_sxw('report.fleet.vehicle.log.fuel', 'fleet.vehicle', 'addons/fleet_guce/report/vehicle_log_fuel.rml',
                      parser=fleet_vehicle_log_fuel)


class fleet_consumption_card(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fleet_consumption_card, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time})


report_sxw.report_sxw('report.fleet.consumption.card', 'fleet.consumption.card',
                      'addons/fleet_guce/report/consumption_card.rml', parser=fleet_consumption_card)


class fleet_consumption_card_log_recharges(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fleet_consumption_card_log_recharges, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time})


report_sxw.report_sxw('report.fleet.consumption.card.log.recharges', 'fleet.consumption.card',
                      'addons/fleet_guce/report/consumption_card_log_recharges.rml',
                      parser=fleet_consumption_card_log_recharges)


class fleet_consumption_card_log_consumptions(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fleet_consumption_card_log_consumptions, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time})


report_sxw.report_sxw('report.fleet.consumption.card.log.consumptions', 'fleet.consumption.card',
                      'addons/fleet_guce/report/consumption_card_log_consumptions.rml',
                      parser=fleet_consumption_card_log_consumptions)

