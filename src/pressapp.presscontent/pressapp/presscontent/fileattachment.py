from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

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
