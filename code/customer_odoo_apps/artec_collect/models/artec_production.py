from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ArtecProduction(models.Model):
    _name = "artec.production"
    
    name = fields.Char(
        string='Name',
        compute = '_compute_name',
        store=True
    )
    
    tank_id = fields.Many2one(
        comodel_name='artec.tank',
        string='Tank',
        required=True
    )
    
    date = fields.Date(
        string='Date',
        required=True
    )
    
    volume = fields.Float(
        string='Production volume',
        compute='_compute_volume',
        store=True
    )
    
    @api.depends('date','tank_id')
    def _compute_name(self):
        for record in self:
            if not record.date or not record.tank_id:
                record.name = False
                continue
            record.name = record.tank_id.name + '-' + str(record.date)
    
    @api.depends('tank_id', 'date')
    def _compute_volume(self):        
        for record in self:
            if not record.tank_id or not record.date:
                continue
            
            gaugings = self.env['artec.gauging'].search([
                ('tank_id', '=', record.tank_id.id)
            ])
            
            if not gaugings:
                raise ValidationError("There is no gaugings for this tank")
            
            previous_gaugings = gaugings.filtered(lambda g: g.date < fields.Datetime.to_datetime(record.date))
            next_gaugings = gaugings.filtered(lambda g: g.date > fields.Datetime.to_datetime(record.date))
            
            if not previous_gaugings or not next_gaugings:
                raise ValidationError("There is no previous or next gaugings for this date")
            
            last_previous_gauging = previous_gaugings.sorted(key=lambda g: g.date, reverse=True)[0]
            first_next_gauging = next_gaugings.sorted(key=lambda g: g.date)[0]
            
            expeditions = self.env['artec.expedition'].search([
                ('tank_id', '=', record.tank_id.id),
                ('start_date', '>', fields.Datetime.to_datetime(last_previous_gauging.date)),
                ('start_date', '<', fields.Datetime.to_datetime(first_next_gauging.date)),
                ('end_date', '>', fields.Datetime.to_datetime(last_previous_gauging.date)),
                ('end_date', '<', fields.Datetime.to_datetime(first_next_gauging.date)),
            ])
            
            expedited_volume = 0
            
            if expeditions:
                for expedition in expeditions:
                    expedited_volume += expedition.expedited_volume
            
            record.volume = first_next_gauging.volume - last_previous_gauging.volume + expedited_volume