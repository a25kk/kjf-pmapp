from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from Products.CMFCore.utils import getToolByName
from pressapp.channelmanagement.vocabulary import ChannelSourceBinder
from plone.dexterity.utils import createContentInContainer
from Products.statusmessages.interfaces import IStatusMessage
from pressapp.presscontent.pressrelease import IPressRelease
from pressapp.presscontent.pressroom import IPressRoom

from pressapp.presscontent import MessageFactory as _


class IPrepareRelease(form.Schema):

    form.widget(channel=AutocompleteMultiFieldWidget)
    channel = schema.List(
        title=_(u"Channels"),
        description=_(u"Please select the channels this recipient "
                      u"is subscribed to."),
        value_type=schema.Choice(
            title=_(u"Channel"),
            source=ChannelSourceBinder(),
        )
    )


class PrepareReleaseForm(form.SchemaEditForm):
    grok.context(IPressRelease)
    grok.require('cmf.AddPortalContent')
    grok.name('prepare-release')

    schema = IPrepareRelease
    ignoreContext = True
    css_class = 'overlayForm'

    label = _(u"Prepare press release for dispatch.")

    def updateActions(self):
        super(PrepareReleaseForm, self).updateActions()
        self.actions['save'].addClass("btn rgd large")
        self.actions['cancel'].addClass("btn large")

    @button.buttonAndHandler(_(u"Dispatch press release"), name="save")
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
            _(u"Dispatch of press release has been cancelled."),
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
