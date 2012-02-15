import datetime
from Acquisition import aq_inner
from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from plone.app.textfield import RichText
from Products.CMFCore.utils import getToolByName

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
        channel = getattr(context, 'channel', None)
        if channel:
            return True

    def has_recipients_info(self):
        context = aq_inner(self.context)
        recipients = getattr(context, 'recipients', None)
        if recipients:
            return True


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
