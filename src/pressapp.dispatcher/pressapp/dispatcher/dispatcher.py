import cStringIO
import formatter
import urllib

from htmllib import HTMLParser
from urlparse import urlparse
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.Header import Header

from Acquisition import aq_inner
from five import grok
from zope.site.hooks import getSite
from zope.component import queryUtility
from zope.component import getUtility
from Products.CMFPlone.utils import safe_unicode

import logging
log = logging.getLogger("pressapp.dispatcher")

from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from Products.CMFCore.interfaces import IContentish

from pressapp.dispatcher.safehtmlparser import SafeHTMLParser


class Dispatcher(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('dispatcher')

    def update(self):
        self.recipients = self._getRecievers()

    def send(self):
        context = aq_inner(self.context)
        mailhost = getToolByName(context, 'MailHost')
        proptool = getToolByName(context, 'portal_properties')
        charset = proptool.getProperty('default_charset')
        send_counter = 0
        send_error_counter = 0
        recipients = self.recipients()
        output_html = self._render_output_html()
        rendered_email = self._exchange_relative_urls(output_html)
        text = rendered_email['html']
        plain_text = rendered_email['plain']
        image_urls = rendered_email['images']
        for recipient in recipients:
            outer = MIMEMultipart('alternative')
            outer['To'] = Header('<%s>' % safe_unicode(recipient['mail']))
            recipient_name = self.safe_portal_encoding(recipient['name'])
            personal_text = text.replace('[[SUBSCRIBER]]', str(recipient_name))
            personal_text_plain = plain_text.replace('[[SUBSCRIBER]]',
                                                     str(recipient_name))
            outer['From'] = self.from_header()
            outer['Subject'] = self.subject_header()
            outer.epilogue = ''
            text_part = MIMEMultipart('related')
            text_part.attach(MIMEText(personal_text_plain, 'plain', charset))
            html_part = MIMEMultipart('related')
            html_text = MIMEText(personal_text, 'html', charset)
            html_part.attach(html_text)
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
                    else:
                        o = self.restrictedTraverse(urllib.unquote(image_url))
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
                    html_part.attach(image)
            outer.attach(text_part)
            outer.attach(html_part)
            try:
                mailhost.send(outer.as_string())
                log.info("Sent newsletter to \"%s\"" % recipient['mail'])
                send_counter += 1
            except Exception, e:
                log.info("Sending to \"%s\" failed" % recipient['mail'])
                send_error_counter += 1
        log.info("Dipatched to %s recipients with %s errors." % (send_counter,
            send_error_counter))
        if not hasattr(self.request, 'test') and not recipients:
            wftool = getToolByName(context, 'portal_workflow')
            if wftool.getInfoFor(context, 'review_state') == 'private':
                wftool.doActionFor(context, 'publish')

    def _getRecievers(self):
        context = aq_inner(self.context)
        recievers = getattr(context, 'recipients', '')
        recipients = []
        if recievers:
            for address in recievers:
                recipient = {}
                recipient_email, recipient_name = address.split(',')
                recipient['mail'] = recipient_email
                recipient['name'] = recipient_name
                recipients.append(recipient)
        return recipients

    def _render_output_html(self):
        """ Return rendered newsletter
            with header+body+footer (raw html).
        """
        enl = self.getNewsletter()
        props = getToolByName(self, "portal_properties").site_properties
        charset = props.getProperty("default_charset")
        # get out_template from ENL object and render it in context of issue
        out_template_pt_field = enl.getField('out_template_pt')
        ObjectField.set(out_template_pt_field, self, ZopePageTemplate(
            out_template_pt_field.getName(),
            enl.getRawOut_template_pt()))
        output_html = self.safe_portal_encoding(
            self.out_template_pt.pt_render())
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

        text = textout.getvalue() + anchorlist
        del textout, formtext, parser, anchorlist
        return text

    def safe_portal_encoding(string):
        portal = getSite()
        props = portal.portal_properties.site_properties
        charset = props.getProperty("default_charset")
        return safe_unicode(string).encode(charset)
