from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.field import NamedBlobFile
from Products.statusmessages.interfaces import IStatusMessage
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
    attachment = NamedBlobFile(
        title=_(u"File Attachment"),
        description=_(u"Upload a file attachment for this press release. The "
                      u"file will be available for download from the e-mail"),
        required=True,
    )


class FileAttachmentAddForm(form.SchemaEditForm):
    grok.context(IPressRelease)
    grok.require('cmf.AddPortalContent')
    grok.name('add-file-attachment')

    schema = IFileAttachmentAdd
    ignoreContext = True
    css_class = 'overlayForm'

    label = _(u"Add new file attachment")

    def updateActions(self):
        super(FileAttachmentAddForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Create file attachment"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        IStatusMessage(self.request).addStatusMessage(
            _(u"The creation of a new attachment has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def applyChanges(self, data):
        context = aq_inner(self.context)
        assert IPressRelease.providedBy(context)
        item = createContentInContainer(context,
            'pressapp.presscontent.fileattachment',
            checkConstraints=True, **data)
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"A new attachment was successfully added"),
            type='info')
        return self.request.response.redirect(context.absolute_url() + '/view')
