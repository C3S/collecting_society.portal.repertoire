# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society_web

import os
import logging

from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import (
    view_config,
    view_defaults
)

from portal_web.models import Tdb
from portal_web.views import ViewBase

from ..services import _
from ..models import Device
from .forms import (
    AddDevice,
    EditDevice
)

log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.DevicesResource')
class DevicesViews(ViewBase):

    @view_config(
        name='',
        renderer='../templates/device/list.pt',
        permission='list_devices')
    def list(self):
        return {}

    @view_config(
        name='add',
        renderer='../templates/device/add.pt',
        permission='add_device')
    def add(self):
        self.register_form(AddDevice)
        return self.process_forms()


@view_defaults(
    context='..resources.DeviceResource')
class DeviceViews(ViewBase):

    @view_config(
        name='',
        renderer='../templates/device/show.pt',
        permission='view_device')
    def show(self):
        return {}

    @view_config(
        name='edit',
        permission='edit_device')
    def edit(self):
        self.register_form(EditDevice)
        return self.process_forms()

    @view_config(
        name='delete',
        decorator=Tdb.transaction(readonly=False),
        permission='delete_device')
    def delete(self):
        name = self.context.device.name
        Content.delete([self.context.device])
        log.info("device delete successful for %s: %s (%s)" % (
            self.request.web_user, name, self.context.code
        ))
        self.request.session.flash(
            _(u"Device deleted: ") + name + ' (' + self.context.code + ')',
            _(u"Device deleted: ${cona} (${coco})",
              mapping={'cona': name, 'coco': self.context.code}),
            'main-alert-success'
        )
        return self.redirect('..')
