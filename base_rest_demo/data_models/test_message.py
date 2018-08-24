# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base_rest.models import DataModel


class TestMessage(DataModel):
    _name = 'base_rest.test.message'

    text = fields.Char(
        help='The message to',
        required=True,
        default='Hello world'
    )

    is_important = fields.Boolean(
        help='True if the message is important'
    )

    type = fields.Selection(
        selection=[('warning', 'Warning'),
                   ('info', 'Info'),
                   ('error', 'Error')]
    )
    author = fields.Many2one(
        'base_rest.test.person'
    )
    followers = fields.Many2Many(
        'base_rest.test.person'
    )
