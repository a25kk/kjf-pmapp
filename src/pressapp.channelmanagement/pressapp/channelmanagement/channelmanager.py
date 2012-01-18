from five import grok
from Acquisition import aq_inner
from plone.directives import dexterity, form

from zope import schema
from z3c.form import group, field

from Products.CMFCore.utils import getToolByName
from plone.app.contentlisting.interfaces import IContentListing
from pressapp.channelmanagement.channel import IChannel
from pressapp.channelmanagement.subscriber import ISubscriber

from pressapp.channelmanagement import MessageFactory as _


class IChannelManager(form.Schema):
    """
    Central managing unit for subscriber channels
    """


class View(grok.View):
    grok.context(IChannelManager)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_channels = len(self.channels()) > 0
        self.has_subscribers = len(self.subscribers()) > 0

    def active_channel(self):
        channels = self.channels()
        return channels[0]

    def channels(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IChannel.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=1))
        return results

    def subscribers(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=ISubscriber.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=2),
                          sort_on='sortable_title')
        subscribers = IContentListing(results)
        return subscribers

    def channel_names(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        channels = catalog.uniqueValuesFor('channel')
        names = []
        for channel in channels:
            info = {}
            info['channel'] = channel
            info['count'] = len(catalog.searchResults(channel=[channel]))
            names.append(info)
        return names
