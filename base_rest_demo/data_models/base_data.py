# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base_rest.models import DataModel


class BaseData(DataModel):
    """
    All DataModel will inherit from 'base.data'
    """
    _inherit = 'base.data'

    create_datatime = fields.Datetime()
