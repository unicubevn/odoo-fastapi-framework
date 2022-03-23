# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from apispec import BasePlugin


class RestMethodSecurityPlugin(BasePlugin):
    def __init__(self, service):
        super(RestMethodSecurityPlugin, self).__init__()
        self._service = service

    def init_spec(self, spec):
        super(RestMethodSecurityPlugin, self).init_spec(spec)
        self.spec = spec
        self.openapi_version = spec.openapi_version

    def operation_helper(self, path=None, operations=None, **kwargs):
        if "jwt" not in self.spec.components._security_schemes:
            jwt_scheme = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "name": "jwt",
                "description": "Enter JWT Bearer Token ** only **",
            }
            self.spec.components.security_scheme("jwt", jwt_scheme)
        routing = kwargs.get("routing")
        if not routing:
            super(RestMethodSecurityPlugin, self).operation_helper(
                path, operations, **kwargs
            )
        if not operations:
            return
        default_auth = self.spec._params.get("default_auth")
        auth = routing.get("auth", default_auth)
        if auth == "public_or_default":
            auth = "public_or_" + default_auth
        if auth and (auth.startswith("jwt") or auth.startswith("public_or_jwt")):
            for _method, params in operations.items():
                security = params.setdefault("security", [])
                security.append({"jwt": []})
