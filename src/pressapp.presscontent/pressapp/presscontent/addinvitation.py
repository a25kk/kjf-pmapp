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


class IPressInvitationAdd(form.Schema):

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Enter the title of the press invitation."),
        required=True,
    )


class PressInvitationAddForm(form.SchemaEditForm):
    grok.context(IPressRoom)
    grok.require('cmf.AddPortalContent')
    grok.name('add-press-invitation')

    schema = IPressInvitationAdd
    ignoreContext = True
    css_class = 'overlayForm'

    label = _(u"Add press invitation")

    def updateActions(self):
        super(PressInvitationAddForm, self).updateActions()
        self.actions['save'].addClass("btn rgd large")
        self.actions['cancel'].addClass("btn large")

    @button.buttonAndHandler(_(u"Create press invitation"), name="save")
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
            _(u"The creation of a new press invitation has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def applyChanges(self, data):
        context = aq_inner(self.context)
        assert IPressRoom.providedBy(context)
        item = createContentInContainer(context,
            'pressapp.presscontent.pressinvitation',
            checkConstraints=True, **data)
        modified(item)
        IStatusMessage(self.request).addStatusMessage(
            _(u"A new press invitation was successfully added"),
            type='info')
        return self.request.response.redirect(item.absolute_url() + '/edit')