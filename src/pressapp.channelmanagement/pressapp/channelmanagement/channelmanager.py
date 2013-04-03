from five import grok
from Acquisition import aq_inner, aq_parent
from plone.directives import form

from zope import schema
from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName
from plone.app.contentlisting.interfaces import IContentListing
from plone.registry.interfaces import IRegistry
from pressapp.presscontent.pressrelease import IPressRelease
from pressapp.presscontent.pressinvitation import IPressInvitation

from pressapp.channelmanagement.channel import IChannel
from pressapp.channelmanagement.subscriber import ISubscriber

from pressapp.channelmanagement import MessageFactory as _


class IChannelManager(form.Schema):
    """
    Central managing unit for subscriber channels
    """
    channels = schema.List(
        title=_(u"Available Channels"),
        description=_(u"Update available channels. One entry per line"),
        required=False,
        value_type=schema.TextLine(
            title=_(u"Channel Title"),
        )
    )


class View(grok.View):
    grok.context(IChannelManager)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_channels = len(self.channels()) > 0
        self.has_subscribers = len(self.subscribers()) > 0
        self.subscriber_count = len(self.subscribers())
        self.key = 'pressapp.channelmanagement.channelList'

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

    def channel_counter(self):
        return len(self.channel_names())

    def channel_names(self):
        context = aq_inner(self.context)
        registry = queryUtility(IRegistry)
        if registry:
            records = registry[self.key]
        catalog = getToolByName(context, 'portal_catalog')
        channels = catalog.uniqueValuesFor('channel')
        names = []
        for channel in channels:
            info = {}
            info['channel'] = channel
            try:
                channelname = records[channel]
            except KeyError:
                channelname = channel
            info['channelname'] = channelname
            info['count'] = len(catalog.searchResults(
                                object_provides=ISubscriber.__identifier__,
                                channel=[channel]))
            names.append(info)
        return names

    def statistic_data(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        channels = catalog.uniqueValuesFor('channel')
        registry = queryUtility(IRegistry)
        if registry:
            records = registry['pressapp.channelmanagement.channelList']
        stats = []
        for channel in channels:
            channel_info = {}
            prs = catalog(object_provides=IPressRelease.__identifier__,
                          channel=[channel])
            pis = catalog(object_provides=IPressInvitation.__identifier__,
                          channel=[channel])
            subs = catalog(object_provides=ISubscriber.__identifier__,
                           channel=[channel])
            try:
                channelname = records[channel]
            except KeyError:
                channelname = channel
            channel_info['name'] = channelname
            channel_info['channel'] = channel
            channel_info['pr_count'] = len(prs)
            channel_info['pi_count'] = len(pis)
            channel_info['subscriber'] = len(subs)
            stats.append(channel_info)
        return stats


class ChannelInformation(grok.View):
    grok.context(IChannelManager)
    grok.require('cmf.ReviewPortalContent')
    grok.name('channel-information')

    def update(self):
        context = aq_inner(self.context)
        self.channelname = self.request.get('channelname', '')
        self.has_info = len(self.channel_info()) > 0
        self.parent_url = aq_parent(context).absolute_url()

    def channel_info(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        registry = queryUtility(IRegistry)
        if registry:
            records = registry['pressapp.channelmanagement.channelList']
        for value in records:
            if records[value] == self.channelname:
                channel = value
            else:
                channel = self.channelname
        results = catalog(object_provides=ISubscriber.__identifier__,
                          channel=channel,
                          sort_on='sortable_title')
        subscribers = IContentListing(results)
        return subscribers

    def usage_statistics(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        stats = {}
        prs = catalog(object_provides=IPressRelease.__identifier__,
                      channel=[self.channelname])
        stats['pr'] = len(prs)
        pis = prs = catalog(object_provides=IPressInvitation.__identifier__,
                            channel=[self.channelname])
        stats['pi'] = len(pis)
        return stats


class ChannelStatistics(grok.View):
    grok.context(IChannelManager)
    grok.require('cmf.ReviewPortalContent')
    grok.name('channel-statistics')

    def update(self):
        self.has_data = len(self.statistic_data()) > 0

    def statistic_data(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        channels = catalog.uniqueValuesFor('channel')
        registry = queryUtility(IRegistry)
        if registry:
            records = registry['pressapp.channelmanagement.channelList']
        stats = []
        for channel in channels:
            channel_info = {}
            prs = catalog(object_provides=IPressRelease.__identifier__,
                          channel=[channel])
            pis = catalog(object_provides=IPressInvitation.__identifier__,
                          channel=[channel])
            subs = catalog(object_provides=ISubscriber.__identifier__,
                           channel=[channel])
            try:
                channelname = records[channel]
            except KeyError:
                channelname = channel
            channel_info['name'] = channelname
            channel_info['channel'] = channel
            channel_info['pr_count'] = len(prs)
            channel_info['pi_count'] = len(pis)
            channel_info['subscriber'] = len(subs)
            stats.append(channel_info)
        return stats
