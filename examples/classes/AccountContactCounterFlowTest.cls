@isTest
public class AccountContactCounterFlowTest {
    
    @TestSetup
    static void setupTestData() {
        List<Account> testAccounts = new List<Account>();
        for(Integer i = 0; i < 5; i++) {
            testAccounts.add(new Account(
                Name = 'Test Account ' + i,
                Count_of_Contacts__c = 0
            ));
        }
        insert testAccounts;
        
        List<Contact> testContacts = new List<Contact>();
        for(Integer i = 0; i < 3; i++) {
            testContacts.add(new Contact(
                FirstName = 'Test',
                LastName = 'Contact ' + i,
                AccountId = testAccounts[0].Id
            ));
        }
        for(Integer i = 3; i < 5; i++) {
            testContacts.add(new Contact(
                FirstName = 'Test',
                LastName = 'Contact ' + i,
                AccountId = testAccounts[1].Id
            ));
        }
        insert testContacts;
    }
    
    @isTest
    static void testContactInsertUpdatesAccountCount() {
        Account testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Name = 'Test Account 2' LIMIT 1];
        
        Test.startTest();
        Contact newContact = new Contact(
            FirstName = 'New',
            LastName = 'Contact',
            AccountId = testAccount.Id
        );
        insert newContact;
        Test.stopTest();
        
        testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Id = :testAccount.Id];
        System.assertEquals(1, testAccount.Count_of_Contacts__c, 'Account contact count should be updated to 1');
    }
    
    @isTest
    static void testContactDeleteUpdatesAccountCount() {
        Account testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Name = 'Test Account 0' LIMIT 1];
        List<Contact> existingContacts = [SELECT Id FROM Contact WHERE AccountId = :testAccount.Id];
        
        Test.startTest();
        delete existingContacts[0];
        Test.stopTest();
        
        testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Id = :testAccount.Id];
        System.assertEquals(2, testAccount.Count_of_Contacts__c, 'Account contact count should be updated to 2');
    }
    
    @isTest
    static void testContactUpdateAccountChangeUpdatesCount() {
        Account sourceAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Name = 'Test Account 0' LIMIT 1];
        Account targetAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Name = 'Test Account 2' LIMIT 1];
        Contact testContact = [SELECT Id, AccountId FROM Contact WHERE AccountId = :sourceAccount.Id LIMIT 1];
        
        Test.startTest();
        testContact.AccountId = targetAccount.Id;
        update testContact;
        Test.stopTest();
        
        sourceAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Id = :sourceAccount.Id];
        targetAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Id = :targetAccount.Id];
        
        System.assertEquals(2, sourceAccount.Count_of_Contacts__c, 'Source account contact count should be decremented');
        System.assertEquals(1, targetAccount.Count_of_Contacts__c, 'Target account contact count should be incremented');
    }
    
    @isTest
    static void testBulkContactInsertUpdatesAccountCount() {
        Account testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Name = 'Test Account 3' LIMIT 1];
        List<Contact> bulkContacts = new List<Contact>();
        
        for(Integer i = 0; i < 200; i++) {
            bulkContacts.add(new Contact(
                FirstName = 'Bulk',
                LastName = 'Contact ' + i,
                AccountId = testAccount.Id
            ));
        }
        
        Test.startTest();
        insert bulkContacts;
        Test.stopTest();
        
        testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Id = :testAccount.Id];
        System.assertEquals(200, testAccount.Count_of_Contacts__c, 'Account contact count should be updated to 200 for bulk insert');
    }
    
    @isTest
    static void testBulkContactDeleteUpdatesAccountCount() {
        Account testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Name = 'Test Account 0' LIMIT 1];
        List<Contact> contactsToDelete = [SELECT Id FROM Contact WHERE AccountId = :testAccount.Id];
        
        Test.startTest();
        delete contactsToDelete;
        Test.stopTest();
        
        testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Id = :testAccount.Id];
        System.assertEquals(0, testAccount.Count_of_Contacts__c, 'Account contact count should be 0 after deleting all contacts');
    }
    
    @isTest
    static void testAccountWithNoContactsHasZeroCount() {
        Account testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Name = 'Test Account 4' LIMIT 1];
        
        Test.startTest();
        Test.stopTest();
        
        System.assertEquals(0, testAccount.Count_of_Contacts__c, 'Account with no contacts should have count of 0');
    }
    
    @isTest
    static void testContactUndeleteUpdatesAccountCount() {
        Account testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Name = 'Test Account 1' LIMIT 1];
        Contact testContact = [SELECT Id FROM Contact WHERE AccountId = :testAccount.Id LIMIT 1];
        
        delete testContact;
        
        Test.startTest();
        undelete testContact;
        Test.stopTest();
        
        testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Id = :testAccount.Id];
        System.assertEquals(2, testAccount.Count_of_Contacts__c, 'Account contact count should be updated after undelete');
    }
    
    @isTest
    static void testMixedContactOperationsUpdateCount() {
        Account testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Name = 'Test Account 2' LIMIT 1];
        
        List<Contact> newContacts = new List<Contact>();
        for(Integer i = 0; i < 3; i++) {
            newContacts.add(new Contact(
                FirstName = 'Mixed',
                LastName = 'Contact ' + i,
                AccountId = testAccount.Id
            ));
        }
        
        Test.startTest();
        insert newContacts;
        delete newContacts[0];
        Test.stopTest();
        
        testAccount = [SELECT Id, Count_of_Contacts__c FROM Account WHERE Id = :testAccount.Id];
        System.assertEquals(2, testAccount.Count_of_Contacts__c, 'Account contact count should reflect mixed operations');
    }
}