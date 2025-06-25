from odoo import api, models

class ArtecTankProductionReport(models.AbstractModel):
    _name = 'report.artec_collect.artec_tank_production_report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        date = data.get('date')
        productions = data.get('productions')
        total_produced_volume = data.get('total_produced_volume')
        
        return {
            'date': date,
            'productions': productions,
            'total_produced_volume': total_produced_volume
        }