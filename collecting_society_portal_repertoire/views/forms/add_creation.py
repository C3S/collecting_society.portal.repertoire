# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.repertoire

import logging
import colander
import deform

from collecting_society_portal.models import (
    Tdb,
    WebUser
)
from collecting_society_portal.views.forms import FormController
from ...services import _
from ...models import (
    CollectingSociety,
    TariffCategory,
    Artist,
    Creation,
    CreationRole,
    Content
)
from .datatables import (
    ContentSequence,
    ContributionSequence,
    OriginalSequence,
    CreationTariffCategorySequence
)

log = logging.getLogger(__name__)


# --- Controller --------------------------------------------------------------

class AddCreation(FormController):
    """
    form controller for add creation
    """

    def controller(self):
        self.form = add_creation_form(self.request)
        if self.submitted():
            if self.validate():
                self.create_creation()
        else:
            self.init_creation()
        return self.response

    # --- Stages --------------------------------------------------------------

    # --- Conditions ----------------------------------------------------------

    # --- Actions -------------------------------------------------------------

    def init_creation(self):
        """
        initializes form with arguments passed via url from Content/Uploads
        """

        self.appstruct = {
            'metadata': {},
            'content': {}
        }
        # add metadata from content uuid, provided by upload form
        content = getattr(self.context, 'content', False)
        if content:
            # self.appstruct['content']['content'] = [(content.id,
            #                                          content.name)]
            self.appstruct['metadata']['title'] = content.metadata_title
            meta_artist = Artist.search_by_name(content.metadata_artist)
            if meta_artist:
                self.appstruct['metadata']['artist'] = meta_artist[0].id

        # render form with init data
        self.render(self.appstruct)

    @Tdb.transaction(readonly=False)
    def create_creation(self):
        web_user = self.request.web_user
        party = self.request.party

        log.debug(self.appstruct)

        # generate vlist
        _creation = {
            'title': self.appstruct['metadata']['title'],
            'artist': self.appstruct['metadata']['artist'],
            'entity_creator': party,
        }

        # creation tariff categories
        _ctcs = self.appstruct['metadata']['tariff_categories']
        if _ctcs:
            ctc_create = []
            # create creation tariff categories
            for _ctc in _ctcs:
                if _ctc['mode'] != "create":
                    continue
                tariff_category = TariffCategory.search_by_oid(
                    _ctc['category'])
                if not tariff_category:
                    continue
                collecting_society = CollectingSociety.search_by_oid(
                    _ctc['collecting_society'])
                if not collecting_society:
                    continue
                ctc_create.append({
                    'category': tariff_category.id,
                    'collecting_society': collecting_society.id
                    })
            # append actions
            _creation['tariff_categories'] = []
            if ctc_create:
                _creation['tariff_categories'].append(('create', ctc_create))

        # contributions
        _contributions = self.appstruct['contributions']['contributions']
        if _contributions:
            contributions_create = []
            for _contribution in _contributions:
                if _contribution['mode'] != "create":
                    continue
                _artist = _contribution['artist'][0]
                _cs = _contribution['collecting_society']
                _nrs = _contribution['neighbouring_rights_society']
                _type = _contribution['contribution_type']
                _role = _contribution['role']

                # create artist
                if _artist['mode'] == "create":
                    artist = Artist.create_foreign(
                        party, _artist['name'], _artist['email'],
                        group=False)
                    if not artist:
                        continue

                # add artist
                else:
                    artist = Artist.search_by_oid(_artist['oid'])
                    if not artist:
                        continue

                # prepare contribution
                create = {
                    'artist': artist.id,
                    'type': _contribution['contribution_type']
                }
                # type: text
                if _type == 'text' and _cs:
                    cs = CollectingSociety.search_by_oid(_cs)
                    if not cs:
                        continue
                    create['collecting_society'] = cs.id
                # type: composition
                if _type == 'composition' and _role:
                    role = CreationRole.search_by_oid(_role)
                    if not role:
                        continue
                    create['roles'] = [('add', [role.id])]
                # type: performance
                if _type == 'performance':
                    create['performance'] = _contribution['performance']
                    if _role:
                        role = CreationRole.search_by_oid(_role)
                        if not role:
                            continue
                        create['roles'] = [('add', [role.id])]
                    if _nrs:
                        nrs = CollectingSociety.search_by_oid(_nrs)
                        if not nrs:
                            continue
                        create['neighbouring_rights_society'] = nrs.id
                # append contribution
                contributions_create.append(create)

            # append actions
            _creation['contributions'] = []
            if contributions_create:
                _creation['contributions'].append(
                    ('create', contributions_create))

        # content
        if self.appstruct['content']['content']:
            _creation['content'] = []
            for content_listenty in self.appstruct['content']['content']:
                content = Content.search_by_code(content_listenty['code'])
                if content:
                    _creation['content'].append(('add', [content.id]))

        # create creation
        creations = Creation.create([_creation])

        # user feedback
        if not creations:
            log.info("creation add failed for %s: %s" % (web_user, _creation))
            self.request.session.flash(
                _(u"Creation could not be added: ") + _creation['title'],
                'main-alert-danger'
            )
            self.redirect()
            return
        creation = creations[0]
        log.info("creation add successful for %s: %s" % (web_user, creation))
        self.request.session.flash(
            _(u"Creation added: ") + creation.title
            + " (" + creation.code + ")", 'main-alert-success'
        )

        # redirect
        self.redirect()


