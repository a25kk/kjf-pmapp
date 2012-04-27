from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.component import getUtility
from zope.schema import getFieldsInOrder
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from Products.statusmessages.interfaces import IStatusMessage

from plone.dexterity.interfaces import IDexterityFTI
from pressapp.presscontent.presscenter import IPressCenter

from pressapp.presscontent import MessageFactory as _


class IGlobalSettings(form.Schema):

    email = schema.TextLine(
        title=_(u"Sender E-Mail-Address"),
        description=_(u"Please enter default send from E-mail address"),
        required=True,
    )
    name = schema.TextLine(
        title=_("Sender Name"),
        description=_(u"Provide a default sender name to be included"),
        required=True,
    )
    testEmail = schema.TextLine(
        title=_(u"E-Mail Address for Tests"),
        description=_(u"Default email address used in test despatches"),
        required=True,
    )
    testRecipients = schema.List(
        title=_(u"Test Recipients"),
        description=_(u"A list of test recipients - one address per line "
                      u"comma seperated in the format: E-mail, Name"),
        value_type=schema.TextLine(
            title=_(u"Recipient"),
        ),
        required=False,
    )
    subscribers = schema.List(
        title=_(u"Subscribers"),
        description=_(u"A list of subscribers - one address per line "
                      u"- these are available as default list"),
        value_type=schema.TextLine(
            title=_(u"Subscriber"),
        ),
        required=False,
    )


class IUpdateTemplatePR(form.Schema):

    mailtemplate = schema.SourceText(
        title=_(u"Press Release E-Mail Template"),
        required=True,
    )


class IUpdateTemplatePI(form.Schema):

    mailtemplate_pi = schema.SourceText(
        title=_(u"Press Invitation E-Mail Template"),
        required=True,
    )


class IUpdateStylesheet(form.Schema):

    stylesheet = schema.Text(
        title=_(u"Stylesheet for HTML E-Mails"),
        required=True,
    )


class GlobalSettingsForm(form.SchemaEditForm):
    grok.context(IPressCenter)
    grok.require('cmf.AddPortalContent')
    grok.name('update-settings')

    schema = IGlobalSettings
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Update default settings")

    def updateActions(self):
        super(GlobalSettingsForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Save Settings"), name="save")
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
            _(u"Update of global settings has been cancelled"),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='pressapp.presscontent.presscenter')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        fti_name = 'pressapp.presscontent.presscenter'
        fti = getUtility(IDexterityFTI, name=fti_name)
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"Global settings successfully updated"),
            type='info')
        return self.request.response.redirect(
                    context.absolute_url() + '/@@global-settings')


class UpdateTemplatePRForm(form.SchemaEditForm):
    grok.context(IPressCenter)
    grok.require('cmf.AddPortalContent')
    grok.name('update-pr-template')

    schema = IUpdateTemplatePR
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Update press release template")

    def updateActions(self):
        super(UpdateTemplatePRForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

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
            _(u"Update of press release template has been cancelled"),
            type='info')
        return self.request.response.redirect(
                context.absolute_url() + '/@@global-settings')

    def getContent(self):
        context = aq_inner(self.context)
        data = {}
        try:
            template = context.mailtemplate
        except:
            template = getattr(context, 'mailtemplate', '')
        data['mailtemplate'] = template
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        new_template = data['mailtemplate']
        if new_template:
            setattr(context, 'mailtemplate', new_template)
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"Global settings successfully updated"),
            type='info')
        return self.request.response.redirect(
                    context.absolute_url() + '/@@global-settings')


class UpdateTemplatePIForm(form.SchemaEditForm):
    grok.context(IPressCenter)
    grok.require('cmf.AddPortalContent')
    grok.name('update-pi-template')

    schema = IUpdateTemplatePI
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Update press invitation template")

    def updateActions(self):
        super(UpdateTemplatePIForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

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
            _(u"Update of press invitation template has been cancelled"),
            type='info')
        return self.request.response.redirect(
                context.absolute_url() + '/@@global-settings')

    def getContent(self):
        context = aq_inner(self.context)
        data = {}
        try:
            template = context.mailtemplate_pi
        except:
            template = getattr(context, 'mailtemplate_pi', '')
        data['mailtemplate_pi'] = template
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        new_template = data['mailtemplate_pi']
        if new_template:
            setattr(context, 'mailtemplate_pi', new_template)
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"Global settings successfully updated"),
            type='info')
        return self.request.response.redirect(
                    context.absolute_url() + '/@@global-settings')


class UpdateStylesheetForm(form.SchemaEditForm):
    grok.context(IPressCenter)
    grok.require('cmf.AddPortalContent')
    grok.name('update-stylesheet')

    schema = IUpdateStylesheet
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Update used CSS file for E-Mails")

    def updateActions(self):
        super(UpdateStylesheetForm, self).updateActions()
        self.actions['save'].addClass("btn")
        self.actions['cancel'].addClass("btn")

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
            _(u"Update of CSS has been cancelled"),
            type='info')
        return self.request.response.redirect(
                context.absolute_url() + '/@@global-settings')

    def getContent(self):
        context = aq_inner(self.context)
        data = {}
        try:
            css = context.stylesheet
        except:
            css = getattr(context, 'stylesheet', '')
        data['stylesheet'] = css
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        new_css = data['stylesheet']
        if new_css:
            setattr(context, 'stylesheet', new_css)
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"Global CSS settings successfully updated"),
            type='info')
        return self.request.response.redirect(
                    context.absolute_url() + '/@@global-settings')
