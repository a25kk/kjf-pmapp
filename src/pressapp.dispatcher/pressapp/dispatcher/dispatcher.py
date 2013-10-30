import cStringIO
import formatter

from htmllib import HTMLParser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from datetime import datetime
from Acquisition import aq_inner
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from five import grok
from zope.i18n import translate
from zope.site.hooks import getSite
from zope.component import getMultiAdapter
from zope.lifecycleevent import modified

from Products.CMFPlone.utils import safe_unicode

import logging
log = logging.getLogger("pressapp.dispatcher")

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.interfaces import IContentish

from pressapp.dispatcher.safehtmlparser import SafeHTMLParser
from pressapp.dispatcher.utils import postprocess_emailtemplate

from plone.uuid.interfaces import IUUID

from pressapp.presscontent.pressrelease import IPressRelease
from pressapp.presscontent.pressinvitation import IPressInvitation

from pressapp.dispatcher import MessageFactory as _


class Dispatcher(grok.View):
    grok.context(IContentish)
    grok.require('cmf.ModifyPortalContent')
    grok.name('dispatcher')

    def update(self):
        context = aq_inner(self.context)
        self.default_data = self._getPressCenterData()
        send_type = self.request.get('type', '')
        if send_type:
            self.recipients = self._getRecievers(send_type)
            self.status = self.send()
            IStatusMessage(self.request).addStatusMessage(
                _(u"Your request has been dispatched"), type='info')
            return self.request.response.redirect(
                context.absolute_url() + '/@@dispatch-success')

    def send(self):
        context = aq_inner(self.context)
        mailhost = getToolByName(context, 'MailHost')
        subject = self.request.get('subject', '')
        if subject == '':
            subject = context.Title()
        subject_header = Header(safe_unicode(subject))
        send_counter = 0
        send_error_counter = 0
        recipients = self.recipients
        context_content = self._dynamic_content()
        output_file = self._render_output_html()
        output_html = self._compose_email_content(output_file, context_content)
        rendered_email = self._exchange_relative_urls(output_html)
        text_html = rendered_email['html']
        plain_text = rendered_email['plain']
        css_file = self.default_data['stylesheet']
        plain_text = plain_text.replace('[[PC_CSS]]', '')
        text = text_html.replace('[[PC_CSS]]', str(css_file))
        for body_charset in 'US-ASCII', 'iso-8859-1', 'UTF-8':
            try:
                plain_text = safe_unicode(plain_text).encode(body_charset)
            except UnicodeError:
                pass
            else:
                break
        for recipient in recipients:
            recipient_name = self.safe_portal_encoding(recipient['name'])
            personal_text = text.replace('[[SUBSCRIBER]]',
                                         str(recipient_name))
            personal_text_plain = plain_text.replace('[[SUBSCRIBER]]',
                                                     str(recipient_name))

            outer = MIMEMultipart('alternative')
            outer['To'] = Header('<%s>' % safe_unicode(recipient['mail']))
            outer['From'] = self.default_data['email']
            outer['Subject'] = subject_header
            outer.epilogue = ''
            outer.preamble = 'This is a multi-part message in MIME format.'
            # cs_utf = Charset('utf-8')
            # plain_part = personal_text_plain.encode(body_charset)
            text_part = MIMEText(personal_text_plain,
                                 'plain',
                                 'UTF-8')
            html_text = MIMEText(personal_text,
                                 'html',
                                 'UTF-8')
            outer.attach(text_part)
            outer.attach(html_text)
            try:
                mailhost.send(outer.as_string())
                log.info("Sent newsletter to \"%s\"" % recipient['mail'])
                send_counter += 1
            except Exception as e:
                log.info("Sending to \"%s\" failed: %s" % (
                         recipient['mail'], e))
                send_error_counter += 1
        log.info("Dipatched to %s recipients with %s errors." % (send_counter,
                 send_error_counter))
        if self.request.get('type') != 'test':
            wftool = getToolByName(context, 'portal_workflow')
            if wftool.getInfoFor(context, 'review_state') == 'private':
                owner = context.getWrappedOwner()
                sm = getSecurityManager()
                # create a new context, as the owner of the folder
                newSecurityManager(self.request, owner)
                try:
                    wftool.doActionFor(context, 'publish')
                    modified(context)
                    context.reindexObject(idxs='modified')
                finally:
                    setSecurityManager(sm)

    def _getRecievers(self, type):
        context = aq_inner(self.context)
        portal = getSite()
        presscenter = portal['presscenter']
        if type == 'test':
            recievers = presscenter.testRecipients
        else:
            recievers = getattr(context, 'recipients', '')
        recipients = []
        if IPressRelease.providedBy(context) and type == 'send_now':
            subscribers = getattr(presscenter, 'subscribers', '')
            if subscribers:
                for item in subscribers:
                    recipient = {}
                    recipient['mail'] = item
                    recipient['name'] = item
                    recipients.append(recipient)
        if recievers:
            for address in recievers:
                recipient = {}
                try:
                    recipient_email, recipient_name = address.split(',')
                except:
                    recipient_email = address
                    recipient_name = address
                recipient['mail'] = recipient_email
                recipient['name'] = safe_unicode(recipient_name)
                recipients.append(recipient)
        return recipients

    def _getPressCenterData(self):
        context = aq_inner(self.context)
        portal = getSite()
        presscenter = portal['presscenter']
        data = {}
        if IPressInvitation.providedBy(context):
            data['template'] = presscenter.mailtemplate_pi
        else:
            data['template'] = presscenter.mailtemplate
        data['stylesheet'] = presscenter.stylesheet
        data['sender'] = presscenter.name
        data['email'] = presscenter.email
        return data

    def _dynamic_content(self):
        context = aq_inner(self.context)
        memberinfo = self.memberdata()
        data = {}
        data['title'] = context.Title()
        data['summary'] = context.Description()
        data['location'] = context.location
        data['text'] = context.text.output
        data['url'] = self._construct_webview_link()
        data['pdf'] = self.pdf_download_link(context)
        data['date'] = self.localize(datetime.now(), longformat=False)
        if IPressRelease.providedBy(context):
            if context.kicker:
                data['kicker'] = context.kicker
            else:
                data['kicker'] = ''
            if context.subtitle:
                data['subtitle'] = context.subtitle
            else:
                data['subtitle'] = ''
            if context.image:
                url = context.absolute_url()
                filename = context.image.filename
                data['file_url'] = url + '/@@download/attachment/' + filename
                data['file_name'] = filename
                data['image_tag'] = self.getImageTag(context)
                data['file_caption'] = context.imagename
            data['attachments'] = self.getAttachments()
        if IPressInvitation.providedBy(context):
            if context.schedule:
                data['schedule'] = context.schedule.output
            else:
                data['schedule'] = ''
            if context.travel:
                data['travel'] = context.travel
            else:
                data['travel'] = ''
            if context.directions:
                data['directions'] = context.directions
            else:
                data['directions'] = ''
            data['start'] = context.start.strftime("%d.%m.%Y %H:%M")
            data['end'] = context.end.strftime("%d.%m.%Y %H:%M")
            closed = context.closed
            if closed is True:
                closed_msg = translate(
                    _(u"Diese Veranstaltung kann nur auf Einladung besucht "
                      u"werden. Von einer Publikation bitten wir daher "
                      u"abzusehen."),
                    domain='pressapp.presscontent',
                    target_language='de')
                data['closed'] = closed_msg
            else:
                data['closed'] = ''
        if memberinfo:
            data['org'] = memberinfo['org']
            data['link'] = memberinfo['link']
        return data

    def _compose_email_content(self, template, data):
        for value in data:
            token = '[[PC_' + value.upper() + ']]'
            try:
                new_value = self.safe_portal_encoding(data[value])
            except AttributeError:
                new_value = str(data[value])
            template = template.replace(str(token), new_value)
        return template

    def _render_output_html(self):
        """ Return rendered newsletter
            with header+body+footer (raw html).
        """
        default_data = self.default_data
        out_template = default_data['template']
        output_html = self.safe_portal_encoding(out_template)
        return output_html

    def _exchange_relative_urls(self, output_html):
        """ exchange relative URLs and
            return dict with html, plain and images
        """
        parser_output_zpt = SafeHTMLParser(self)
        parser_output_zpt.feed(output_html)
        text_raw = parser_output_zpt.html
        text_raw_clean = text_raw.replace('\r', '')
        text = postprocess_emailtemplate(text_raw_clean)
        text_plain = self.create_plaintext_message(text)
        image_urls = parser_output_zpt.image_urls
        return dict(html=text, plain=text_plain, images=image_urls)

    def create_plaintext_message(self, text):
        """ Create a plain-text-message by parsing the html
            and attaching links as endnotes
        """
        plain_text_maxcols = 72
        textout = cStringIO.StringIO()
        formtext = formatter.AbstractFormatter(formatter.DumbWriter(
                                               textout, plain_text_maxcols))
        parser = HTMLParser(formtext)
        parser.feed(text)
        parser.close()
        # append the anchorlist at the bottom of a message
        # to keep the message readable.
        counter = 0
        anchorlist = "\n\n" + ("-" * plain_text_maxcols) + "\n\n"
        for item in parser.anchorlist:
            counter += 1
            if item.startswith('https://'):
                new_item = item.replace('https://', 'http://')
            else:
                new_item = item
            anchorlist += "[%d] %s\n" % (counter, new_item)
        text = textout.getvalue() + anchorlist
        del textout, formtext, parser, anchorlist
        return text

    def _construct_webview_link(self):
        context = aq_inner(self.context)
        portal = getSite()
        portal_url = portal.absolute_url()
        uuid = IUUID(context, None)
        url = portal_url + '/@@pressitem-view?uid=' + uuid
        return url

    def pdf_download_link(self, obj):
        portal = getSite()
        portal_url = portal.absolute_url()
        uuid = IUUID(obj, None)
        url = portal_url + '/@@download-file-version?uid=' + uuid
        return url

    def memberdata(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        memberinfo = {}
        memberinfo['org'] = member.getProperty('organization', '')
        memberinfo['link'] = member.getProperty('home_page', '')
        return memberinfo

    def getImageTag(self, item):
        obj = item
        scales = getMultiAdapter((obj, self.request), name='images')
        scale = scales.scale('image', scale='preview')
        imageTag = None
        if scale is not None:
            imageTag = scale.tag()
        return imageTag

    def getAttachments(self):
        context = aq_inner(self.context)
        target_uid = IUUID(context, None)
        ptool = getToolByName(context, 'portal_url')
        portal = ptool.getPortalObject()
        attachments = portal.unrestrictedTraverse(
            '@@pressitem-attachments')(uid=target_uid)
        return attachments

    def safe_portal_encoding(self, string):
        portal = getSite()
        props = portal.portal_properties.site_properties
        charset = props.getProperty("default_charset")
        return safe_unicode(string).encode(charset)

    def localize(self, time, longformat):
        return self._time_localizer()(time.isoformat(),
                                      long_format=longformat,
                                      context=self.context,
                                      domain='plonelocales')

    def _time_localizer(self):
        translation_service = getToolByName(self.context,
                                            'translation_service')
        return translation_service.ulocalized_time


class DispatchSuccess(grok.View):
    grok.context(IContentish)
    grok.require('cmf.ModifyPortalContent')
    grok.name('dispatch-success')
