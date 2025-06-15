from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ArtecExpedition(models.Model):
    _name = 'artec.expedition'
    
    name = fields.Char(
        string='Name',
        compute = '_compute_name',
        store=True
    )
    
    tank_id = fields.Many2one(
        comodel_name='artec.tank',
        string='Tank',
        required=True
    )
    
    expedited_volume = fields.Float(
        string='Expedited Volume [m3]',
        compute = '_compute_expedited_volume',
        store=True
    )
    
    start_temperature = fields.Float(
        string='Temperature before expedition [c°]'
    )
    
    start_density = fields.Float(
        string='Density before expedition [sg]'
    )
    
    start_date = fields.Datetime(
        string='Start date',
        required=True
    )    
    
    start_depth = fields.Float(
        string='Depth before expedition [m]',
        required=True
    )
    
    start_theoretical_volume = fields.Float(
        string='Theoretical volume before expedition [m3]',
        compute='_compute_start_theoretical_volume',
        store=True
    )
    
    start_coefficient = fields.Float(
        compute='_compute_start_coefficient',
        string='Coefficient before expedition',
        store=True
    )
    
    start_volume = fields.Float(
        string='Volume before expedition [m3]',
        compute = '_compute_start_volume',
        store=True
    )
    
    end_temperature = fields.Float(
        string='Temperature after expedition [c°]'
    )
    
    end_density = fields.Float(
        string='Density after expedition [sg]'
    )
    
    end_date = fields.Datetime(
        string='End date',
        required=True
    )    
    
    end_depth = fields.Float(
        string='Depth after expedition [m]',
        required=True
    )
    
    end_theoretical_volume = fields.Float(
        string='Theoretical volume after expedition [m3]',
        compute='_compute_end_theoretical_volume',
        store=True
    )
    
    end_coefficient = fields.Float(
        compute='_compute_end_coefficient',
        string='Coefficient after expedition',
        store=True
    )
    
    end_volume = fields.Float(
        string='Volume after expedition [m3]',
        compute = '_compute_end_volume',
        store=True
    )  
    
    @api.depends('start_date','tank_id')
    def _compute_name(self):
        for record in self:
            if not record.start_date or not record.tank_id:
                record.name = False
                continue
            record.name = record.tank_id.name + '-' + str(record.start_date).replace(' ', '-')
    
    @api.depends('start_date','tank_id','start_depth')
    def _compute_start_theoretical_volume(self):
        for record in self:
            if not record.start_date or not record.tank_id or not record.start_depth:
                record.start_theoretical_volume = 0.0
                continue
            strapping = self.env['artec.strapping'].with_context(active_test=False).search([
                ('tank_id', '=', record.tank_id.id),
                ('start_date', '<=', record.start_date),
                ('state', '=', 'confirmed'),
                '|',
                ('end_date', '=', False),
                ('end_date', '>', record.start_date)
            ])
            if strapping:
                strapping_lines = strapping.strapping_line_ids
                
                if strapping_lines:
                    valid_line = strapping_lines.filtered(lambda l: l.depth == record.start_depth)
                    if valid_line:
                        record.start_theoretical_volume = valid_line.volume
                    else:
                        lower_lines = strapping_lines.filtered(lambda l: l.depth < record.start_depth)
                        upper_lines = strapping_lines.filtered(lambda l: l.depth > record.start_depth)
                        
                        if lower_lines and upper_lines:
                            lower_line = max(lower_lines, key=lambda l: l.depth)
                            upper_line = min(upper_lines, key=lambda l: l.depth)
                            
                            lower_depth = lower_line.depth
                            lower_volume = lower_line.volume
                            upper_depth = upper_line.depth
                            upper_volume = upper_line.volume
                            
                            record.start_theoretical_volume = ((upper_volume-lower_volume)/(upper_depth-lower_depth))*(record.start_depth-lower_depth)+lower_volume
                        else:
                            raise ValidationError(
                                f"The depth before expedition is out of strapping range"
                            )
                else:
                    raise ValidationError(
                        "There is no lines in this strapping"
                    )
            else:
                raise ValidationError(
                    "There is no strapping"
                )
    
    @api.depends('end_date','tank_id','end_depth')
    def _compute_end_theoretical_volume(self):
        for record in self:
            if not record.end_date or not record.tank_id or not record.end_depth:
                record.end_theoretical_volume = 0.0
                continue
            strapping = self.env['artec.strapping'].with_context(active_test=False).search([
                ('tank_id', '=', record.tank_id.id),
                ('start_date', '<=', record.end_date),
                ('state', '=', 'confirmed'),
                '|',
                ('end_date', '=', False),
                ('end_date', '>', record.end_date)
            ])
            if strapping:
                strapping_lines = strapping.strapping_line_ids
                
                if strapping_lines:
                    valid_line = strapping_lines.filtered(lambda l: l.depth == record.end_depth)
                    if valid_line:
                        record.end_theoretical_volume = valid_line.volume
                    else:
                        lower_lines = strapping_lines.filtered(lambda l: l.depth < record.end_depth)
                        upper_lines = strapping_lines.filtered(lambda l: l.depth > record.end_depth)
                        
                        if lower_lines and upper_lines:
                            lower_line = max(lower_lines, key=lambda l: l.depth)
                            upper_line = min(upper_lines, key=lambda l: l.depth)
                            
                            lower_depth = lower_line.depth
                            lower_volume = lower_line.volume
                            upper_depth = upper_line.depth
                            upper_volume = upper_line.volume
                            
                            record.end_theoretical_volume = ((upper_volume-lower_volume)/(upper_depth-lower_depth))*(record.end_depth-lower_depth)+lower_volume
                        else:
                            raise ValidationError(
                                f"The depth after expedition is out of strapping range"
                            )
                else:
                    raise ValidationError(
                        "There is no lines in this strapping"
                    )
            else:
                raise ValidationError(
                    "There is no strapping"
                )