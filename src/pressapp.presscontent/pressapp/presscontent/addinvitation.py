import datetime
from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from plone.dexterity.utils import createContentInContainer
from plone.app.textfield import RichText
from Products.statusmessages.interfaces import IStatusMessage
from pressapp.presscontent.pressroom import IPressRoom

from pressapp.presscontent import MessageFactory as _


class IPressInvitationAdd(form.Schema):

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Enter the title of the press invitation."),
        required=True,
    )
    text = RichText(
        title=_(u"Text"),
        required=True,
    )
    start = schema.Datetime(
        title=_(u"Start Date"),
        required=True,
    )
    end = schema.Datetime(
        title=_(u"End Date"),
        required=True,
    )
    location = schema.TextLine(
        title=_(u"Event Location"),
        required=True,
    )
    schedule = RichText(
        title=_(u"Event Schedule"),
        description=_(u"Enter optional schedule information."),
        required=False,
    )
    travel = schema.Text(
        title=_(u"Travel information"),
        description=_(u"Enter optional travel information."),
        required=False,
    )
    directions = schema.URI(
        title=_(u"Directions Link"),
        description=_(u"Enter link to Google Map for directions"),
        required=False,
    )
    closed = schema.Bool(
        title=_(u"Closed Event"),
        description=_(u"Please select if the event is public."),
        required=False,
    )
    description = schema.Text(
        title=_(u"Summary"),
        description=_(u"Optional summary that is useful as a preview text "
                      u"in email clients that support this feature."),
        required=False,
    )


@form.default_value(field=IPressInvitationAdd['start'])
def startDefaultValue(data):
    return datetime.datetime.today() + datetime.timedelta(7)


@form.default_value(field=IPressInvitationAdd['end'])
def endDefaultValue(data):
    return datetime.datetime.today() + datetime.timedelta(10)


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
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

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
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"A new press invitation was successfully added"),
            type='info')
        return self.request.response.redirect(item.absolute_url())
