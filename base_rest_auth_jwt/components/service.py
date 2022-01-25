# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.component.core import AbstractComponent


class BaseRestService(AbstractComponent):
    _inherit = "base.rest.service"

    def to_openapi(self):
        openapi = super(BaseRestService, self).to_openapi()
        jwt_scheme = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "name": "jwt",
            "description": "Enter JWT Bearer Token ** only **",
        }
        security_definitions = openapi.get("securityDefinitions", {})
        security_definitions["jwt"] = jwt_scheme
        openapi["securityDefinitions"] = security_definitions
        return openapi
