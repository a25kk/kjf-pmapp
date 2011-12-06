from five import grok
from Acquisition import aq_inner

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
        info['last_login_time'] = member.getProperty('last_login_time', '2011/01/01')
        return info
        
        