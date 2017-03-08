# -*- coding: utf-8 -*-
#__author__ = 'Koufana'
{
    'name': 'Appacheur Fleet Management',
    'version': '1.0',
    'author': 'Koufana Crepin Sosthene, APPACHEUR',
    'sequence': '10',
    'category': 'Managing vehicles',
    'website': 'www.appacheur.org',
    'summary': 'Appacheur, Vehicle, Consumption Card, insurances, costs',
    'description': """
    """,
    'depends': ['base', 'fleet'],
    'qweb': ['static/src/xml/*.xml'],
    'data': [
        'fleet_appacheur_view.xml',
        'fleet_appacheur_workflow.xml',
        'fleet_appacheur_data.xml',
        'wizard/fleet_appacheur_wizard_view.xml',
    ],
    'update_xml': ['security/fleet_appacheur_security.xml', 'security/ir.model.access.csv', 'report/fleet_report_view.xml'],
    'instalable': 'true',
}
