from five import grok
from Acquisition import aq_inner, aq_parent
from zope import schema
from zope.lifecycleevent import modified
from zope.component import getUtility

from plone.directives import form
from z3c.form import button
from plone.namedfile.field import NamedBlobImage
from Products.CMFPlone.utils import safe_unicode

from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.blob.interfaces import IATBlobFile
from pressapp.presscontent.pressroom import IPressRelease

from pressapp.presscontent import MessageFactory as _


class IFileAttachmentAdd(form.Schema):

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    description = schema.Text(
        title=_(u"Description"),
        description=_(u"A short description used as caption"),
        required=False,
    )
    attachment = NamedBlobImage(
        title=_(u"Image Attachment"),
        description=_(u"Upload a file attachment for this press release. The "
                      u"file will be available for download from the e-mail "
                      u"and provided as a thumbnail preview"),
        required=True,
    )


class FileAttachmentAddForm(form.SchemaEditForm):
    grok.context(IATBlobFile)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-file-attachment')

    schema = IFileAttachmentAdd
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Edit file attachment")

    def updateActions(self):
        super(FileAttachmentAddForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Update file attachment"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Updating file attachment has been cancelled."),
            type='info')
        return self.request.response.redirect(parent.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        data = {}
        data['title'] = context.Title()
        data['description'] = safe_unicode(context.Description())
        data['attachment'] = context.getFile()
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        assert IATBlobFile.providedBy(context)
        item_obj = context
        new_title = data['title']
        new_desc = data['description']
        attachment = data['attachment'].data
        item_obj.setFile(attachment)
        item_obj.setTitle(new_title)
        item_obj.setDescription(new_desc)
        modified(item_obj)
        item_obj.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"File attachment has successfully been updated"),
            type='info')
        return self.request.response.redirect(parent.absolute_url() + '/view')
