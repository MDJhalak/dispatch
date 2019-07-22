# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ConcretePlacementLog(models.Model):
    _name = 'concrete.placement.log'

    task_id = fields.Many2one(comodel_name='project.task', name='Project Task')
    field_id = fields.Many2one(comodel_name='daily.field.report', name='Daily Field')
    load_no = fields.Char('Load no.')
    truck_no = fields.Char('Truck No.')
    cubic_yards = fields.Char('Cubic Yards')
    cum_yards = fields.Char('Cum. Yards')
    batch_time = fields.Float('Batch Time')
    start_time = fields.Float('Start Time')
    sample_time = fields.Float('Sample Time')
    finish_time = fields.Float('Finish Time')
    total_time = fields.Float('Total Time')
    spec_location = fields.Char('Specific Location')


class InspectionChecklist(models.Model):
    _name = 'inspection.checklist'

    name = fields.Char('Checklist Name')
    items = fields.One2many('checklist.items', 'inspection_id', 'Checklist Tasks')


class InspectionChecklistItems(models.Model):
    _name = 'checklist.items'

    name = fields.Char('Tasks')
    inspection_id = fields.Many2one('inspection.checklist', 'Inspection Checklist')


class InspectionChecklistTasks(models.Model):
    _name = 'checklist.tasks'

    checklist_id = fields.Many2one('inspection.checklist', 'Checklist')
    checklist_items = fields.Many2one('checklist.items', 'Inspection Task')
    is_done = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('na', 'N/A')], 'In Conformance')
    comments = fields.Text('Comments')
    task_id = fields.Many2one('project.task', 'Task')
    project_id = fields.Many2one('project.project', 'Project')
    field_id = fields.Many2one('daily.field.report', 'Daily Field Report')


class TestResultSummary(models.Model):
    _name = 'test.result.summary'

    name = fields.Char('Name')
    supplier = fields.Many2one('res.partner', 'Supplier')
    mix_id = fields.Char('Mix ID')
    req_strength = fields.Char('Required Strength')
    slump = fields.Char('Slump')
    unit_weight = fields.Char('Unit Weight')
    air_content = fields.Char('Air Content')
    test_ids = fields.One2many('child.test.items', 'tr_summary_id', 'Tests')
    field_id = fields.Many2one('daily.field.report', 'Daily Field Report')


class ChildTestItems(models.Model):
    _name = 'child.test.items'

    set = fields.Char('Set #')
    load = fields.Char('Load #')
    mix_temp = fields.Char('Mix Temp.')
    slump = fields.Char('Slump')
    unit_weight = fields.Char('Unit Weight')
    air_content = fields.Char('Air Content')
    tag = fields.Char('Tag #')
    samples = fields.Char('# of Samples')
    comments = fields.Text('Comments')
    tr_summary_id = fields.Many2one('test.result.summary', 'Summary')


class HrTaskTeam(models.Model):
    _name = 'hr.task.team'
    emp_skill = fields.Many2one('hr.employee.category', 'Employee Skill')
    employee = fields.Many2one('hr.employee', 'Employee')
    task_id = fields.Many2one('project.task', 'Task')


class DailyFieldReport(models.Model):
    _name = 'daily.field.report'

    name = fields.Char('Name')
    date = fields.Date('Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ], string='Status', help='State', default='draft')
    type = fields.Selection([('concrete', 'Concrete'),
                             ('aggregate', 'Aggregate'),
                             ('soil', 'Soil'),
                             ('asphalt', 'Asphalt'),
                             ('masonary', 'Masonary'),
                             ('fire_resistive', 'Fire Resistive')], 'Type')
    outcome = fields.Selection([('conformance', 'Conformance'),
                                ('non-conformance', 'With Non-conformance'),
                                ('wip', 'Work in Progress')],
                               help=" * Conformance: To the best of my knowledge, work area(s) inspected was/were in accordance with the approved plans, specifications\n"
                                    "                and applicable workmanship provisions of the New York City Building Code/New York State Building Code, except as noted below.\n"
                                    " * With Non-conformance: The work area(s) inspected was/were not in conformance (See separate Non Conformance Report). Re-Inspection Is Required.\n"
                                    " * Work in Progress: The work area(s) inspected was/were not completed at the time of inspection. Re-Inspection is required.")
    task_list = fields.Text('Re-Inspection Note')
    concr_plc_log_ids = fields.One2many('concrete.placement.log', 'field_id', 'Concrete Placement Log')

    inspection_checklists = fields.Many2many('inspection.checklist', 'inspection_checklist_rels', 'task_id',
                                             'inspection_id', string='Checklist')
    checklist_tasks = fields.One2many('checklist.tasks', 'field_id', 'Inspection Tasks')
    test_summary = fields.One2many('test.result.summary', 'field_id', 'Test Summary')
    task_id = fields.Many2one('project.task', 'Task')

    @api.onchange('inspection_checklists')
    def inspection_checklist_change(self):
        if self.checklist_tasks:
            self.checklist_tasks = False
        value = {}
        check_ids = []
        for i in self.inspection_checklists:
            for j in i.items:
                check_ids.append((0, 0, {'checklist_items': j.id,
                                         'checklist_id': i.id,
                                         # 'project_id': self.project_id.id,
                                         }))
        value['checklist_tasks'] = check_ids
        return {'value': value}

    @api.multi
    def send_for_approval(self):
        for record in self:
            record.write({'state': 'pending'})
        return True

    @api.multi
    def approve_report(self):
        for record in self:
            record.write({'state': 'approved'})
        return True

    @api.multi
    def cancel_report(self):
        for record in self:
            record.write({'state': 'cancelled'})
        return True

# class dispatch_solution(models.Model):
#     _name = 'dispatch_solution.dispatch_solution'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
