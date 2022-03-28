# -*- coding: utf-8 -*-

import base64
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, UserError, ValidationError


class CustomerPortal(CustomerPortal):

	CustomerPortal.OPTIONAL_BILLING_FIELDS.append("image_1920")	
	# CustomerPortal.MANDATORY_BILLING_FIELDS.append("image_1920")	

	def _prepare_portal_layout_values(self):
		
		res =  super(CustomerPortal, self)._prepare_portal_layout_values()

		partner = request.env.user.partner_id
		if partner.image_512:
			res['profile_image'] = partner.image_512
		
		else:
			res['profile_image'] = False

		return res
	

	@route()
	def account(self, redirect=None, **post):
        
		if post and request.httprequest.method == 'POST':

			post.pop('image_1920', None)
			# raise UserError(str(post))
			image = False
			files_to_send = request.httprequest.files.getlist('image_1920')

			for file in files_to_send:

				post['image_1920'] = base64.b64encode(file.read())
				image = base64.b64encode(file.read())
			
			if image:
				request.env.user.sudo().write({'image_1920': image})		
		
		return super(CustomerPortal, self).account(redirect, **post)

	