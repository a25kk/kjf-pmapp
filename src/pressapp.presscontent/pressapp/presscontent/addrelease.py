from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from plone.dexterity.utils import createContentInContainer
from Products.statusmessages.interfaces import IStatusMessage
from pressapp.presscontent.pressrelease import IPressRelease
from pressapp.presscontent.pressroom import IPressRoom

from pressapp.presscontent import MessageFactory as _


class IPressReleaseAdd(form.Schema):

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Enter the title of the press release."),
        required=True,
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
        self.actions['save'].addClass("btn rgd large")
        self.actions['cancel'].addClass("btn large")

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
        IStatusMessage(self.request).addStatusMessage(
            _(u"A new press release was successfully added"),
            type='info')
        return self.request.response.redirect(item.absolute_url() + '/edit')
