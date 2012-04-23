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
        return self.stream_file()

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
            #file_data = portal.restrictedTraverse(load_file)
            return self.download_blob(item.image)

    def stream_file(self):
        context = aq_inner(self.context)
        item = self.target_item
        portal_type = item.portal_type
        if portal_type == 'File':
            file_obj = item.getFile()
            file_id = item.getId()
            item_path = item.absolute_url_path
            return self.downlaod_blob(file_id, file_obj)
        else:
            file_obj = item.image
            filename = item.image.filename
            set_headers(file_obj, self.request.response, filename)
            return stream_data(file_obj)

    def download_blob(self, file_id, file):
        """ Stream animation or image BLOB to the browser.
            @param context: Context object name is used to set the filename if
            blob itself doesn't provide one
            @param file: Blob object
        """
        context = aq_inner(self.context)
        request = self.request
        if file == None:
            raise NotFound(context, '', request)
        filename = getattr(file, 'filename', file_id + "_download")
        set_headers(file, request.response, filename)
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


class DownloadFileVersion(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('download-file-version')

    def update(self):
        self.target_item = self.resolveItemByID()

    def render(self):
        return self.generate_pdf()

    def generate_pdf(self):
        context = aq_inner(self.context)
        item = self.target_item
        attachment = item.unrestrictedTraverse(
            '@@asPlainPDF')(converter='pdf-pisa',
                            resource='pressapp_resource',
                            template='pdf_template_standalone')
        return attachment

    def resolveItemByID(self):
        uid = self.request.get('uid', '')
        if uid:
            obj = uuidToObject(uid)
            if not obj:
                IStatusMessage(self.request).addStatusMessage(
                    _(u"The requested item was not found"), type='error')
            else:
                return obj
