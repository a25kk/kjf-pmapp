from Acquisition import aq_inner
from five import grok

from pressapp.presscontent.interfaces import IPressContent


class PrepareRelease(grok.View):
    grok.context(IPressContent)
    grok.require('zope2.View')
    grok.name('prepare-release')

    def update(self):
        self.recipient_count = len(self.recipient_list())
        self.has_recipients = self.recipient_count > 0

    def recipient_list(self):
        context = aq_inner(self.context)
        recipients = getattr(context, 'recipients', '')
        return recipients

    def reformat_recipients(self, item):
        item = item.split(',', 1)
        return item
