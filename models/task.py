from odoo import models, fields, api, _
from datetime import date
from datetime import datetime as dt



class ToDoTask(models.Model):
    _name = 'todo.task'


    name = fields.Char(string="Task Name", placeholder="e.g.Create new module", required=1)
    reference = fields.Char(string="Reference", default="New", required=True, copy=False, readonly=True)
    project_id = fields.Many2one('todo.project', string="Project")
    partner_id = fields.Many2one('res.partner', string="Assign To", required=True)
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

    history_line_ids = fields.One2many('history.lines', 'task_id')

    active_duration = fields.Char(string="Duration", compute="_compute_active_duration", default="00:00:00")

    starti




    #Generate auto reference
    @api.model
    def create(self, vals):
        res = super(ToDoTask, self).create(vals)
        if res.reference == 'New':
            res.reference = self.env['ir.sequence'].next_by_code('todo.task.sequence')
        return res

    def action_in_progress(self):
        for rec in self:
            rec.state = 'inprogress'
            rec.history_line_ids = [(0, 0, {
                'state': 'start',
                'date_time': fields.Datetime.now(),
            })]
    
    def action_paused(self):
        for rec in self:
            rec.state = 'paused'
            rec.history_line_ids = [(0, 0, {
                'state': 'paused',
                'date_time': fields.Datetime.now(),
            })]
    
    def action_resume(self):
        for rec in self:
            rec.state = 'inprogress'
            rec.history_line_ids = [(0, 0, {
                'state': 'resume',
                'date_time': fields.Datetime.now(),
            })]
    
    def action_completed(self):
        for rec in self:
            rec.deadline_date = ''
            rec.state = 'completed'
            rec.history_line_ids = [(0, 0, {
                'state': 'completed',
                'date_time': fields.Datetime.now(),
            })]

    def action_cancelled(self):
        for rec in self:
            rec.state = 'cancelled'
            rec.history_line_ids = [(0, 0, {
                'state': 'cancelled',
                'date_time': fields.Datetime.now(),
            })]
    
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
    
    def _compute_active_duration(self):
        for rec in self:
            total_seconds = 0
            lines = rec.history_line_ids.sorted('date_time')
            start_time = None

            for line in lines:
                if line.state in ('start', 'resume'):
                    start_time = line.date_time
                elif line.state in ('paused', 'completed') and start_time and line.date_time:
                    duration = (line.date_time - start_time).total_seconds()
                    total_seconds += max(0, duration)
                    start_time = None

            # ✅ Handle "in progress" time still running
            if rec.state == 'inprogress' and start_time:
                now = fields.Datetime.now()
                duration = (now - start_time).total_seconds()
                total_seconds += max(0, duration)

            # Format the result
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            rec.active_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def action_refresh_active_duration(self):
        for rec in self:
            rec._compute_active_duration()
   










class HistoryLines(models.Model):
    _name = 'history.lines'


    task_id = fields.Many2one('todo.task')
    state = fields.Selection([
        ('start', 'Start'),
        ('paused', 'Paused'),
        ('resume', 'Resume'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default="start")
    
    date_time = fields.Datetime(string="Time")