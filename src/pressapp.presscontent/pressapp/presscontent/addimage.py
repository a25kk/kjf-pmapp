import base64
import random
import hashlib
from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from plone.namedfile.field import NamedBlobImage
from plone.dexterity.utils import createContentInContainer
from Products.statusmessages.interfaces import IStatusMessage
from pressapp.presscontent.pressroom import IPressRelease

from pressapp.presscontent import MessageFactory as _


class IImageAttachmentAdd(form.Schema):

    description = schema.Text(
        title=_(u"Image Caption"),
        description=_(u"Enter a short summary of the image contents"),
        required=True,
    )
    image = NamedBlobImage(
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

    label = _(u"Add new image attachment")

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
        base_string = u'assets-'
        random_key = self.generate_random_key()
        new_title = base_string + random_key
        data['title'] = new_title
        item = createContentInContainer(context,
            'pressapp.presscontent.imageattachment',
            checkConstraints=True, **data)
        item.setDescription(data['description'])
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"A new image attachment was successfully been added"),
            type='info')
        return self.request.response.redirect(context.absolute_url() + '/view')

    def generate_random_key(self):
        key = base64.b64encode(
                hashlib.sha256(str(random.getrandbits(256))
                ).digest(), random.choice([
                'rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')
        return key
