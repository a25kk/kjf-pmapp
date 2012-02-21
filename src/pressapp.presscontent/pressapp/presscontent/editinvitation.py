from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified
from zope.component import getUtility
from zope.schema import getFieldsInOrder

from plone.directives import form
from z3c.form import button
from plone.app.textfield import RichText
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from pressapp.presscontent.pressinvitation import IPressInvitation

from pressapp.presscontent import MessageFactory as _


class IPressInvitationEdit(form.Schema):

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


class PressInvitationEditForm(form.SchemaEditForm):
    grok.context(IPressInvitation)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-press-invitation')

    schema = IPressInvitationEdit
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Edit press invitation")

    def updateActions(self):
        super(PressInvitationEditForm, self).updateActions()
        self.actions['save'].addClass("btn btn-large")
        self.actions['cancel'].addClass("btn btn-large")

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
            _(u"Editing this press invitation has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                name='pressapp.presscontent.pressinvitation')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        data['description'] = safe_unicode(context.Description())
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        assert IPressInvitation.providedBy(context)
        fti = getUtility(IDexterityFTI,
                name='pressapp.presscontent.pressinvitation')
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
            _(u"Press invitation was successfully updated"),
            type='info')
        return self.request.response.redirect(context.absolute_url() + '/view')
