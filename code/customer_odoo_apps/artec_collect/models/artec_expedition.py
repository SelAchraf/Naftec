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
        string='Expedited Volume [m³]',
        compute = '_compute_expedited_volume',
        store=True
    )
    
    start_temperature = fields.Float(
        string='Temperature before expedition [c°]'
    )
    
    start_density = fields.Float(
        string='Density before expedition [sg]'
    )
    
    start_datetime = fields.Datetime(
        string='Start date',
        required=True
    )    
    
    start_depth = fields.Float(
        string='Depth before expedition [m]',
    )
    
    start_theoretical_volume = fields.Float(
        string='Theoretical volume before expedition [m³]',
        compute='_compute_start_theoretical_volume',
        store=True
    )
    
    start_coefficient = fields.Float(
        compute='_compute_start_coefficient',
        string='Coefficient before expedition',
        store=True
    )
    
    start_volume = fields.Float(
        string='Volume before expedition [m³]',
        compute = '_compute_start_volume',
        store=True
    )
    
    end_temperature = fields.Float(
        string='Temperature after expedition [c°]'
    )
    
    end_density = fields.Float(
        string='Density after expedition [sg]'
    )
    
    end_datetime = fields.Datetime(
        string='End date',
    )    
    
    end_depth = fields.Float(
        string='Depth after expedition [m]',
    )
    
    end_theoretical_volume = fields.Float(
        string='Theoretical volume after expedition [m³]',
        compute='_compute_end_theoretical_volume',
        store=True
    )
    
    end_coefficient = fields.Float(
        compute='_compute_end_coefficient',
        string='Coefficient after expedition',
        store=True
    )
    
    end_volume = fields.Float(
        string='Volume after expedition [m³]',
        compute = '_compute_end_volume',
        store=True
    )  
    
    @api.constrains('start_depth')
    def _check_start_depth_not_zero(self):
        for record in self:
            if record.start_depth == 0:
                raise ValidationError("The depth before expedition must not be zero.")
    
    @api.depends('start_datetime','tank_id')
    def _compute_name(self):
        for record in self:
            if not record.start_datetime or not record.tank_id:
                record.name = False
                continue
            record.name = record.tank_id.name + '-' + str(record.start_datetime).replace(' ', '-')
    
    @api.depends('start_datetime','tank_id','start_depth')
    def _compute_start_theoretical_volume(self):
        for record in self:
            if not record.start_datetime or not record.tank_id or not record.start_depth:
                record.start_theoretical_volume = 0
                continue
            strapping = self.env['artec.strapping'].with_context(active_test=False).search([
                ('tank_id', '=', record.tank_id.id),
                ('start_datetime', '<=', record.start_datetime),
                ('state', '=', 'confirmed'),
                '|',
                ('end_datetime', '=', False),
                ('end_datetime', '>', record.start_datetime)
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
    
    @api.depends('end_datetime','tank_id','end_depth')
    def _compute_end_theoretical_volume(self):
        for record in self:
            if not record.end_datetime or not record.tank_id:
                record.end_theoretical_volume = 0
                continue
            strapping = self.env['artec.strapping'].with_context(active_test=False).search([
                ('tank_id', '=', record.tank_id.id),
                ('start_datetime', '<=', record.end_datetime),
                ('state', '=', 'confirmed'),
                '|',
                ('end_datetime', '=', False),
                ('end_datetime', '>', record.end_datetime)
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
                
    @api.depends('start_datetime', 'start_temperature', 'start_density')
    def _compute_start_coefficient(self):
        for record in self:
            if not record.start_datetime:
                record.start_coefficient = 0
                continue
            
            astm = self.env['artec.astm'].with_context(active_test=False).search([
                ('start_datetime', '<=', record.start_datetime),
                ('state', '=', 'confirmed'),
                '|',
                ('end_datetime', '=', False),
                ('end_datetime', '>', record.start_datetime)
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
                    Tg = record.start_temperature
                    Dg = record.start_density
                    
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

                    record.start_coefficient = (C1+C2+C3+C4)/4
                    
    @api.depends('end_datetime', 'end_temperature', 'end_density')
    def _compute_end_coefficient(self):
        for record in self:
            if not record.end_datetime:
                record.end_coefficient = 0
                continue
            
            astm = self.env['artec.astm'].with_context(active_test=False).search([
                ('start_datetime', '<=', record.end_datetime),
                ('state', '=', 'confirmed'),
                '|',
                ('end_datetime', '=', False),
                ('end_datetime', '>', record.end_datetime)
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
                    Tg = record.end_temperature
                    Dg = record.end_density
                    
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

                    record.end_coefficient = (C1+C2+C3+C4)/4
                    
    
    @api.depends('start_theoretical_volume', 'start_coefficient')
    def _compute_start_volume(self):
        for record in self:
            record.start_volume = record.start_theoretical_volume * record.start_coefficient
            
    @api.depends('end_theoretical_volume', 'end_coefficient')
    def _compute_end_volume(self):
        for record in self:
            record.end_volume = record.end_theoretical_volume * record.end_coefficient
            
    @api.depends('start_volume', 'end_volume')
    def _compute_expedited_volume(self):
        for record in self:
            if not record.start_volume:
                record.expedited_volume = 0
                continue
            elif record.start_volume <= record.end_volume:
                raise ValidationError("The volume after expedition must be less than the volume before expedition, please verify the entered parameters")
            
            record.expedited_volume = record.start_volume - record.end_volume