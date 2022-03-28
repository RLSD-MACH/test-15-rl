# -*- coding: utf-8 -*-

from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

	CustomerPortal.OPTIONAL_BILLING_FIELDS.append("function")	