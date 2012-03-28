from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified
from zope.component import getUtility

from plone.directives import form
from z3c.form import button
from plone.namedfile.field import NamedBlobImage
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.statusmessages.interfaces import IStatusMessage
from pressapp.presscontent.pressroom import IPressRelease

from pressapp.presscontent import MessageFactory as _


class IImageAttachmentAdd(form.Schema):

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


class ImageAttachmentAddForm(form.SchemaEditForm):
    grok.context(IPressRelease)
    grok.require('cmf.AddPortalContent')
    grok.name('add-image-attachment')

    schema = IImageAttachmentAdd
    ignoreContext = True
    css_class = 'overlayForm'

    label = _(u"Add new file attachment")

    def updateActions(self):
        super(ImageAttachmentAddForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Create image attachment"), name="save")
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
            _(u"The creation of a new image attachment has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def applyChanges(self, data):
        context = aq_inner(self.context)
        assert IPressRelease.providedBy(context)
        new_title = data['title']
        new_id = getUtility(IIDNormalizer).normalize(new_title)
        item = context.invokeFactory(type_name='Image',
                                     id=new_id,
                                     title=new_title)
        item_obj = context[item]
        attachment = data['attachment'].data
        item_obj.setImage(attachment)
        modified(item_obj)
        item_obj.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"A new image attachment was successfully been added"),
            type='info')
        return self.request.response.redirect(context.absolute_url() + '/view')
