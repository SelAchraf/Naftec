from odoo import fields, models
from odoo.exceptions import ValidationError
from datetime import timedelta

class ArtecExpeditionReportWizard(models.TransientModel):
    _name = 'artec.expedition.report.wizard'
    
    date = fields.Date(
        string='Date',
        required=True,
    )
    
    def action_report_expedition(self, data=None):
        start_of_day = fields.Datetime.to_datetime(self.date)
        end_of_day = start_of_day + timedelta(days=1)
        
        expedition_ids = self.env['artec.expedition'].search([
            ('start_datetime', '>=', start_of_day),
            ('start_datetime', '<', end_of_day)
        ])
        
        if not expedition_ids:
            raise ValidationError("There is no expeditions in this date.")
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/artec_expedition/excel/report/{list(expedition_ids.ids)}',
            'target': 'new'
        }