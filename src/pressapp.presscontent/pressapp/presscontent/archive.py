from five import grok

from plone.app.uuid.utils import uuidToObject
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.statusmessages.interfaces import IStatusMessage

from pressapp.presscontent import MessageFactory as _


class PressItemView(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('pressitem-view')

    def resolvePressItem(self):
        uid = self.request.get('uid', '')
        if uid:
            obj = uuidToObject(uid)
            if not obj:
                IStatusMessage(self.request).addStatusMessage(
                    _(u"The requested item was not found"), type='error')
            else:
                return obj
