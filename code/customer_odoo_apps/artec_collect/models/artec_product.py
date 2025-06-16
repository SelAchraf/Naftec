from odoo import fields, models

class ArtecProduct(models.Model):
    _name = "artec.product"
    
    name = fields.Char(
        string='Name',
        required=True
    )
    
    color = fields.Integer(
        string='Color',
        required=True
    )
    
    tank_ids = fields.One2many(
        comodel_name='artec.tank', 
        inverse_name='product_id',
        string="Tank",
    )
