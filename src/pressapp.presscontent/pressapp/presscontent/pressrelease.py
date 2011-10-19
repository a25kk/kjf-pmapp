from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from pressapp.presscontent import MessageFactory as _


class IPressRelease(form.Schema):
    """
    A press release content type.
    """


class View(grok.View):
    grok.context(IPressRelease)
    grok.require('zope2.View')
    grok.name('view')