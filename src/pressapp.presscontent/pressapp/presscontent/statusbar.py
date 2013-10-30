import datetime
from five import grok
from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName

from Products.CMFCore.interfaces import IContentish
from plone.app.contentlisting.interfaces import IContentListing


class StatusView(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('status-view')

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()
        self.has_modifications = len(self.modified_content()) > 0

    def modified_content(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        login_time = member.getProperty('login_time', '')
        query_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
        results = catalog(path='/'.join(context.getPhysicalPath()),
                          modified=dict(query=[login_time, query_time],
                                        range='minmax'),
                          sort_on='modified')
        results = IContentListing(results)
        return results
