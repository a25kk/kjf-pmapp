from zope.interface import Interface, implements
from zope import schema
from plone.app.users.userdataschema import IUserDataSchemaProvider
from plone.app.users.userdataschema import IUserDataSchema

from pressapp.memberprofiles import MessageFactory as _

class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)
    
    def getSchema(self):
        """ Subclass member schema """
        return IEnhancedUserDataSchema

class IEnhancedUserDataSchema(IUserDataSchema):
    """ Use the default user data schema fields and add
        custom extra fields.
    """
    
    organization = schema.TextLine(
        title=_(u'label_organization', default=_(u'Organization')),
        description=_(u'help_organization',
            default=_(u'Enter the official name of the organization. This will be automatically inserted into press releases')),
        required=True,
    )
    presslink = schema.URI(
        title=_(u'label_presslink', default=_(u'Press Link')),
        description=_(u'help_presslink', default=_(u'Please enter specific press link.')),
        required=True,
    )