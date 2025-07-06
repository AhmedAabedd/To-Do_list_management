from odoo import models, fields, api, _




class TodoConfirmComplete(models.TransientModel):
    _name = 'todo.confirm.complete'


    task_id = fields.Many2one('todo.task')
    message = fields.Text(string="Message")

    def action_set_completed(self):
        self.task_id.action_completed()
        return {'type': 'ir.actions.act_window_close'}#to close the wizard when confirming