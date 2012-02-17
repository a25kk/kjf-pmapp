# -*- coding: utf-8 -*-

import string
import StringIO
import csv
from logging import getLogger
from five import grok
from zope.lifecycleevent import modified
from zope.component import getUtility

from plone.directives import form
from z3c.form import button
from Acquisition import aq_inner
from plone.namedfile import field as namedfile
from plone.dexterity.utils import createContentInContainer
from plone.i18n.normalizer.interfaces import IIDNormalizer

from Products.statusmessages.interfaces import IStatusMessage
from pressapp.channelmanagement.channel import IChannel

from pressapp.channelmanagement import MessageFactory as _

# Cleanup potentially bad chars from the system
MULTISPACE = u'\u3000'.encode('utf-8')
NBSPACE = u'\xa0'.encode('utf-8')


def quote_chars(s):
    if MULTISPACE in s:
        s = s.replace(MULTISPACE, ' ')
    if NBSPACE in s:
        s = s.replace(NBSPACE, '')
    return s


class ISubscriberImport(form.Schema):
    """Subscriber import schema"""

    csvfile = namedfile.NamedFile(
        title=_(u"File Upload"),
        description=_(u"Please upload a file in csv format containing the "
                      u"user information to be imported."),
        required=True,
    )


class SubscriberImportForm(form.SchemaForm):
    grok.context(IChannel)
    grok.require('zope2.View')
    grok.name('import-recipients')

    schema = ISubscriberImport
    ignoreContext = True

    label =_(u"Address Import Form")
    description = _(u"Upload existing address information by supplying a "
                    u"csv file.")

    def update(self):
        self.request.set('disable_border', True)
        super(SubscriberImportForm, self).update()

    @button.buttonAndHandler(_(u"Import"))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Process uploaded file and import recipients
        recipientdata = data['csvfile'].data
        subscriber_records = self.processSubscriberRecordsFile(recipientdata)
        if subscriber_records is not None:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Imported records: ") + unicode(subscriber_records),
                type='info')

    def processSubscriberRecordsFile(self, data):
        """ Process the uploaded file and import recipient addresses
        """
        context = aq_inner(self.context)
        logger = getLogger('Userimport')
        io = StringIO.StringIO(data)
        reader = csv.reader(io, delimiter=';', dialect="excel", quotechar='"')
        header = reader.next()
        processed_records = 0
        for row in reader:
            name = self.getSpecificRecord(header, row, name=u'title')
            email = self.getSpecificRecord(header, row, name=u'email')
            contact = self.getSpecificRecord(header, row, name=u'contact')
            phone = self.getSpecificRecord(header, row, name=u'phone')
            fax = self.getSpecificRecord(header, row, name=u'fax')
            mobile = self.getSpecificRecord(header, row, name=u"mobile")
            comment = self.getSpecificRecord(header, row, name=u'comment')
            channel = self.getSpecificRecord(header, row, name=u'channel')
            clean_channels = self.cleanupChannelNames(channel)
            data = {
                'title': name,
                'email': email,
                'contact': contact,
                'fax': fax,
                'phone': phone,
                'mobile': mobile,
                'comment': comment,
                'channel': clean_channels}
            if not email:
                logger.info('E-mail missing: invalid record for %s' % name)
            else:
                logger.info('Processing user: %s' % name)
                subscriber = createContentInContainer(context,
                                'pressapp.channelmanagement.subscriber',
                                checkConstraints=True, **data)
                modified(subscriber)
            processed_records += 1
        return processed_records

    def getSpecificRecord(self, header, row, name):
        """ Process a specific record in the import file accessing
            a specific cell by its name
        """
        assert type(name) == unicode
        index = None
        for i in range(0, len(header)):
            if header[i].decode("utf-8") == name:
                index = i
        if index is None:
            raise RuntimeError(
                "Uploaded file does not have the column:" + name)
        record = quote_chars(row[index]).decode('utf-8')
        return record

    def cleanupChannelNames(self, channels):
        normalizer = getUtility(IIDNormalizer)
        cleaned_channels = []
        for entry in string.split(channels, ', '):
            channelname = normalizer.normalize(entry)
            cleaned_channels.append(channelname)
        return cleaned_channels

    def is_ascii(self, s):
        for c in s:
            if not ord(c) < 128:
                return False
        return True
