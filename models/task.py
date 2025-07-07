from odoo import models, fields, api, _
from datetime import date
from datetime import datetime as dt
from odoo.exceptions import ValidationError



class ToDoTask(models.Model):
    _name = 'todo.task'


    name = fields.Char(string="Task Name", placeholder="e.g.Create new module", required=1)
    reference = fields.Char(string="Reference", default="New", required=True, copy=False, readonly=True)
    project_id = fields.Many2one('todo.project', string="Project")
    partner_id = fields.Many2one(
        'res.partner',
        string="Assign To",
        domain=[('is_company', '=', False)],
        required=True
    )
    description = fields.Text(string="Description")
    due_date = fields.Date(string="Due Date", required=1)
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

    start_time = fields.Datetime(string="Starting time")
    finish_time = fields.Datetime(string="Finishing time")
    active_duration = fields.Char(string="Duration", compute="_compute_active_duration", default="00:00:00")

    git_push = fields.Boolean(string="Push To Git")

    cancel_reason = fields.Text(string="Reason")

    track_progress = fields.Boolean(string="Show Progress Details", default=False, help="Enable this option only if you already know how many items the task includes, so progress tracking fields can be shown.")
    hint = fields.Text(default="Enable this option only if you already know how many items the task includes, so progress tracking fields can be shown.")
    total_units = fields.Float(string="Total Units", help="e.g., Total tutorial videos to watch")
    completed_units = fields.Float(string="Completed Units", help="e.g., Number of videos watched")
    progress = fields.Float(string="Progress", compute="_compute_progress", store=True)

    estimated_time = fields.Char(string="Estimated", compute="_compute_estimated_time")



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
            rec.start_time = fields.Datetime.now()
            rec.history_line_ids = [(0, 0, {
                'action': 'start',
                'date_time': fields.Datetime.now(),
            })]
    
    def action_paused(self):
        for rec in self:
            rec.state = 'paused'
            rec.history_line_ids = [(0, 0, {
                'action': 'pause',
                'date_time': fields.Datetime.now(),
            })]
    
    def action_resume(self):
        for rec in self:
            rec.state = 'inprogress'
            rec.history_line_ids = [(0, 0, {
                'action': 'resume',
                'date_time': fields.Datetime.now(),
            })]
    
    def action_completed(self):
        for rec in self:
            rec.deadline_date = ''
            rec.state = 'completed'
            rec.finish_time = fields.Datetime.now()
            rec.history_line_ids = [(0, 0, {
                'action': 'complete',
                'date_time': fields.Datetime.now(),
            })]

    def action_cancelled(self):
        for rec in self:
            return{
                'type': 'ir.actions.act_window',
                'name': 'Adddd Reason',
                'res_model': 'add.reason',
                'view_mode': 'form',
                'target':'new',
                'context': {
                    'default_task_id': rec.id
                }
            }
    
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
            else:
                rec.deadline_date = "No due date"

    def _compute_start_time(self):
        for rec in self:
            rec.start_time = fields.Datetime.now()
    
    def _finish_time(self):
        for rec in self:
            rec.finish_time = fields.Datetime.now()
    
    def _compute_active_duration(self):
        for rec in self:
            total_seconds = 0
            lines = rec.history_line_ids.sorted('date_time')
            start_time = None

            for line in lines:
                if line.action in ('start', 'resume'):
                    start_time = line.date_time
                elif line.action in ('pause', 'complete') and start_time and line.date_time:
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

    @api.depends('total_units', 'completed_units')
    def _compute_progress(self):
        for rec in self:
            if rec.total_units > 0:
                rec.progress = (rec.completed_units / rec.total_units) * 100
            else:
                rec.progress = 0
   
    def action_increase_completed_units(self):
        for rec in self:
            rec.completed_units += 1

            if rec.completed_units > rec.total_units:
                rec.completed_units = rec.total_units

            if rec.completed_units == rec.total_units:
                return{
                    'type': 'ir.actions.act_window',
                    'name': 'Complete Task ?',
                    'res_model': 'todo.confirm.complete',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_task_id': rec.id,
                        'default_message': f"You completed all the units ({rec.completed_units}/{rec.total_units}). Do you want to mark this task as completed ?"
                    }
                }
    
    def action_decrease_completed_units(self):
        for rec in self:
            rec.completed_units -= 1
    
    def _compute_estimated_time(self):
        for rec in self:
            if rec.progress != 0:
                duration_str = rec.active_duration  # example: "02:01:03"
                parts = duration_str.split(':')      # → ['02', '01', '03']
                hours = int(parts[0])                # → 2
                minutes = int(parts[1])              # → 1
                duration_minutes = hours * 60 + minutes # → 121

                incomplete_progress = 100 - rec.progress

                estimated_minutes = (incomplete_progress * duration_minutes) / rec.progress
                
                h = int(estimated_minutes // 60)
                m = int(estimated_minutes % 60)

            rec.estimated_time = f"(Estimated: {h:02d}:{m:02d})"
    
    @api.constrains('completed_units')
    def check_completed_units(self):
        for rec in self:
            if rec.completed_units < 0:
                raise ValidationError(_("Completed Units can't be negative !"))
            if rec.completed_units > rec.total_units:
                raise ValidationError(_(f"Completed Units can't exceed Total Units ({rec.total_units}) !"))
    
    @api.constrains('total_units')
    def check_total_units(self):
        for rec in self:
            if rec.total_units < 0:
                raise ValidationError(_("Total Units can't be negative !"))










class HistoryLines(models.Model):
    _name = 'history.lines'


    task_id = fields.Many2one('todo.task')
    action = fields.Selection([
        ('start', 'Start'),
        ('pause', 'Pause'),
        ('resume', 'Resume'),
        ('complete', 'Complete'),
        ('cancel', 'Cancel')
    ])
    
    date_time = fields.Datetime(string="Time")