import unittest2 as unittest
from optilux.policy.testing import PRESSAPP_POLICY_INTEGRATION_TESTING

from Products.CMFCore.utils import getToolByName

class TestSetup(unittest.TestCase):
    
    layer = PRESSAPP_POLICY_INTEGRATION_TESTING
    
    def test_portal_title(self):
        portal = self.layer['portal']
        self.assertEqual("Optilux Cinemas", portal.getProperty('title'))
    
    def test_portal_description(self):
        portal = self.layer['portal']
        self.assertEqual("Welcome to Optilux Cinemas", portal.getProperty('description'))
    
    #def test_role_added(self):
    #    portal = self.layer['portal']
    #    self.assertTrue("StaffMember" in portal.validRoles())
    #
    #def test_workflow_installed(self):
    #    portal = self.layer['portal']
    #    workflow = getToolByName(portal, 'portal_workflow')
    #    
    #    self.assertTrue('pressapp_sitecontent_workflow' in workflow)
