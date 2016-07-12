import unittest
import jiraInterface
import getpass

class TestSequenceFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        config = {}
        config['JIRA'] = {}
        config['JIRA']['apiuser'] = getpass.getpass("User: ")
        config['JIRA']['apipassword'] = getpass.getpass() 
        config['JIRA']['apiurl'] = "https://jira.ika.rwth-aachen.de/rest/api/2/"
        jiraInterface.init(config)
        self.s = jiraInterface.jiraServer()

    def test_DongleInfoUsbAddress1(self):
        d = self.s.getDongle("1-1.2.6")
        address = d.getUsbAddress()
        self.assertEqual("1-1.2.6", address)
    
    def test_DongleInfoUsbAddress2(self):    
        d = self.s.getDongle("1-1.3.1.5")
        address = d.getUsbAddress()
        self.assertEqual("1-1.3.1.5", address)

    def test_DongleInfoUsbVid1(self):    
        d = self.s.getDongle("1-1.2.6")
        vid = d.getUsbVid()
        self.assertEqual("12345", vid)
    
    def test_DongleInfoUsbVid2(self):    
        d = self.s.getDongle("1-1.3.1.5")
        vid = d.getUsbVid()
        self.assertEqual("", vid)
        
    def test_DongleInfoUsbPid1(self):    
        d = self.s.getDongle("1-1.2.6")
        pid = d.getUsbPid()
        self.assertEqual("54321", pid)
        
    def test_DongleInfoUsbPid2(self):    
        d = self.s.getDongle("1-1.3.1.5")
        pid = d.getUsbPid()
        self.assertEqual("", pid)

    def test_DongleInfoDescription1(self):    
        d = self.s.getDongle("1-1.2.6")
        desc = d.getDescription()
        self.assertEqual("Silab #B", desc)

if __name__ == '__main__':
    unittest.main()