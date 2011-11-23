from five import grok
from plone.directives import dexterity, form

from zope import schema
from Acquisition import aq_inner
from z3c.form import group, field
from Products.CMFCore.utils import getToolByName
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.app.contentlisting.interfaces import IContentListing

from pressapp.presscontent.pressrelease import IPressRelease

from pressapp.presscontent import MessageFactory as _


class IPressRoom(form.Schema):
    """
    A single press room that will be the workspace for members.
    """
    

class View(grok.View):
    grok.context(IPressRoom)
    grok.require('zope2.View')
    grok.name('view')
    
    def update(self):
        context = aq_inner(self.context)
        self.has_releases = len(self.contained_pressreleases()) > 0
        self.pressreleases = self.contained_pressreleases()
    
    def contained_pressreleases(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IPressRelease.__identifier__,
                          path='/'.join(context.getPhysicalPath()))
        items = IContentListing(results)
        return items
    
