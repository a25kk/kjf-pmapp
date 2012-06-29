from Acquisition import aq_inner
from five import grok
from plone.directives import form

from zope import schema
from zope.component import queryUtility

from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from Products.CMFCore.utils import getToolByName
from pressapp.channelmanagement.vocabulary import ChannelSourceBinder

from plone.registry.interfaces import IRegistry

from plone.app.layout.viewlets.interfaces import IAboveContent

from pressapp.channelmanagement import MessageFactory as _


class ISubscriber(form.Schema):
    """
    A single recipient/subscriber object
    """
    title = schema.TextLine(
        title=_(u"Contact Title"),
        required=True,
    )
    email = schema.TextLine(
        title=_(u"Email"),
        required=True,
    )
    contact = schema.TextLine(
        title=_(u"Contact Person"),
        required=False,
    )
    phone = schema.TextLine(
        title=_(u"Phone"),
        required=False,
    )
    mobile = schema.TextLine(
        title=_(u"Mobile Phone"),
        required=False,
    )
    fax = schema.TextLine(
        title=_(u"Fax"),
        required=False,
    )
    comment = schema.Text(
        title=_(u"Comment"),
        required=False,
    )
    form.widget(channel=AutocompleteMultiFieldWidget)
    channel = schema.List(
        title=_(u"Channels"),
        description=_(u"Please select the channels this recipient "
                      u"is subscribed to."),
        value_type=schema.Choice(
            title=_(u"Channel"),
            source=ChannelSourceBinder(),
        )
    )


class View(grok.View):
    grok.context(ISubscriber)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.key = 'pressapp.channelmanagement.channelList'

    def channels(self):
        records = self.channel_records()
        channels = []
        for channel in records:
            info = {}
            info['channel'] = channel
            try:
                channelname = records[channel]
            except KeyError:
                channelname = channel
            info['channelname'] = channelname
            context_channels = getattr(self.context, 'channel', None)
            if channel not in context_channels:
                info['active'] = True
            else:
                info['active'] = False
            channels.append(info)
        return channels

    def selected_channels(self):
        context = aq_inner(self.context)
        records = self.channel_records()
        names = []
        channels = getattr(context, 'channel', None)
        for channel in channels:
            info = {}
            info['channel'] = channel
            try:
                channelname = records[channel]
            except KeyError:
                channelname = channel
            info['channelname'] = channelname
            names.append(info)
        return names

    def channel_names(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        channels = catalog.uniqueValuesFor('channel')
        records = self.channel_records()
        names = []
        for channel in channels:
            info = {}
            info['channel'] = channel
            try:
                channelname = records[channel]
            except KeyError:
                channelname = channel
            info['channelname'] = channelname
            names.append(info)
        return names

    def channel_records(self):
        registry = queryUtility(IRegistry)
        if registry:
            records = registry['pressapp.channelmanagement.channelList']
        return records


class SubscriberActions(grok.Viewlet):
    grok.name('pressapp.membercontent.SubscriberActions')
    grok.context(ISubscriber)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()

    def homefolder_url(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        home_folder = member.getHomeFolder().absolute_url()
        return home_folder
