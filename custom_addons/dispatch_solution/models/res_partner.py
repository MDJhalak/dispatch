from odoo import api, fields, models


class PartnerExt(models.Model):
    _inherit = "res.partner"

    @api.multi
    @api.depends("project_ids")
    def _project_count(self):
        self.ensure_one()
        self.project_count = len(self.project_ids)

    @api.multi
    def action_view_projects(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        self.ensure_one()
        action = self.env.ref('project.open_view_project_all')
        result = action.read()[0]

        # override the context to get rid of the default filtering on operation type
        result['context'] = {}
        project_ids = self.mapped('project_ids')
        result['context'].update({
            'partner_id': self.id,
        })
        if not project_ids or len(project_ids) >= 1:
            result['domain'] = "[('id','in',%s)]" % (project_ids.ids)
        return result

    project_count = fields.Integer(compute="_project_count")
    project_ids = fields.One2many(comodel_name="project.project", inverse_name="partner_id", string='Projects')

