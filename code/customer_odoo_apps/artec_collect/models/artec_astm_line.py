from odoo import fields, models

class ArtecAstmLine(models.Model):
    _name="artec.astm.line"
    
    temperature = fields.Float(
        string='Temperature [c°]',
        required=True
    )

    density = fields.Float(
        string='Density [sg]',
        required=True
    )
    
    coefficient = fields.Float(
        string='Coefficient',
        required=True
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