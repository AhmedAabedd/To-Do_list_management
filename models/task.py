from odoo import models, fields, api, _
from datetime import date



class ToDoTask(models.Model):
    _name = 'todo.task'


    name = fields.Char(string="Task Name", required=1)
    assign_to = fields.Many2one('res.partner', string="Assign To", required=True)
    description = fields.Text(string="Description")
    due_date = fields.Date(string="Due Date")
    state = fields.Selection([
        ('new', 'New'),
        ('inprogress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'cancelled')
    ], default="new")

    remaining_state = fields.Selection([
        ('normal', 'Normal'),
        ('warning', 'Warning'),
        ('danger', 'Danger')
    ], default="normal", compute="_compute_remaining_state")

    deadline_date = fields.Char(string="Deadline", compute="_compute_deadline_date")


    def action_in_progress(self):
        for rec in self:
            rec.state = 'inprogress'
    
    def action_paused(self):
        for rec in self:
            rec.state = 'paused'
    
    def action_completed(self):
        for rec in self:
            rec.deadline_date = ''
            rec.state = 'completed'

    def action_cancelled(self):
        for rec in self:
            rec.state = 'cancelled'
    
    def _compute_remaining_state(self):
        today = fields.Date.today()
        for rec in self:
            if rec.due_date:
                delta = (rec.due_date - today).days
                if delta == 0 or delta == 1 :
                    rec.remaining_state = 'warning'
                elif delta < 0 :
                    rec.remaining_state = 'danger'
                else:
                    rec.remaining_state = 'normal'
            else:
                rec.remaining_state = 'normal'

    def _compute_deadline_date(self):
        today = fields.Date.today()
        print('/////////////////// TODAY IS ',today,' ////////////////////')
        for rec in self:
            if rec.due_date:
                delta = (rec.due_date - today).days
                if delta == 0:
                    rec.deadline_date = "Today"
                elif delta == 1:
                    rec.deadline_date = "Tomorrow"
                elif delta > 1:
                    rec.deadline_date = f"In {delta} days"
                elif delta == -1:
                    rec.deadline_date = "Yesterday"
                else:
                    rec.deadline_date = f"{abs(delta)} days ago"