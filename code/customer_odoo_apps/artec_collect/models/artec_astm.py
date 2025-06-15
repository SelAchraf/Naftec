from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ArtecAstm(models.Model):
    _name = 'artec.astm'
    
    name = fields.Char(
        string='Name'
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
    
    astm_line_ids = fields.One2many(
        comodel_name='artec.astm.line',
        inverse_name='astm_id',
        string='ASTM Lines'
    )
    
    @api.constrains('start_date', 'end_date')
    def _check_end_date_after_start_date(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError("End date must be greater than start date.")
    
    @api.constrains('end_date', 'active')
    def _check_end_date_required(self):
        for record in self:
            if not record.active and not record.end_date:
                raise ValidationError("End date is required when the ASTM is inactive.")
    
    @api.depends('start_date', 'end_date')
    def _compute_active(self):
        for record in self:
            today = fields.Datetime.today()
            if (not record.end_date or (record.end_date and record.end_date > today)) and record.start_date and record.start_date <= today:
                record.active = True
            else:
                record.active = False
    
    @api.constrains('start_date', 'end_date')
    def _check_date_overlap(self):
        for record in self:
            # Search for all ASTM records, excluding the current record
            domain = [('id', '!=', record.id)]
            all_astms = self.with_context(active_test=False).search(domain)
            
            def is_date_overlap(astm):
                astm_start = astm.start_date
                astm_end = astm.end_date
                
                overlap_status = (
                    (astm_end and ((astm_start < record.start_date < astm_end) or (record.end_date and (astm_start < record.end_date < astm_end))))
                    or ((not astm_end and record.end_date) and (record.start_date < astm_start < record.end_date))
                    or (not astm_end and not record.end_date and astm_start == record.start_date)
                )
                return overlap_status
            
            overlapping_astms = all_astms.filtered(is_date_overlap)
            
            if overlapping_astms:
                raise ValidationError(
                    f"Date overlap detected with existing ASTM records. "
                    "Please ensure date ranges do not overlap with other ASTM records."
                )
            elif record.active:
                active_astms = all_astms.filtered(lambda s: s.active and s.start_date < record.start_date)
                if active_astms:
                    for active_astm in active_astms:
                        active_astm.end_date = record.start_date
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'