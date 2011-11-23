from zope.component import queryUtility
from zope.i18n.locales import locales
from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer
from plone.i18n.normalizer.interfaces import IURLNormalizer

def addPressPortalContent(p):
    """ Setup the press application language and add 
        a press center folder as member folder.
        Note: most of the language specific code is borrowed
        from the Products.CMFPlone default profile.
    """
    
    existing = p.keys()
    language = p.Language()
    parts = (language.split('-') + [None, None])[:3]
    locale = locales.getLocale(*parts)
    target_language = base_language = locale.id.language

    # If we get a territory, we enable the combined language codes
    use_combined = False
    if locale.id.territory:
        use_combined = True
        target_language += '_' + locale.id.territory

    # As we have a sensible language code set now, we disable the
    # start neutral functionality
    tool = getToolByName(p, "portal_languages")
    pprop = getToolByName(p, "portal_properties")
    sheet = pprop.site_properties

    tool.manage_setLanguageSettings(language,
        [language],
        setUseCombinedLanguageCodes=use_combined,
        startNeutral=False)

    # Set the first day of the week, defaulting to Sunday, as the
    # locale data doesn't provide a value for English. European
    # languages / countries have an entry of Monday, though.
    calendar = getToolByName(p, "portal_calendar", None)
    if calendar is not None:
        first = 6
        gregorian = locale.dates.calendars.get(u'gregorian', None)
        if gregorian is not None:
            first = gregorian.week.get('firstDay', None)
            # on the locale object we have: mon : 1 ... sun : 7
            # on the calendar tool we have: mon : 0 ... sun : 6
            if first is not None:
                first = first - 1

        calendar.firstweekday = first

    # Enable visible_ids for non-latin scripts

    # See if we have an url normalizer
    normalizer = queryUtility(IURLNormalizer, name=target_language)
    if normalizer is None:
        normalizer = queryUtility(IURLNormalizer, name=base_language)

    # If we get a script other than Latn we enable visible_ids
    if locale.id.script is not None:
        if locale.id.script.lower() != 'latn':
            sheet.visible_ids = True

    # If we have a normalizer it is safe to disable the visible ids
    if normalizer is not None:
        sheet.visible_ids = False
    
    if 'presse-center' not in existing:
        item = createContentInContainer(p, 'pressapp.presscontent.presscenter',
                             id="presse-center",
                             title=u"Presse Center")
        if base_language != 'en':
            item.setLanguage(language)
        item.reindexObject()
    mtool = getToolByName(p, 'portal_membership')
    mtool.memberareaCreationFlag = 1
    mtool.setMembersFolderById('presse-center')
    mtool.setMemberAreaType('pressapp.presscontent.pressroom')


def importVarious(context):
    """ Miscellanous steps import handle """
    
    if context.readDataFile('pressapp.presscontent-various.txt') is None:
        return
    portal = context.getSite()
    #addPressPortalContent(portal)
