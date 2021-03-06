from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.dexterity.utils import createContentInContainer
from Products.statusmessages.interfaces import IStatusMessage
from pressapp.presscontent.pressroom import IPressRoom

from pressapp.presscontent import MessageFactory as _


class IPressReleaseAdd(form.Schema):

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
        required=True,
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
    imagename = schema.TextLine(
        title=_(u"Image Title"),
        required=True,
    )
    description = schema.Text(
        title=_(u"Summary"),
        description=_(u"Optional summary that is useful as a preview text "
                      u"in email clients that support this feature."),
        required=False,
    )


class PressReleaseAddForm(form.SchemaEditForm):
    grok.context(IPressRoom)
    grok.require('cmf.AddPortalContent')
    grok.name('add-press-release')

    schema = IPressReleaseAdd
    ignoreContext = True
    css_class = 'overlayForm'

    label = _(u"Add new press release")

    def updateActions(self):
        super(PressReleaseAddForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary")
        self.actions['cancel'].addClass("btn btn-link")

    @button.buttonAndHandler(_(u"Create press release"), name="save")
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
            _(u"The creation of a new press release has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def applyChanges(self, data):
        context = aq_inner(self.context)
        assert IPressRoom.providedBy(context)
        item = createContentInContainer(context,
            'pressapp.presscontent.pressrelease',
            checkConstraints=True, **data)
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"A new press release was successfully added"),
            type='info')
        return self.request.response.redirect(item.absolute_url() + '/view')
