from five import grok

from Products.CMFCore.utils import getToolByName
from ZTUtils.Zope import make_query
from Products.CMFPlone.utils import safe_unicode
from Products.PythonScripts.standard import html_quote
from Products.CMFCore.interfaces import IContentish


class LiveSearch(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('live-search')

    def update(self):
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.ploneUtils = getToolByName(self.context, 'plone_utils')
        self.plone_view = self.context.restrictedTraverse('@@plone')
        props = getToolByName(self.context, 'portal_properties')
        self.site_props = getattr(props, 'site_properties', None)
        self.searchterm = None # this will be set by the get_results method
        self.useViewActions = self.site_props and self.site_props.getProperty(
                                'typesUseViewActionInListings', []) or []
        self.MAX_TITLE = 29
        self.MAX_DESCRIPTION = 93
        self.read_direction = self.context.restrictedTraverse(
            '@@plone_portal_state').is_rtl() and 'rtl' or 'ltr'

    def quote_bad_chars(self, s):

        def quotestring(s):
            return '"%s"' % s
        bad_chars = ["(", ")"]
        for char in bad_chars:
            s = s.replace(char, quotestring(char))
        return s

    def get_results(self):
        """ Returns the results found in portal_catalog for query 'q'.
        @param: 'q': the query that s searched for
        @param: 'limit': what to limit results list to (default 10)
        @param: 'path': constrain only to path (default None)
        """
        query_string = self.request.get('q', None)
        if query_string != None:
            limit = self.request.get('limit', 10)
            path = self.request.get('path', None)

            for char in '?-+*':
                query_string = query_string.replace(char, ' ')

            anded_parts = " AND ".join(query_string.split())
            anded_parts = self.quote_bad_chars(anded_parts)+'*'
            self.searchterm = make_query({'searchterm': anded_parts})

            query = {}
            query['SearchableText'] = anded_parts
            query['portal_type'] = self.ploneUtils.getUserFriendlyTypes()
            if path:
                query['path'] = path

            return self.catalog(query)[:limit]

    def get_icon(self, result):
        """Returns the icon object for a given result"""
        return self.plone_view.getIcon(result)

    def get_url(self, result):
        """Returns the url to the result"""
        url = result.getURL()
        if result.portal_type in self.useViewActions:
            url += '/view'
        return self.searchterm and url + '?'+self.searchterm or url

    def get_title(self, result):
        """Returns the title for the result"""
        return safe_unicode(self.ploneUtils.pretty_title_or_id(result))

    def get_display_title(self, result):
        """Returns a title suitable for display."""
        title = self.get_title(result)
        if len(title) > self.MAX_TITLE:
            return ''.join((title[:self.MAX_TITLE], '...'))
        return title

    def get_description(self, result):
        """Returns a displayable description"""
        description = safe_unicode(result.Description)
        if len(description) > self.MAX_DESCRIPTION:
            description = ''.join((description[:self.MAX_DESCRIPTION], '...'))
        return html_quote(description)
