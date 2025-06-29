from odoo import models, fields, api, _



class ToDoProject(models.Model):
    _name = 'todo.project'


    name = fields.Char(string="Project Name", required='1')
    task_ids = fields.Many2one(
        'todo.task',
        'project_id',
        domain="[('project_id', '=', id)]"
    )