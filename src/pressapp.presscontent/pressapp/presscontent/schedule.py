from five import grok
from Acquisition import aq_inner
from pressapp.presscontent.pressroom import IPressRoom

class ScheduleDashboard(grok.View):
    grok.context(IPressRoom)
    grok.require('cmf.ModifyPortalContent')
    grok.name('dashboard-schedule')
    
    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()