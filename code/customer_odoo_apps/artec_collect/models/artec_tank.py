from odoo import api, fields, models
from datetime import datetime

class ArtecTank(models.Model):
    _name = "artec.tank"
    
    name = fields.Char(
        string='Name',
    )
    
    width = fields.Float(
        string='Width [m]',
    )
    
    length = fields.Float(
        string='Length [m]',
    )
    
    product_id = fields.Many2one(
        comodel_name='artec.product',
        string='Product'
    )
    
    strapping_ids = fields.One2many(
        comodel_name="artec.strapping",
        inverse_name="tank_id",
        string="Strapping",
    )    
    
    expedition_ids = fields.One2many(
        comodel_name="artec.expedition",
        inverse_name="tank_id",
        string="Expedition",
    )    
    
    production_ids = fields.One2many(
        comodel_name="artec.production",
        inverse_name="tank_id",
        string="Production",
    )
    
    strapping_count = fields.Integer(
        string='Strapping Count',
        compute='_compute_strapping_count',
        store=False,
    )
    
    expedition_count = fields.Integer(
        string='Expedition Count',
        compute='_compute_expedition_count',
        store=False,
    )       
    
    production_count = fields.Integer(
        string='Production Count',
        compute='_compute_production_count',
        store=False,
    )
    
    @api.depends('strapping_ids')
    def _compute_strapping_count(self):
        for record in self:
            record.strapping_count = len(record.strapping_ids)    
            
    @api.depends('expedition_ids')
    def _compute_expedition_count(self):
        for record in self:
            record.expedition_count = len(record.expedition_ids)            
            
    @api.depends('production_ids')
    def _compute_production_count(self):
        for record in self:
            record.production_count = len(record.production_ids)
    
    def action_get_strapping_records(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Strappings',
            'view_mode': 'list,form',
            'res_model': 'artec.strapping',
            'domain': [('tank_id', '=', self.id)],
            'context': {
                'default_tank_id': self.id,
            },
        }    
        
    def action_get_expedition_records(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expedition',
            'view_mode': 'list,form',
            'res_model': 'artec.expedition',
            'domain': [('tank_id', '=', self.id)],
            'context': {
                'default_tank_id': self.id,
            },
        }
        
    def action_get_production_records(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Production',
            'view_mode': 'list,form',
            'res_model': 'artec.production',
            'domain': [('tank_id', '=', self.id)],
            'context': {
                'default_tank_id': self.id,
            },
        }
