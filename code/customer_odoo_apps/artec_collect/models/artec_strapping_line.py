from odoo import fields, models

class ArtecStrappingLine(models.Model):
    _name="artec.strapping.line"
    
    depth = fields.Float(
        string='Depth [m]',
        required=True
    )

    volume = fields.Float(
        string='Volume [m3]',
        required=True
    )
    
    strapping_id = fields.Many2one(
        comodel_name='artec.strapping',
        string='Strapping'
    )