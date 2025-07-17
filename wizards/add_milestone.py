from odoo import models, fields, api, _
from datetime import date
from datetime import datetime as dt



class AddMilestone(models.TransientModel):
    _name = 'add.milestone'


    task_id = fields.Many2one('todo.task', string="Task")
    date_time = fields.Datetime(string="On")
    duration = fields.Char(string="Duration")
    name = fields.Char(string="Description", required=True)



    def action_add_milestone(self):
        for rec in self:
            if self.name:
                rec.task_id.history_line_ids = [(0, 0, {
                    'action': 'milestone',
                    'date_time': rec.date_time,
                    'duration': rec.duration,
                    'name': rec.name
                })]
                return {'type': 'ir.actions.act_window_close'}#to close the wizard when confirming