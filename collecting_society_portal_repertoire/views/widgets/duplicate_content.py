# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.repertoire

from pyramid.renderers import render

from ...services import _


class DuplicateContentWidget(request):

    def root(self):
        heading = _(u'Duplicates: ' + duplicate_content_count(request.user))
        body = render(
            '../../templates/widgets/duplicate_content.pt',
            {'news': request.context.registry['content']['duplicate_content']},
            request=request
        )

    def duplicate_content_count(user):
        return Content.search_duplicates_by_user(user.id)
