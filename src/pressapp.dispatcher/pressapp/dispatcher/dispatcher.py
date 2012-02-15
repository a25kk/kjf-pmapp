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
        pass

    def render(self):
        return ''

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
