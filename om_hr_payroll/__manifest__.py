# -*- coding:utf-8 -*-

{
    'name': 'Odoo 14 HR Payroll',
    'category': 'Generic Modules/Human Resources',
    'version': '14.0.8.0.0',
    'sequence': 1,
    'license': 'LGPL-3',
    'author': 'Odoo Mates, Odoo SA',
    'summary': 'Payroll For Odoo 14 Community Edition',
    'live_test_url': 'https://www.youtube.com/watch?v=0kaHMTtn7oY',
    'description': "",
    'website': 'https://www.odoomates.tech',
    'depends': [
        'hr_contract',
        'hr_holidays',
    ],
    'data': [
        'security/hr_payroll_security.xml',
        'security/ir.model.access.csv',
        'data/hr_payroll_sequence.xml',
        'data/hr_payroll_category.xml',
        'data/hr_payroll_data.xml',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payroll_report.xml',
        'wizard/hr_payroll_contribution_register_report_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_contribution_register_templates.xml',
        'views/report_payslip_templates.xml',
        'views/report_payslip_details_templates.xml',
        'views/pension_fund_administrators.xml',
        'data/mail_template.xml',
        'data/ir_cron_data.xml'
    ],
    'images': ['static/description/banner.png'],
    'application': True,
}
