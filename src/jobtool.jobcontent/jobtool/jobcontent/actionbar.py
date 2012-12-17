from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from zope.interface import Interface
from zope.component import getMultiAdapter

from plone.app.layout.viewlets.interfaces import IAboveContent


class ActionBar(grok.Viewlet):
    grok.name('jobtool.jobcontent.ActionBarViewlet')
    grok.context(Interface)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()
        self.parent_url = aq_parent(context).absolute_url()
        self.portal_state = getMultiAdapter((context, self.request),
                                            name='plone_portal_state')
        self.anonymous = self.portal_state.anonymous()
