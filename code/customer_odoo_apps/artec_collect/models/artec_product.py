from odoo import fields, models

class ArtecProduct(models.Model):
    _name = "artec.product"
    
    name = fields.Char(
        string='Name',
    )
    
    color = fields.Integer(
        string='Color',
    )
    
    tank_ids = fields.One2many(
        comodel_name='artec.tank', 
        inverse_name='product_id',
        string="Tank",
    )
