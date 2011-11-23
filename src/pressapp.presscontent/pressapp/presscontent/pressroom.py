from five import grok
from plone.directives import dexterity, form

from zope import schema
from Acquisition import aq_inner
from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

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
        self.has_pressrooms = len(self.contained_pressrooms()) > 0
        self.pressrooms = self.contained_pressrooms()
    
    def contained_pressrooms(self):
        context = aq_inner(self.context)
        items = context.items()
        return items
