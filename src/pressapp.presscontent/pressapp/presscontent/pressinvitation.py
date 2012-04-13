import datetime
from Acquisition import aq_inner
from five import grok
from plone.directives import form

from zope import schema
from zope.component import getMultiAdapter
from zope.site.hooks import getSite

from plone.app.textfield import RichText
from Products.CMFCore.utils import getToolByName

from plone.uuid.interfaces import IUUID
from plone.app.layout.viewlets.interfaces import IAboveContent

from pressapp.presscontent import MessageFactory as _


class IPressInvitation(form.Schema):
    """
    A press invitation.
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    text = RichText(
        title=_(u"Text"),
        required=True,
    )
    start = schema.Datetime(
        title=_(u"Start Date"),
        required=True,
    )
    end = schema.Datetime(
        title=_(u"End Date"),
        required=True,
    )
    location = schema.TextLine(
        title=_(u"Event Location"),
        required=True,
    )
    schedule = RichText(
        title=_(u"Schedule"),
        description=_(u"Enter optional schedule information."),
        required=False,
    )
    travel = schema.Text(
        title=_(u"Travel information"),
        description=_(u"Enter optional travel information."),
        required=False,
    )
    directions = schema.URI(
        title=_(u"Directions Link"),
        description=_(u"Enter link to Google Map for directions"),
        required=False,
    )
    closed = schema.Bool(
        title=_(u"Closed Event"),
        description=_(u"Please select if the event is public."),
        required=False,
    )
    description = schema.Text(
        title=_(u"Summary"),
        description=_(u"Optional summary that is useful as a preview text "
                      u"in email clients that support this feature."),
        required=False,
    )


@form.default_value(field=IPressInvitation['start'])
def startDefaultValue(data):
    return datetime.datetime.today() + datetime.timedelta(7)


@form.default_value(field=IPressInvitation['end'])
def endDefaultValue(data):
    return datetime.datetime.today() + datetime.timedelta(10)


class View(grok.View):
    grok.context(IPressInvitation)
    grok.require('zope2.View')
    grok.name('view')

    def has_channel_info(self):
        context = aq_inner(self.context)
        channelinfo = False
        channel = getattr(context, 'channel', None)
        if channel is not None:
            channelinfo = True
        return channelinfo

    def has_recipients_info(self):
        context = aq_inner(self.context)
        info = False
        recipients = getattr(context, 'recipients', None)
        if recipients is not None:
            info = True
        return info

    def constructPreviewURL(self):
        context = aq_inner(self.context)
        portal = getSite()
        portal_url = portal.absolute_url()
        uuid = IUUID(context, None)
        url = portal_url + '/@@pressitem-view?uid=' + uuid
        return url


class Preview(grok.View):
    grok.context(IPressInvitation)
    grok.require('zope2.View')
    grok.name('pressinvitation-preview')


class AsHtmlView(grok.View):
    grok.context(IPressInvitation)
    grok.require('zope2.View')
    grok.name('asHTML')

    def additional_data(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getMemberById(context.Creator())
        data = {}
        data['location'] = context.location
        data['date'] = context.Date()
        data['org'] = member.getProperty('organization', '')
        data['link'] = member.getProperty('home_page', '')
        return data

    def getImageTag(self, item):
        obj = item
        scales = getMultiAdapter((obj, self.request), name='images')
        scale = scales.scale('image', scale='mini')
        imageTag = None
        if scale is not None:
            imageTag = scale.tag()
        return imageTag


class PressInvitationActions(grok.Viewlet):
    grok.name('pressapp.membercontent.PressReleaseActions')
    grok.context(IPressInvitation)
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
