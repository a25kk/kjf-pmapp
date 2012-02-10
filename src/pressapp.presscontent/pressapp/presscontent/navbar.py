from five import grok
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl import getSecurityManager
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IContentish

from plone.app.layout.viewlets.interfaces import IPortalTop


class NavBarViewlet(grok.Viewlet):
    grok.name('pressapp.membercontent.EditBarViewlet')
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalTop)

    def update(self):
        context = aq_inner(self.context)
        self.portal_state = getMultiAdapter((context, self.request),
                                            name='plone_portal_state')
        self.anonymous = self.portal_state.anonymous()
        self.portal_url = self.portal_state.portal_url
        self.context_url = context.absolute_url()
        self.parent_url = aq_parent(context).absolute_url()

    def is_administrator(self):
        context = aq_inner(self.context)
        return bool(getSecurityManager().checkPermission(
                    'Portlets: Manage own portlets', context))

    def home_url(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        home_url = member.getHomeFolder().absolute_url()
        return home_url
