from Acquisition import aq_inner
from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field

from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobFile
from Products.CMFCore.utils import getToolByName

from plone.app.layout.viewlets.interfaces import IAboveContent

from pressapp.presscontent import MessageFactory as _


class IPressRelease(form.Schema):
    """
    A press release content type.
    """
    kicker = schema.TextLine(
        title=_(u"Kicker"),
        description=_(u"Enter optional kicker / teaser line."),
        required=False,
    )
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    subtitle = schema.TextLine(
        title=_(u"Subtitle"),
        description=_(u"Please enter an optional subtitle here."),
        required=False,
    )
    location = schema.TextLine(
        title=_(u"Location"),
        description=_(u"Provide a location for this press release that will "
                      u"be prepended to the main body text."),
        required=False,
    )
    text = RichText(
        title=_(u"Text"),
        required=True,
    )
    attachment = NamedBlobFile(
        title=_(u"Attachment"),
        description=_(u"Upload an attachment for this press release. The "
                      u"attachment can be an image, file or video."),
        required=True,
    )
    caption = schema.TextLine(
        title=_(u"Attachment Caption"),
        description=_(u"Enter optional caption describing the attachment"),
        required=True,
    )
    description = schema.Text(
        title=_(u"Summary"),
        description=_(u"Optional summary that is useful as a preview text "
                      u"in email clients that support this feature."),
        required=False,
    )


class View(grok.View):
    grok.context(IPressRelease)
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


class Preview(grok.View):
    grok.context(IPressRelease)
    grok.require('zope2.View')
    grok.name('pressrelease-preview')


class PressReleaseActions(grok.Viewlet):
    grok.name('pressapp.membercontent.PressReleaseActions')
    grok.context(IPressRelease)
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
