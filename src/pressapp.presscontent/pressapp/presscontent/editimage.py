from five import grok
from Acquisition import aq_inner, aq_parent
from zope import schema
from zope.schema import getFieldsInOrder
from zope.component import getUtility
from zope.lifecycleevent import modified
from plone.directives import form
from z3c.form import button
from plone.namedfile.field import NamedBlobImage
from Products.CMFPlone.utils import safe_unicode

from plone.dexterity.interfaces import IDexterityFTI

from Products.statusmessages.interfaces import IStatusMessage
from pressapp.presscontent.imageattachment import IImageAttachment

from pressapp.presscontent import MessageFactory as _


class IImageAttachmentEdit(form.Schema):

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    image = NamedBlobImage(
        title=_(u"Image Attachment"),
        description=_(u"Upload a file attachment for this press release. The "
                      u"file will be available for download from the e-mail "
                      u"and provided as a thumbnail preview"),
        required=True,
    )


class ImageAttachmentEditForm(form.SchemaEditForm):
    grok.context(IImageAttachment)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-image-attachment')

    schema = IImageAttachmentEdit
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Edit Image attachment")

    def updateActions(self):
        super(ImageAttachmentEditForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Update image attachment"), name="save")
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
            _(u"Updating image attachment has been cancelled."),
            type='info')
        return self.request.response.redirect(parent.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                name='pressapp.presscontent.imageattachment')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        data['title'] = safe_unicode(context.Title())
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        assert IImageAttachment.providedBy(context)
        fti = getUtility(IDexterityFTI,
                name='pressapp.presscontent.imageattachment')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"Image attachment has successfully been updated"),
            type='info')
        return self.request.response.redirect(parent.absolute_url() + '/view')
