from five import grok
from Acquisition import aq_inner, aq_parent
from zope import schema
from zope.component import getUtility
from zope.schema import getFieldsInOrder
from zope.lifecycleevent import modified
from plone.directives import form
from z3c.form import button
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone.utils import safe_unicode

from Products.statusmessages.interfaces import IStatusMessage
from pressapp.channelmanagement.subscriber import ISubscriber

from pressapp.presscontent import MessageFactory as _


class ISubscriberEdit(form.Schema):

    title = schema.TextLine(
        title=_(u"Contact Title"),
        required=True,
    )
    email = schema.TextLine(
        title=_(u"Email"),
        required=True,
    )
    contact = schema.TextLine(
        title=_(u"Contact Person"),
        required=False,
    )
    phone = schema.TextLine(
        title=_(u"Phone"),
        required=False,
    )
    mobile = schema.TextLine(
        title=_(u"Mobile Phone"),
        required=False,
    )
    fax = schema.TextLine(
        title=_(u"Fax"),
        required=False,
    )
    comment = schema.Text(
        title=_(u"Comment"),
        required=False,
    )
    channel = schema.Set(
        title=_(u"Channels"),
        description=_(u"Please select the channels this recipient "
                      u"is subscribed to."),
        value_type=schema.Choice(
            title=_(u"Channel"),
            vocabulary='pressapp.channelmanagement.channellisting',
        )
    )


class SubscriberEditForm(form.SchemaEditForm):
    grok.context(ISubscriber)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-subscriber')

    schema = ISubscriberEdit
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Edit subscriber")

    def updateActions(self):
        super(SubscriberEditForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Update subscriber"), name="save")
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
            _(u"Updating susbcriber has been cancelled."),
            type='info')
        return self.request.response.redirect(parent.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='pressapp.channelmanagement.subscriber')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        data['title'] = safe_unicode(context.Title())
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        assert ISubscriber.providedBy(context)
        fti = getUtility(IDexterityFTI,
                         name='pressapp.channelmanagement.subscriber')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        setattr(context, 'channel', list(data['channel']))
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"SUbscriber has successfully been updated"),
            type='info')
        return self.request.response.redirect(context.absolute_url())
