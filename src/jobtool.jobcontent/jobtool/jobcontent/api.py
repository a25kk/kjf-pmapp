# -*- coding: utf-8 -*-
"""Module providing api access to jobpostings """

import json
import time
from Acquisition import aq_inner
from five import grok
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.jsonapi.core import router
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import url_for
from zope.schema.vocabulary import getVocabularyRegistry

from jobtool.jobcontent.interfaces import IJobTool
from jobtool.jobcontent.jobopening import IJobOpening


# GET JOBPOSTINGS
@router.add_route('/jobpostings', 'jobpostings', methods=['GET'])
@router.add_route('/jobpostings/<string:uid>', 'jobpostings', methods=['GET'])
def get(context, request, token=None, uid=None):
    """ get job postings """
    items = get_items('jobtool.jobcontent.jobopening',
                      request,
                      uid=uid,
                      endpoint='jobpostings')
    return {
        'url': url_for('jobpostings'),
        'count': len(items),
        'items': items,
    }


class JobOpeningsAPI(grok.View):
    grok.context(INavigationRoot)
    grok.layer(IJobTool)
    grok.require('zope2.View')
    grok.name('api')

    def update(self):
        self.subpath = []

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

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
        if self.subpath:
            token = self.subpath[0]
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
