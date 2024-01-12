# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>> DELTA SYSTEM
# >>> DESCRIPCION: CAMPOS VÁLIDOS PARA NÓMINAS.
# >>> NUMERO    FECHA (DD/MM/YYYY)  DESARROLLADOR               CAMBIOS EFECTUADOS
# >>> 00001     20/12/2022          GIANMARCO CONTRERAS         AGREGA CAMPOS PARA PERSONALIZACIÓN DE NÓMINAS.
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import pytz

AFP_SELECTION = [
    ('capital', 'Capital'),
    ('cuprum', 'Cuprum'),
    ('habitat', 'Habitat'),
    ('modelo', 'Modelo'),
    ('planvital', 'Planvital'),
    ('provida', 'Provida'),
    ('uno', 'Uno'),
    ('primer_trabajo', 'Primer trabajo'),
    ('no_cotiza', 'No cotiza')
]


from odoo import api, fields, models


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', index=True, default='monthly',
    help="Defines the frequency of the wage payment.")
    resource_calendar_id = fields.Many2one(required=True, help="Employee's working schedule.")
    hra = fields.Monetary(string='HRA', help="House rent allowance.")
    travel_allowance = fields.Monetary(string="Travel Allowance", help="Travel allowance")
    da = fields.Monetary(string="DA", help="Dearness allowance")
    meal_allowance = fields.Monetary(string="Meal Allowance", help="Meal allowance")
    medical_allowance = fields.Monetary(string="Medical Allowance", help="Medical allowance")
    other_allowance = fields.Monetary(string="Other Allowance", help="Other allowances")

    # HABERES IMPONIBLES
    legal_gratification = fields.Monetary(string='Gratificación legal', copy=False)  # ???
    commissions = fields.Monetary(string='Comisiones', copy=False)
    production_bonus = fields.Monetary(string='Bonos de producción', copy=False)
    extra_hours = fields.Monetary(string='Horas extras', copy=False)  # ???
    total_taxable_assets = fields.Monetary(string='Total de Haberes imponibles')

    # HABERES NO IMPONIBLES
    movilization = fields.Monetary(string='Movilización')
    cash_loss = fields.Monetary(string='Pérdida de caja')
    tool_wear = fields.Monetary(string='Desgaste de herramientas')
    collation = fields.Monetary(string='Colación')
    travel_expenses = fields.Monetary(string='Viáticos')
    household_allowance = fields.Monetary(
        string='Asignación familiar', help='Prestaciones familiares otorgadas en conformidad a la ley.')  # ???
    compensation_years_service = fields.Monetary(string='Indemnización por años de servicios')  # ???
    compensation_termination_employment_relationship = fields.Monetary(
        string='Indemnizaciones que proceda pagar al extinguirse la relación laboral')  # ???
    total_non_taxable_assets = fields.Monetary(string='Total de Haberes no imponibles')

    # DESCUENTOS PREVISIONALES
    # afp = fields.Selection(AFP_SELECTION, string='AFP')
    pension_fund_administrators_id = fields.Many2one(comodel_name='pension.fund.administrators', string='AFP', tracking=True)  # ???
    afp_amount = fields.Monetary(string='Monto AFP', readonly=True)
    unemployment_insurance = fields.Monetary(string='Seguro de desempleo')
    fonasa = fields.Monetary(string='Fonasa')  # ???
    isapre = fields.Monetary(string='Isapre')  # ???
    total_provisional_discounts = fields.Monetary(string='Total de descuentos previsionales')

    # CÁLCULO DE IMPUESTO A LA RENTA

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
                 then first level children and so on) and without duplicata
        """
        structures = self.mapped('struct_id')
        if not structures:
            return []
        # YTI TODO return browse records
        return list(set(structures._get_parent_structure().ids))

    def get_attribute(self, code, attribute):
        return self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1)[attribute]

    def set_attribute_value(self, code, active):
        for contract in self:
            if active:
                value = self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1).default_value
                contract[code] = value
            else:
                contract[code] = 0.0

    def get_total_taxable_assets(self):
        return self.wage + self.legal_gratification + self.commissions + self.production_bonus + self.extra_hours

    def set_taxable_assets(self):
        movilization = 553.266666666667 * 30
        collation = 553.266666666667 * 30
        data = {
            'movilization': movilization,
            'collation': collation
        }
        self.write(data)

    def set_provisional_discounts(self):
        params = self.env['ir.config_parameter'].sudo()
        total_taxable_assets = self.get_total_taxable_assets()
        afp_amount = total_taxable_assets * (self.pension_fund_administrators_id.variable_commission / 100)

        # SEGURO DE DESEMPLEO
        unemployment_insurance_parameter = params.get_param('om_hr_payroll.unemployment_insurance')
        # unemployment_insurance_amount = total_taxable_assets * (0.6 / 100)
        unemployment_insurance_amount = total_taxable_assets * (float(unemployment_insurance_parameter) / 100)

        # UNIDAD DE FOMENTO
        value_uf = params.get_param('om_hr_payroll.value_uf')

        fonasa_amount = total_taxable_assets * (7 / 100)
        data = {
            'afp_amount': afp_amount,
            'unemployment_insurance': unemployment_insurance_amount,
            'fonasa': fonasa_amount
        }
        self.write(data)

    @api.model
    def _set_value_uf(self):
        cron = self.env.ref('om_hr_payroll.ir_cron_calculate_benefits_discounts')
        # DEFINIR LA ZONA HORARIA DE DESTINO (SANTIAGO/CHILE)
        # timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'America/Santiago')
        timezone = pytz.timezone('America/Santiago')

        # AGREGAR INFORMACIÓN DE ZONA HORARIA AL OBJETO DATETIME
        datetime_utc = pytz.utc.localize(cron.nextcall)
        datetime_timezone = datetime_utc.astimezone(timezone)

        value_uf = self.env['res.config.settings'].sudo().get_value_uf(date=datetime_timezone)
        self.env['ir.config_parameter'].sudo().set_param('om_hr_payroll.value_uf', value_uf)

    def cron_calculate_benefits_discounts(self):
        self.set_taxable_assets()
        self.set_provisional_discounts()


class HrContractAdvantageTemplate(models.Model):
    _name = 'hr.contract.advantage.template'
    _description = "Employee's Advantage on Contract"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    lower_bound = fields.Float('Lower Bound', help="Lower bound authorized by the employer for this advantage")
    upper_bound = fields.Float('Upper Bound', help="Upper bound authorized by the employer for this advantage")
    default_value = fields.Float('Default value for this advantage')
