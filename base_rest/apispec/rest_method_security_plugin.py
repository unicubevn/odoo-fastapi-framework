# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from apispec import BasePlugin


class RestMethodSecurityPlugin(BasePlugin):
    """
    APISpec plugin to generate path security from a services method
    """

    def __init__(self, service, user_auths=("user",)):
        super(RestMethodSecurityPlugin, self).__init__()
        self._service = service
        self._supported_user_auths = user_auths

    def init_spec(self, spec):
        super(RestMethodSecurityPlugin, self).init_spec(spec)
        self.spec = spec
        self.openapi_version = spec.openapi_version

    def operation_helper(self, path=None, operations=None, **kwargs):
        if "user" not in self.spec.components._security_schemes:
            user_scheme = {"type": "apiKey", "in": "cookie", "name": "session_id"}
            self.spec.components.security_scheme("user", user_scheme)

        routing = kwargs.get("routing")
        if not routing:
            super(RestMethodSecurityPlugin, self).operation_helper(
                path, operations, **kwargs
            )
        if not operations:
            return
        auth = routing.get("auth", self.spec._params.get("default_auth"))
        is_user_auth = auth in self._supported_user_auths
        is_public_or_auth = auth and auth.startswith("public_or_")
        if is_user_auth or is_public_or_auth:
            for _method, params in operations.items():
                security = params.setdefault("security", [])
                if is_public_or_auth:
                    security.append({})
                if is_user_auth:
                    security.append({"user": []})
