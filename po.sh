pot-create -o collecting_society_portal_repertoire/locale/collecting_society_portal_repertoire.pot collecting_society_portal_repertoire
msgmerge --update collecting_society_portal_repertoire/locale/*/LC_MESSAGES/collecting_society_portal_repertoire.po collecting_society_portal_repertoire/locale/collecting_society_portal_repertoire.pot
poedit collecting_society_portal_repertoire/locale/de/LC_MESSAGES/collecting_society_portal_repertoire.po
msgfmt -o collecting_society_portal_repertoire/locale/de/LC_MESSAGES/collecting_society_portal_repertoire.mo collecting_society_portal_repertoire/locale/de/LC_MESSAGES/collecting_society_portal_repertoire.po
echo "You might want to restart the portal container now in order to see the new translations."
