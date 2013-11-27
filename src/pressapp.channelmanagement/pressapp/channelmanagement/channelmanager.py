from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl import Unauthorized
from five import grok
from plone import api
from zope import schema
from zope.component import queryUtility
from zope.component import getMultiAdapter

from plone.directives import form
from zope.lifecycleevent import modified

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.app.contentlisting.interfaces import IContentListing
from Products.statusmessages.interfaces import IStatusMessage
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

    def channel_title(self):
        channel = self.channelname
        registry = queryUtility(IRegistry)
        if registry:
            records = registry['pressapp.channelmanagement.channelList']
        try:
            channelname = records[channel]
        except KeyError:
            channelname = channel
        return channelname

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


class ChannelCreate(grok.View):
    grok.context(IChannelManager)
    grok.require('cmf.ReviewPortalContent')
    grok.name('channel-create')

    def update(self):
        self.key = 'pressapp.channelmanagement.channelList'
        context = aq_inner(self.context)
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            form = self.request.form
            cname = form['channelname']
            newkey = queryUtility(IIDNormalizer).normalize(cname)
            if type(newkey) == str:
                clean_key = unicode(newkey, "utf-8", errors="ignore")
            else:
                clean_key = unicode(newkey)
            records = api.portal.get_registry_record(self.key)
            records[clean_key] = safe_unicode(cname)
            api.portal.set_registry_record(self.key, records)
            IStatusMessage(self.request).addStatusMessage(
                _(u"New channel has been added to the registry"),
                type='info')
            return self.request.response.redirect(context.absolute_url())

    def channel_counter(self):
        key = 'pressapp.channelmanagement.channelList'
        records = api.portal.get_registry_record(key)
        return len(records)


class ChannelUpdate(grok.View):
    grok.context(IChannelManager)
    grok.require('cmf.ReviewPortalContent')
    grok.name('channel-update')

    def update(self):
        self.key = 'pressapp.channelmanagement.channelList'
        context = aq_inner(self.context)
        unwanted = ('_authenticator', 'form.button.Submit')
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            form = self.request.form
            data = {}
            for field in form:
                if field not in unwanted:
                    data[field] = field
            cl = api.portal.get_registry_record(self.key)
            obsolete = list()
            cleaned = dict()
            for key in cl:
                if key in data:
                    cleaned[key] = cl[key]
                else:
                    obsolete.append(key)
            if len(cleaned) > 0:
                return self.process_channel_update(cleaned, obsolete)
            else:
                IStatusMessage(self.request).addStatusMessage(
                    _(u"Removal of selected channels was not possible"),
                    type='error')
                return self.request.response.redirect(context.absolute_url())

    def process_channel_update(self, cleaned, obsolete):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name="portal_catalog")
        idx = 0
        for cn in obsolete:
            brains = catalog(object_provides=ISubscriber.__identifier__,
                             channel=[cn])
            if len(brains) > 0:
                sidx = self.update_subscribers(brains, cn)
                idx += sidx
        IStatusMessage(self.request).addStatusMessage(
            _(u"%s Subscriber objects have been updated" % idx),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def update_subscribers(self, items, channelname):
        cidx = 0
        for i in items:
            channels = getattr(i, 'channel', '')
            updated = list()
            for channel in channels:
                if channel != channelname:
                    updated.append(channel)
                else:
                    cidx += 1
            obj = i.getObject()
            setattr(obj, 'channel', updated)
            modified(obj)
            obj.reindexObject(idxs='modified')
        return cidx

    def channel_counter(self):
        return len(self.channel_names())

    def channel_names(self):
        key = 'pressapp.channelmanagement.channelList'
        records = api.portal.get_registry_record(key)
        catalog = api.portal.get_tool(name="portal_catalog")
        channels = catalog.uniqueValuesFor('channel')
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
            channel_info['channelname'] = channelname
            channel_info['channel'] = channel
            channel_info['pr_count'] = len(prs)
            channel_info['pi_count'] = len(pis)
            channel_info['sub_count'] = len(subs)
            stats.append(channel_info)
        return stats
