# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.repertoire

import colander
import deform
import logging

from collecting_society_portal.views.forms import FormController
from ...services import _

log = logging.getLogger(__name__)


# --- Controller --------------------------------------------------------------

class SearchArtistMember(FormController):
    """
    form controller for searching members to add to group artists
    """

    def controller(self):
        # hide search form, if creation form is active
        if self.submitted(form='CreateArtistMember'):
            return {}
        # add form
        self.form = search_artists_form(self.request)
        # if save search term is given, save into context
        if self.submitted() and self.validate(data=True):
            self.context.search_string = self.appstruct['name']
        # return response
        return self.response

    # --- Stages --------------------------------------------------------------

    # --- Conditions ----------------------------------------------------------

    # --- Actions -------------------------------------------------------------


# --- Validators --------------------------------------------------------------

# --- Options -----------------------------------------------------------------

# --- Fields ------------------------------------------------------------------

class NameField(colander.SchemaNode):
    oid = "name"
    schema_type = colander.String


# --- Schemas -----------------------------------------------------------------

class SearchArtistsSchema(colander.Schema):
    name = NameField(
        title=_(u"Name")
    )


# --- Forms -------------------------------------------------------------------

def search_artists_form(request):
    return deform.Form(
        schema=SearchArtistsSchema().bind(request=request),
        buttons=[
            deform.Button('search', _(u"Search artist"))
        ]
    )
