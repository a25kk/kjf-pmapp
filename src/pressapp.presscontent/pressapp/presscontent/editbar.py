from five import grok
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.interfaces import IAboveContent
from pressapp.presscontent.presscenter import IPressCenter
from pressapp.presscontent.pressroom import IPressRoom
from pressapp.channelmanagement.channelmanager import IChannelManager
from pressapp.channelmanagement.channel import IChannel


class EditBarViewlet(grok.Viewlet):
    grok.name('pressapp.membercontent.EditBarViewlet')
    grok.context(IPressRoom)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()
        self.parent_url = aq_parent(context).absolute_url()

    def is_administrator(self):
        context = aq_inner(self.context)
        return bool(getSecurityManager().checkPermission(
                    'Portlets: manage own portlets', context))


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


class ChannelEditBarViewlet(grok.Viewlet):
    grok.name('pressapp.membercontent.ChannelEditBarViewlet')
    grok.context(IChannelManager)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()
        self.parent_url = aq_parent(context).absolute_url()

    def my_workspace(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        home_url = member.getHomeFolder().absolute_url()
        return home_url

class SingleChannelEditBarViewlet(grok.Viewlet):
    grok.name('pressapp.membercontent.SingleChannelEditBarViewlet')
    grok.context(IChannel)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()
        self.parent_url = aq_parent(context).absolute_url()

    def my_workspace(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        home_url = member.getHomeFolder().absolute_url()
        return home_url
