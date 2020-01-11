# coding=utf-8

# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society_web

"""
Functions to include resources/views and register content by the plugin system.

The following functions are called by convention on app creation:

- web_resources
- web_registry
- web_views
- api_views
"""

import logging

from portal_web.resources import (
    FrontendResource,
    BackendResource,
    ProfileResource,
    DebugResource
)

from .services import (
    _,
    C3SMembershipApiClient
)
from .resources import (
    ArtistsResource,
    ReleasesResource,
    CreationsResource,
    RepertoireResource,
    UseworkResource,
    FilesResource,
    DebugC3sMembershipApiResource
)
from .views.widgets import (
    MissingArtistsWidget,
    MissingContentWidget,
    MissingReleasesWidget,
    RejectedContentWidget,
    OrphanedContentWidget,
    UncommitedContentWidget,
    UnprocessedContentWidget
)

log = logging.getLogger(__name__)


def web_resources(config):
    """
    Extends the resource tree for the web service.

    Note:
        The function is called by the plugin system, when the app is created.

    Args:
        config (pyramid.config.Configurator): App config

    Returns:
        None
    """
    BackendResource.add_child(ProfileResource)
    BackendResource.add_child(RepertoireResource)
    BackendResource.add_child(UseworkResource)

    RepertoireResource.add_child(FilesResource)
    RepertoireResource.add_child(ArtistsResource)
    RepertoireResource.add_child(ReleasesResource)
    RepertoireResource.add_child(CreationsResource)

    UseworkResource.add_child(FilesResource)

    DebugResource.add_child(DebugC3sMembershipApiResource)


