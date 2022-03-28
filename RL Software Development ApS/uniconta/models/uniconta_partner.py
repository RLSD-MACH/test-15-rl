from odoo import api, fields, models


class UnicontaPartner(models.Model):
    
    _name = 'uniconta.partner'
    _description = 'Uniconta Partner'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    uniconta_row_id = fields.Integer(string='Row ID')
    uniconta_keystr = fields.Char(string='Key String')    
    uniconta_firm_id = fields.Many2one('uniconta.firm', string='Firm')

    account = fields.Char(string='account')
    # active = fields.Char(string='active')
    address1 = fields.Char(string='address1')
    address2 = fields.Char(string='address2')
    address3 = fields.Char(string='address3')
    balancemethod = fields.Char(string='balancemethod')
    bankaccounttype = fields.Char(string='bankaccounttype')
    blocked = fields.Char(string='blocked')
    city = fields.Char(string='city')
    companyid = fields.Char(string='companyid')
    companyregno = fields.Char(string='companyregno')
    contactemail = fields.Char(string='contactemail')
    contactperson = fields.Char(string='contactperson')
    country = fields.Char(string='country')
    countryname = fields.Char(string='countryname')
    created = fields.Char(string='created')
    creditmax = fields.Char(string='creditmax')
    curbalance = fields.Char(string='curbalance')
    curbalancecur = fields.Char(string='curbalancecur')
    currency = fields.Char(string='currency')
    deliveryaddress1 = fields.Char(string='deliveryaddress1')
    deliveryaddress2 = fields.Char(string='deliveryaddress2')
    deliveryaddress3 = fields.Char(string='deliveryaddress3')
    deliverycity = fields.Char(string='deliverycity')
    deliverycountry = fields.Char(string='deliverycountry')
    deliverycountryname = fields.Char(string='deliverycountryname')
    deliveryname = fields.Char(string='deliveryname')
    deliveryzipcode = fields.Char(string='deliveryzipcode')
    directdebitactive = fields.Char(string='directdebitactive')
    ean = fields.Char(string='ean')
    eeisnotvatdeclorg = fields.Char(string='eeisnotvatdeclorg')
    emaildocuments = fields.Char(string='emaildocuments')
    enddiscountpct = fields.Char(string='enddiscountpct')
    group = fields.Char(string='group')
    hasdocs = fields.Char(string='hasdocs')
    hasnotes = fields.Char(string='hasnotes')
    invoiceemail = fields.Char(string='invoiceemail')
    invoiceinxml = fields.Char(string='invoiceinxml')
    keyname = fields.Char(string='keyname')
    # keystr = fields.Char(string='keystr')
    lastinvoice = fields.Char(string='lastinvoice')
    layoutgroup = fields.Char(string='layoutgroup')
    linediscountpct = fields.Char(string='linediscountpct')
    mobilphone = fields.Char(string='mobilphone')
    overdue = fields.Char(string='overdue')
    overduecur = fields.Char(string='overduecur')
    payment = fields.Char(string='payment')
    paymentfee = fields.Char(string='paymentfee')
    phone = fields.Char(string='phone')
    pricegroup = fields.Char(string='pricegroup')
    pricelist = fields.Char(string='pricelist')
    pricesinclvat = fields.Char(string='pricesinclvat')
    # rowid = fields.Char(string='rowid')
    updatedat = fields.Char(string='updatedat')
    userattachment = fields.Char(string='userattachment')
    userfields = fields.Char(string='userfields')
    userlangaugeid = fields.Char(string='userlangaugeid')
    userlanguage = fields.Char(string='userlanguage')
    usernote = fields.Char(string='usernote')
    vat = fields.Char(string='vat')
    vatnumber = fields.Char(string='vatnumber')
    vatzone = fields.Char(string='vatzone')
    www = fields.Char(string='www')
    zipcode = fields.Char(string='zipcode')
    paymentid = fields.Char(string='paymentid')
    paymentmethod = fields.Char(string='paymentmethod')
    postingaccount = fields.Char(string='postingaccount')
    swift = fields.Char(string='swift') 



    res_partner_id = fields.Many2one('res.partner', string='Contact')

    active = fields.Boolean(required=True, string='Active', default=True)

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   

    def action_create_partner_in_odoo(self):

        for row in self:
            
            if row.res_partner_id:

                new_values = row._get_partner_values()

                try:

                    row.res_partner_id.write(new_values)
                    row.active = False

                except:

                    continue
                

            else:
                    
                new_values = row._get_partner_values()

                try:

                    new_partner = self.env['res.partner'].create(new_values)

                    row.res_partner_id = new_partner.id
                    row.active = False

                except:

                    continue            
                
    
    def _get_partner_values(self):
        
        countryid = False

        if self.countryname:
            matches = self.env['res.country'].search([['name','=',self.countryname]])

            if len(matches) == 1:
                countryid = matches[0].id

        currencyid = False

        if self.currency:
            matches = self.env['res.currency'].search([['name','=',self.currency]])

            if len(matches) == 1:
                currencyid = matches[0].id

        adresses = []

        if self.address2:

            adresses.append(self.address2)

        if self.address3:

            adresses.append(self.address3)

        emails =  []

        if self.contactemail:

            emails.append(self.contactemail)

        if self.invoiceemail:

            emails.append(self.invoiceemail)

        if self.countryname == 'Denmark' and self.companyregno:
            if len(self.companyregno) == 8:
                self.companyregno = 'DK' + str(self.companyregno)

        values = {

            'company_type': 'company',
            'name': self.name,
            'vat': self.companyregno,
            'phone': self.phone,
            'mobile': self.mobilphone,
            'ref': self.account,
            'street': self.address1,
            'street2': " ".join(adresses),
            'city': self.city,
            'email': ";".join(emails),
            'zip': self.zipcode,
            'website': self.www,
            'country_id': countryid,
            'currency_id': currencyid,
            'credit_limit': self.creditmax,

        }

        # mapping = [

        #     ('blocked','blocked'),
        #     ('contactperson','contactperson'),
        #     ('deliveryaddress1','deliveryaddress1'),
        #     ('deliveryaddress2','deliveryaddress2'),
        #     ('deliveryaddress3','deliveryaddress3'),
        #     ('deliverycity','deliverycity'),
        #     ('deliverycountry','deliverycountry'),
        #     ('deliverycountryname','deliverycountryname'),
        #     ('deliveryname','deliveryname'),
        #     ('deliveryzipcode','deliveryzipcode'),
        #     ('directdebitactive','directdebitactive'),
        #     ('ean','ean'),
        #     ('eeisnotvatdeclorg','eeisnotvatdeclorg'),
        #     ('emaildocuments','emaildocuments'),
        #     ('enddiscountpct','enddiscountpct'),
        #     ('group','group'),
        #     ('linediscountpct','linediscountpct'),
        #     ('overdue','overdue'),
        #     ('overduecur','overduecur'),
        #     ('payment','payment'),
        #     ('paymentfee','paymentfee'),
        #     ('pricegroup','pricegroup'),
        #     ('pricelist','pricelist'),
        #     ('pricesinclvat','pricesinclvat'),
        #     ('userlangaugeid','userlangaugeid'),
        #     ('userlanguage','userlanguage'),
        #     ('vatzone','vatzone'),
        #     ('paymentid','paymentid'),
        #     ('paymentmethod','paymentmethod'),
        #     ('postingaccount','postingaccount'),
        #     ('swift','swift'), 
        #     ]

        return values