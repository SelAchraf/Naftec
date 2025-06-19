from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ArtecAstm(models.Model):
    _name = 'artec.astm'
    
    name = fields.Char(
        string='Name',
        required=True
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
    
    astm_line_ids = fields.One2many(
        comodel_name='artec.astm.line',
        inverse_name='astm_id',
        string='ASTM Lines'
    )
    
    @api.constrains('start_datetime', 'end_datetime')
    def _check_end_date_after_start_date(self):
        for record in self:
            if record.start_datetime and record.end_datetime:
                if record.end_datetime <= record.start_datetime:
                    raise ValidationError("End date must be greater than start date.")
    
    @api.constrains('end_datetime', 'active')
    def _check_end_date_required(self):
        for record in self:
            if not record.active and not record.end_datetime:
                raise ValidationError("End date is required when the ASTM is inactive.")
    
    @api.depends('start_datetime', 'end_datetime')
    def _compute_active(self):
        for record in self:
            now = fields.Datetime.now()
            if (not record.end_datetime or (record.end_datetime and record.end_datetime > now)) and record.start_datetime and record.start_datetime <= now:
                record.active = True
            else:
                record.active = False
    
    @api.constrains('start_datetime', 'end_datetime')
    def _check_date_overlap(self):
        for record in self:
            # Search for all ASTM records, excluding the current record
            domain = [('id', '!=', record.id)]
            all_astms = self.with_context(active_test=False).search(domain)
            
            def is_date_overlap(astm):
                astm_start = astm.start_datetime
                astm_end = astm.end_datetime
                
                overlap_status = (
                    (astm_end and ((astm_start < record.start_datetime < astm_end) or (record.end_datetime and (astm_start < record.end_datetime < astm_end))))
                    or ((not astm_end and record.end_datetime) and (record.start_datetime < astm_start < record.end_datetime))
                    or (not astm_end and not record.end_datetime and astm_start == record.start_datetime)
                )
                return overlap_status
            
            overlapping_astms = all_astms.filtered(is_date_overlap)
            
            if overlapping_astms:
                raise ValidationError(
                    f"Date overlap detected with existing ASTM records. "
                    "Please ensure date ranges do not overlap with other ASTM records."
                )
            elif record.active:
                active_astms = all_astms.filtered(lambda s: s.active and s.start_datetime < record.start_datetime)
                if active_astms:
                    for active_astm in active_astms:
                        active_astm.end_datetime = record.start_datetime
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'