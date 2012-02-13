from Acquisition import aq_inner
from five import grok

from Products.CMFCore.utils import getToolByName

from Products.CMFCore.interfaces import IContentish
from plone.app.contentlisting.interfaces import IContentListing
from pressapp.channelmanagement.subscriber import ISubscriber
from pressapp.presscontent import MessageFactory as _


class RecipientList(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('recipient-list')

    def update(self):
        self.has_subscribers = len(self.subscriber_listing()) > 0

    def subscriber_listing(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        channels = context.channel
        subscribers = []
        for channelname in channels:
            results = catalog(object_provides=ISubscriber.__identifier__,
                              channel=[channelname],
                              sort_on='sortable_title')
            for item in results:
                info = {}
                info['name'] = item.Title
                info['email'] = item.email
                subscribers.append(info)
        return subscribers
