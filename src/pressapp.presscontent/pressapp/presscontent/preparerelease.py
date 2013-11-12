from Acquisition import aq_inner
from five import grok
from plone import api
from zope.component.hooks import getSite

from pressapp.presscontent.pressinvitation import IPressInvitation
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

    def is_administrator(self):
        context = aq_inner(self.context)
        is_admin = False
        admin_roles = ('Site Administrator', 'Manager')
        user = api.user.get_current()
        roles = api.user.get_roles(username=user.getId(), obj=context)
        for role in roles:
            if role in admin_roles:
                is_admin = True
        return is_admin

    def is_pressinvitation(self):
        context = aq_inner(self.context)
        return IPressInvitation.providedBy(context)

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

    def has_channel_info(self):
        context = aq_inner(self.context)
        channel = getattr(context, 'channel', None)
        if channel:
            return True

    def has_recipients_info(self):
        context = aq_inner(self.context)
        recipients = getattr(context, 'recipients', None)
        if recipients:
            return True
