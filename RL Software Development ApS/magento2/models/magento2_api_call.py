from odoo import api, fields, models
from openerp.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import requests
import json


class Magento2ApiCall(models.Model):
    
    _name = 'magento2.api.call'
    _description = 'Magento2 API Call'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    login_id = fields.Many2one('magento2.login', 'Login', required=True)
    store_ids = fields.Many2many(comodel_name ='magento2.store', relation="magento2_api_call_magento2_store_rel", column1="magento2_api_call_id", column2="magento2_store_id", string='Stores', required=True)
    datatable_id = fields.Many2one('magento2.datatable', 'Datatable', required=True)
    action_type = fields.Selection([('PUT', 'PUT'),('PUT_BULK', 'PUT/BULK'),('GET', 'GET'),('POST', 'POST'),('DELETE', 'DELETE')], 'Action', required=True, default='GET')    
    body = fields.Text(required=False,string='Body')
    fields_text = fields.Char(required=False,string='Fields')
    search_text = fields.Char(required=False,string='Search')
    state = fields.Selection([('new', 'New'),('failed', 'Failed'),('success', 'Success')], 'State', required=True, default='new')   
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    def action_excecute_planned_calls(self):

        record_set = self.env['magento2.api.call'].search([['state','in',[False, 'new']]], limit=200)

        for row in record_set:

            self.excecute_call(row)

    def action_excecute_selected_calls(self):
        
        for row in self:

            self.excecute_call(row)

    def excecute_call(self):

        row = self
        
        action_type = row.action_type
        
        if action_type != "GET" and action_type != "PUT" and action_type != "PUT_BULK":
            
            raise UserError("Sorry - we do not support this action: " + str(action_type))
            
        app_name = 'magento2'
        
        url = row.login_id.url
        
        if row.login_id.token == False or row.login_id.token == "" or row.login_id.token_expire < datetime.datetime.now():
        
            url_token = url + "rest/V1/integration/admin/token"
            
            headers = {
                
                'content-type': "application/json",
                'cache-control': "no-cache"
                
            }
            
            data = {
                
                'username': row.login_id.name,
                'password': row.login_id.password
            
            }
            
            self.env['api.call'].create({
                'status_code': 0,
                'value': "Request url: " + str(url_token) + " | Headers: " + str(headers) + " | Body: " + str(data),
                'action': app_name,
                'active': "True",
                'type': action_type
            })    
        
            response_return = requests.request("POST", url_token, json=data, headers=headers)

            self.env['api.call'].create({
                'status_code': response_return.status_code,
                'value': str(response_return.content),
                'action': app_name,
                'active': "True",
                'type': action_type
            })
            
            if response_return.status_code == 200:
            
                token = response_return.content.decode("utf-8")[1:len(response_return.content.decode("utf-8"))-1]
                
                row.login_id.write({
                    
                    'token': token,
                    'token_expire': datetime.datetime.now() + datetime.timedelta(0, 60*30)
                    
                })
            
            else:
            
                self.env['api.call'].create({
                    'status_code': response_return.status_code,
                    'value': str(response_return.content),
                    'action': app_name,
                    'active': "True",
                    'type': action_type
                })
        
        
        if row.login_id.token != False and row.login_id.token != "" and row.login_id.token_expire > datetime.datetime.now():
            
            if action_type == "GET":
            
                urls = []
                
                if len(row.store_ids.ids) > 0:
                    
                    for store in row.store_ids:
                    
                        url_action = url + "rest/" + store.store_code + "/V1/" + row.datatable_id.name
                        urls.append(url_action)
                    
                else:
                    
                    url_action = url + "rest/V1/" + row.datatable_id.name
                    urls.append(url_action)
                    
                if row.search_text != '' and row.search_text != False:
                    
                    for i, element in enumerate(urls):
                    
                        urls[i] += "?" + row.search_text  
                    
                else:
                    
                    #for i, element in enumerate(urls):
                    
                    #urls[i] += "/search?searchCriteria=[]"
                    
                    pass
                    
                if row.fields_text != "" and row.fields_text != False:
                    
                    for i, element in enumerate(urls):
                    
                        urls[i] += "&fields=items[" + row.fields_text + "]"
                
                store_number = 0
                
                for url_action in urls:
                    
                    headers = {
                        
                        'content-type': "application/json",
                        'cache-control': "no-cache",
                        'Authorization': "Bearer " + row.login_id.token
                    
                    }
                    
                    self.env['api.call'].create({
                        'status_code': 0,
                        'value': "Request url: " + str(url_action) + " | Headers: " + str(headers),
                        'action': app_name,
                        'active': "True",
                        'type': action_type
                    })
                    
                    response_return = requests.request(action_type, url_action, headers=headers)
                    
                    self.env['api.call'].create({
                        'status_code': response_return.status_code,
                        'value': str(response_return.content),
                        'action': app_name,
                        'active': "True",
                        'type': action_type
                    })
                
                    if response_return.status_code == 200:
                    
                        object_response = json.loads(response_return.content)
                        object_response = object_response['items']
                    
                        model_name = app_name.lower() + ".data_" + row.datatable_id.name
                        
                        model_name = model_name.replace(' ','_').replace('(','_').replace(')','_').replace('-','_').replace('__','_').replace('__','_').lower().replace('relation','rel').replace('/',"_")
                    
                        if len(model_name)>48:
                    
                            model_name = model_name[0:47]
                    
                        if row.datatable_id.model_id.id == False:
                        
                            exists_model = self.env['ir.model'].search([['model','=', "x_" + model_name]])
                            
                            model_exists = False
                            
                            if len(exists_model) == 0:
                            
                                system_name = app_name.lower()
                                order = 'id'
                                
                                new_model = {
                            
                                    'name': model_name,
                                    'model':'x_' + model_name,
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
                            
                                    type_name = 'char'
                                    
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
                                
                                x_store_id = False
                                        
                                for field in fields:
                            
                                    if field['name'] == 'x_store_id':
                                        x_store_id = True
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
                                    
                                if x_store_id == False:
                                                
                                    fields.append({
                            
                                        'name': 'x_store_id',
                                        'required': False,
                                        'field_description': 'Store',
                                        'readonly': False,
                                        'store': True,
                                        'index': False,
                                        'copied': True,
                                        'tracking': False,
                                        'state': 'manual', 
                                        'ttype': 'integer',
                            
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
                            
                                    architectur = architectur + '\n' + '<filter name="' + field['name'] + '" string="' + field['field_description'] + '" context="{\'group_by\': \''+ field['name'] +'\'}"/>'
                            
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
                            
                                        view['groups_id'] = [group_id]
                                        view['model'] = 'x_' + model_to_add[3]
                            
                                        new_view_id = self.env['ir.ui.view'].create(view)
                            
                                        if view['type'] == 'search':
                            
                                            search_view_id = new_view_id.id               

                                    menu_id = self.env.ref('magnento2.magento2_data_api_menu').id
                                    
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
                            
                                model_exists = True
                                model_exists = False
                            
                        else:
                            
                            pass
                            #raise UserError("Not False?" ) 
                            
                        new_records = []      
                        
                        for rowss in object_response:
                            
                            new_record = {'x_active': True}
                            
                            z = 0
                            
                            for column in rowss:
                            
                                name = column
                                name = name.replace(' ','_').replace('(','_').replace(')','_').replace('-','_').lower()
                        
                                if name.isalnum() == False:
                            
                                    name = ''.join(e for e in name if e.isalnum() or e == "_" or e == ".")
                            
                                    name = name.replace('ö','o')
                            
                                    while name[len(name)-1:] == "_":
                            
                                        name = name[0:len(name)-1]
                            
                                #try: 
                                
                                if isinstance(rowss[column], list):
                                    
                                    new_record["x_" + name] = str(json.dumps(rowss[column]))
                                    
                                else:
                                    
                                    new_record["x_" + name] = str(rowss[column])
                                
                                z+=1
                            
                            if len(row.store_ids.ids) > 0:
                            
                                new_record["x_store_id"] = row.x_store_ids.ids[store_number]
                            
                            else:
                            
                                new_record["x_store_id"] = False
                            
                            new_records.append(new_record)
                            
                        if len(new_records) > 0:
                            
                            self.env['x_' + model_name].create(new_records)
                            
                            row.write({
                            
                                'state': "success",
                                'active': False
                            
                            })
                            
                        else:
                            
                            raise UserError("No records to add?" ) 
                    
                    else:
                    
                        row.write({
                            
                            'state': "failed"
                            
                        })

                        # raise UserError("Error: " + str(response_return.content.decode("utf-8")) + " | URL: " + str(url_action))
                        
                        pass

                    store_number += store_number

            elif action_type == "PUT":
            
                urls = []
                
                if len(row.store_ids.ids) > 0:
                    
                    for store in row.store_ids:
                    
                        url_action = url + "rest/" + store.store_code + "/V1/" + row.datatable_id.name + "/" + row.search_text
                        urls.append(url_action)
                    
                else:
                    
                    url_action = url + "rest/V1/" + row.datatable_id.name + "/" + row.search_text
                    urls.append(url_action)
                    
                if row.fields_text != "" and row.fields_text != False:
                    
                    for url in urls:
                    
                        url = url + "&fields=items[" + row.fields_text + "]"
                
                for url_action in urls:
                    
                    headers = {
                        
                        'content-type': "application/json",
                        'cache-control': "no-cache",
                        'Authorization': "Bearer " + row.login_id.token 
                    
                    }
                    
                    self.env['api.call'].create({
                        'status_code': 0,
                        'value': "Request url: " + str(url_action) + " | Headers: " + str(headers) + " | " + str(row.body),
                        'action': app_name,
                        'active': "True",
                        'type': action_type
                    })
                    
                    response_return = requests.request(action_type, url_action, headers=headers, data=row.body)
                    
                    self.env['api.call'].create({
                        'status_code': response_return.status_code,
                        'value': str(response_return.content),
                        'action': app_name,
                        'active': "True",
                        'type': action_type
                    })
                    
                    if response_return.status_code == 200:
                    
                        object_response = json.loads(response_return.content)
                        #object_response = object_response['items']
                        
                        row.write({
                            
                            'state': "success",
                            'active': False
                            
                        })
                    
                    else:
                    
                        #raise UserError("Error: code: " + str(response_return.status_code) + " | " + str(response_return.content.decode("utf-8")))
                        row.write({
                            
                            'state': "failed"
                            
                        })
                    
                    pass
                
            elif action_type == "PUT_BULK":
            
                urls = []
                
                if len(row.store_ids.ids) > 0:
                    
                    for store in row.store_ids:
                    
                        url_action = url  + "rest/" + store.store_code + "/async/bulk/V1/" + row.datatable_id.name
                        urls.append(url_action)
                    
                else:
                    
                    url_action = url + "rest/async/bulk/V1/" + row.datatable_id.name
                    urls.append(url_action)
                
                for url_action in urls:
                    
                    headers = {
                        
                        'content-type': "application/json",
                        'cache-control': "no-cache",
                        'Authorization': "Bearer " + row.login_id.token 
                    
                    }
                    
                    self.env['api.call'].create({
                        'status_code': 0,
                        'value': "Request url: " + str(url_action) + " | Headers: " + str(headers) + " | " + str(row.body),
                        'action': app_name,
                        'active': "True",
                        'type': action_type
                    })
                    
                    response_return = requests.request("PUT", url_action, headers=headers, data=row.body)
                    
                    self.env['api.call'].create({
                        'status_code': response_return.status_code,
                        'value': str(response_return.content),
                        'action': app_name,
                        'active': "True",
                        'type': action_type
                    })
                    
                    if response_return.status_code == 200:
                    
                        object_response = json.loads(response_return.content)
                        #object_response = object_response['items']
                        
                        row.write({
                            
                            'state': "success",
                            'active': False
                            
                        })
                    
                    else:
                    
                        #raise UserError("Error: code: " + str(response_return.status_code) + " | " + str(response_return.content.decode("utf-8")))
                        row.write({
                            
                            'state': "failed"
                            
                        })
                        
                        pass
                    
   