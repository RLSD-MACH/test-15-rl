# -*- coding: utf-8 -*-

import ast

from odoo import api, fields, models, _
from openerp.exceptions import ValidationError, UserError

class MailComposeMessageInherit(models.TransientModel):
    
    _inherit = 'mail.compose.message'

    @api.model
    def get_default_email_cc(self):

        model = self.env.context.get('default_model')
        res_id = self.env.context.get('default_res_id')

        cc = ""

        if(self.env.context.get('default_model') == 'sale.order'):

            order = self.env[model].browse(res_id)
            partner = order.partner_id

            if partner:
            
                cc = partner.email_cc
       
        return cc

    @api.model
    def get_default_email_bcc(self):

        model = self.env.context.get('default_model')
        res_id = self.env.context.get('default_res_id')

        bcc = ""

        if(self.env.context.get('default_model') == 'sale.order'):

            order = self.env[model].browse(res_id)
            partner = order.partner_id

            if partner:
            
                bcc = partner.email_bcc
       
        return bcc

    @api.model
    def get_default_contact_cc_ids(self):

        model = self.env.context.get('default_model')
        res_id = self.env.context.get('default_res_id')

        contact_cc_ids = False

        if(self.env.context.get('default_model') == 'sale.order'):

            order = self.env[model].browse(res_id)
            partner = order.partner_id

            if partner:
                
                contact_cc_ids = partner.contact_cc_ids.ids if partner.contact_cc_ids else False
       
        return contact_cc_ids

    @api.model
    def get_default_contact_bcc_ids(self):

        model = self.env.context.get('default_model')
        res_id = self.env.context.get('default_res_id')

        contact_bcc_ids = False

        if(self.env.context.get('default_model') == 'sale.order'):

            order = self.env[model].browse(res_id)
            partner = order.partner_id

            if partner:
                
                contact_bcc_ids = partner.contact_bcc_ids.ids if partner.contact_bcc_ids else False
       
        return contact_bcc_ids

    @api.model
    def get_default_bcc_emails(self):

        return self.model if self.model else None


    email_cc = fields.Char(string='Email CC', required=False, store=True, default=get_default_email_cc)
    email_bcc = fields.Char(string='Email BCC', required=False, store=True, default=get_default_email_bcc)

    partner_cc_ids = fields.Many2many('res.partner', "mail_compose_message_contact_cc_rel", 's_partner_id', 'res_partner_id', string='Contacts CC', required=False, default=get_default_contact_cc_ids, domain="['|', ('email', '!=', False),('id','not in',partner_bcc_ids)]")
    partner_bcc_ids = fields.Many2many('res.partner', "mail_compose_message_contact_bcc_rel", 's_partner_id', 'res_partner_id', string='Contacts BCC', required=False, default=get_default_contact_bcc_ids, domain="['|', ('email', '!=', False),('id','not in',partner_cc_ids)]")
    
    def get_mail_values(self, res_ids):
        
        res_array = super(MailComposeMessageInherit, self).get_mail_values(res_ids)

        for res in res_array:
            
            cc = ""
            bcc = ""

            if self.email_cc:

                cc += self.email_cc + ";"

            if self.email_bcc:

                bcc += self.email_bcc + ";"

            res_array[res]['email_cc'] = cc
            res_array[res]['email_bcc'] = bcc

            if res_array[res].get('recipient_cc_ids'):

                res_array[res]['recipient_cc_ids'] += self.partner_cc_ids.ids
            
            else: 

                res_array[res]['recipient_cc_ids'] = self.partner_cc_ids.ids
            
            if res_array[res].get('recipient_bcc_ids'):

                res_array[res]['recipient_bcc_ids'] += self.partner_bcc_ids.ids
            
            else: 

                res_array[res]['recipient_bcc_ids'] = self.partner_bcc_ids.ids
                           
        return res_array

    def send_mail(self, auto_commit=False):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        notif_layout = self._context.get('custom_layout')
        # Several custom layouts make use of the model description at rendering, e.g. in the
        # 'View <document>' button. Some models are used for different business concepts, such as
        # 'purchase.order' which is used for a RFQ and and PO. To avoid confusion, we must use a
        # different wording depending on the state of the object.
        # Therefore, we can set the description in the context from the beginning to avoid falling
        # back on the regular display_name retrieved in '_notify_prepare_template_context'.
        model_description = self._context.get('model_description')
        for wizard in self:
            # Duplicate attachments linked to the email.template.
            # Indeed, basic mail.compose.message wizard duplicates attachments in mass
            # mailing mode. But in 'single post' mode, attachments of an email template
            # also have to be duplicated to avoid changing their ownership.
            if wizard.attachment_ids and wizard.composition_mode != 'mass_mail' and wizard.template_id:
                new_attachment_ids = []
                for attachment in wizard.attachment_ids:
                    if attachment in wizard.template_id.attachment_ids:
                        new_attachment_ids.append(attachment.copy({'res_model': 'mail.compose.message', 'res_id': wizard.id}).id)
                    else:
                        new_attachment_ids.append(attachment.id)
                new_attachment_ids.reverse()
                wizard.write({'attachment_ids': [(6, 0, new_attachment_ids)]})

            # Mass Mailing
            mass_mode = wizard.composition_mode in ('mass_mail', 'mass_post')

            ActiveModel = self.env[wizard.model] if wizard.model and hasattr(self.env[wizard.model], 'message_post') else self.env['mail.thread']
            if wizard.composition_mode == 'mass_post':
                # do not send emails directly but use the queue instead
                # add context key to avoid subscribing the author
                ActiveModel = ActiveModel.with_context(mail_notify_force_send=False, mail_create_nosubscribe=True)
            # wizard works in batch mode: [res_id] or active_ids or active_domain
            if mass_mode and wizard.use_active_domain and wizard.model:
                res_ids = self.env[wizard.model].search(ast.literal_eval(wizard.active_domain)).ids
            elif mass_mode and wizard.model and self._context.get('active_ids'):
                res_ids = self._context['active_ids']
            else:
                res_ids = [wizard.res_id]

            batch_size = int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size')) or self._batch_size
            sliced_res_ids = [res_ids[i:i + batch_size] for i in range(0, len(res_ids), batch_size)]

            if wizard.composition_mode == 'mass_mail' or wizard.is_log or (wizard.composition_mode == 'mass_post' and not wizard.notify):  # log a note: subtype is False
                subtype_id = False
            elif wizard.subtype_id:
                subtype_id = wizard.subtype_id.id
            else:
                subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')

            for res_ids in sliced_res_ids:
                # mass mail mode: mail are sudo-ed, as when going through get_mail_values
                # standard access rights on related records will be checked when browsing them
                # to compute mail values. If people have access to the records they have rights
                # to create lots of emails in sudo as it is consdiered as a technical model.
                batch_mails_sudo = self.env['mail.mail'].sudo()
                all_mail_values = wizard.get_mail_values(res_ids)

                for res_id, mail_values in all_mail_values.items():

                    if wizard.composition_mode == 'mass_mail':

                        batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
                        
                    else:

                        post_params = dict(

                            message_type=wizard.message_type,
                            subtype_id=subtype_id,
                            email_layout_xmlid=notif_layout,
                            add_sign=not bool(wizard.template_id),
                            mail_auto_delete=wizard.template_id.auto_delete if wizard.template_id else self._context.get('mail_auto_delete', True),
                            model_description=model_description
                            
                        )

                        post_params.update(mail_values)

                        if ActiveModel._name == 'mail.thread':

                            if wizard.model:

                                post_params['model'] = wizard.model
                                post_params['res_id'] = res_id

                            if not ActiveModel.message_notify(**post_params):

                                # if message_notify returns an empty record set, no recipients where found.
                                raise UserError(_("No recipient found."))
                                
                        elif post_params.get('email_cc', False) or post_params.get('email_bcc', False):
                            
                            to_mail = self.env['mail.mail'].sudo().create(mail_values)

                            if post_params.get('partner_ids'):

                                to_mail.recipient_ids = [(6, 0, mail_values.get('partner_ids'))]
                            
                            if post_params.get('partner_cc_ids'):

                                to_mail.recipient_cc_ids = [(6, 0, mail_values.get('recipient_cc_ids'))]

                            if post_params.get('partner_bcc_ids'):

                                to_mail.recipient_bcc_ids = [(6, 0, mail_values.get('recipient_bcc_ids'))]

                            if post_params.get('email_cc'):

                                to_mail.email_cc = mail_values.get('email_cc')
                            
                            if post_params.get('email_bcc'):

                                to_mail.email_bcc = mail_values.get('email_bcc')

                            to_mail.res_id = res_id
                            to_mail.model = ActiveModel._name
                            # to_mail.email_to = mail_values.get('partner_ids')
                            # to_mail.sudo().model = False

                            # raise UserError(str(to_mail) + "    - - -   " + str(mail_values) + "    - - -   " + str(post_params))

                            to_mail.send(auto_commit=auto_commit)
                        
                        else:

                            ActiveModel.browse(res_id).message_post(**post_params)

                if wizard.composition_mode == 'mass_mail':

                    batch_mails_sudo.send(auto_commit=auto_commit)
    