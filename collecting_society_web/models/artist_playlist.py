# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society_web

import logging

from portal_web.models import Tdb, MixinSearchById

log = logging.getLogger(__name__)


class ArtistPlaylist(Tdb, MixinSearchById):
    """
    Model wrapper for Tryton model object 'artist.playlist'
    """
    __name__ = 'artist.playlist'
