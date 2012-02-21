from StringIO import StringIO
from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.utils import cleanId
from Products.PlonePAS.utils import scale_image
from OFS.Image import Image
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.interfaces import IContentish
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
    organization = schema.TextLine(
        title=_(u"Organisation"),
        description=_(u"Enter your organisation's name"),
        required=True,
    )
    home_page = schema.TextLine(
        title=_(u"Homepage"),
        description=_(u"Enter URL of your company's homepage"),
        required=False,
    )
    presslink = schema.TextLine(
        title=_(u"Press Link"),
        description=_(u"Enter direct press link."),
        required=True,
    )
    portrait = NamedBlobImage(
        title=_(u"Portrait"),
        description=_(u"Upload a personal portrait or company logo"),
        required=False,
    )


class MemberInformationForm(form.SchemaEditForm):
    grok.context(IContentish)
    grok.require('cmf.AddPortalContent')
    grok.name('member-information')

    schema = IMemberInformation
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Update member information")

    def updateActions(self):
        super(MemberInformationForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary")
        self.actions['cancel'].addClass("btn")

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

    def getContent(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        data = {}
        data['fullname'] = safe_unicode(member.getProperty('fullname', ''))
        data['location'] = safe_unicode(member.getProperty('location', ''))
        data['home_page'] = safe_unicode(member.getProperty('home_page', ''))
        data['organization'] = safe_unicode(member.getProperty('organization',
                                                               ''))
        data['presslink'] = safe_unicode(member.getProperty('presslink', ''))
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        member.setMemberProperties({
            'fullname': data['fullname'],
            'location': data['location'],
            'home_page': data['home_page'],
            'organization': data['organization'],
            'presslink': data['presslink']})
        image_file = data['portrait']
        if image_file:
            portrait = StringIO(image_file.data)
            scaled, mimetype = scale_image(portrait)
            portrait = Image(id=cleanId(member.getId()), file=scaled, title='')
            mdata = getToolByName(context, 'portal_memberdata')
            mdata._setPortrait(portrait, cleanId(member.getId()))
        IStatusMessage(self.request).addStatusMessage(
            _(u"Member information has been updated successfully."),
            type='info')
        return self.request.response.redirect(context.absolute_url())
