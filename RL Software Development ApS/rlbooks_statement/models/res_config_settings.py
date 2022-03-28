from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    customer_statement_account_ids = fields.Many2many("account.account", relation="account_account_customer_statement_account_ids_rel", string='Customer statement accounts', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    supplier_statement_account_ids = fields.Many2many("account.account", relation="account_account_supplier_statement_account_ids_rel", string='Supplier statement accounts', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    statement_goods_product_ids = fields.Many2many("product.product", relation="product_product_statement_goods_product_ids_rel", string='Calc products as goods', domain="['&',('type','!=','product'),('type','not in',statement_consus_product_ids),('type','not in',statement_services_product_ids),('type','not in',statement_services_product_ids),'|', ('company_id', '=', False), ('company_id', '=', company_id)]", readonly=False)
    statement_services_product_ids = fields.Many2many("product.product", relation="product_product_statement_services_product_ids_rel", string='Calc products as services', domain="['&',('type','!=','service'),('type','not in',statement_goods_product_ids),('type','not in',statement_consus_product_ids),('type','not in',statement_services_product_ids),'|', ('company_id', '=', False), ('company_id', '=', company_id)]", readonly=False)
    statement_consus_product_ids = fields.Many2many("product.product", relation="product_product_statement_consus_product_ids_rel", string='Calc products as consumables', domain="['&',('type','!=','consu'),('type','not in',statement_goods_product_ids),('type','not in',statement_services_product_ids),('type','not in',statement_consus_product_ids),'|', ('company_id', '=', False), ('company_id', '=', company_id)]", readonly=False)

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'
    
    customer_statement_account_ids = fields.Many2many("account.account", relation="account_account_customer_statement_account_ids_rel", related='company_id.customer_statement_account_ids', readonly=False)
    supplier_statement_account_ids = fields.Many2many("account.account", relation="account_account_supplier_statement_account_ids_rel", related='company_id.supplier_statement_account_ids', readonly=False)   
    statement_goods_product_ids = fields.Many2many("product.product", relation="product_product_statement_goods_product_ids_rel", related='company_id.statement_goods_product_ids', string='Calc products as goods', domain="['&',('type','!=','product'),('type','not in',statement_consus_product_ids),('type','not in',statement_services_product_ids),('type','not in',statement_services_product_ids),'|', ('company_id', '=', False), ('company_id', '=', company_id)]", readonly=False)
    statement_services_product_ids = fields.Many2many("product.product", relation="product_product_statement_services_product_ids_rel", related='company_id.statement_services_product_ids', string='Calc products as services', domain="['&',('type','!=','service'),('type','not in',statement_goods_product_ids),('type','not in',statement_consus_product_ids),('type','not in',statement_services_product_ids),'|', ('company_id', '=', False), ('company_id', '=', company_id)]", readonly=False)
    statement_consus_product_ids = fields.Many2many("product.product", relation="product_product_statement_consus_product_ids_rel", related='company_id.statement_consus_product_ids', string='Calc products as consumables', domain="['&',('type','!=','consu'),('type','not in',statement_goods_product_ids),('type','not in',statement_services_product_ids),('type','not in',statement_consus_product_ids),'|', ('company_id', '=', False), ('company_id', '=', company_id)]", readonly=False)
