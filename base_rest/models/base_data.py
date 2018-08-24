# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, excetions

from .data_model import DataModel


class BaseData(DataModel):
    """ The base.data model, which is implicitly inherited by all data
        models.
    """
    _name = 'base.data'

    @api.model
    def from_json(self, json_data):
        """
        Return an in memory recordset of data model initialized from the
        json data

        :param json_data:
        :return: new DataModel recordset
        """
        #return self.new(....)

    def to_json(self):
        result = []
        values = {}
        for record in self:
            try:
                values = {}
                if self._with_id_field:
                    values = {'id': record.id}
                for name, field in self._fields.items():
                    values[name] = field.convert_to_read(
                        record[name], record,use_name_get=False)
                result.append(values)
            except exceptions.MissingError:
                pass
        if len(self._ids) > 1:
            return result
        return values

    def validate(self):
        return True

    def to_json_schema(self):
        """ Return the definition of the model as json schema
        see http://json-schema.org/
        """