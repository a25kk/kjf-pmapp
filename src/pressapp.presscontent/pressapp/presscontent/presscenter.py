from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from pressapp.presscontent import MessageFactory as _


# Interface class; used to define content-type schema.

class IPressCenter(form.Schema):
    """
    Press center that will act as the global members folder.
    """
    

class View(grok.View):
    grok.context(IPressCenter)
    grok.require('zope2.View')
    grok.name('view')