from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import json


class UnicontaApiCall(models.Model):
    
    _name = 'uniconta.api.call'
    _description = 'Uniconta API Call'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    login_id = fields.Many2one('uniconta.login', 'Login', required=True)
    firm_id = fields.Many2one('uniconta.firm', 'Firm', required=True)
    datatable_id = fields.Many2one('uniconta.datatable', 'Datatable', required=True)
    action_type = fields.Selection([('read', 'Read'),('insert', 'Insert'),('delete', 'Delete'),('update', 'Update'),('all', 'All')], 'Action', required=True, default='read')   
    search_text = fields.Char(required=False,string='Search')
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   

    def action_excecute_calls(self):
                   
        for row in self:

            action_type = str(row.action_type)
              
            response_returned, object_response, app_name = row.action_uniconta_call(action_type, row.datatable_id.name, row.firm_id.primary_key_id, row.login_id.name, row.login_id.password, row.search_text)

            if response_returned.status_code == 200:

                if row.datatable_id.name == "DebtorGroupClient":

                    row._debtor_group_client_table(object_response)

                elif row.datatable_id.name == "CreditorGroupClient":

                    row._creditor_group_client_table(object_response)

                elif row.datatable_id.name == "CreditorClient" or row.datatable_id.name == "DebtorClient":

                    row._creditor_and_debtor_client_table(object_response)
                    
                else:

                    if row.datatable_id.model_id.id == False:
                    
                        model_name = "uniconta.data_" + row.datatable_id.name
                    
                        model_name = model_name.replace(' ','_').replace('(','_').replace(')','_').replace('-','_').replace('__','_').replace('__','_').lower().replace('relation','rel')
                    
                        if len(model_name) > 48:
                    
                            model_name = model_name[0:47]
                        
                        exists_model = self.env['ir.model'].search([['model','=', "x_" + model_name]])
                    
                        model_exists = False
                    
                        if len(exists_model) == 0:
                            
                            system_name = "uniconta"
                            order = 'id'
                            
                            new_model = {
                        
                                'name': model_name,
                                'model': "x_" + model_name,
                                'order': order
                                
                            }
                            
                            array_data = object_response
                        
                            fields = []
                            
                            coloums = []
                            
                            for row_array_data in  array_data:
                            
                                for coloumn_row_array_data in row_array_data:
                                    
                                    if coloumn_row_array_data not in coloums:
                                    
                                        coloums.append(coloumn_row_array_data)
                            
                            for coloumn in coloums:
                        
                                types = []
                                        
                                types.append('str')
                                
                                if len(types) == 1:
                        
                                    if types[0] == 'int':
                                        
                                        type_name = 'integer'
                                
                                    elif types[0] == 'str':
                                        
                                        type_name = 'char'
                                
                                    elif types[0] == 'datetime.datetime':
                                        
                                        type_name = 'datetime'
                                    
                                    elif types[0] == 'decimal.Decimal' or types[0] == 'float':
                                        
                                        type_name = 'float'
                        
                                    elif types[0] == 'bytearray':
                                        
                                        type_name = 'char'
                        
                                    elif types[0] == 'bool':
                                        
                                        type_name = 'boolean'                
                                    
                                    elif types[0] == "timestamp":
                                        
                                        type_name = ''            
                        
                                    else:
                                        
                                        raise UserError("Missing term? : " + types[0] )
                                        
                                else:
                        
                                    raise UserError("multiple?... " + coloumn + "?... ", types)
                        
                                if coloumn.replace(' ','_').replace('(','_').replace(')','_').replace('-','_').lower() != 'name' and type_name != '':
                                    
                                    name = coloumn
                                    name = name.replace(' ','_').replace('(','_').replace(')','_').replace('-','_').lower()

                                    if name.isalnum() == False:
                                
                                        name = ''.join(e for e in name if e.isalnum() or e == "_" or e == ".")
                                
                                        name = name.replace('ö','o')
                                
                                        while name[len(name)-1:] == "_":
                                
                                            name = name[0:len(name)-1]
                                
                                    new_field = {
                        
                                        'name': 'x_' + name,
                                        'required': False,
                                        'field_description': coloumn,
                                        'readonly': False,
                                        'store': True,
                                        'index': False,
                                        'copied': True,
                                        'tracking': False,
                                        'state': 'manual', 
                                        'ttype': type_name,
                                        #'depends': 0
                        
                                    }
                        
                                    if len(new_field['name']) > 63:
                        
                                        new_field['name'] = new_field['name'][0:62]
                        
                                    
                                    fields.append(new_field)
                    
                
                            x_active = False
                        
                            for field in fields:
                        
                                if field['name'] == 'x_active':

                                    x_active = True

                                    break
                        
                            if x_active == False:
                                            
                                fields.append({
                        
                                    'name': 'x_active',
                                    'required': True,
                                    'field_description': 'Active or not',
                                    'readonly': False,
                                    'store': True,
                                    'index': False,
                                    'copied': True,
                                    'tracking': False,
                                    'state': 'manual', 
                                    'ttype': 'boolean',
                        
                                })
                        
                            
                            views = []
                        
                            #Tree View 
                        
                            architectur = '<?xml version="1.0"?>'
                            
                            architectur = architectur + '\n\n' + '<tree string="' + model_name + '" editable="top" create="1" delete="1" multi_edit="1" sample="1">'
                        
                            architectur = architectur + '\n\n' + '<field name="id" optional="hide" readonly="1"/>'
                            architectur = architectur + '\n' + '<field name="x_name" optional="show" readonly="1"/>'
                        
                            for field in fields:
                        
                                if field['ttype'] == "many2one":
                        
                                    architectur = architectur + '\n' + '<field name="' + field['name'] + '" optional="show" widget="many2one" domain="[]"/>'
                        
                                else:
                        
                                    architectur = architectur + '\n' + '<field name="' + field['name'] + '" optional="show" readonly="1"/>'
                        
                            architectur = architectur + '\n\n' + '</tree>'
                        
                            views.append({
                        
                                'name': 'x_' + model_name + '.tree',
                                'type': 'tree',
                                'priority': 8,
                                'active': True,
                                'mode': 'primary',
                                'arch_base': architectur
                        
                            })
                        
                            #Select View 
                            
                            architectur = '<?xml version="1.0"?>'
                            
                            architectur = architectur + '\n\n' + '<search string="Search ' + model_name + '">'
                        
                            architectur = architectur + '\n\n' + '<field name="x_name" filter_domain="[\'|\', \'|\', (\'display_name\', \'ilike\', self)]"/>'
                            architectur = architectur + '\n' + '<separator/>'
                        
                            architectur = architectur + '\n' + '<separator/>'
                            architectur = architectur + '\n' + '<filter string="Archived" name="inactive" domain="[(\'x_active\', \'=\', False)]"/>'
                            architectur = architectur + '\n' + '<separator/>'
                        
                            architectur = architectur + '\n' + '<group expand="0" name="group_by" string="Group By">'
                            architectur = architectur + '\n' + '<filter name="create_date" string="Created date" domain="[]" context="{\'group_by\' : \'create_date\'}"/>'
                            
                            for field in fields:
                        
                                architectur = architectur + '\n' + '<filter name="' + field['name'] + '" string="' + field['name'] + '" context="{\'group_by\': \''+ field['name'] +'\'}"/>'
                        
                            architectur = architectur + '\n' + '</group>'
                            architectur = architectur + '\n\n' + '</search>'
                        
                            views.append({
                        
                                'name': 'x_' + model_name + '.select',
                                'type': 'search',
                                'priority': 16,
                                'active': True,
                                'mode': 'primary',
                                'arch_base': architectur
                        
                            })
                                
                            model_to_add = [new_model, fields, views, model_name]
                            
                            new_model = self.env['ir.model'].create(model_to_add[0])
                            new_model_id = new_model.id
                            
                            row.datatable_id.write({'model_id': new_model_id })
                            
                            newview = []
                            
                            if len(model_to_add[1]) > 0:
                        
                                for field in model_to_add[1]:
                        
                                    field['model_id'] = new_model_id
                                    field['model'] = 'x_' + model_name
                                    
                                fields = model_to_add[1]
                                
                                if len(fields) > 40:

                                    x = 0
                                    total_records = len(fields)
                            
                                    while x < total_records:
                                    
                                        y = x + 10
                        
                                        if y > total_records:
                                        
                                            y = total_records
                                    
                                        newview.append(self.env['ir.model.fields'].create(fields[x:y]))
                        
                                        x = y
                        
                                else:
                            
                                    newview.append(self.env['ir.model.fields'].create(fields))
                        
                            
                                if order != 'id':
                                
                                    new_model.write({'order': order})
                        
                                #Add access rigths
                                
                                Groups = self.env['res.groups'].search([['name', '=', 'Special Taskforce']])
                                
                                new_access = []

                                if len(Groups) != 1:

                                    group_id = False
                                    
                                    new_access.append({
                                    
                                        "name":"None",
                                        "active": True,
                                        "model_id": new_model_id,
                                        "perm_read": True,
                                        "perm_write": True,
                                        "perm_create":True,
                                        "perm_unlink":True
                            
                                    })
                                
                                else:
                                
                                    group_id = Groups[0].id

                                    new_access.append({
                                    
                                        "name":"Special Taskforce",
                                        "active": True,
                                        "model_id": new_model_id,
                                        "group_id": group_id,
                                        "perm_read": True,
                                        "perm_write": True,
                                        "perm_create":True,
                                        "perm_unlink":True
                            
                                    })
                        
                                
                                
                                
                                self.env['ir.model.access'].create(new_access)
                        
                            else:
                        
                                raise UserError("No fields to add??")
                                            
                    
                            if len(model_to_add[2]) > 0:
                        
                                for view in model_to_add[2]:
                                    
                                    if group_id != False:

                                        view['groups_id'] = [group_id]

                                    view['model'] = 'x_' + model_to_add[3]
                        
                                    new_view_id = self.env['ir.ui.view'].create(view)
                        
                                    if view['type'] == 'search':
                        
                                        search_view_id = new_view_id.id               
                        
                                menu_id = self.env.ref('uniconta.uniconta_data_api_menu').id
                                    
                                new_action = {
                        
                                    'name': app_name + ' ' + model_to_add[3],
                                    'res_model': 'x_' + model_to_add[3],
                                    'type': 'ir.actions.act_window',
                                    'target': 'current',
                                    'context': '{}',
                                    'limit': 80,
                                    'view_mode': 'tree,form',
                                    'search_view_id': search_view_id,
                                    'help': 'Translated from ' + system_name
                        
                                }
                        
                                action_id = self.env['ir.actions.act_window'].create(new_action)
                        
                                new_submenu = {

                                    'name': row.datatable_id.name, #model_to_add[3],
                                    'parent_id': menu_id,
                                    'sequence': 10,
                                    'action': 'ir.actions.act_window,' + str(action_id[0].id)

                                }
                                
                                submenu_id = self.env['ir.ui.menu'].create(new_submenu)
                            
                            model_exists = True
                            
                        elif len(exists_model) == 1:
                            
                            row.datatable_id.write({'model_id': exists_model[0].id })
                            
                            model_exists = True
                        
                        else:
                            
                            model_exists = False
                            
                    else:
                        
                        model_exists = True
                        model_name = row.datatable_id.model_id.model[2:]
                        
                        #pass
                        #raise UserError("Not False?" ) 
                        
                    new_records = []   
                    
                    for row in object_response:
                    
                        new_record = {'x_active': True}
                    
                        for column in row:
                            
                            name = column
                            name = name.replace(' ','_').replace('(','_').replace(')','_').replace('-','_').lower()

                            if name.isalnum() == False:
                        
                                name = ''.join(e for e in name if e.isalnum() or e == "_" or e == ".")
                        
                                name = name.replace('ö','o')
                        
                                while name[len(name)-1:] == "_":
                        
                                    name = name[0:len(name)-1]
                                
                            new_record["x_" + name] = row.get(column)
                    
                        new_records.append(new_record)
                    
                    if len(new_records) > 0:
                    
                        self.env['x_' + model_name].create(new_records)
                    
                    else:
                    
                        raise UserError("No records to add?" ) 

                    row.update({

                        'active': False

                    })
            
            else:
                
                self.env['api.call'].create({
                        'status_code': response_returned.status_code,
                        'value': str(response_returned.content),
                        'action': 'Uniconta',
                        'active': True,
                        'type': action_type
                    })                                  
        
    def action_uniconta_call(self, action_type, datatable_name, primary_key_id, login_name, login_password, search_text=False):

        if action_type not in ['all','read']:
                
            raise UserError("Sorry - we do not support this action: " + str(action_type))
            
        CompanyID = str(primary_key_id)

        if len(CompanyID) < 7:

            for x in range(7 - len(CompanyID)):

                CompanyID = "0" + CompanyID
                    
        system_username = CompanyID + "/" + login_name
        
        app_name = 'uniconta'

        url = 'https://odata.uniconta.com/api/Entities/'

        if action_type != 'all':

            url = url + action_type + '/' 

        url = url + datatable_name 

        if search_text != '' and search_text != False:

            url = url + "?" + search_text  
            
        self.env['api.call'].create([{
            
            'status_code': 0,
            'value': "Request url: " + str(url) + " | " + str((system_username)),
            'action': 'Uniconta',
            'active': True,
            'type': action_type
            
        }])
                    
        response_returned = requests.get(url, auth=(system_username, login_password))
        
        object_response = json.loads(response_returned.content)

        self.env['api.call'].create([{
            
            'status_code': response_returned.status_code,
            'value': str(object_response),
            'action': 'Uniconta',
            'active': True,
            'type': action_type
            
            }])

        return response_returned, object_response, app_name

    def _debtor_group_client_table(self, object_response):

        mapping = [('group','name'),('rowid','uniconta_row_id'),('keystr','uniconta_keystr')]
    
        new_records = []   
                    
        for row in object_response:
        
            new_record = {
                'active': True,
                'uniconta_firm_id': self.firm_id.id,
                }
        
            for column in row:
                
                name = column
                name = name.replace(' ','_').replace('(','_').replace(')','_').replace('-','_').lower()

                if name.isalnum() == False:
            
                    name = ''.join(e for e in name if e.isalnum() or e == "_" or e == ".")
            
                    name = name.replace('ö','o')
            
                    while name[len(name)-1:] == "_":
            
                        name = name[0:len(name)-1]
                    
                for map in mapping:

                    if map[0] == name:

                        new_record[map[1]] = row.get(column)

                        break
        
            new_group = self.env['res.partner.group'].create({

                'name': new_record['name'],
                'active': True

            })

            new_record['res_partner_group_id'] = new_group.id
            
            new_records.append(new_record)
        
        if len(new_records) > 0:
                    
            self.env['uniconta.debtor.group'].create(new_records)
        
        else:
        
            raise UserError("No records to add?" ) 

    def _creditor_group_client_table(self, object_response):

        mapping = [('group','name'),('rowid','uniconta_row_id'),('keystr','uniconta_keystr')]
    
        new_records = []   
                    
        for row in object_response:
        
            new_record = {
                'active': True,
                'uniconta_firm_id': self.firm_id.id,
                }
        
            for column in row:
                
                name = column
                name = name.replace(' ','_').replace('(','_').replace(')','_').replace('-','_').lower()

                if name.isalnum() == False:
            
                    name = ''.join(e for e in name if e.isalnum() or e == "_" or e == ".")
            
                    name = name.replace('ö','o')
            
                    while name[len(name)-1:] == "_":
            
                        name = name[0:len(name)-1]
                    
                for map in mapping:

                    if map[0] == name:

                        new_record[map[1]] = row.get(column)

                        break
        
            new_group = self.env['res.partner.group'].create({

                'name': new_record['name'],
                'active': True

            })

            new_record['res_partner_group_id'] = new_group.id
            
            new_records.append(new_record)
        
        if len(new_records) > 0:
                    
            self.env['uniconta.creditor.group'].create(new_records)
        
        else:
        
            raise UserError("No records to add?" )

    def _creditor_and_debtor_client_table(self, object_response):

        mapping = [

            ('rowid','uniconta_row_id'),
            ('keystr','uniconta_keystr'),
            ('account','account'),
            ('active','active'),
            ('address1','address1'),
            ('address2','address2'),
            ('address3','address3'),
            ('balancemethod','balancemethod'),
            ('bankaccounttype','bankaccounttype'),
            ('blocked','blocked'),
            ('city','city'),
            ('companyid','companyid'),
            ('companyregno','companyregno'),
            ('contactemail','contactemail'),
            ('contactperson','contactperson'),
            ('country','country'),
            ('countryname','countryname'),
            ('created','created'),
            ('creditmax','creditmax'),
            ('curbalance','curbalance'),
            ('curbalancecur','curbalancecur'),
            ('currency','currency'),
            ('deliveryaddress1','deliveryaddress1'),
            ('deliveryaddress2','deliveryaddress2'),
            ('deliveryaddress3','deliveryaddress3'),
            ('deliverycity','deliverycity'),
            ('deliverycountry','deliverycountry'),
            ('deliverycountryname','deliverycountryname'),
            ('deliveryname','deliveryname'),
            ('deliveryzipcode','deliveryzipcode'),
            ('directdebitactive','directdebitactive'),
            ('ean','ean'),
            ('eeisnotvatdeclorg','eeisnotvatdeclorg'),
            ('emaildocuments','emaildocuments'),
            ('enddiscountpct','enddiscountpct'),
            ('group','group'),
            ('hasdocs','hasdocs'),
            ('hasnotes','hasnotes'),
            ('invoiceemail','invoiceemail'),
            ('invoiceinxml','invoiceinxml'),
            ('keyname','keyname'),
            ('lastinvoice','lastinvoice'),
            ('layoutgroup','layoutgroup'),
            ('linediscountpct','linediscountpct'),
            ('mobilphone','mobilphone'),
            ('name','name'),
            ('overdue','overdue'),
            ('overduecur','overduecur'),
            ('payment','payment'),
            ('paymentfee','paymentfee'),
            ('phone','phone'),
            ('pricegroup','pricegroup'),
            ('pricelist','pricelist'),
            ('pricesinclvat','pricesinclvat'),
            ('updatedat','updatedat'),
            ('userattachment','userattachment'),
            ('userfields','userfields'),
            ('userlangaugeid','userlangaugeid'),
            ('userlanguage','userlanguage'),
            ('usernote','usernote'),
            ('vat','vat'),
            ('vatnumber','vatnumber'),
            ('vatzone','vatzone'),
            ('www','www'),
            ('zipcode','zipcode'),
            ('paymentid','paymentid'),
            ('paymentmethod','paymentmethod'),
            ('postingaccount','postingaccount'),
            ('swift','swift'), 
            ]
    
        new_records = []   
                    
        for row in object_response:
        
            new_record = {
                'active': True,
                'uniconta_firm_id': self.firm_id.id,
                }
        
            for column in row:
                
                name = column
                name = name.replace(' ','_').replace('(','_').replace(')','_').replace('-','_').lower()

                if name.isalnum() == False:
            
                    name = ''.join(e for e in name if e.isalnum() or e == "_" or e == ".")
            
                    name = name.replace('ö','o')
            
                    while name[len(name)-1:] == "_":
            
                        name = name[0:len(name)-1]
                    
                for map in mapping:

                    if map[0] == name:

                        new_record[map[1]] = row.get(column)

                        break
        
            try:

                new_group = self.env['res.partner'].create({

                    'name': new_record.get('name',False),
                    'vat': new_record.get('companyregno',False),
                    'ref': new_record.get('account',False),
                    'city': new_record.get('city',False),
                    # 'company_type': new_record.get('company_type',False),
                    'credit_limit': new_record.get('creditmax',False),
                    
                    'active': True

                })

                new_record['res_partner_id'] = new_group.id
            
            except:

                continue
            
            new_records.append(new_record)
        
        if len(new_records) > 0:
        
            self.env['uniconta.partner'].create(new_records)
        
        else:
        
            raise UserError("No records to add?" )


    # def _mapping_partner(self):

    #     mapping = [

    #         ('rowid','uniconta_row_id'),
    #         ('keystr','uniconta_keystr')
    #         ('account','account'),
    #         ('active', 'active'),
    #         ('address1', 'address1'),
    #         ('address2', 'address2'),
    #         ('address3', 'address3'),
    #         ('balancemethod', 'balancemethod'),
    #         ('bankaccounttype', 'bankaccounttype'),
    #         ('blocked', 'blocked'),
    #         ('city', 'city'),
    #         ('companyid', 'companyid'),
    #         ('companyregno', 'companyregno'),
    #         ('contactemail', 'contactemail'),
    #         ('contactperson', 'contactperson'),
    #         ('country', 'country'),
    #         ('countryname', 'countryname'),
    #         ('created', 'created'),
    #         ('creditmax', 'creditmax'),
    #         ('curbalance', 'curbalance'),
    #         ('curbalancecur', 'curbalancecur'),
    #         ('currency', 'currency'),
    #         ('deliveryaddress1', 'deliveryaddress1'),
    #         ('deliveryaddress2', 'deliveryaddress2'),
    #         ('deliveryaddress3', 'deliveryaddress3'),
    #         ('deliverycity', 'deliverycity'),
    #         ('deliverycountry', 'deliverycountry'),
    #         ('deliverycountryname', 'deliverycountryname'),
    #         ('deliveryname', 'deliveryname'),
    #         ('deliveryzipcode', 'deliveryzipcode'),
    #         ('directdebitactive', 'directdebitactive'),
    #         ('ean', 'ean'),
    #         ('eeisnotvatdeclorg', 'eeisnotvatdeclorg'),
    #         ('emaildocuments', 'emaildocuments'),
    #         ('enddiscountpct', 'enddiscountpct'),
    #         ('group', 'group'),
    #         ('hasdocs', 'hasdocs'),
    #         ('hasnotes', 'hasnotes'),
    #         ('invoiceemail', 'invoiceemail'),
    #         ('invoiceinxml', 'invoiceinxml'),
    #         ('keyname', 'keyname'),
    #         # ('keystr', 'keystr'),
    #         ('lastinvoice', 'lastinvoice'),
    #         ('layoutgroup', 'layoutgroup'),
    #         ('linediscountpct', 'linediscountpct'),
    #         ('mobilphone', 'mobilphone'),
    #         ('name', 'name'),
    #         ('overdue', 'overdue'),
    #         ('overduecur', 'overduecur'),
    #         ('payment', 'payment'),
    #         ('paymentfee', 'paymentfee'),
    #         ('phone', 'phone'),
    #         ('pricegroup', 'pricegroup'),
    #         ('pricelist', 'pricelist'),
    #         ('pricesinclvat', 'pricesinclvat'),
    #         # ('rowid', 'rowid'),
    #         ('updatedat', 'updatedat'),
    #         ('userattachment', 'userattachment'),
    #         ('userfields', 'userfields'),
    #         ('userlangaugeid', 'userlangaugeid'),
    #         ('userlanguage', 'userlanguage'),
    #         ('usernote', 'usernote'),
    #         ('vat', 'vat'),
    #         ('vatnumber', 'vatnumber'),
    #         ('vatzone', 'vatzone'),
    #         ('www', 'www'),
    #         ('zipcode', 'zipcode'),
            
    #         ]

    #     return mapping