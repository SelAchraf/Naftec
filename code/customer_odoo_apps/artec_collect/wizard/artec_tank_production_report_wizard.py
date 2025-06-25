from odoo import fields, models
from odoo.exceptions import ValidationError

class ArtecTankProductionReportWizard(models.TransientModel):
    _name = 'artec.tank.production.report.wizard'
    
    date = fields.Date(
        string='Date',
        required=True,
    )
    
    def action_report_tank_production(self, data=None):
        productions = self.env['artec.production'].search([
            ('date', '=', self.date),
        ])
        
        if not productions:
            raise ValidationError("There is no productions in this date.")
        
        grouped_productions = {}
        total_produced_volume = 0.0
        for production in productions:
            tank_id = production.tank_id.id
            
            if tank_id not in grouped_productions:
                grouped_productions[tank_id] = {
                    'tank_name': production.tank_id.name,
                    'produced_volume': 0.0
                }
            
            grouped_productions[tank_id]['produced_volume'] += production.produced_volume or 0.0
            total_produced_volume += production.produced_volume or 0.0
            
        # Round volumes to 2 decimal places
        for tank_id in grouped_productions:
            grouped_productions[tank_id]['produced_volume'] = round(grouped_productions[tank_id]['produced_volume'], 2)
        
        total_produced_volume = round(total_produced_volume, 2)
        data = {
            'date': self.date,
            'productions': grouped_productions,
            'total_produced_volume': total_produced_volume,
        }
        
        return self.env.ref('artec_collect.artec_action_report_tank_production').report_action(None, data=data)