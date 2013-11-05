from five import grok
from plone import api
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl import getSecurityManager
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IContentish

from plone.app.layout.viewlets.interfaces import IPortalTop

from plone.app.contentlisting.interfaces import IContentListing

from pressapp.presscontent.interfaces import IPressAppPolicy


class NavBarViewlet(grok.Viewlet):
    grok.name('pressapp.membercontent.EditBarViewlet')
    grok.context(IContentish)
    grok.layer(IPressAppPolicy)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalTop)

    def update(self):
        context = aq_inner(self.context)
        self.portal_state = getMultiAdapter((context, self.request),
                                            name='plone_portal_state')
        self.anonymous = api.user.is_anonymous()
        self.portal_url = self.portal_state.portal_url
        self.context_url = context.absolute_url()
        self.parent_url = aq_parent(context).absolute_url()

    def channel_index(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        channels = catalog.uniqueValuesFor('channel')
        return len(channels)

    def pr_index(self):
        items = self.get_data(ptype='pressapp.presscontent.pressrelease')
        return len(items)

    def pi_index(self):
        items = self.get_data(ptype='pressapp.presscontent.pressinvitation')
        return len(items)

    def get_data(self, ptype=None):
        catalog = api.portal.get_tool(name='portal_catalog')
        query = self.base_query()
        presstypes = ['pressapp.presscontent.pressrelease',
                      'pressapp.presscontent.pressinvitation']
        if ptype is not None:
            query['portal_type'] = ptype
        else:
            query['portal_type'] = presstypes
        query['Creator'] = api.user.get_current().getId()
        brains = catalog.searchResults(**query)
        results = IContentListing(brains)
        return results

    def base_query(self):
        return dict(sort_on='modified',
                    sort_order='reverse')

    def is_administrator(self):
        context = aq_inner(self.context)
        is_admin = False
        admin_roles = ('Site Administrator', 'Manager')
        user = api.user.get_current()
        roles = api.user.get_roles(username=user.getId(), obj=context)
        for role in roles:
            if role in admin_roles:
                is_admin = True
        return is_admin

    def memberinfo(self):
        mtool = api.portal.get_tool(name='portal_membership')
        member = api.user.get_current()
        if member:
            import pdb; pdb.set_trace( )
            info = {}
            info['home_url'] = member.getHomeFolder().absolute_url()
            fullname = member.getProperty('fullname', None)
            if fullname:
                info['username'] = fullname
            else:
                info['username'] = member.getId()
            info['location'] = member.getProperty('location', '')
            info['organization'] = member.getProperty('organization', '')
            info['home_page'] = member.getProperty('home_page', '')
            info['presslink'] = member.getProperty('presslink', '')
            info['portrait'] = mtool.getPersonalPortrait(id=member.getId())
            info['login_time'] = member.getProperty('login_time', '2011/01/01')
            info['last_login_time'] = member.getProperty('last_login_time',
                                                         '2011/01/01')
            return info
