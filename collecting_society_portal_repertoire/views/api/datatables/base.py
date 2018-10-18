# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.repertoire

import os
import colander

from pyramid.security import (
    Allow,
    DENY_ALL,
)

_prefix = 'datatables'


# --- methods -----------------------------------------------------------------

def get_cors_policy():
    return {
        'origins': os.environ['API_DATATABLES_CORS_ORIGINS'].split(","),
        'credentials': True
    }


def get_cors_headers():
    return ', '.join([
        'content-type',
    ])


# --- schemas -----------------------------------------------------------------

class OrderSchema(colander.MappingSchema):
    column = colander.SchemaNode(
        colander.Integer(), validator=colander.Range(0))
    dir = colander.SchemaNode(
        colander.String(), validator=colander.OneOf(['asc', 'desc']))


class OrdersSchema(colander.SequenceSchema):
    order = OrderSchema()


class SearchSchema(colander.MappingSchema):
    regex = colander.SchemaNode(
        colander.Boolean())
    value = colander.SchemaNode(
        colander.String(), missing="")


class ColumnSchema(colander.MappingSchema):
    data = colander.SchemaNode(
        colander.String(), missing="")
    name = colander.SchemaNode(
        colander.String())
    orderable = colander.SchemaNode(
        colander.Boolean())
    search = SearchSchema()
    searchable = colander.SchemaNode(
        colander.Boolean())


class ColumnsSchema(colander.SequenceSchema):
    column = ColumnSchema()


class DatatablesSchema(colander.MappingSchema):
    columns = ColumnsSchema()
    order = OrdersSchema()
    search = SearchSchema()
    draw = colander.SchemaNode(
        colander.Integer(), validator=colander.Range(0))
    start = colander.SchemaNode(
        colander.Integer(), validator=colander.Range(0))
    length = colander.SchemaNode(
        colander.Integer(), validator=colander.Range(0))


# --- resources ---------------------------------------------------------------

class DatatablesResource(object):

    def __init__(self, request):
        self.request = request

    def __acl__(self):
        # no webuser logged in
        if not self.request.user:
            return [DENY_ALL]
        # webuser logged in
        return [
            (
                Allow,
                self.request.unauthenticated_userid,
                ('read')
            ),
            DENY_ALL
        ]