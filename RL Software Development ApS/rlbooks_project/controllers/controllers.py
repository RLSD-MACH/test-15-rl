# -*- coding: utf-8 -*-
from odoo import http

class Project(http.Controller):
    @http.route('/rlbooks.project/rlbooks.project/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/rlbooks.project/rlbooks.project/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('rlbooks.project.listing', {
            'root': '/rlbooks.project/rlbooks.project',
            'objects': http.request.env['rlbooks.project'].search([]),
        })

    @http.route('/rlbooks.project/rlbooks.project/objects/<model("rlbooks.project"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('rlbooks.project.object', {
            'object': obj
        })