from odoo import api, fields, models

class ClearhausTransaction(models.Model):
    
    _name = 'clearhaus.transaction'
    _description = 'Clearhaus transaction'
    _order = 'id'
    _check_company_auto = True

    secure_status_3d = fields.Char(string='3dsecure status', required=False, readonly=True)
    secure_version_3d = fields.Char(string='3dsecure version', required=False, readonly=True)
    arn = fields.Char(string='ARN', required=False, readonly=True, help='ARN stands for “Acquirer Reference Number” and is available for transactions where type is one of capture, refund, credit. Note that the ARN is only available after a transaction has been cleared by the card scheme, which in some rare cases can take several business days.')
    card_bin = fields.Char(string='Card bin', required=False, readonly=True, help='')
    card_country = fields.Char(string='Card country', required=False, readonly=True, help='')
    card_expire_month = fields.Char(string='Card expire month', required=False, readonly=True, help='')
    card_expire_year = fields.Char(string='	Card expire year', required=False, readonly=True, help='')
    card_last4 = fields.Char(string='Card last4', required=False, readonly=True, help='')
    card_scheme = fields.Char(string='Card scheme', required=False, readonly=True, help='')
    card_type = fields.Char(string='Card type', required=False, readonly=True, help='')
    currency = fields.Char(string='Currency', required=True, readonly=True, help='ISO 4217 3-letter code')
    fraud_type = fields.Char(string='Fraud type', required=False, readonly=True, help='Fraud information is collected from TC40/SAFE data.')
    transaction_id = fields.Char(string='Transaction ID', required=True, readonly=True, help='')
    payment_method = fields.Char(string='Payment method', required=False, readonly=True, help='One of: card, applepay, mobilepayonline, samsungpay, googlepay, vipps, tokenized_card.')
    processed_at_ISO = fields.Char(string='Processed ISO', required=False, readonly=True, help='')
    reference = fields.Char(string='Reference', required=False, readonly=True, help='')
    region = fields.Char(string='Region', required=False, readonly=True, help='One of: inter, intra, domestic')
    rrn = fields.Char(string='RRN', required=True, readonly=True, help='RRN stands for “Retrieval Reference Number”.')
    settlement_currency = fields.Char(string='Settlement currency', required=False, readonly=True, help='ISO 4217 3-letter code Settlement information is collected when the transaction is settled with card schemes. The settlement currency is the currency of the account.')
    settlement_fee_details = fields.Char(string='Settlement fee details', required=False, readonly=True, help='')
    status_message = fields.Char(string='Status message', required=False, readonly=True, help='')
    fraud_date = fields.Char(string='Fraud date', required=False, readonly=True, help='Fraud information is collected from TC40/SAFE data. ISO 8601 date')
    settlement_date = fields.Char(string='Settlement date', required=False, readonly=True, help='ISO 8601 date')
    processed_at = fields.Datetime(string='Processed', required=False, readonly=True, help='ISO 8601 date and time in UTC')
    amount = fields.Float(string='Amount', required=True, readonly=True, help='Amount in minor units of given currency (e.g. cents if in Euro).')
    settlement_amount_gross = fields.Float(string='Settlement amount gross', required=True, readonly=True, help='')
    settlement_amount_net = fields.Float(string='Settlement amount net', required=True, readonly=True, help='')
    settlement_fees = fields.Float(string='Settlement fees', required=True, readonly=True, help='')
    status_code = fields.Integer(string='Status code', required=False, readonly=True, help='')
    api_call_id = fields.Many2one('api.call',string='API Call', required=False, readonly=True, ondelete="set null", help='')
    login_id = fields.Many2one('clearhaus.login', 'Login ID', required=True, readonly=True, ondelete="restrict", help='') 
    threed_secure = fields.Selection(selection = [('false', 'False'),('attempt', 'Attempt'),('full', 'Full')], string='Threed secure', required=True, readonly=True, help='One of: false, attempt, full.')
    type = fields.Selection(selection = [('authorization', 'Authorization'),('capture', 'Capture'),('refund', 'Refund'),('credit', 'Credit'),('void', 'Void')], string='Type', required=True, readonly=True, help='One of: authorization, capture, refund, credit, void.')
    text_on_statement = fields.Text(string='Text on statement', required=False, readonly=True, help='')

    recurring = fields.Boolean(string='Recurring', required=True, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   
   