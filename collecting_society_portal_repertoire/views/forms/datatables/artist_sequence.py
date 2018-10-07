# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.repertoire

import logging

import colander
import deform

from collecting_society_portal.views.forms.datatables import (
    DatatableSequenceWidget
)

log = logging.getLogger(__name__)


def ignore_required_email(value):
    return value if value else "IGNORE@DUMMY.EMAIL"


# --- Fields ------------------------------------------------------------------

@colander.deferred
def artist_sequence_widget(node, kw):
    return DatatableSequenceWidget(
        request=kw.get('request'),
        template='datatables/artist_sequence'
    )


class ModeField(colander.SchemaNode):
    oid = "mode"
    schema_type = colander.String
    widget = deform.widget.HiddenWidget()


class NameField(colander.SchemaNode):
    oid = "name"
    schema_type = colander.String
    widget = deform.widget.TextInputWidget()


class CodeField(colander.SchemaNode):
    oid = "code"
    schema_type = colander.String
    widget = deform.widget.HiddenWidget()
    missing = ""


class DescriptionField(colander.SchemaNode):
    oid = "description"
    schema_type = colander.String
    widget = deform.widget.HiddenWidget()
    missing = ""


class EmailField(colander.SchemaNode):
    oid = "email"
    schema_type = colander.String
    widget = deform.widget.TextInputWidget()
    validator = colander.Email()
    preparer = [ignore_required_email]


# --- Schemas -----------------------------------------------------------------

class ArtistSchema(colander.Schema):
    mode = ModeField()
    name = NameField()
    description = DescriptionField()
    code = CodeField()
    email = EmailField()
    title = ""


class ArtistSequence(colander.SequenceSchema):
    artist = ArtistSchema()
    widget = artist_sequence_widget
