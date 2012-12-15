from five import grok
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.app.layout.navigation.interfaces import INavigationRoot


class FrontpageView(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('frontpage-view')

    def render(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        if mtool.isAnonymousUser():
            return self.request.response.redirect(
                context.absolute_url() + "/login_form")
        else:
            try:
                member = mtool.getAuthenticatedMember()
                home_url = member.getHomeFolder().absolute_url()
                return self.request.response.redirect(home_url)
            except:
                home_url = mtool.getMembersFolder().absolute_url()
                return self.request.response.redirect(home_url)
