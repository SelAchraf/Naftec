from odoo import fields, models
from odoo.exceptions import ValidationError
from datetime import timedelta

class ArtecTankExpeditionReportWizard(models.TransientModel):
    _name = 'artec.tank.expedition.report.wizard'
    
    date = fields.Date(
        string='Date',
        required=True,
    )
    
    def action_report_tank_expedition(self, data=None):
        start_of_day = fields.Datetime.to_datetime(self.date)
        end_of_day = start_of_day + timedelta(days=1)
        
        expeditions = self.env['artec.expedition'].search([
            ('start_datetime', '>=', start_of_day),
            ('start_datetime', '<', end_of_day)
        ])
        
        if not expeditions:
            raise ValidationError("There is no expeditions in this date.")
        
        grouped_expeditions = {}
        total_expedited_volume = 0.0
        for expedition in expeditions:
            tank_id = expedition.tank_id.id
            
            if tank_id not in grouped_expeditions:
                grouped_expeditions[tank_id] = {
                    'tank_name': expedition.tank_id.name,
                    'expedited_volume': 0.0
                }
            
            grouped_expeditions[tank_id]['expedited_volume'] += expedition.expedited_volume or 0.0
            total_expedited_volume += expedition.expedited_volume or 0.0
            
        # Round volumes to 2 decimal places
        for tank_id in grouped_expeditions:
            grouped_expeditions[tank_id]['expedited_volume'] = round(grouped_expeditions[tank_id]['expedited_volume'], 2)
        
        total_expedited_volume = round(total_expedited_volume, 2)
        data = {
            'date': self.date,
            'expeditions': grouped_expeditions,
            'total_expedited_volume': total_expedited_volume,
        }
        
        return self.env.ref('artec_collect.artec_action_report_tank_expedition').report_action(None, data=data)