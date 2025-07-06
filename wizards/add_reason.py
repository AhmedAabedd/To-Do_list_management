from odoo import models, fields, api, _




class AddReason(models.TransientModel):
    _name = 'add.reason'


    task_id = fields.Many2one('todo.task')
    reason_description = fields.Text(string="Reason", required=1)




    def action_confirm_add_reason(self):
        for rec in self:
            if rec.reason_description:
                rec.task_id.cancel_reason = rec.reason_description

                rec.task_id.state = 'cancelled'
                rec.task_id.history_line_ids = [(0, 0, {
                    'action': 'cancel',
                    'date_time': fields.Datetime.now(),
                })]
                return {'type': 'ir.actions.act_window_close'}#to close the wizard when confirming