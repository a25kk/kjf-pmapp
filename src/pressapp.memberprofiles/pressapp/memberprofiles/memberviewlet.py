from five import grok
from Acquisition import aq_inner
from zope.component import getMultiAdapter

from plone.app.layout.viewlets.interfaces import IBelowContent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IContentish


class MemberViewlet(grok.Viewlet):
    grok.name('pressapp.memberprofiles.MemberViewlet')
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContent)

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()
        self.portal_state = getMultiAdapter((context, self.request),
                                            name='plone_portal_state')
        self.anonymous = self.portal_state.anonymous()

    def must_edit(self):
        data = self.memberdetails()
        if not data['home_page'] or not data['organization']:
            return True

    def memberdetails(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        info = {}
        info['name'] = member.getProperty('fullname') or member.getId()
        info['location'] = member.getProperty('location', '')
        info['organization'] = member.getProperty('organization', '')
        info['home_page'] = member.getProperty('home_page', '')
        info['presslink'] = member.getProperty('presslink', '')
        info['portrait'] = mtool.getPersonalPortrait(id=member.getId())
        info['login_time'] = member.getProperty('login_time', '2011/01/01')
        info['last_login_time'] = member.getProperty('last_login_time',
                                                     '2011/01/01')
        info['home_folder'] = member.getHomeFolder().absolute_url()
        return info
