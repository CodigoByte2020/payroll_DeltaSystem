from odoo import api, fields, models


class PensionFundAdministrators(models.Model):

    _name = 'pension.fund.administrators'
    _description = 'Pension Fund Administrators'

    name = fields.Char(string='AFP', required=True, tracking=True)
    # POR AHORA SE ESTA SETEANDO UN MONTO FIJO
    variable_commission = fields.Float(string='Comisión variable %', tracking=True)
