from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ArtecGauging(models.Model):
    _name="artec.gauging"

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
    
    date = fields.Datetime(
        string='Date',
        required=True
    )
    
    depth = fields.Float(
        string='Depth [m]',
    )
    
    theoretical_volume = fields.Float(
        compute='_compute_theoretical_volume',
        string='Theoretical Volume [m3]',
        store=True
    )
    
    temperature = fields.Float(
        string='Temperature [c°]'
    )
    
    density = fields.Float(
        string='Density [sg]'
    )
    
    coefficient = fields.Float(
        compute='_compute_coefficient',
        string='Coefficient',
        store=True
    )
    
    volume = fields.Float(
        string='Volume',
        compute='_compute_volume',
        store=True
    )
    
    @api.depends('date','tank_id')
    def _compute_name(self):
        for record in self:
            if not record.date or not record.tank_id:
                record.name = False
                continue
            record.name = record.tank_id.name + '-' + str(record.date).replace(' ', '-')
    
    @api.depends('date','tank_id','depth')
    def _compute_theoretical_volume(self):
        for record in self:
            if not record.date or not record.tank_id or not record.depth:
                record.theoretical_volume = 0
                continue
            strapping = self.env['artec.strapping'].with_context(active_test=False).search([
                ('tank_id', '=', record.tank_id.id),
                ('start_date', '<=', record.date),
                ('state', '=', 'confirmed'),
                '|',
                ('end_date', '=', False),
                ('end_date', '>', record.date)
            ])
            if strapping:
                strapping_lines = strapping.strapping_line_ids
                
                if strapping_lines:
                    valid_line = strapping_lines.filtered(lambda l: l.depth == record.depth)
                    if valid_line:
                        record.theoretical_volume = valid_line.volume
                    else:
                        # Find the closest lines with depth less than and greater than record.depth
                        lower_lines = strapping_lines.filtered(lambda l: l.depth < record.depth)
                        upper_lines = strapping_lines.filtered(lambda l: l.depth > record.depth)
                        
                        if lower_lines and upper_lines:
                            lower_line = max(lower_lines, key=lambda l: l.depth)
                            upper_line = min(upper_lines, key=lambda l: l.depth)
                            
                            lower_depth = lower_line.depth
                            lower_volume = lower_line.volume
                            upper_depth = upper_line.depth
                            upper_volume = upper_line.volume
                            
                            record.theoretical_volume = ((upper_volume-lower_volume)/(upper_depth-lower_depth))*(record.depth-lower_depth)+lower_volume
                        else:
                            raise ValidationError(
                                f"The depth is out of strapping range"
                            )
                else:
                    raise ValidationError(
                        "There is no lines in this strapping"
                    )
            else:
                raise ValidationError(
                    "There is no strapping"
                )
    
    @api.depends('date', 'temperature', 'density')
    def _compute_coefficient(self):
        for record in self:
            if not record.date:
                record.coefficient = 0
                continue
            
            astm = self.env['artec.astm'].with_context(active_test=False).search([
                ('start_date', '<=', record.date),
                ('state', '=', 'confirmed'),
                '|',
                ('end_date', '=', False),
                ('end_date', '>', record.date)
            ])
            if not astm:
                raise ValidationError(
                    "There is no ASTM"
                )
            else:
                astm_lines = astm.astm_line_ids
                if not astm_lines:
                    raise ValidationError(
                        "There are no lines in this ASTM"
                    )
                else:         
                    Tg = record.temperature
                    Dg = record.density
                    
                    astm11 = astm_lines.filtered(lambda l:l.temperature <= Tg and l.density <= Dg)
                    if not astm11:
                        raise ValidationError("The data is out of ASTM's range")
                    else:
                        astm11 = sorted(astm11, key=lambda l: (l.temperature, l.density))[-1]
                        Ti = astm11.temperature
                        Di = astm11.density
                        C11 = astm11.coefficient
                        
                        astm12 = astm_lines.filtered(lambda l:l.temperature == Ti and l.density >= Dg)
                        if not astm12:
                            raise ValidationError("The data is out of ASTM's range")
                        else:
                            astm12 = sorted(astm12, key=lambda l: (l.temperature, l.density))[0]
                            Ds = astm12.density
                            C12 = astm12.coefficient
                        
                        astm21 = astm_lines.filtered(lambda l:l.temperature >= Tg and l.density == Di)
                        if not astm21:
                            raise ValidationError("The data is out of ASTM's range")
                        else:
                            astm21 = sorted(astm21, key=lambda l: (l.temperature, l.density))[0]
                            Ts = astm21.temperature
                            C21 = astm21.coefficient
                        
                        astm22 = astm_lines.filtered(lambda l:l.temperature == Ts and l.density == Ds)
                        if not astm22:
                            raise ValidationError("The data is out of ASTM's range")
                        else:
                            C22 = astm22.coefficient
                    
                    if Tg == Ti:
                        C1 = C11
                        C2 = C12
                    else:
                        C1 = ((C21-C11)/(Ts-Ti))*(Tg-Ti) + C11
                        C2 = ((C22-C12)/(Ts-Ti))*(Tg-Ti) + C12
                    
                    if Dg == Di:
                        C3 = C11
                        C4 = C21
                    else:
                        C3 = ((C12-C11)/(Ds-Di))*(Dg-Di) + C11
                        C4 = ((C22-C21)/(Ds-Di))*(Dg-Di) + C21

                    record.coefficient = (C1+C2+C3+C4)/4
                    
    @api.depends('theoretical_volume', 'coefficient')
    def _compute_volume(self):
        for record in self:
            record.volume = record.theoretical_volume * record.coefficient