# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>> DELTA SYSTEM
# >>> DESCRIPCION: CAMPOS VÁLIDOS PARA NÓMINAS.
# >>> NUMERO    FECHA (DD/MM/YYYY)  DESARROLLADOR               CAMBIOS EFECTUADOS
# >>> 00001     20/12/2022          GIANMARCO CONTRERAS         AGREGA CAMPOS PARA PERSONALIZACIÓN DE NÓMINAS.
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_om_hr_payroll_account = fields.Boolean(string='Payroll Accounting')

    minimum_wage = fields.Float(string='Minimum Wage', config_parameter='om_hr_payroll.minimum_wage')
    value_uit = fields.Float(string='Valor de la UIT', help='UIT: Unidad Impositiva Tributaria',
                             config_parameter='om_hr_payroll.value_uit')
    unemployment_insurance = fields.Float(string='Seguro de desempleo',
                                          config_parameter='om_hr_payroll.unemployment_insurance')
    value_uf = fields.Float(string='Valor de la UF', help='UF: Unidad de Fomento',
                            config_parameter='om_hr_payroll.value_uf')
