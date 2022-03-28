# -*- coding: utf-8 -*-

# import logging
# import werkzeug

from odoo import http, _
# from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
# from odoo.addons.base_setup.controllers.main import BaseSetup
from odoo.exceptions import UserError
from odoo.http import request

# _logger = logging.getLogger(__name__)

class AuthSignupHome(Home):

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""

        res = super(AuthSignupHome, self).get_auth_signup_config() 

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        res.update({
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat')
        })

        return res
        
    def _prepare_signup_values(self, qcontext):

        values = { key: qcontext.get(key) for key in ('login', 'name', 'password', 'company_name', 'vat', 'street', 'street2', 'city', 'state_id', 'country_id', 'phone') }
        
        if 'country_id' in values:

            if values['country_id'] == '':
                
                values.pop('country_id', False)
                values.pop('state_id', False)

            else:
                
                values['country_id'] = int(values['country_id'])

        if not values['state_id']:

            values.pop('state_id', False)

        values['zip'] = qcontext.get('zipcode')

        # raise UserError(str(values))

        if not values:
            raise UserError(_("The form was not properly filled in."))

        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))

        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]

        lang = request.context.get('lang', '')

        if lang in supported_lang_codes:
            values['lang'] = lang

        return values