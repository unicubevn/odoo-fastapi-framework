# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# @author Guewen Baconnier <guewen.baconnier@camptocamp.com>
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import json
import logging
import traceback

from six import raise_from
from werkzeug.urls import url_encode, url_join
from werkzeug.wrappers import Response

from odoo import exceptions, registry
from odoo.http import request

from odoo.addons.base_rest.http import JSONEncoder
from odoo.addons.component.core import AbstractComponent

from ..exceptions import (
    RESTServiceDispatchException,
    RESTServiceUserErrorException,
    RESTServiceValidationErrorException,
)

_logger = logging.getLogger(__name__)


def json_dump(data):
    """Encode data to JSON as we like."""
    return json.dumps(data, cls=JSONEncoder, indent=4, sort_keys=True, default=str)


class BaseRESTService(AbstractComponent):
    _inherit = "base.rest.service"
    # can be overridden to enable logging of requests to DB
    _log_calls_in_db = False

    def dispatch(self, method_name, *args, **kwargs):
        if not self._db_logging_active(method_name):
            return super(BaseRESTService, self).dispatch(method_name, *args, **kwargs)
        return self._dispatch_with_db_logging(method_name, *args, **kwargs)

    def _dispatch_with_db_logging(self, method_name, *args, **kwargs):
        try:
            with self.env.cr.savepoint():
                result = super(BaseRESTService, self).dispatch(
                    method_name, *args, **kwargs
                )
        except exceptions.UserError as orig_exception:
            self._dispatch_exception(
                method_name,
                RESTServiceUserErrorException,
                orig_exception,
                *args,
                **kwargs
            )
        except exceptions.ValidationError as orig_exception:
            self._dispatch_exception(
                method_name,
                RESTServiceValidationErrorException,
                orig_exception,
                *args,
                **kwargs
            )
        except Exception as orig_exception:
            self._dispatch_exception(
                method_name,
                RESTServiceDispatchException,
                orig_exception,
                *args,
                **kwargs
            )
        self._log_dispatch_success(method_name, result, *args, **kwargs)
        return result

    def _log_dispatch_success(self, method_name, result, *args, **kwargs):
        try:
            with self.env.cr.savepoint():
                log_kwargs = dict(kwargs, result=result)
                log_entry = self._log_call_in_db(
                    self.env, request, method_name, *args, **log_kwargs
                )
                if log_entry and not isinstance(result, Response):
                    log_entry_url = self._get_log_entry_url(log_entry)
                    result["log_entry_url"] = log_entry_url
        except Exception as e:
            _logger.exception("Rest Log Error Creation: %s", e)

    def _dispatch_exception(
        self, method_name, exception_klass, orig_exception, *args, **kwargs
    ):
        exc_msg, log_entry_url = None, None  # in case it fails below
        try:
            exc_msg = self._get_exception_message(orig_exception)
            tb = traceback.format_exc()
            log_kwargs = dict(
                dict(**kwargs), traceback=tb, orig_exception=orig_exception
            )
            with registry(self.env.cr.dbname).cursor() as cr:
                log_entry = self._log_call_in_db(
                    self.env(cr=cr), request, method_name, *args, **log_kwargs
                )
                log_entry_url = self._get_log_entry_url(log_entry)
        except Exception as e:
            _logger.exception("Rest Log Error Creation: %s", e)
        raise_from(exception_klass(exc_msg, log_entry_url), orig_exception)

    def _get_exception_message(self, exception):
        return getattr(exception, "name", str(exception))

    def _get_log_entry_url(self, entry):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        url_params = {
            "action": self.env.ref("rest_log.action_rest_log").id,
            "view_type": "form",
            "model": entry._name,
            "id": entry.id,
        }
        url = "/web?#%s" % url_encode(url_params)
        return url_join(base_url, url)

    @property
    def _log_call_header_strip(self):
        return ("Cookie", "Api-Key")

    def _log_call_in_db_values(self, _request, *args, **kw):
        httprequest = _request.httprequest
        headers = dict(httprequest.headers)
        for header_key in self._log_call_header_strip:
            if header_key in headers:
                headers[header_key] = "<redacted>"
        params = kw.get("params", {})
        if args:
            params = dict(params, args=args)
        result = kw.get("result")
        if isinstance(result, Response):
            result = {"content": "Binary response"}
        else:
            result = json_dump(result)
        error = kw.get("traceback")
        orig_exception = kw.get("orig_exception")
        exception_name = None
        exception_message = None
        if orig_exception:
            exception_name = orig_exception.__class__.__name__
            if hasattr(orig_exception, "__module__"):
                exception_name = orig_exception.__module__ + "." + exception_name
            exception_message = self._get_exception_message(orig_exception)
        return {
            "collection": self._collection,
            "request_url": httprequest.url,
            "request_method": httprequest.method,
            "params": json_dump(params),
            "headers": json_dump(headers),
            "result": result,
            "error": error,
            "exception_name": exception_name,
            "exception_message": exception_message,
            "state": "success" if result else "failed",
        }

    def _log_call_in_db(self, env, _request, method_name, *args, **kw):
        values = self._log_call_in_db_values(_request, *args, **kw)
        enabled_states = self._get_matching_active_conf(method_name)
        if not values or enabled_states and values["state"] not in enabled_states:
            return
        return env["rest.log"].sudo().create(values)

    def _db_logging_active(self, method_name):
        enabled = self._log_calls_in_db
        if not enabled:
            enabled = bool(self._get_matching_active_conf(method_name))
        return request and enabled and self.env["rest.log"].logging_active()

    def _get_matching_active_conf(self, method_name):
        return self.env["rest.log"]._get_matching_active_conf(
            self._collection, self._usage, method_name
        )
