# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society_web

import logging

import colander
import deform

from pyramid.i18n import get_localizer

from portal_web.views.forms.datatables import (
    DatatableSequence,
    DatatableSequenceWidget
)

from . import ArtistIndividual, CreationRightSequence
from ....services import _
from ....models import CreationRightsholder

log = logging.getLogger(__name__)


def prepare_ignored(value):
    # workaround for conditinally required fields, as form validators are not
    # processed, if a normal required field is missing
    return value if value else "IGNORED"


def prepare_required(value):
    # oid required for add/edit
    return value if value else "IGNORED"


# --- Options -----------------------------------------------------------------


# --- Fields ------------------------------------------------------------------

@colander.deferred
def creation_rightsholder_sequence_widget(node, kw):
    request = kw.get('request')
    # return widget
    return DatatableSequenceWidget(
        request=request,
        template='datatables/creation_rightsholder_sequence',
        # source_data=source_data,
        # source_data_total=total
    )


class ModeField(colander.SchemaNode):
    oid = "mode"
    schema_type = colander.String
    widget = deform.widget.HiddenWidget()
    validator = colander.OneOf(
        ['create', 'edit'])


# --- Schemas -----------------------------------------------------------------


class CreationRightsholderSchema(colander.Schema):
    mode = ModeField()
    subject = ArtistIndividual(title=_(u"Rightsholder"))
    rights = CreationRightSequence(min_len=1)
    preparer = [prepare_required]
    title = ""


class CreationRightsholderSequence(DatatableSequence):
    creation_rightsholder_sequence = CreationRightsholderSchema()
    widget = creation_rightsholder_sequence_widget
    actions = ['create', 'edit']
