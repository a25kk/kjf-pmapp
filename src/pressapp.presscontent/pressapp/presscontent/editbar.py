from five import grok
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.interfaces import IAboveContent
from pressapp.presscontent.presscenter import IPressCenter
from pressapp.presscontent.pressroom import IPressRoom


class EditBarViewlet(grok.Viewlet):
    grok.name('pressapp.membercontent.EditBarViewlet')
    grok.context(IPressRoom)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()


class PressCenterEditBarViewlet(grok.Viewlet):
    grok.name('pressapp.membercontent.PressCenterEditBarViewlet')
    grok.context(IPressCenter)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()

    def my_workspace(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        home_url = member.getHomeFolder().absolute_url()
        return home_url
