from five import grok
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl import getSecurityManager

from zope.interface import Interface
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IContentish

from plone.app.layout.viewlets.interfaces import IPortalTop

from jobtool.jobcontent.interfaces import IJobTool


class NavBarViewlet(grok.Viewlet):
    grok.name('jobtool.jobcontent.NavBarViewlet')
    grok.context(Interface)
    grok.layer(IJobTool)
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

    def memberinfo(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        if member:
            info = {}
            fullname = member.getProperty('fullname', None)
            if fullname:
                info['username'] = fullname
            else:
                info['username'] = member.getId()
            info['location'] = member.getProperty('location', '')
            info['organization'] = member.getProperty('organization', '')
            info['home_page'] = member.getProperty('home_page', '')
            info['portrait'] = mtool.getPersonalPortrait(id=member.getId())
            info['login_time'] = member.getProperty('login_time', '2011/01/01')
            info['last_login_time'] = member.getProperty('last_login_time',
                                                         '2011/01/01')
            return info
