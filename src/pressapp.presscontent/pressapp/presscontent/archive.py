import hashlib
from datetime import datetime
from Acquisition import aq_inner
from five import grok
from App.config import getConfiguration
from zope.i18n import translate
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite
from zope.schema.vocabulary import getVocabularyRegistry

from plone.app.uuid.utils import uuidToObject
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.statusmessages.interfaces import IStatusMessage
from pressapp.dispatcher.safehtmlparser import SafeHTMLParser
from pressapp.dispatcher.utils import postprocess_emailtemplate

from plone.app.contentlisting.interfaces import IContentListing
from plone.uuid.interfaces import IUUID

from pressapp.presscontent.pressrelease import IPressRelease
from pressapp.presscontent.pressinvitation import IPressInvitation
from pressapp.presscontent.imageattachment import IImageAttachment

from pressapp.presscontent import MessageFactory as _


class ArchiveView(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('press-archive')

    def update(self):
        self.has_items = len(self.press_content()) > 0

    def press_content(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        dist_id = self.request.get('distid', None)
        if dist_id:
            results = catalog(object_provides=IPressRelease.__identifier__,
                          review_state='published',
                          archive=True,
                          distributor=dist_id,
                          sort_on='effective')
        else:
            results = catalog(object_provides=IPressRelease.__identifier__,
                              review_state='published',
                              archive=True,
                              sort_on='effective')
        resultlist = IContentListing(results)
        return resultlist

    def generate_hashes(self):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        dist_vocab = vr.get(context,
            'pressapp.presscontent.externalDistributors')
        data = {}
        for entry in dist_vocab:
            key = entry.value
            h = hashlib.sha1()
            h.update(key)
            data[key] = h.hexdigest()
        return data


class PressItemView(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('pressitem-view')

    def update(self):
        self.presscontent = self.resolvePressItem()
        self.default_data = self._getPressCenterData(self.presscontent)

    def webversion(self):
        obj = self.presscontent
        context_content = self._dynamic_content(obj)
        output_file = self._render_output_html()
        output_html = self._compose_email_content(output_file, context_content)
        rendered = self._exchange_relative_urls(output_html)
        rendered_email = postprocess_emailtemplate(rendered)
        css_file = self.default_data['stylesheet']
        text = rendered_email.replace('[[PC_CSS]]', str(css_file))
        return text

    def resolvePressItem(self):
        uid = self.request.get('uid', '')
        if uid:
            obj = uuidToObject(uid)
            if not obj:
                IStatusMessage(self.request).addStatusMessage(
                    _(u"The requested item was not found"), type='error')
            else:
                return obj

    def _getPressCenterData(self, obj):
        context = obj
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

    def _dynamic_content(self, target_obj):
        context = target_obj
        memberinfo = self.memberdata()
        data = {}
        data['title'] = context.Title()
        data['summary'] = context.Description()
        data['location'] = context.location
        data['text'] = context.text.output
        data['url'] = self._construct_webview_link(context)
        data['pdf'] = self.pdf_download_link(context)
        data['date'] = self.localize(datetime.now(), longformat=False)
        if IPressRelease.providedBy(context):
            if context.kicker:
                data['kicker'] = getattr(context, 'kicker', '')
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
            if closed == True:
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
        text = parser_output_zpt.html
        return text

    def _construct_webview_link(self, obj):
        portal = getSite()
        portal_url = portal.absolute_url()
        uuid = IUUID(obj, None)
        url = portal_url + '/@@pressitem-view?uid=' + uuid
        return url

    def pdf_download_link(self, obj):
        portal_url = self.clean_portal_url()
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
        scale = scales.scale('image', scale='mini')
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

    def clean_portal_url(self):
        portal = getSite()
        portal_url = portal.absolute_url()
        static_url = 'http://kjf-presse.de'
        if getConfiguration().debug_mode:
            return portal_url
        else:
            return static_url

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


class AttachmentsView(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('pressitem-attachments')

    def __call__(self, *args, **kw):
        portal_url = self.clean_portal_url()
        view_name = '/@@download-assets?uid='
        params = kw.copy()
        if params.get('uid'):
            self.target_uid = params.get('uid', None)
        self.presscontent = self.resolvePressItem(self.target_uid)
        options = {'items': list()}
        pressitem = self.presscontent
        iteminfo = {}
        if pressitem.imagename:
            iteminfo['title'] = pressitem.imagename
        else:
            iteminfo['title'] = pressitem.Title()
        uuid = IUUID(pressitem, None)
        timestamp_string = self.generate_timestamp(pressitem)
        iteminfo['url'] = portal_url + view_name + uuid + timestamp_string
        iteminfo['type'] = 'MainImage'
        iteminfo['image'] = self.getImageTag(pressitem)
        options['items'].append(iteminfo)
        attachments = self.queryAttachments()
        for item in attachments:
            item_obj = item.getObject()
            item_uuid = IUUID(item_obj, None)
            item_timestamp = self.generate_timestamp(item_obj)
            info = {}
            info['title'] = item.Title
            info['url'] = portal_url + view_name + item_uuid + item_timestamp
            info['type'] = item.portal_type
            if IImageAttachment.providedBy(item_obj):
                image_tag = self.getImageTag(item_obj)
                info['image'] = image_tag
            else:
                info['image'] = ''
            options['items'].append(info)
        template = ViewPageTemplateFile('attachments.pt')(self, **options)
        #clean_template = self.fix_ssl_links(template)
        return template

    def update(self):
        self.target_uid = self.request.get('uid', None)
        self.presscontent = self.resolvePressItem()

    def getImageTag(self, item):
        obj = item
        scales = getMultiAdapter((obj, self.request), name='images')
        scale = scales.scale('image', scale='thumb')
        imageTag = None
        if scale is not None:
            imageTag = scale.tag()
        return imageTag

    def queryAttachments(self):
        context = aq_inner(self.context)
        obj = self.presscontent
        catalog = getToolByName(context, 'portal_catalog')
        items = catalog(portal_type=['pressapp.presscontent.fileattachment',
                                     'pressapp.presscontent.imageattachment',
                                     'Image'],
                        path=dict(query='/'.join(obj.getPhysicalPath()),
                                  depth=1))
        #results = IContentListing(items)
        return items

    def resolvePressItem(self, uid=None):
        #uid = self.request.get('uid', '')
        if uid:
            obj = uuidToObject(uid)
            if not obj:
                IStatusMessage(self.request).addStatusMessage(
                    _(u"The requested item was not found"), type='error')
            else:
                return obj

    def clean_portal_url(self):
        portal = getSite()
        portal_url = portal.absolute_url()
        static_url = 'http://kjf-presse.de'
        if getConfiguration().debug_mode:
            return portal_url
        else:
            return static_url

    def generate_timestamp(self, item):
        url_param = '&timestamp='
        if hasattr(item, '_p_mtime'):
            timestamp = item._p_mtime
        else:
            timestamp = ''
        ts_string = url_param + str(timestamp)
        return ts_string
