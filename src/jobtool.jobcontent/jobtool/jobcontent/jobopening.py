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

from jobtool.jobcontent import MessageFactory as _



class IJobOpening(form.Schema, IImageScaleTraversable):
    """
    A job opening describing the vacancy
    """


class JobOpening(dexterity.Item):
    grok.implements(IJobOpening)


class View(grok.View):
    grok.context(IJobOpening)
    grok.require('zope2.View')
    grok.name('view')
