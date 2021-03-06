# -*- coding: utf-8 -*-
"""Module providing api access to jobpostings """

import json
import time
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode
from five import grok
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.keyring import django_random
from zope.component import getMultiAdapter
from zope.schema.vocabulary import getVocabularyRegistry

from jobtool.jobcontent.interfaces import IJobTool
from jobtool.jobcontent.jobopening import IJobOpening

from jobtool.jobcontent import MessageFactory as _


class JobOpeningsAPI(grok.View):
    grok.context(INavigationRoot)
    grok.layer(IJobTool)
    grok.require('zope2.View')
    grok.name('api')

    def update(self):
        self.user_token = self.request.get('token', None)

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
            self.subpath.append(name)
        return

    def is_equal(self, a, b):
        """ Constant time comparison """
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        return result == 0

    def get_stored_records(self, token):
        key_base = 'jobtool.jobcontent.interfaces.IJobToolSettings'
        key = key_base + '.' + token
        return api.portal.get_registry_record(key)

    def valid_token(self):
        if self.user_token:
            token = self.user_token
            keys = self.get_stored_records('api_access_keys')
            if token in keys:
                return True
        return False

    def active_jobs(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        results = catalog(object_provides=IJobOpening.__identifier__,
                          review_state='published',
                          archive=True,
                          sort_on='start',
                          sort_order='reverse')
        return results

    def pretty_term(self, vocab, term):
        context = aq_inner(self.context)
        vocabulary = 'jobtool.jobcontent.' + vocab
        vr = getVocabularyRegistry()
        records = vr.get(context, vocabulary)
        try:
            vocabterm = records.getTerm(term)
            prettyname = vocabterm.title
        except (LookupError, KeyError):
            prettyname = term
        return prettyname

    def get_item_data(self, item):
        obj = item.getObject()
        pts = api.portal.get_tool(name="translation_service")
        uuid = api.content.get_uuid(obj=obj)
        portal_url = api.portal.get().absolute_url()
        obj_url = portal_url + '/@@jobdetails?juid=' + uuid
        job_type = self.pretty_term('jobTypes', obj.jobtype)
        translated_jobtype = pts.translate(job_type,
                                           'jobtool.jobcenter',
                                           target_language='de')
        location_alt = getattr(obj, 'locationOverride', None)
        if location_alt and location_alt is not None:
            job_location = location_alt
        else:
            job_location = self.pretty_term('jobLocations', obj.location)
        info = {}
        info['uid'] = uuid
        info['created'] = item.created.ISO8601()
        info['modified'] = item.modified.ISO8601()
        info['id'] = item.getId
        info['title'] = item.Title
        info['url'] = obj_url
        info['institution'] = self.pretty_term('jobInstitutions',
                                               obj.institution)
        info['location'] = job_location
        info['type'] = translated_jobtype
        info['date'] = item.start.isoformat()
        info['summary'] = obj.text.output
        return info

    def get_items(self):
        results = self.active_jobs()
        items = []
        for r in results:
            item = self.get_item_data(r)
            items.append(item)
        return items

    def _process_request(self):
        api_url = self.request.get('ACTUAL_URL')
        data = {
            'url': api_url,
            'timestamp': int(time.time()),
        }
        if self.valid_token():
            items = self.get_items()
            data['count'] = len(items)
            data['items'] = items
        else:
            data['error'] = u"Access token invalid or missing from request"
        return data

    def render(self):
        start = time.time()
        data = self._process_request()
        end = time.time()
        data.update(dict(_runtime=end-start))
        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(data)


class JobOpeningsAPISettings(grok.View):
    grok.context(INavigationRoot)
    grok.layer(IJobTool)
    grok.require('cmf.ManagePortal')
    grok.name('api-settings')

    def update(self):
        self.has_records = self._has_records()
        self.errors = {}
        unwanted = ('_authenticator', 'form.button.Submit')
        required = ('tokenidx')
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((self.context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            form = self.request.form
            form_data = {}
            form_errors = {}
            errorIdx = 0
            for value in form:
                if value not in unwanted:
                    form_data[value] = safe_unicode(form[value])
                    if not form[value] and value in required:
                        error = {}
                        error['active'] = True
                        error['msg'] = _(u"This field is required")
                        form_errors[value] = error
                        errorIdx += 1
                    else:
                        error = {}
                        error['active'] = False
                        error['msg'] = form[value]
                        form_errors[value] = error
            if errorIdx > 0:
                self.errors = form_errors
            else:
                self._create_token(form)

    def _get_records(self):
        key = 'jobtool.jobcontent.interfaces.IJobToolSettings.api_access_keys'
        return api.portal.get_registry_record(key)

    def _set_records(self, data):
        context = aq_inner(self.context)
        key = 'jobtool.jobcontent.interfaces.IJobToolSettings.api_access_keys'
        api.portal.set_registry_record(key, data)
        url = '{0}/@@api-settings'.format(context.absolute_url())
        return self.request.response.redirect(url)

    def stored_records(self):
        return self._get_records()

    def _has_records(self):
        records = False
        if self.stored_records() is not None and len(self.stored_records()):
            records = True
        return records

    def _create_token(self, data):
        context = aq_inner(self.context)
        idx = int(data['tokenidx'])
        records = self._get_records()
        keys = []
        if records is not None:
            keys = list(records)
        for x in range(int(idx)):
            token = django_random.get_random_string(length=40)
            keys.append(safe_unicode(token))
        self._set_records(tuple(keys))
        msg = _(u"Successfully generated API access tokens")
        api.portal.show_message(msg, request=self.request)
        url = '{0}/@@api-settings'.format(context.absolute_url())
        return self.request.response.redirect(url)
