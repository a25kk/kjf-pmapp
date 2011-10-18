from plone.app.users.browser.personalpreferences import UserDataPanelAdapter

class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
    """ Adapter to add custom fields to personlize form """
    
    def get_organization(self):
        return unicode(self.context.getProperty('organization', ''), 'utf-8')
    def set_organization(self, value):
        return self.context.setMemberProperties({'organization': value})
    organization = property(get_organization, set_organization)
    
    def get_presslink(self):
        return unicode(self.context.getProperty('presslink', ''), 'utf-8')
    def set_presslink(self, value):
        return self.context.setMemberProperties({'presslink': value})
    presslink = property(get_presslink, set_presslink)