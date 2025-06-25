from odoo import api, models

class ArtecTankExpeditionReport(models.AbstractModel):
    _name = 'report.artec_collect.artec_tank_expedition_report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        date = data.get('date')
        expeditions = data.get('expeditions')
        total_expedited_volume = data.get('total_expedited_volume')
        
        return {
            'date': date,
            'expeditions': expeditions,
            'total_expedited_volume': total_expedited_volume
        }