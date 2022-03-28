# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    
    fsc_certificate_id = fields.Many2one('fsc.certificate', string='FSC Certificate', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    fsc_claim_id = fields.Many2one('fsc.claim', string='FSC Claim', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    fsc_weigthin_kg = fields.Float(string='Weight of FSC Paper in kgs.', default="0")

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            
           vals = self._check_fsc_claim_on_products(vals, skip_states = [], create = True)

        res = super(AccountMoveInherit, self).create(vals_list)

        for record in res:

            if record.fsc_certificate_id:

                record._autoverificate_certificate()
                    
        return res

    def write(self, vals):
                
        if len(self) <= 1:

            if self.state not in ['draft', 'sent']:
                        
                if 'fsc_certificate_id' in vals or 'fsc_claim_id' in vals:

                    raise UserError("You can't change FSC-settings on a %s with state: %s | vals: %s" % (str(self.move_type),str(self.state),str(vals)))

            if self.move_type in ['out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt']:

                vals = self._check_fsc_claim_on_products(vals, skip_states = [])
                   
        res = super(AccountMoveInherit, self).write(vals)
        
        if len(self) <= 1:
            
            if 'fsc_certificate_id' in vals:

                self._autoverificate_certificate()
       
        return res

    def _check_fsc_claim_on_products(self, vals, skip_states = [], create = False):
        
        if create == False:
            self.ensure_one()
        
        if create == True:

            if len(self) > 1:

                # raise UserError("Error in _check_fsc_claim_on_products | Multiple? | " + str(self))
                return vals

        record = self

        if record.state not in skip_states or create == True:

            claims_int = []
            claims = []
            claims_names = []
            skip_lines = []
            
            if 'invoice_line_ids' in vals:

                if len(vals['invoice_line_ids']):

                    for line in vals['invoice_line_ids']:

                        try:

                            if line[0] == 0:
                            
                                x = 1
                                order_line_id = 0
                                
                            else:

                                x = 1
                                order_line_id = line[1]

                            if line[1+x] == False:

                                skip_lines.append(order_line_id)                                

                            elif line[1+x].get('product_id',False) if line[1+x] else False:

                                product = self.env['product.product'].browse(line[1+x].get('product_id',False))
                                    
                                claim = product.fsc_claim_id

                                if claim.id != False:         

                                    if claim.id not in claims_int and claim.allowed_with_other_claims == False and claim.is_claim == True:

                                        claims_int.append(claim.id)
                                        claims.append(claim)
                                        claims_names.append(claim.name)

                                if order_line_id > 0:

                                    skip_lines.append(order_line_id)
                        
                        except  Exception as e:

                            raise UserError("order_line: " + str(line) + " |  Exception: " + str(e))
                
                for line in record.invoice_line_ids:
                    
                    if line.id not in skip_lines:

                        claim = line.product_id.fsc_claim_id

                        if claim.id != False:         

                            if claim.id not in claims_int and claim.allowed_with_other_claims == False and claim.is_claim == True:

                                claims_int.append(claim.id)
                                claims.append(claim)
                                claims_names.append(claim.name)
            
            if 'invoice_line_ids' in vals:
                
                if len(claims) == 1:
                    
                    std_claim = False

                    if vals.get('sale_order_id', False):

                        salesorder = self.env['sale.order'].browse(vals.get('sale_order_id'))

                        if salesorder.fsc_certificate_id.id:

                            std_claim = salesorder.fsc_certificate_id 
                    
                    elif not create:

                        if self.sale_order_id.id:
                            
                            if self.sale_order_id.fsc_certificate_id.id:

                                std_claim = self.sale_order_id.fsc_certificate_id 
                                                                        
                    if not std_claim:

                        if vals.get('company_id', False):
                            
                            company = self.env['res.company'].browse(vals.get('company_id', False))

                            std_claim = company.fsc_certificate_id.id
                        
                        elif self.company_id:
                            
                            std_claim = self.company_id.fsc_certificate_id.id
                            
                        else:
                            
                            std_claim = self.company.fsc_certificate_id.id

                    if std_claim:

                        vals.update(fsc_certificate_id = std_claim, fsc_claim_id = claims[0].id )
                    
                    else:

                        raise UserError("No standard FSC Certificate were found in the Company settings!?")
                    
                elif len(claims) > 1:

                    raise ValidationError("We cant have different FSC Claims on the same document. \r\n" + str(claims_names) + "\r\n \r\n OBS: You don't need to lose your data. Open a new browser window and fix the products, if the settings on the product templates are wrong. Afterwards you can press save again and it will go through if the claims are the same.")

                else:

                    vals.update(fsc_certificate_id = False, fsc_claim_id = False)

        return vals

    def _autoverificate_certificate(self):

        auto = self.env.company.fsc_run_auto_account_move
        
        if auto:

            days = self.env.company.fsc_days_between_validations
                
            for record in self:
                
                if record.fsc_certificate_id:
            
                    fsc_certificate = record.fsc_certificate_id

                    if fsc_certificate.last_validation_id.id:

                        deadline = fsc_certificate.last_validation_date + timedelta(days=days)

                        if date.today() > deadline.date() or fsc_certificate.last_validation_valid == False:

                            fsc_certificate.action_control_certificate(silent=True)

                    else:

                        fsc_certificate.action_control_certificate(silent=True)

    @api.constrains('fsc_claim_id')
    def _check_stage(self):

        for record in self:

            if record.fsc_claim_id and not record.fsc_certificate_id:

                raise ValidationError("You need to choose a FSC Certificate to choose a claim!")
