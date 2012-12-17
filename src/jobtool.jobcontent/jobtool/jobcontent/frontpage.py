from five import grok
from Acquisition import aq_inner
from plone import api

from Products.CMFCore.utils import getToolByName
from plone.app.layout.navigation.interfaces import INavigationRoot

from jobtool.jobcontent.interfaces import IJobTool


class FrontpageView(grok.View):
    grok.context(INavigationRoot)
    grok.layer(IJobTool)
    grok.require('zope2.View')
    grok.name('frontpage-view')

    def render(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        if mtool.isAnonymousUser():
            return self.request.response.redirect(
                context.absolute_url() + "/login_form")
        else:
            portal_url = api.portal.get().absolute_url()
            url = portal_url + '/@@jobcenter-dashboard'
            return self.request.response.redirect(url)
