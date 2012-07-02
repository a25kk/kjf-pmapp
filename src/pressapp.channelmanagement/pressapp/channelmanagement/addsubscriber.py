from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.field import NamedBlobFile
from Products.statusmessages.interfaces import IStatusMessage
from pressapp.channelmanagement.channel import IChannel

from pressapp.presscontent import MessageFactory as _


class ISubscriberAdd(form.Schema):

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


class SubscriberAddForm(form.SchemaEditForm):
    grok.context(IChannel)
    grok.require('cmf.AddPortalContent')
    grok.name('add-subscriber')

    schema = ISubscriberAdd
    ignoreContext = True
    css_class = 'overlayForm'

    label = _(u"Add new subscriber address")

    def updateActions(self):
        super(SubscriberAddForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Create subscriber"), name="save")
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
            _(u"The creation of a new subscriber has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def applyChanges(self, data):
        context = aq_inner(self.context)
        assert IChannel.providedBy(context)
        item = createContentInContainer(context,
            'pressapp.channelmanagement.subscriber',
            checkConstraints=True, **data)
        setattr(context, 'channel', list(data['channel']))
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"A new address was successfully added"),
            type='info')
        return self.request.response.redirect(item.absolute_url())
