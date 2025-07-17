from odoo import models, fields, api, _



class AddGitCommit(models.TransientModel):
    _name = 'add.git.commit'


    task_id = fields.Many2one('todo.task', string="Task")
    name = fields.Char(string="Commit Name", required=True)
    date_time = fields.Datetime(string="On")
    duration = fields.Char(string="Duration")

    def action_add_git_commit(self):
        for rec in self:
            if self.name:
                rec.task_id.history_line_ids = [(0, 0, {
                        'action': 'commit',
                        'date_time': rec.date_time,
                        'duration': rec.duration,
                        'name': rec.name
                    })]