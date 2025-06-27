from odoo import models, fields, api, _
from datetime import date
from datetime import datetime as dt



class ToDoTask(models.Model):
    _name = 'todo.task'


    name = fields.Char(string="Task Name", required=1)
    reference = fields.Char(string="Reference", default="New", required=True, copy=False, readonly=True)
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

    history_line_ids = fields.One2many('history.lines', 'task_id')

    total_duration = fields.Float(string="Active Hours", compute="_compute_total_duration")
    formatted_duration = fields.Char(string="Active Duration", compute="_compute_total_duration")



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
    
    @api.depends('history_line_ids')
    def _compute_total_duration(self):
        for rec in self:
            total_seconds = 0
            lines = rec.history_line_ids.sorted('date_time')
            start_time = None

            for line in lines:
                if line.state in ('start', 'resume'):
                    start_time = line.date_time
                elif line.state in ('paused', 'completed') and start_time:
                    if line.date_time and start_time:
                        duration = (line.date_time - start_time).total_seconds()
                        total_seconds += duration
                        start_time = None

            rec.total_duration = round(total_seconds / 3600, 2)

            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            rec.formatted_duration = f"{hours:02d}:{minutes:02d}"

    

   










class HistoryLines(models.Model):
    _name = 'history.lines'


    task_id = fields.Many2one('todo.task')
    state = fields.Selection([
        ('start', 'Start'),
        ('paused', 'Paused'),
        ('resume', 'Resume'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refresh', 'Refresh'),
    ], default="start")
    
    date_time = fields.Datetime(string="Time")