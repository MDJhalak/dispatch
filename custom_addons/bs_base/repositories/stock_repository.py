# -*- coding: utf-8 -*-

from odoo import fields, models, api, SUPERUSER_ID


class StockRepository(models.TransientModel):
    _name = "bs.stock.repository"

    @api.multi
    def get_user_warehouse_parent_location(self, user):
        if user:
            # also known as "View Location"
            pos_warehouse_location = user.pos_configure_id.sudo().stock_location_id
            return pos_warehouse_location if pos_warehouse_location.usage == "view" else pos_warehouse_location.location_id
        return None

    @api.multi
    def get_user_warehouse_stock_location(self, user):
        if user:
            view_location = self.get_user_warehouse_parent_location(user)
            return self.env['stock.location'].sudo().search(['&', '&',
                                                            ('active', '=', True),
                                                            ('location_id', '=', view_location.id),
                                                            ('name', '=', 'Stock')], limit=1)
        return None

    @api.multi
    def get_user_warehouse_scrap_location(self, user):
        if user:
            view_location = self.get_user_warehouse_parent_location(user)
            return self.env['stock.location'].sudo().search(['&', '&',
                                                            ('active', '=', True),
                                                            ('location_id', '=', view_location.id),
                                                            ('name', '=', 'Scrap')], limit=1)
        return None

    @api.multi
    def get_company_transit_location(self, company):
        if company:
            return self.env['stock.location'].sudo().search(['&', '&',
                                                            ('active', '=', True),
                                                            ('usage', '=', 'transit'),
                                                            ('company_id', '=', company.id)], limit=1)
        return None

    @api.multi
    def get_company_production_location(self):
        return self.env['stock.location'].sudo().search(['&', '&',
                                                        ('active', '=', True),
                                                        ('usage', '=', 'production'),
                                                        ('location_id', '=', self._get_virtual_location_parent().id)], limit=1)

    @api.multi
    def get_company_vendor_location(self):
        return self.env['stock.location'].sudo().search(['&', '&',
                                                        ('active', '=', True),
                                                        ('usage', '=', 'supplier'),
                                                        ('location_id', '=', self._get_partner_location_parent().id)], limit=1)

    @api.multi
    def get_user_warehouse(self, user):
        if user:
            stock_location = self.get_user_warehouse_stock_location(user)
            view_location = self.get_user_warehouse_parent_location(user)
            return self.env['stock.warehouse'].sudo().search(['&', '&',
                                                             ('active', '=', True),
                                                             ('view_location_id.id', '=', view_location.id),
                                                             ('lot_stock_id.id', '=', stock_location.id)], limit=1)
        return None

    @api.multi
    def get_warehouse_of_location(self, location):
        if location.usage in ['view', 'internal'] and location.location_id:
            parent_location = location if location.usage == 'view' else location.location_id
            return self.env['stock.warehouse'].sudo().search(['&',
                                                              ('active', '=', True),
                                                              ('view_location_id.id', '=', parent_location.id)], limit=1)
        return None

    def _get_virtual_location_parent(self):
        return self.env['stock.location'].sudo().search(['&', '&',
                                                        ('active', '=', True),
                                                        ('usage', '=', 'view'),
                                                        ('name', '=', 'Virtual Locations')], limit=1)

    def _get_partner_location_parent(self):
        return self.env['stock.location'].sudo().search(['&', '&',
                                                        ('active', '=', True),
                                                        ('usage', '=', 'view'),
                                                        ('name', '=', 'Partner Locations')], limit=1)
