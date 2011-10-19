from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from pressapp.presscontent import MessageFactory as _

class IPressInvitation(form.Schema):
    """
    A press invitation.
    """
    
class View(grok.View):
    grok.context(IPressInvitation)
    grok.require('zope2.View')
    grok.name('view')
