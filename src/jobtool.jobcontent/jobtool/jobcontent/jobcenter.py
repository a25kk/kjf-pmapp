from five import grok
from plone.directives import dexterity, form

from plone.namedfile.interfaces import IImageScaleTraversable

from jobtool.jobcontent import MessageFactory as _


class IJobCenter(form.Schema, IImageScaleTraversable):
    """
    Folderish jobcenter and managing unit
    """


class JobCenter(dexterity.Container):
    grok.implements(IJobCenter)


class View(grok.View):
    grok.context(IJobCenter)
    grok.require('zope2.View')
    grok.name('view')
