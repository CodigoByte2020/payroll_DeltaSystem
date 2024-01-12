# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>> DELTA SYSTEM
# >>> DESCRIPCION: CAMPOS VÁLIDOS PARA NÓMINAS.
# >>> NUMERO    FECHA (DD/MM/YYYY)  DESARROLLADOR               CAMBIOS EFECTUADOS
# >>> 00001     20/12/2022          GIANMARCO CONTRERAS         AGREGA CAMPOS PARA PERSONALIZACIÓN DE NÓMINAS.
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import json
import logging
import requests
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_om_hr_payroll_account = fields.Boolean(string='Payroll Accounting')

    minimum_wage = fields.Float(string='Minimum Wage', config_parameter='om_hr_payroll.minimum_wage')
    value_uit = fields.Float(string='Valor de la UIT', help='UIT: Unidad Impositiva Tributaria',
                             config_parameter='om_hr_payroll.value_uit')
    unemployment_insurance = fields.Float(string='Seguro de desempleo',
                                          config_parameter='om_hr_payroll.unemployment_insurance')
    value_uf = fields.Float(string='Valor de la UF', help='UF: Unidad de Fomento')

    @staticmethod
    def get_value_uf(date=None):
        today = fields.Date.today().strftime('%d-%m-%Y')
        date = date and date.strftime('%d-%m-%Y')
        url = f'https://mindicador.cl/api/uf/{date or today}'
        # url = f'https://mindicador.cl/api/uf/03-01-2024'
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as exception:
            _logger.info(f'****************************** LA CONEXIÓN FALLO ****************************** {exception}')
            raise ValidationError('La conexión falló al consultar los datos. !!!')
        else:
            if response.status_code == 200:
                data = json.loads(response.text.encode("utf-8"))
                value_uf = data['serie'][0]['valor']
                return value_uf
            else:
                raise ValidationError('Estado de respuesta diferente a 200')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('om_hr_payroll.value_uf', self.value_uf)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        value_uf = params.get_param('om_hr_payroll.value_uf')
        res.update(value_uf=value_uf)
        return res
