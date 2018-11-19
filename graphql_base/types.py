# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import graphene

from odoo import fields


def odoo_attr_resolver(attname, default_value, root, info, **args):
    """An attr resolver that converts False to None.

    Except for Odoo Boolean fields.

    This is necessary because Odoo null values are often represented
    as False, and graphene would convert a String field with value False
    to "false".
    """
    value = getattr(root, attname, default_value)
    if value is False:
        if hasattr(root, "_fields"):
            field = root._fields.get(attname)
            if not isinstance(field, fields.Boolean):
                return None
    return value


class OdooObjectType(graphene.ObjectType):
    """A graphene ObjectType with an Odoo aware default resolver."""

    @classmethod
    def __init_subclass_with_meta__(cls, default_resolver=None, **options):
        if default_resolver is None:
            default_resolver = odoo_attr_resolver

        return super(OdooObjectType, cls).__init_subclass_with_meta__(
            default_resolver=default_resolver, **options
        )
