from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field

from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobFile

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


class View(grok.View):
    grok.context(IPressRelease)
    grok.require('zope2.View')
    grok.name('view')