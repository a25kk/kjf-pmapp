# -*- coding: utf-8 -*-
"""Module providing api access to jobpostings """

from plone.jsonapi.core import router
from plone.jsonapi.routes.api import url_for

from plone.jsonapi.routes.api import get_items


# GET JOBPOSTINGS
@router.add_route('/jobpostings', 'jobpostings', methods=['GET'])
@router.add_route('/jobpostings/<string:uid>', 'jobpostings', methods=['GET'])
def get(context, request, uid=None):
    """ get job postings """
    items = get_items('jobtool.jobcontent.jobposting',
                      request,
                      uid=uid,
                      endpoint='jobpostings')
    return {
        'url': url_for('jobpostings'),
        'count': len(items),
        'items': items,
    }
