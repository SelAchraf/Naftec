from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ArtecStrappingLine(models.Model):
    _name="artec.strapping.line"
    
    depth = fields.Float(
        string='Depth [m]',
    )

    volume = fields.Float(
        string='Volume [m3]',
    )
    
    strapping_id = fields.Many2one(
        comodel_name='artec.strapping',
        string='Strapping'
    )
    
    @api.constrains('depth', 'volume')
    def _check_depth_volume_zero(self):
        for record in self:
            if (record.depth == 0.0 and record.volume != 0.0) or (record.volume == 0.0 and record.depth != 0.0):
                raise ValidationError("If one of depth or volume is zero, the other must also be zero.")