from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ArtecAstmLine(models.Model):
    _name="artec.astm.line"
    
    temperature = fields.Float(
        string='Temperature [c°]',
    )

    density = fields.Float(
        string='Density [sg]',
    )
    
    coefficient = fields.Float(
        string='Coefficient',
    )
    
    astm_id = fields.Many2one(
        comodel_name='artec.astm',
        string='Astm'
    )
    
    _sql_constraints = [
        ('unique_temperature_density_astm',
        'UNIQUE(temperature, density, astm_id)',
        'Duplicate temperature and density combination is not allowed within the same ASTM.')
    ]
    
    @api.constrains('coefficient')
    def _check_coefficient_not_zero(self):
        for record in self:
            if record.coefficient == 0:
                raise ValidationError("The coefficient must not be zero.")