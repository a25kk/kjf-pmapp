import StringIO
from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from pressapp.presscontent.pressroom import IPressRoom

from pressapp.memberprofiles import MessageFactory as _


class IMemberInformation(form.Schema):

    fullname = schema.TextLine(
        title=_(u"Fullname"),
        description=_(u"Please enter first- and lastname"),
        required=True,
    )
    location = schema.TextLine(
        title=_(u"Location"),
        description=_(u"Please enter location"),
        required=True,
    )
    portrait = NamedBlobImage(
        title=_(u"Portrait"),
        description=_(u"Upload a personal portrait or company logo"),
        required=True,
    )


class MemberInformationForm(form.SchemaEditForm):
    grok.context(IPressRoom)
    grok.require('cmf.AddPortalContent')
    grok.name('member-information')

    schema = IMemberInformation
    ignoreContext = True
    css_class = 'overlayForm'

    label = _(u"Update member information")

    def updateActions(self):
        super(MemberInformationForm, self).updateActions()
        self.actions['save'].addClass("btn rgd large")
        self.actions['cancel'].addClass("btn large")

    @button.buttonAndHandler(_(u"Update"), name="save")
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
            _(u"Updating your member information has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def applyChanges(self, data):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        member.setMemberProperties({
            'fullname': data['fullname'],
            'location': data['location']
        })
        image_file = data['portrait']
        if image_file:
            portrait = StringIO(image_file.data)
            portrait.filename = image_file.filename
            mtool.changeMemberPortrait(portrait, member.getId())
        IStatusMessage(self.request).addStatusMessage(
            _(u"member information has been updated successfully."),
            type='info')
        return self.request.response.redirect(context.absolute_url())
