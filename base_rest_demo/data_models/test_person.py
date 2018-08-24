# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base_rest.models import DataModel


class TestPerson(DataModel):
    """ Person informations
    """
    _name = 'base_rest.test.person'

    first_name = fields.Char(
        help='The person first name',
        required=True
    )

    las_name = fields.Char(
        help='The person last name'
    )
