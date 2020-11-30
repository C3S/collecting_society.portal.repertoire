# For copyright and genre terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society_web

import logging

from portal_web.models import Tdb

log = logging.getLogger(__name__)


class CreationRight(Tdb):
    """
    Model wrapper for Tryton model object 'creation.right'
    """
    __name__ = 'creation.right'

    @classmethod
    def search(cls, domain, offset=None, limit=None, order=None,
               escape=False):
        """
        Searches creation rights by domain

        Args:
          domain (list): domain passed to tryton

        Returns:
          obj: list of creation rights
        """
        # prepare query
        if escape:
            domain = cls.escape_domain(domain)
        # search
        result = cls.get().search(domain, offset, limit, order)
        return result

    @classmethod
    def search_count(cls, domain, escape=False, active=True):
        """
        Counts creation rights by domain

        Args:
          domain (list): domain passed to tryton

        Returns:
          int: number of creation rights
        """
        # prepare query
        if escape:
            domain = cls.escape(domain)
        if active:
            domain.append(('active', 'in', (True, active)))
        # search
        result = cls.get().search_count(domain)
        return result


    @classmethod
    def create(cls, vlist):
        """
        Creates creation.right relations

        Args:
          vlist (list): list of dicts with attributes 
          to create creation.right relations::

            [
                {
                    'rightsholder': right_subject.id,
                    'rightsobject': creation.id,
                    'type_of_right': "copyright",
                    'contribution': "production",
                    'instruments': instruments_dict,
                },
                {
                    ...
                }
            ]

        Raises:
          KeyError: if required field is missing

        Returns:
          list: created creation.right relations
          None: if no object was created
        """
        log.debug('create CreationRight:\n{}'.format(vlist))
        result = cls.get().create(vlist)
        return result or None