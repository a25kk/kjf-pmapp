from five import grok
from plone.directives import dexterity, form

from zope import schema
from AccessControl import getSecurityManager
from plone.memoize.instance import memoize

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from pressapp.presscontent import MessageFactory as _


class IPressCenter(form.Schema):
    """
    Press center that will act as the global members folder.
    """


class View(grok.View):
    grok.context(IPressCenter)
    grok.require('zope2.View')
    grok.name('view')
    
    @memoize
    def can_edit(self):
        return bool(getSecurityManager().checkPermission('Portlets: Manage own portlets', self.context))