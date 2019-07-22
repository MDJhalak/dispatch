# -*- coding: utf-8 -*-
from odoo import http

# class DispatchSolution(http.Controller):
#     @http.route('/dispatch_solution/dispatch_solution/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dispatch_solution/dispatch_solution/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dispatch_solution.listing', {
#             'root': '/dispatch_solution/dispatch_solution',
#             'objects': http.request.env['dispatch_solution.dispatch_solution'].search([]),
#         })

#     @http.route('/dispatch_solution/dispatch_solution/objects/<model("dispatch_solution.dispatch_solution"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dispatch_solution.object', {
#             'object': obj
#         })