from Acquisition import aq_inner
from five import grok
from zope.component.hooks import getSite

from pressapp.presscontent.interfaces import IPressContent


class PrepareRelease(grok.View):
    grok.context(IPressContent)
    grok.require('cmf.ModifyPortalContent')
    grok.name('prepare-release')

    def update(self):
        self.recipient_count = len(self.recipient_list())
        self.has_recipients = self.recipient_count > 0
        self.subscriber_count = len(self.subscriber_list())
        self.has_subscribers = self.subscriber_count > 0

    def recipient_list(self):
        context = aq_inner(self.context)
        recipients = getattr(context, 'recipients', '')
        return recipients

    def subscriber_list(self):
        portal = getSite()
        presscenter = portal['presscenter']
        subscribers = getattr(presscenter, 'subscribers', '')
        return subscribers

    def reformat_recipients(self, item):
        item = item.split(',', 1)
        return item