def web_registry(config):
    """
    Extends the registry for content elements for the web service.

    Note:
        The function is called by the plugin system, when the app is created.

    Args:
        config (pyramid.config.Configurator): App config

    Returns:
        None
    """
    settings = config.get_settings()

    # Metadata shared by Frontend and Backend
    def meta(request):
        return {
            'title': _(u'C3S - Repertoire'),
            'keywords': _(u'c3s,repertoire'),
            'description': _(u'registration of repertoire for C3S'),
            'languages': [
                {
                    'id': 'en',
                    'name': _(u'english'),
                    'icon': request.static_path(
                                'portal_web:'
                                'static/img/en.png')},
                {
                    'id': 'de',
                    'name': _(u'deutsch'),
                    'icon': request.static_path(
                                'portal_web:'
                                'static/img/de.png')},
                # {
                #     'id': 'es',
                #     'name': _(u'español'),
                #     'icon': request.static_path(
                #                 'portal_web:'
                #                 'static/img/es.gif')}
            ]
        }

    @FrontendResource.extend_registry
    def frontend(self):
        reg = self.dict()
        # meta
        reg['meta'] = meta(self.request)
        # css
        reg['static']['css'] = [
            self.request.static_path(
                'collecting_society_web:'
                'static/css/frontend.css')
        ]
        # favicon
        reg['static']['favicon'] = self.request.static_path(
            'collecting_society_web:static/img/favicon.png')
        # logo
        reg['static']['logo'] = self.request.static_path(
            'collecting_society_web:static/img/logo-c3s.png')
        # services
        reg['services']['c3smembership'] = C3SMembershipApiClient(
            base_url=settings['api.c3smembership.url'],
            version=settings['api.c3smembership.version'],
            api_key=settings['api.c3smembership.api_key'])
        # top menue
        reg['menues']['top'] = []
        if reg['services']['c3smembership'].is_connected():
            reg['menues']['top'] += [
                {
                    'name': _(u'register'),
                    'page': 'register'}
            ]
        reg['menues']['top'] += [
            {
                'name': _(u'survey'),
                'page': 'survey'},
            {
                'name': _(u'bug hunters'),
                'page': 'bughunters'},
            {
                'name': _(u'caution'),
                'page': 'caution'},
            {
                'name': _(u'terms'),
                'page': 'terms'}
        ]
        return reg

    @BackendResource.extend_registry
    def backend(self):
        reg = self.dict()
        # meta
        reg['meta'] = meta(self.request)
        # css
        reg['static']['css'] = [
            self.request.static_path(
                'portal_web:'
                'static/lib/DataTables/datatables.min.css'),
            self.request.static_path(
                'collecting_society_web:'
                'static/css/backend.css'),
        ]
        # js head
        reg['static']['js']['head'] = [
            {
                'src':  self.request.static_path(
                            'portal_web:'
                            'static/lib/JavaScript-Templates/js/tmpl.min.js')},
            {
                'src':  self.request.static_path(
                            'portal_web:'
                            'static/lib/DataTables/datatables.min.js')},
            {
                'src':  self.request.static_path(
                            'portal_web:'
                            'static/js/deform.datatables.widget.js')},
        ]
        # favicon
        reg['static']['favicon'] = self.request.static_path(
            'collecting_society_web:static/img/favicon.png')
        # logo
        reg['static']['logo'] = self.request.static_path(
            'collecting_society_web:static/img/logo-c3s.png')
        # main menue
        reg['menues']['roles'] = [
            {
                'name': _(u'Repertoire'), 'active': RepertoireResource,
                'url':  self.request.resource_path(
                            RepertoireResource(self.request), '')},
            {
                'name': _(u'Use Work'), 'active': UseworkResource,
                'url':  self.request.resource_path(
                            UseworkResource(self.request), '')}
        ]
        # top menue
        reg['menues']['top'] = [
            {
                'name': _(u'Profile'),
                'url':  self.request.resource_path(
                            BackendResource(self.request), 'profile')},
            {
                'name': _(u'Help'),
                'url':  self.request.resource_path(
                            BackendResource(self.request), 'help')},
            {
                'name': _(u'Contact'),
                'url':  self.request.resource_path(
                            BackendResource(self.request), 'contact')},
            {
                'name': _(u'Terms'),
                'url':  self.request.resource_path(
                            BackendResource(self.request), 'terms')},
            {
                'name': _(u'Logout'),
                'url':  self.request.resource_path(
                            BackendResource(self.request), 'logout')}
        ]
        # main menue
        reg['menues']['main'] = [
            {
                'name': _(u'Dashboard'),
                'url':  self.request.resource_path(
                            RepertoireResource(self.request), 'dashboard'),
                'icon': self.request.static_path(
                            'collecting_society_web:'
                            'static/img/element-icon-dashboard.png')},
            {
                'name': _(u'Files'),
                'url':  self.request.resource_path(
                            FilesResource(self.request)),
                'icon': self.request.static_path(
                            'collecting_society_web:'
                            'static/img/element-icon-upload.png')},
            {
                'name': _(u'Artists'),
                'url':  self.request.resource_path(
                            ArtistsResource(self.request)),
                'icon': self.request.static_path(
                            'collecting_society_web:'
                            'static/img/element-icon-soloartists.png')},
            {
                'name': _(u'Creations'),
                'url':  self.request.resource_path(
                            CreationsResource(self.request)),
                'icon': self.request.static_path(
                            'collecting_society_web:'
                            'static/img/element-icon-songs.png')},
            {
                'name': _(u'Releases'),
                'url':  self.request.resource_path(
                            ReleasesResource(self.request)),
                'icon': self.request.static_path(
                            'collecting_society_web:'
                            'static/img/element-icon-releases.png')},
        ]
        # widgets content-right
        reg['widgets']['content-right'] = [
            # news_widget
        ]
        return reg

    @RepertoireResource.extend_registry
    def repertoire(self):
        reg = self.dict()
        reg['widgets']['dashboard-central-widgets'] = [
            MissingArtistsWidget(self.request),
            MissingContentWidget(self.request),
            MissingReleasesWidget(self.request),
            RejectedContentWidget(self.request),
            OrphanedContentWidget(self.request),
            # UncommitedContentWidget(self.request),
            UnprocessedContentWidget(self.request),
        ]
        return reg

    @FilesResource.extend_registry
    def upload(self):
        reg = self.dict()
        jfu = 'portal_web:static/lib/jQuery-File-Upload/'
        # css
        reg['static']['css'] = [
            self.request.static_path(
                'collecting_society_web:'
                'static/css/backend.css'),
            self.request.static_path(
                jfu + 'css/jquery.fileupload.css'),
            self.request.static_path(
                jfu + 'css/jquery.fileupload-ui.css')
        ]
        # js
        reg['static']['js']['body'] = [
            {
                "src": self.request.static_path(
                    jfu + 'js/vendor/jquery.ui.widget.js')},
            {
                "src": self.request.static_path(
                    'portal_web:'
                    'static/lib/JavaScript-Load-Image/js/'
                    'load-image.all.min.js')},
            {
                "src": self.request.static_path(
                    jfu + 'js/jquery.iframe-transport.js')},
            {
                "src": self.request.static_path(
                    jfu + 'js/jquery.fileupload.js')},
            {
                "src": self.request.static_path(
                    jfu + 'js/jquery.fileupload-process.js')},
            {
                "src": self.request.static_path(
                    jfu + 'js/jquery.fileupload-audio.js')},
            {
                "src": self.request.static_path(
                    jfu + 'js/jquery.fileupload-validate.js')},
            {
                "src": self.request.static_path(
                    jfu + 'js/jquery.fileupload-ui.js')},
            {
                "src": self.request.static_path(
                    'collecting_society_web:'
                    'static/js/jquery.fileupload.init.js')},
            {
                "src": self.request.static_path(
                    'portal_web:static/js/portal.js')},
        ]
        return reg


def web_views(config):
    """
    Adds the views for the web service.

    Note:
        The function is called by the plugin system, when the app is created.

    Args:
        config (pyramid.config.Configurator): App config

    Returns:
        None
    """
    config.add_static_view('static/repertoire', 'static', cache_max_age=3600)
    config.scan(ignore='.views.api')


def api_views(config):
    """
    Adds the views for the api service.

    Note:
        The function is called by the plugin system, when the app is created.

    Args:
        config (pyramid.config.Configurator): App config

    Returns:
        None
    """

    # routes
    # ...

    # views
    config.add_static_view(
        'static/repertoire', 'static', cache_max_age=3600,
        environment='development'
    )
    config.scan('.views.api')
