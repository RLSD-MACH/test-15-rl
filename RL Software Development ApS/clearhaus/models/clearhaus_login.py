from odoo import api, fields, models
from datetime import datetime
from datetime import timedelta
import requests
import base64
import json


class ClearhausLogin(models.Model):
    
    _name = 'clearhaus.login'
    _description = 'Clearhaus login'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    client_id = fields.Char(required=True,string='Client ID')
    client_secret = fields.Char(required=True,string='Client Secret')        
    next_url = fields.Char(required=False,string='Next')
    token_ids = fields.One2many('clearhaus.token', 'login_id', store=True)
    transaction_ids = fields.One2many('clearhaus.transaction', 'login_id', store=True)
    url = fields.Char(required=True,string='Url')
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   

    def action_get_token(self):

        for row in self:
  
            tokens = self.env['clearhaus.token'].search([['active','=',True],['login_id','=', row.id]])
            
            now = datetime.now()
            
            if len(tokens) > 0:
                
                for token in tokens:
                
                    if token.expires > now:
                        
                        
                        
                        pass
                    
                    else:
                        
                        token.write({'active': False})
                    
                
            tokens = self.env['clearhaus.token'].search([['active','=',True],['login_id','=', row.id]])
            
            if len(tokens) == 0:
            
                url = row.url

                userpass = row.client_id + ':' + row.client_secret
                base64authorization = base64.b64encode(userpass.encode()).decode()

                headers = {
      
                'authorization': "Basic %s" % base64authorization,
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache"
                
                }
                
                payload = "audience=" + url + "&grant_type=client_credentials"
                                
                response = requests.request("POST", url + "/oauth/token", data=payload, headers=headers)
                
                if response.status_code == 200:
                    
                    self.env['api.call'].create({
                                'status_code': response.status_code,
                                'value': str(response.content),
                                'action': 'Clearhaus'
                            })
                            
                    object_response = json.loads(response.content)
                    
                    new_datetime = datetime.now() + timedelta(0, object_response['expires_in'])
                            
                    self.env['clearhaus.token'].create({
                                'login_id': row.id,
                                'expires': new_datetime,
                                'token': object_response.get('access_token',''),
                                'active': True
                            })
                    
                    
                    for variable in object_response:
                        
                        self.env['api.call'].create({
                                'status_code': response.status_code,
                                'value': variable + ": " + str(object_response.get(variable,'')),
                                'action': 'Clearhaus'
                            })
                            
                    tokens = self.env['clearhaus.token'].search([['active','=',True]])
                
                else:
                
                    self.env['api.call'].create({
                            'status_code': response.status_code,
                            'value': str(response.content),
                            'action': 'Clearhaus'
                        })
                        
            else:
                
                self.env['api.call'].create({
                            'status_code': 0,
                            'value': "Action called: 'Clearhaus Token', and we have an active Token already.",
                            'action': 'Clearhaus'
                        })
    
    def action_get_transactions(self):

        for row in self:

            tokens = self.env['clearhaus.token'].search([['active','=',True],['login_id','=', row.id]])
  
            now = datetime.now()
            
            if len(tokens) > 0:
                
                for token in tokens:
                
                    if token.expires > now:
                        
                        
                        
                        pass
                    
                    else:
                        
                        token.write({'active': False})
                
                
            tokens = self.env['clearhaus.token'].search([['active','=',True],['login_id','=', row.id]])
            
            if len(tokens) > 0:
                
                last_batch = 20
                
                while last_batch == 20:
                
                    url = "https://merchant.clearhaus.com/transactions"
                    page = 1
                    per_page = 20
                    last_batch = 0
                    
                    url += "?page=" + str(page) + "&per_page=" + str(per_page)
                    
                    if row.next_url != False and row.next_url != '':
                        
                        url = row.next_url
                    
                    payload = "audience=https://merchant.clearhaus.com&grant_type=client_credentials"
                    
                    headers = {
                        
                        'authorization': "Bearer " + str(tokens[0]['token']),
                        'content-type': "application/x-www-form-urlencoded",
                        'cache-control': "no-cache"
                        
                    }
                    
                    response = requests.request("GET", url, data=payload, headers=headers)
                    
                    if response.status_code == 200:
                            
                        call_id = self.env['api.call'].create({
                                'status_code': response.status_code,
                                'value': str(response.content),
                                'action': 'Clearhaus'
                            })
                            
                        object_response = json.loads(response.content)
                        
                        if object_response.get('_links','') != '':
                        
                            if object_response['_links'].get('next','') != '':
                                
                                row.write({'next_url': object_response['_links'].get('next','')['href']})
                        
                        _embedded = object_response.get('_embedded','')
                        transactions = _embedded.get('ch:transactions','')
                        
                        last_batch = len(transactions)
                        
                        for transaction in transactions:
                        
                            new = {
                                
                                'transaction_id': transaction.get('id',''),
                                'rrn': transaction.get('rrn',''),
                                'type': transaction.get('type',''),
                                'processed_at_ISO': transaction.get('processed_at',''),
                                'amount': transaction.get('amount',0) / 100,
                                'currency': transaction.get('currency',''),
                                'text_on_statement': transaction.get('text_on_statement',''),
                                'reference': transaction.get('reference',''),
                                'threed_secure': transaction.get('threed_secure',''),
                                'recurring': transaction.get('recurring',''),
                                'payment_method': transaction.get('payment_method',''),
                                'status_code': transaction['status']['code'],
                                'api_call_id': call_id.id,
                                'login_id': row.id
                                
                            }
                            
                            if transaction.get('card','') != '':
                                
                                new['card_bin'] = transaction.get('card.bin','')
                                new['card_country'] = transaction.get('card.country','')
                                new['card_last4'] = transaction.get('card.last4','')
                                new['card_scheme'] = transaction.get('card.scheme','')
                                new['card_type'] = transaction.get('card.type','')
                                new['card_expire_year'] = transaction.get('card.expire_year','')
                                new['card_expire_month'] = transaction.get('card.expire_month','')
                            
                            if transaction.get('settlement','') != '':
                                
                                #new['settlement_date'] = datetime.strptime(transaction.get('settlement.date',''), "%Y-%m-%dT%H:%M:%S%z")
                                new['settlement_fee_details'] = transaction['settlement'].get('fee_details','')
                                new['settlement_amount_gross'] = transaction['settlement']['amount_gross'] / 100
                                new['settlement_amount_net'] = transaction['settlement']['amount_net'] / 100
                                new['settlement_fees'] = transaction['settlement']['fees'] / 100
                                
                            else:
                                
                                new['settlement_amount_gross'] = 0
                                new['settlement_amount_net'] = 0
                                new['settlement_fees'] = 0
                            
                                
                            
                            self.env['clearhaus.transaction'].create(new)
                                
                    else:
                        
                        self.env['api.call'].create({
                                'status_code': response.status_code,
                                'value': str(response.content),
                                'action': 'Clearhaus'
                            })
                        
            else:
                
                self.env['api.call'].create({
                        'status_code': 0,
                        'value': "Action called: 'Clearhaus Transactions', but we don't have any active Token.",
                        'action': 'Clearhaus'
                    })