# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    fsc_certificate_id = fields.Many2one('fsc.certificate', string='FSC Certificate', required=False, domain="[('partner_id.ref_company_ids','in',[company_id])]")
    fsc_claim_id = fields.Many2one('fsc.claim', string='FSC Claim', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    fsc_weigthin_kg = fields.Float(string='Weight of FSC Paper in kgs.', default="0")
    
    @api.model
    def create(self, vals):

        vals = self._check_fsc_claim_on_products(vals, skip_states = [], create = True)

        res =  super(SaleOrderInherit, self).create(vals)

        self._autoverificate_certificate()

        return res

    def write(self, vals):
       
        if len(self) > 0 and not self.env.context.get("noonchange"):

            skip_states = []

            for record in self:

                if record.state not in ['draft', 'sent']:
                    
                    if 'fsc_certificate_id' in vals or 'fsc_claim_id' in vals:

                        raise UserError("You can't change FSC-settings on a SO with state: %s | vals: %s" % (str(record.state),str(vals)))

                if record.fsc_certificate_id:

                    skip_states = ['done','sale','cancel']

            vals = self._check_fsc_claim_on_products(vals, skip_states = skip_states)
       
        res = super(SaleOrderInherit, self).write(vals)

        if len(self) > 0:

            for record in self:

                record._autoverificate_certificate()

        return res

    def action_check_fsc_claim_on_products(self):

        self._check_fsc_claim_on_products(recalc = True)

    def _check_fsc_claim_on_products(self, vals=[], skip_states = [], create = False, recalc = False):

        if create == False:

            self.ensure_one()
        
        if create == True:

            if len(self) > 1:

                # raise UserError("Error in _check_fsc_claim_on_products")
                return vals

        record = self
        
        if record.state not in skip_states or create == True:

            claims_int = []
            claims = []
            claims_names = []
            skip_lines = []

            if 'order_line' in vals or recalc == True:

                if recalc == False:

                    if len(vals['order_line']):

                        for line in vals['order_line']:

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
                    
                for line in record.order_line:
                    
                    if line.id not in skip_lines:

                        claim = line.product_id.fsc_claim_id

                        if claim.id != False:         

                            if claim.id not in claims_int and claim.allowed_with_other_claims == False and claim.is_claim == True:

                                claims_int.append(claim.id)
                                claims.append(claim)
                                claims_names.append(claim.name)

            skip_lines = []

            if 'sale_order_option_ids' in vals:

                if len(vals['sale_order_option_ids']):

                    for line in vals['sale_order_option_ids']:
                            
                        try:

                            if line[0] == 0:
                            
                                x = 1
                                order_line_id = 0
                                
                            else:

                                x = 1
                                order_line_id = line[1]


                            if line[1] == False or line[2] == False:

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

                            raise UserError("sale_order_option_ids: " + str(line) + " |  Exception: " + str(e))

                for line in record.sale_order_option_ids:
                    
                    if line.id not in skip_lines:

                        claim = line.product_id.fsc_claim_id

                        if claim.id != False:         

                            if claim.id not in claims_int and claim.allowed_with_other_claims == False and claim.is_claim == True:

                                claims_int.append(claim.id)
                                claims.append(claim)
                                claims_names.append(claim.name)

            if 'sale_order_option_ids' in vals or 'order_line' in vals:

                if len(claims) == 1:

                    if create == True:

                        std_claim = self.env.company.fsc_certificate_id.id

                    else:

                        std_claim = record.company_id.fsc_certificate_id.id

                    if std_claim:

                        vals.update(fsc_certificate_id = std_claim, fsc_claim_id = claims[0].id )
                    
                elif len(claims) > 1:

                    raise ValidationError("We cant have different FSC Claims on the same order. \r\n" + str(claims_names) + "\r\n \r\n OBS: You don't need to lose your data. Open a new browser window and fix the products, if the settings on the product templates are wrong. Afterwards you can press save again and it will go through if the claims are the same.")

                else:

                    vals.update(fsc_certificate_id = False, fsc_claim_id = False)

            elif recalc == True:

                if len(claims) == 1:

                    std_claim = record.company_id.fsc_certificate_id.id

                    if std_claim:

                        record.with_context(noonchange=True).update({
                            
                            "fsc_certificate_id": std_claim, 
                            "fsc_claim_id": claims[0].id
                            
                        })
                    
                elif len(claims) > 1:

                    raise ValidationError("We cant have different FSC Claims on the same order. \r\n" + str(claims_names) + "\r\n \r\n OBS: You don't need to lose your data. Open a new browser window and fix the products, if the settings on the product templates are wrong. Afterwards you can press save again and it will go through if the claims are the same.")

                else:
                    
                    record.update({
                            
                        "fsc_certificate_id": False, 
                        "fsc_claim_id": False
                            
                    })

        return vals

    def _autoverificate_certificate(self):

        auto = self.env.company.fsc_run_auto_sale_order
        
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

