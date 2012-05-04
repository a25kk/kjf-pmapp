from five import grok
from plone.directives import dexterity, form

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage

from pressapp.presscontent import MessageFactory as _


# Interface class; used to define content-type schema.

class IImageAttachment(form.Schema, IImageScaleTraversable):
    """
    Custom image attachment type
    """
    form.primary('image')
    image = NamedBlobImage(
        title=_(u"Image Attachment"),
        description=_(u"Upload an image attachment for this press release"),
        required=True,
    )


class ImageAttachment(dexterity.Item):
    grok.implements(IImageAttachment)


class View(grok.View):
    grok.context(IImageAttachment)
    grok.require('zope2.View')
    grok.name('view')
