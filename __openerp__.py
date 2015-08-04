# -*- coding: utf-8 -*-
#__author__ = 'yenke'
{
    'name': 'GUCE Fleet Management',
    'version': '1.0',
    'author': 'Yenke Mbeuyo Marius, ICS ENGINEERING',
    'sequence': '10',
    'category': 'Managing vehicles',
    'website': 'www.ics-engineering.net',
    'summary': 'GUCE, Vehicle, Consumption Card, insurances, costs',
    'description': """
    """,
    'depends': ['base', 'fleet'],
    'data': [
        'fleet_guce_view.xml',
        'fleet_guce_workflow.xml',
        'wizard/fleet_guce_wizard_view.xml',
    ],
    'update_xml': ['security/fleet_guce_security.xml', 'security/ir.model.access.csv', 'report/fleet_report_view.xml'],
    'instalable': 'true',
}
