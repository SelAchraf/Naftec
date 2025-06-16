from odoo import fields, models

class ArtecTank(models.Model):
    _name = "artec.tank"
    
    name = fields.Char(
        string='Name',
    )
    
    width = fields.Float(
        string='Width',
    )
    
    length = fields.Float(
        string='Length',
    )
    
    product_id = fields.Many2one(
        comodel_name='artec.product',
        string='Product'
    )
    
    strapping_ids = fields.One2many(
        comodel_name="artec.strapping",
        inverse_name="tank_id",
        string="Strapping",
    )