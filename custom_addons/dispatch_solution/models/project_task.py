# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectTaskExt(models.Model):
    _inherit = 'project.task'

    type = fields.Selection([('concrete', 'Concrete'),
                             ('aggregate', 'Aggregate'),
                             ('soil', 'Soil'),
                             ('asphalt', 'Asphalt'),
                             ('masonary', 'Masonary'),
                             ('fire_resistive', 'Fire Resistive')], 'Type')
    concr_plc_log_ids = fields.One2many('concrete.placement.log', 'task_id', 'Concrete Placement Log')
    inspection_checklists = fields.Many2many('inspection.checklist', 'inspection_checklist_rel', 'task_id',
                                            'inspection_id', string='Checklist')
    checklist_tasks = fields.One2many('checklist.tasks', 'task_id', 'Inspection Tasks')
    daily_field_report = fields.One2many('daily.field.report', 'task_id', 'Field Report')
    employee_team = fields.One2many('hr.task.team', 'task_id', 'Team')

    @api.onchange('inspection_checklists')
    def inspection_checklist_change(self):
        if self.checklist_tasks:
            self.checklist_tasks = False
        value={}
        check_ids = []
        for i in self.inspection_checklists:
            for j in i.items:
                check_ids.append((0, 0, {'checklist_items': j.id,
                                         'checklist_id': i.id,
                                         'project_id': self.project_id.id,}))
        value['checklist_tasks'] = check_ids
        return{'value':value}
