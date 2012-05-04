from five import grok
from plone.directives import dexterity, form

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobFile

from pressapp.presscontent import MessageFactory as _


# Interface class; used to define content-type schema.

class IFileAttachment(form.Schema, IImageScaleTraversable):
    """
    A basic file attachment for presscontents
    """
    attachment = NamedBlobFile(
        title=_(u"File Attachment"),
        description=_(u"Uplaod file attachment. Note: for images that should "
                      u"also provide previews use a special image attachment"),
        required=True,
    )


class FileAttachment(dexterity.Item):
    grok.implements(IFileAttachment)


class View(grok.View):
    grok.context(IFileAttachment)
    grok.require('zope2.View')
    grok.name('view')
