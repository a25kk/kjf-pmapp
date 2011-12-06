from five import grok
from Acquisition import aq_inner
from plone.app.layout.viewlets.interfaces import IBelowContent
from Products.CMFCore.interfaces import IContentish


class MemberViewlet(grok.Viewlet):
    grok.name('pressapp.memberprofiles.MemberViewlet')
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContent)
    
    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()