# --- Validators --------------------------------------------------------------

def validate_content(node, values, **kwargs):  # multifield validator
    """Check if content is already assigned to another creation"""

    # Content.search_by_id()
    request = node.bindings["request"]
    contents = values["content"]["content"]
    if contents == [] or None:
        return
        # raise colander.Invalid(node, _(
        #     u"Please assign a uploaded file to this creation"))
    audio_count = 0
    sheet_count = 0
    edit_creation_code = getattr(request.context, 'code', None)
    for content_listenty in contents:
        c = Content.search_by_code(content_listenty['code'])
        if c.creation:  # selected content is already assigned some creation
            crco = c.creation.code  # creation code of content_listenty
            if (edit_creation_code is None or  # either in Add Creation or
                    edit_creation_code != crco):    # in Edit Creation and code
                raise colander.Invalid(    # doesn't fit the creation?
                    node, _(u"Content file ${coco} is "
                            "already assigned to creation ${crco}.",
                            mapping={'coco': c.code, 'crco': crco}))
        if c.category == 'audio':
            audio_count = audio_count + 1
        if c.category == 'sheet':
            sheet_count = sheet_count + 1
    if audio_count > 1 or sheet_count > 1:
        raise colander.Invalid(node, _(u"Only one uploaded content file "
                                       "for each file type (audio and sheet "
                                       "music)."))


# --- Options -----------------------------------------------------------------

# --- Widgets -----------------------------------------------------------------

@colander.deferred
def current_artists_select_widget(node, kw):
    request = kw.get('request')
    web_user = WebUser.current_web_user(request)
    artists = Artist.search_by_party(web_user.party.id)
    artist_options = [(artist.id, artist.name) for artist in artists]
    widget = deform.widget.Select2Widget(values=artist_options)
    return widget


# --- Fields ------------------------------------------------------------------

class TitleField(colander.SchemaNode):
    oid = "title"
    schema_type = colander.String


class FeaturedArtistField(colander.SchemaNode):
    oid = "artist"
    schema_type = colander.Integer
    widget = current_artists_select_widget


class LyricsField(colander.SchemaNode):
    oid = "lyrics"
    schema_type = colander.String
    widget = deform.widget.TextAreaWidget()
    missing = ""


# --- Schemas -----------------------------------------------------------------

class MetadataSchema(colander.Schema):
    title = _(u"Metadata")
    widget = deform.widget.MappingWidget(template='navs/mapping')
    working_title = TitleField(name='title', title=_(u"Working Title"))
    artist = FeaturedArtistField(title=_(u"Featured Artist"))
    tariff_categories = CreationTariffCategorySequence()


class ContributionsSchema(colander.Schema):
    title = _(u"Contributions")
    widget = deform.widget.MappingWidget(template='navs/mapping')
    contributions = ContributionSequence(title="", min_len=1)


class OriginalsSchema(colander.Schema):
    title = _(u"Derivation")
    widget = deform.widget.MappingWidget(template='navs/mapping')
    originals = OriginalSequence(title="")


class ContentSchema(colander.Schema):
    title = _(u"Content")
    widget = deform.widget.MappingWidget(template='navs/mapping')
    content = ContentSequence(title="", actions=['add'])


class LyricsSchema(colander.Schema):
    title = _(u"Lyrics")
    widget = deform.widget.MappingWidget(template='navs/mapping')
    lyrics = LyricsField()


class AddCreationSchema(colander.Schema):
    widget = deform.widget.FormWidget(template='navs/form', navstyle='tabs')
    metadata = MetadataSchema()
    contributions = ContributionsSchema()
    originals = OriginalsSchema()
    content = ContentSchema()
    lyrics = LyricsSchema()


# --- Forms -------------------------------------------------------------------

def add_creation_form(request):
    return deform.Form(
        schema=AddCreationSchema(validator=validate_content).bind(
            request=request),
        buttons=[
            deform.Button('submit', _(u"Submit"))
        ]
    )
