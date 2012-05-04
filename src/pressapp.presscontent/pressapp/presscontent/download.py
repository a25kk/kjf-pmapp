from five import grok
from AccessControl.ZopeGuards import guarded_getattr
from zope.publisher.interfaces import NotFound

from plone.namedfile.utils import set_headers, stream_data

from plone.app.uuid.utils import uuidToObject
from Products.CMFPlone.utils import safe_unicode
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.statusmessages.interfaces import IStatusMessage

from pressapp.presscontent.pressrelease import IPressRelease
from pressapp.presscontent.pressinvitation import IPressInvitation

from pressapp.presscontent import MessageFactory as _


class DownloadAssets(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('download-assets')

    def update(self):
        self.target_item = self.resolveItemByID()

    def render(self):
        return self.stream_file()

    def stream_file(self):
        item = self.target_item
        is_file = getattr(item, 'attachment', None)
        if is_file:
            file_obj = item.attachment
            filename = item.attachment.filename
            set_headers(file_obj, self.request.response, filename)
            return stream_data(file_obj)
        else:
            info = IPrimaryFieldInfo(item, None)
            if info is None:
                file_obj = item.image
                filename = (item.image.filename).decode('utf-8')
                set_headers(file_obj, self.request.response, filename)
                return stream_data(file_obj)
            self.fieldname = info.fieldname
            file = info.value
            self.filename = getattr(file, 'filename', self.fieldname)
            try:
                str(self.filename)
            except UnicodeEncodeError:
                self.filename = (self.filename).encode('utf-8')
            set_headers(file, self.request.response, self.filename)
            return stream_data(file)
            #file_obj = item.image
            #filename = (item.image.filename).decode('utf-8')
            #set_headers(file_obj, self.request.response, filename)
            #return stream_data(file_obj)

    def _getFile(self):
        if not self.fieldname:
            info = IPrimaryFieldInfo(self.context, None)
            if info is None:
                # Ensure that we have at least a filedname
                raise NotFound(self, '', self.request)
            self.fieldname = info.fieldname
            file = info.value
        else:
            context = getattr(self.context, 'aq_explicit', self.context)
            file = guarded_getattr(context, self.fieldname, None)
        if file is None:
            raise NotFound(self, self.fieldname, self.request)
        return file

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
        item = self.target_item
        if IPressRelease.providedBy(item):
            attachment = item.unrestrictedTraverse(
                '@@asPlainPDFCustom')(converter='pdf-pisa',
                                resource='pressapp_resource',
                                template='pdf_template_standalone')
        if IPressInvitation.providedBy(item):
            attachment = item.unrestrictedTraverse(
                '@@asPlainPDFCustom')(converter='pdf-pisa',
                                      resource='pressapp_resource',
                                      template='pdf_template_standalone_pi')
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
