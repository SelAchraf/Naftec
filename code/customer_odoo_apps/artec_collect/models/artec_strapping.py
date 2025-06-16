from odoo import api, fields, models
from odoo.exceptions import ValidationError

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
        required=True,
    )
    
    strapping_line_ids = fields.One2many(
        comodel_name='artec.strapping.line',
        inverse_name='strapping_id',
        string='Strapping Lines'
    )
    
    start_date = fields.Datetime(
        string='Start date',
        required=True,
    )    
    
    end_date = fields.Datetime(
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
    
    @api.constrains('start_date', 'end_date')
    def _check_end_date_after_start_date(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError("End date must be greater than start date.")
    
    @api.constrains('end_date', 'active')
    def _check_end_date_required(self):        
        for record in self:
            domain = [
                ('tank_id', '=', record.tank_id.id),
                ('id', '!=', record.id),
            ]
            all_strappings = self.with_context(active_test=False).search(domain)
            after_strappings = all_strappings.filtered(lambda s: s.start_date > record.start_date)
            
            if after_strappings and not record.end_date:
                raise ValidationError("End date is required when there are strappings present after this start date")
                
            if not record.active and not record.end_date:
                raise ValidationError("End date is required when the strapping is inactive.")
    
    @api.depends('start_date', 'end_date')
    def _compute_active(self):
        for record in self:
            today = fields.Datetime.now()
            if (not record.end_date or (record.end_date and record.end_date > today)) and record.start_date and record.start_date <= today:
                record.active = True
            else:
                record.active = False
            
    @api.constrains('start_date', 'end_date', 'tank_id')
    def _check_date_overlap(self):
        for record in self:
            domain = [
                ('tank_id', '=', record.tank_id.id),
                ('id', '!=', record.id),
            ]
            all_strappings = self.with_context(active_test=False).search(domain)
            
            def is_date_overlap(strapping):
                strapping_start = strapping.start_date
                strapping_end = strapping.end_date
                
                overlap_status = (
                    (strapping_end and ((strapping_start < record.start_date < strapping_end) or (record.end_date and (strapping_start < record.end_date < strapping_end))))
                    or ((not strapping_end and record.end_date) and (record.start_date < strapping_start < record.end_date))
                )
                return overlap_status
            
            overlapping_strappings = all_strappings.filtered(is_date_overlap)
            
            if overlapping_strappings:
                raise ValidationError(
                    f"Date overlap detected with existing strapping records for tank {record.tank_id.name}. "
                    "Please ensure date ranges do not overlap with other strappings."
                )
            elif record.active:
                active_strappings = all_strappings.filtered(lambda s: s.active and s.start_date < record.start_date)
                if active_strappings:
                    for active_strapping in active_strappings:
                        active_strapping.end_date = record.start_date
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'