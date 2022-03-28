# -*- encoding: utf-8 -*-
# Copyright 2019 Odoo House
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Denmark - Accounting (E-conomic)',
    'summary': 'Danmarkspakken',
    'version': '13.0.1.0.0',
    'author': 'Odoo House ApS',
    'website': 'https://odoohouse.dk',
    'category': 'Localization',
    'description': """
    
Localization Module for Denmark
===============================

This is the module to manage the **e-conomic accounting chart for Denmark**.
  
**Modulet opsætter:**

- **Dansk e-conomic kontoplan**

- Dansk moms
        - 25% moms
        - Hotel moms 12,50%
        - Resturationsmoms 6,25%
        - Omvendt betalingspligt
        
- Konteringsgrupper
        - EU (Virksomhed)
        - EU (Privat)
        - 3.lande

- Finans raporter
        - Resulttopgørelse
        - Balance
        - Momsafregning
            - Afregning
            - Rubrik A, B og C
            
- **Anglo-Saxon regnskabsmetode**

.

Produkt setup:
==============

**Vare**

**Salgsmoms:**      Salgmoms 25%

**Salgskonto:**     1010 Salg af vare, m/moms

**Købsmoms:**       Købsmoms 25%

**Købskonto:**      2010 Direkte omkostninger vare, m/moms

.

**Ydelse**

**Salgsmoms:**      Salgmoms 25%, ydelser

**Salgskonto:**     1011 Salg af ydelser, m/moms

**Købsmoms:**       Købsmoms 25%, ydelser

**Købskonto:**      2011 Direkte omkostninger ydelser, m/moms

.

**Vare med omvendt betalingspligt**

**Salgsmoms:**      Salg omvendt betalingspligt

**Salgskonto:**     1050 Salg indland uden moms

**Købsmoms:**       Køb omvendt betalingspligt

**Købskonto:**      

.

**Hotelophold**

**Købsmoms:**       Hotel moms 12,50%, købsmoms

**Købskonto:**      

.

**Restauration**

**Købsmoms:**       Restaurationsmoms 6,25%, købsmoms

**Købskonto:**         

.
    
Copyright 2019 Odoo House ApS
    """,
    'images': ['images/modul_image.png'],
    'depends': ['account', 'base_iban', 'base_vat', ],
    'demo_xml': [],
    'data': [
        'data/account_group_data.xml',
        'data/l10n_dk_ec_chart_data.xml',
        'data/account.account.template.csv',
        'data/l10n_dk_ec_chart_post_data.xml',
        'data/account_tax_data.xml',
        'data/account_fiscal_position_data.xml',
        'data/account_chart_template_configuration_data.xml',
    ],
    'active': False,
    'installable': True
}
