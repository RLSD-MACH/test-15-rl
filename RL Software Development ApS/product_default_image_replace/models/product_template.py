from odoo import api, fields, models

class ProductTemplateInherit(models.Model):

    _inherit = 'product.template'

    def _get_placeholder_filename(self, field):
        image_fields = ['image_%s' % size for size in [1920, 1024, 512, 256, 128]]
        if field in image_fields:
            return 'product_default_image_replace/static/img/placeholder.png'
        return super()._get_placeholder_filename(field)