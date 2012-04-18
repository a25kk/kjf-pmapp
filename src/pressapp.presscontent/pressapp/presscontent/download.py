from Acquisition import aq_inner
from five import grok
from zope.publisher.interfaces import NotFound
from plone.namedfile.utils import set_headers, stream_data

from plone.app.uuid.utils import uuidToObject
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from pressapp.presscontent.pressrelease import IPressRelease

from pressapp.presscontent import MessageFactory as _


class DownloadAssets(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('download-assets')

    def update(self):
        self.target_item = self.resolveItemByID()

    def render(self):
        return self.download_url()

    def download_url(self):
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'portal_url')
        portal = ptool.getPortalObject()
        item = self.target_item
        if IPressRelease.providedBy(item):
            url = item.absolute_url()
            item_path = item.absolute_url_path()
            filename = item.image.filename
            load_file = item_path[1:] + '/@@download/image/' + filename
            download_url = url + '/@@download/image/' + filename
            file_data = portal.restrictedTraverse(load_file)
            return download_url

    def download_blob(context, request, file):
        """ Stream animation or image BLOB to the browser.
            @param context: Context object name is used to set the filename if
            blob itself doesn't provide one
            @param file: Blob object
        """
        if file == None:
            raise NotFound(context, '', request)
        filename = getattr(file, 'filename', context.id + "_download")
        set_headers(file, request.response)
        cd = 'inline; filename=%s' % filename
        request.response.setHeader("Content-Disposition", cd)
        return stream_data(file)

    def resolveItemByID(self):
        uid = self.request.get('uid', '')
        if uid:
            obj = uuidToObject(uid)
            if not obj:
                IStatusMessage(self.request).addStatusMessage(
                    _(u"The requested item was not found"), type='error')
            else:
                return obj
