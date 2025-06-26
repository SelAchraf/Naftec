from odoo import fields, models
from odoo.exceptions import ValidationError
from datetime import timedelta

class ArtecProductionReportWizard(models.TransientModel):
    _name = 'artec.production.report.wizard'
    
    date = fields.Date(
        string='Date',
        required=True,
    )
    
    def action_report_production(self, data=None):
        production_ids = self.env['artec.production'].search([
            ('date', '=', self.date),
        ])
        
        if not production_ids:
            raise ValidationError("There is no productions in this date.")
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/artec_production/excel/report/{list(production_ids.ids)}',
            'target': 'new'
        }