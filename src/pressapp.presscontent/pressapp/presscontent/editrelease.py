from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified
from zope.component import getUtility
from zope.schema import getFieldsInOrder

from plone.directives import form
from z3c.form import button
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from pressapp.presscontent.pressrelease import IPressRelease

from pressapp.presscontent import MessageFactory as _


class IPressReleaseEdit(form.Schema):

    kicker = schema.TextLine(
        title=_(u"Kicker"),
        description=_(u"Enter optional kicker / teaser line."),
        required=False,
    )
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    subtitle = schema.TextLine(
        title=_(u"Subtitle"),
        description=_(u"Please enter an optional subtitle here."),
        required=False,
    )
    location = schema.TextLine(
        title=_(u"Location"),
        description=_(u"Provide a location for this press release that will "
                      u"be prepended to the main body text."),
        required=False,
    )
    text = RichText(
        title=_(u"Text"),
        required=True,
    )
    image = NamedBlobImage(
        title=_(u"Image Attachment"),
        description=_(u"Upload an image for this press release. The "
                      u"image should be already optimized since sending "
                      u"a large image file via E-mail is not recommended"),
        required=True,
    )
    caption = schema.TextLine(
        title=_(u"Attachment Caption"),
        description=_(u"Enter optional caption describing the attachment"),
        required=True,
    )
    description = schema.Text(
        title=_(u"Summary"),
        description=_(u"Optional summary that is useful as a preview text "
                      u"in email clients that support this feature."),
        required=False,
    )
    archive = schema.Bool(
        title=_(u"Visible in Archive?"),
        description=_(u"Mark this press release as visible in the archive."),
        required=False,
        default=True,
    )


class PressReleaseEditForm(form.SchemaEditForm):
    grok.context(IPressRelease)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-press-release')

    schema = IPressReleaseEdit
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Edit press release")

    def updateActions(self):
        super(PressReleaseEditForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Save"), name="save")
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
            _(u"Editing has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                name='pressapp.presscontent.pressrelease')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        data['description'] = safe_unicode(context.Description())
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        assert IPressRelease.providedBy(context)
        fti = getUtility(IDexterityFTI,
                name='pressapp.presscontent.pressrelease')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        context.setDescription(data['description'])
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The press release was successfully updated"),
            type='info')
        return self.request.response.redirect(context.absolute_url() + '/view')
