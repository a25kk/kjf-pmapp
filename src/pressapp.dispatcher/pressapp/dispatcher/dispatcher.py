import cStringIO
import formatter
import urllib

from htmllib import HTMLParser
from urlparse import urlparse
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.Header import Header

from datetime import datetime
from Acquisition import aq_inner
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from five import grok
from zope.site.hooks import getSite
from zope.component import getMultiAdapter
from Products.CMFPlone.utils import safe_unicode

import logging
log = logging.getLogger("pressapp.dispatcher")

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.interfaces import IContentish

from pressapp.dispatcher.safehtmlparser import SafeHTMLParser

from plone.uuid.interfaces import IUUID

from pressapp.presscontent.pressrelease import IPressRelease
from pressapp.presscontent.pressinvitation import IPressInvitation
from pressapp.dispatcher import MessageFactory as _


class Dispatcher(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
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
        proptool = getToolByName(context, 'portal_properties')
        charset = proptool.getProperty('default_charset')
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
        image_urls = rendered_email['images']
        css_file = self.default_data['stylesheet']
        plain_text = plain_text.replace('[[PC_CSS]]', '')
        text = text_html.replace('[[PC_CSS]]', str(css_file))
        for recipient in recipients:
            recipient_name = self.safe_portal_encoding(recipient['name'])
            personal_text = text.replace('[[SUBSCRIBER]]',
                str(recipient_name))
            personal_text_plain = plain_text.replace('[[SUBSCRIBER]]',
                str(recipient_name))

            outer = MIMEMultipart('related')
            outer['To'] = Header('<%s>' % safe_unicode(recipient['mail']))
            outer['From'] = self.default_data['email']
            outer['Subject'] = subject_header
            outer.epilogue = ''
            outer.preamble = 'This is a multi-part message in MIME format.'
            alternatives = MIMEMultipart('alternative')
            outer.attach(alternatives)
            text_part = MIMEText(personal_text_plain, 'plain', charset)
            html_text = MIMEText(personal_text, 'html', charset)
            image_number = 0
            reference_tool = getToolByName(context, 'reference_catalog')
            for image_url in image_urls:
                try:
                    image_url = urlparse(image_url)[2]
                    if 'resolveuid' in image_url:
                        urlparts = image_url.split('/')[1:]
                        uuid = urlparts.pop(0)
                        o = reference_tool.lookupObject(uuid)
                        if o and urlparts:
                            o = o.restrictedTraverse(urlparts[0])
                    if "@@images" in image_url:
                        image_url = image_url[:image_url.index('@@images')]
                        o = context.restrictedTraverse(
                                urllib.unquote(image_url))
                    else:
                        o = context.restrictedTraverse(
                                urllib.unquote(image_url))
                except Exception, e:
                    log.error('Could not resolve the image \"%s\": %s'
                                % (image_url, e))
                else:
                    if hasattr(o, "_data"):
                        image = MIMEImage(o._data)
                    elif hasattr(o, "data"):
                        image = MIMEImage(o.data)
                    else:
                        image = MIMEImage(o.GET())
                    image["Content-ID"] = "<image_%s>" % image_number
                    image_number += 1
                    alternatives.attach(image)
            alternatives.attach(text_part)
            alternatives.attach(html_text)
            try:
                mailhost.send(outer.as_string())
                log.info("Sent newsletter to \"%s\"" % recipient['mail'])
                send_counter += 1
            except Exception, e:
                log.info("Sending to \"%s\" failed" % recipient['mail'])
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
                finally:
                    setSecurityManager(sm)

    def _getRecievers(self, type):
        context = aq_inner(self.context)
        if type == 'test':
            portal = getSite()
            presscenter = portal['presscenter']
            recievers = presscenter.testRecipients
        else:
            recievers = getattr(context, 'recipients', '')
        recipients = []
        if recievers:
            for address in recievers:
                recipient = {}
                recipient_email, recipient_name = address.split(',')
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
        data['date'] = self.localize(datetime.now(), longformat=False)
        if IPressRelease.providedBy(context):
            data['kicker'] = context.kicker
            data['subtitle'] = context.subtitle
            if context.image:
                url = context.absolute_url()
                filename = context.image.filename
                data['file_url'] = url + '/@@download/attachment/' + filename
                data['file_name'] = filename
                data['image_tag'] = self.getImageTag(context)
                data['file_caption'] = context.caption
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
            data['start'] = self.localize(context.start, longformat=True)
            data['end'] = self.localize(context.end, longformat=True)
            closed = context.closed
            if closed == True:
                data['closed'] = _(u"Admittance for invited guests only")
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
        text = parser_output_zpt.html
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
            anchorlist += "[%d] %s\n" % (counter, item)
        #text = textout.getvalue() + anchorlist
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
        target_uid = self.request.get('uid')
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
    grok.require('zope2.View')
    grok.name('dispatch-success')
