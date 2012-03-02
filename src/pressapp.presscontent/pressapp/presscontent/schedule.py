from five import grok
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from pressapp.presscontent.pressroom import IPressRoom
from pressapp.presscontent.interfaces import IPressContent


class ScheduleDashboard(grok.View):
    grok.context(IPressRoom)
    grok.require('cmf.ModifyPortalContent')
    grok.name('dashboard-schedule')

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()

    def presscontent(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IPressContent.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=2),
                          sort_on='modified',
                          sort_order='reverse')
        return results
