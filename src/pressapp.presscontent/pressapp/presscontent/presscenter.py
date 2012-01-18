from five import grok
from plone.directives import dexterity, form
from Acquisition import aq_inner
from zope import schema
from AccessControl import getSecurityManager
from plone.memoize.instance import memoize

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from Products.CMFCore.utils import getToolByName

from pressapp.presscontent.pressroom import IPressRoom

from pressapp.presscontent import MessageFactory as _


class IPressCenter(form.Schema):
    """
    Press center that will act as the global members folder.
    """


class View(grok.View):
    grok.context(IPressCenter)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_pressrooms = len(self.contained_pressrooms()) > 0
        self.pressrooms = self.contained_pressrooms()

    def contained_pressrooms(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IPressRoom.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=1),
                          sort_on='sortable_title')
        return results

    def memberinfo(self, owner):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getMemberById(owner)
        login_time = member.getProperty('last_login_time', '2011/01/01')
        return login_time

    @memoize
    def can_edit(self):
        return bool(getSecurityManager().checkPermission(
                    'Portlets: Manage own portlets', self.context))
