from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime

class ArtecStrapping(models.Model):
    _name="artec.strapping"
    
    sequence = fields.Char(
        string='Sequence'
    )
    
    name = fields.Char(
        string='Name',
        copy=False,
        compute='_compute_name',
        store=True
    )
    
    tank_id = fields.Many2one(
        comodel_name="artec.tank",
        string="Tank",
        default=lambda self: self._context.get('default_tank_id', False),
        required=True,
    )
    
    strapping_line_ids = fields.One2many(
        comodel_name='artec.strapping.line',
        inverse_name='strapping_id',
        string='Strapping Lines'
    )
    
    start_datetime = fields.Datetime(
        string='Start date',
        required=True,
    )    
    
    end_datetime = fields.Datetime(
        string='End date',
    )  
    
    active = fields.Boolean(
        string='Active',
        compute='_compute_active',
        store=True
    )
    
    state = fields.Selection(
        string='State',
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed')
        ],
        default='draft'
    )
    
    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('artec.strapping')        
        return super(ArtecStrapping, self).create(vals)
    
    @api.depends('tank_id', 'sequence')
    def _compute_name(self):
        for record in self:
            if not record.tank_id or not record.sequence:
                record.name = False
                continue
            record.name = f"{record.tank_id.name}_Strapping_{record.sequence}"
    
    @api.constrains('start_datetime', 'end_datetime')
    def _check_end_date_after_start_date(self):
        for record in self:
            if record.start_datetime and record.end_datetime:
                if record.end_datetime <= record.start_datetime:
                    raise ValidationError("End date must be greater than start date.")
    
    @api.constrains('end_datetime', 'active')
    def _check_end_date_required(self):        
        for record in self:
            domain = [
                ('tank_id', '=', record.tank_id.id),
                ('id', '!=', record.id),
            ]
            all_strappings = self.with_context(active_test=False).search(domain)
            after_strappings = all_strappings.filtered(lambda s: s.start_datetime > record.start_datetime)
            
            if after_strappings and not record.end_datetime:
                raise ValidationError("End date is required when there are strappings present after this start date")
                
            if not record.active and not record.end_datetime:
                raise ValidationError("End date is required when the strapping is inactive.")
    
    @api.depends('start_datetime', 'end_datetime')
    def _compute_active(self):
        for record in self:
            now = fields.Datetime.now()
            if (not record.end_datetime or (record.end_datetime and record.end_datetime > now)) and record.start_datetime and record.start_datetime <= now:
                record.active = True
            else:
                record.active = False
            
    @api.constrains('start_datetime', 'end_datetime', 'tank_id')
    def _check_date_overlap(self):
        for record in self:
            domain = [
                ('tank_id', '=', record.tank_id.id),
                ('id', '!=', record.id),
            ]
            all_strappings = self.with_context(active_test=False).search(domain)
            
            def is_date_overlap(strapping):
                strapping_start = strapping.start_datetime
                strapping_end = strapping.end_datetime
                
                overlap_status = (
                    (strapping_end and ((strapping_start < record.start_datetime < strapping_end) or (record.end_datetime and (strapping_start < record.end_datetime < strapping_end))))
                    or ((not strapping_end and record.end_datetime) and (record.start_datetime < strapping_start < record.end_datetime))
                )
                return overlap_status
            
            overlapping_strappings = all_strappings.filtered(is_date_overlap)
            
            if overlapping_strappings:
                raise ValidationError(
                    f"Date overlap detected with existing strapping records for tank {record.tank_id.name}. "
                    "Please ensure date ranges do not overlap with other strappings."
                )
            elif record.active:
                active_strappings = all_strappings.filtered(lambda s: s.active and s.start_datetime < record.start_datetime)
                if active_strappings:
                    for active_strapping in active_strappings:
                        active_strapping.end_datetime = record.start_datetime
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
            
    def _cron_auto_change_active(self):
        tanks = self.search([]).mapped('tank_id')
        
        for tank in tanks:
            active_strapping = self.search([
                ('tank_id', '=', tank.id),
                ('active', '=', True)
            ], limit=1)

            new_strapping = self.search([
                ('tank_id', '=', tank.id),
                ('start_datetime', '<=', fields.Datetime.now()),
                ('end_datetime', '>=', fields.Datetime.now()),
                ('active', '=', False)
            ], limit=1)
            
            if active_strapping and active_strapping.end_datetime and active_strapping.end_datetime <= fields.Datetime.now():
                active_strapping.active = False
            
            if new_strapping:
                if active_strapping and not active_strapping.end_datetime:
                    active_strapping.end_datetime = new_strapping.start_datetime
                new_strapping.active = True

class ArtecStrappingLine(models.Model):
    _name="artec.strapping.line"
    
    depth = fields.Float(
        string='Depth [m]',
    )

    volume = fields.Float(
        string='Volume [m³]',
    )
    
    strapping_id = fields.Many2one(
        comodel_name='artec.strapping',
        string='Strapping'
    )
    
    @api.constrains('depth', 'volume')
    def _check_depth_volume_zero(self):
        for record in self:
            if (record.depth == 0 and record.volume != 0) or (record.volume == 0 and record.depth != 0):
                raise ValidationError("If one of depth or volume is zero, the other must also be zero.")