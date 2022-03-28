# -*- coding: utf-8 -*-

from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super(IrConfigParameter, self).create(vals)
