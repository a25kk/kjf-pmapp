from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.component import getUtility
from zope.schema import getFieldsInOrder
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from pressapp.channelmanagement.vocabulary import ChannelSourceBinder
from Products.statusmessages.interfaces import IStatusMessage

from plone.dexterity.interfaces import IDexterityFTI
from pressapp.presscontent.interfaces import IPressContent
from pressapp.presscontent.pressrelease import IPressRelease
from pressapp.presscontent.pressinvitation import IPressInvitation

from pressapp.presscontent import MessageFactory as _


class IChannelSelection(form.Schema):

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


class ChannelSelectionForm(form.SchemaEditForm):
    grok.context(IPressContent)
    grok.require('cmf.AddPortalContent')
    grok.name('select-channel')

    schema = IChannelSelection
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Select the channel for dispatch")

    def updateActions(self):
        super(ChannelSelectionForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Save Selection"), name="save")
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
            _(u"Selection of dispatch channel has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        data = {}
        try:
            channelinfo = context.channel
        except:
            channelinfo = getattr(context, 'channel', '')
        data['channel'] = channelinfo
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        if IPressRelease.providedBy(context):
            fti_name = 'pressapp.presscontent.pressrelease'
        if IPressInvitation.providedBy(context):
            fti_name = 'pressapp.presscontent.pressinvitation'
        fti = getUtility(IDexterityFTI, name=fti_name)
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        setattr(context, 'channel', data['channel'])
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"A channel was successfully selected"),
            type='info')
        return self.request.response.redirect(
                    context.absolute_url()+'/@@recipient-list')
