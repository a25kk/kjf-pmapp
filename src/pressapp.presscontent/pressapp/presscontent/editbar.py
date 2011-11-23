from five import grok
from Acquisition import aq_inner
from plone.app.layout.viewlets.interfaces import IAboveContent
from pressapp.presscontent.pressroom import IPressRoom

class EditBarViewlet(grok.Viewlet):
    grok.name('pressapp.membercontent.EditBarViewlet')
    grok.context(IPressRoom)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)
    
    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()
    