from odoo import api, fields, models
class ArtecTank(models.Model):
    _name = "artec.tank"
    
    name = fields.Char(
        string='Name',
        required=True
    )
    
    product_id = fields.Many2one(
        comodel_name='artec.product',
        string='Product',
        required=True
    )
    
    color = fields.Integer(
        related='product_id.color'
    )
    
    height = fields.Float(
        string='Height [m]',
    )
    
    width = fields.Float(
        string='Width [m]',
    )
    
    current_volume = fields.Float(
        compute="_compute_current_volume",
        string= "Current volume [m³]",
        store=True,
        digits=(16, 2)
    )
    
    capacity = fields.Float(
        string="Capacity [m³]"
    )
    
    percentage = fields.Float(
        string="Percentage %",
        compute="_compute_percentage",
        store=True
    )
    
    strapping_ids = fields.One2many(
        comodel_name="artec.strapping",
        inverse_name="tank_id",
        string="Strapping",
    )    
    
    gauging_ids = fields.One2many(
        comodel_name="artec.gauging",
        inverse_name="tank_id",
        string="Gauging",
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
    
    gauging_count = fields.Integer(
        string='Gauging Count',
        compute='_compute_gauging_count',
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
    
    @api.depends('gauging_ids')
    def _compute_current_volume(self):        
        for record in self:
            gaugings = self.env['artec.gauging'].search([
                ('tank_id', '=', record.id)
            ])
            
            if not gaugings:
                record.current_volume = 0
                continue
            
            last_gauging = gaugings.sorted(key=lambda g: g.datetime, reverse=True)[0]
            record.current_volume = last_gauging.volume
    
    @api.depends('capacity', 'current_volume')
    def _compute_percentage(self):
        for record in self:
            if record.capacity:
                record.percentage = (record.current_volume * 100) / record.capacity
            else:
                record.percentage = 0
            
    @api.depends('strapping_ids')
    def _compute_strapping_count(self):
        for record in self:
            record.strapping_count = len(record.strapping_ids)      
            
    @api.depends('gauging_ids')
    def _compute_gauging_count(self):
        for record in self:
            record.gauging_count = len(record.gauging_ids)    
            
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
        view_mode = 'form' if self.strapping_count == 1 else 'list,form'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Strappings',
            'view_mode': view_mode,
            'res_model': 'artec.strapping',
            'domain': [('tank_id', '=', self.id)],
            'context': {
                'default_tank_id': self.id,
            },
        }      
        
    def action_get_gauging_records(self):
        self.ensure_one()
        view_mode = 'form' if self.gauging_count == 1 else 'list,form'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gaugings',
            'view_mode': view_mode,
            'res_model': 'artec.gauging',
            'domain': [('tank_id', '=', self.id)],
            'context': {
                'default_tank_id': self.id,
            },
        }    
        
    def action_get_expedition_records(self):
        self.ensure_one()
        view_mode = 'form' if self.expedition_count == 1 else 'list,form'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expedition',
            'view_mode': view_mode,
            'res_model': 'artec.expedition',
            'domain': [('tank_id', '=', self.id)],
            'context': {
                'default_tank_id': self.id,
            },
        }
        
    def action_get_production_records(self):
        self.ensure_one()
        view_mode = 'form' if self.production_count == 1 else 'list,form'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Production',
            'view_mode': view_mode,
            'res_model': 'artec.production',
            'domain': [('tank_id', '=', self.id)],
            'context': {
                'default_tank_id': self.id,
            },
        }
