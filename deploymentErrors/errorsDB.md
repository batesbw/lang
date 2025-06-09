# Salesforce Deployment Errors Database

This file automatically logs deployment failures with comprehensive error details and web search suggestions for fixes.

## Overview

Each entry includes:
- **Full deployment error text** - Complete error messages from Salesforce
- **Deployment package content** - The metadata XML that was attempted to be deployed
- **Suggested fixes** - Web search results with solutions and troubleshooting guides

## Search Tips

Use Ctrl+F to search for:
- Specific error messages
- Component names 
- Component types (Flow, CustomObject, etc.)
- Solution keywords

---

---

## Deployment Error - 2025-06-07T21:56:58.422170

**Request ID:** test_error_log_123  
**Deployment ID:** test_deploy_456  
**Status:** Failed  
**Total Components:** 1  
**Failed Components:** 1  

### Full Deployment Error Text

**Main Error:** Deployment failed with 1 error(s) out of 1 component(s)

**Component Errors:**

- **TestErrorFlow (Flow):** INVALID_FIELD_FOR_INSERT_UPDATE: Unable to create/update fields: Account.NonExistentField__c. Please check the security settings of this field and verify that it is read/write for your profile or permission set.

### Deployment Package Content

#### Component 1: TestErrorFlow (Flow)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>59.0</apiVersion>
    <interviewLabel>Test Error Flow $Flow.CurrentDateTime</interviewLabel>
    <label>Test Error Flow</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value><stringValue>LightningFlowBuilder</stringValue></value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <recordUpdates>
        <name>Update_Account_Record</name>
        <label>Update Account Record</label>
        <locationX>176</locationX>
        <locationY>158</locationY>
        <inputAssignments>
            <field>NonExistentField__c</field>
            <value>
                <stringValue>Test Value</stringValue>
            </value>
        </inputAssignments>
        <inputReference>$Record</inputReference>
        <object>Account</object>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector>
            <targetReference>Update_Account_Record</targetReference>
        </connector>
    </start>
    <status>Active</status>
</Flow>
```

### Suggested Fixes (Web Search Results)


#### ✅ Fix for TestErrorFlow (Flow)

**Error:** INVALID_FIELD_FOR_INSERT_UPDATE: Unable to create/update fields: Account.NonExistentField__c. Please check the security settings of this field and verify that it is read/write for your profile or permission set.

**Search Query:** `Salesforce Flow deployment error: INVALID_FIELD_FOR_INSERT_UPDATE: Unable to create/update fields: Account.NonExistentField__c. Please check the security settings of this field and verify that it is read/write for your profile or perm`

**Suggested Solutions:**

**AI Summary:**
The error indicates a field does not exist or is not accessible. Ensure the field exists and is set to read/write for your profile or permission set.

**Relevant Resources:**
1. **[INVALID_FIELD_FOR_INSERT_UPDATE | Salesforce Trailblazer Community](https://trailhead.salesforce.com/es/trailblazer-community/feed/0D54V00007T4DU5SAN)**
   First exception on row 0; first error: INVALID_FIELD_FOR_INSERT_UPDATE, Unable to create/update fields: Name. Please check the security settings of this field and verify that it is read/write for your profile or permission set.: [Name] Stack Trace: Class.EnvioDeCorreoTest.InsertAccount: line 12, column 1 Class.EnvioDeCorreoTest

2. **[INVALID_FIELD_FOR_INSERT_UPDATE in Salesforce via API](https://stackoverflow.com/questions/39457082/invalid-field-for-insert-update-in-salesforce-via-api)**
   OneLogin Error: User failed creating in app. INVALID_FIELD_FOR_INSERT_UPDATE: Unable to create/update fields: ProfileId. Please check the security settings of this field and verify that it is read/write for your profile or permission set. Fix to the error: Audit Field Update Settings: Salesforce typically restricts direct access to certain

3. **[Flow INVALID_FIELD_FOR_INSERT_UPDATE error - Salesforce Stack Exchange](https://salesforce.stackexchange.com/questions/346325/flow-invalid-field-for-insert-update-error)**
   When I run the flow with my system administrator profile everything goes as expected. When I try to run with a supervisior profile I have an issue when it tries to update some fields on OrderDeliveryGroupSummary Object and I have this error: : INVALID_FIELD_FOR_INSERT_UPDATE: Unable to create/update fields: DeliverToCountry, DeliverToCity

4. **[Updating an existing Object fails with error INVALID_FIELD_FOR_INSERT ...](https://salesforce.stackexchange.com/questions/151652/updating-an-existing-object-fails-with-error-invalid-field-for-insert-update)**
   UserInfo={NSLocalizedFailureReason=INVALID_FIELD_FOR_INSERT_UPDATE, isAuthenticationFailure=false, NSLocalizedDescription=Unable to create/update fields: XXXX_C__c. Please check the security settings of this field and verify that it is read/write for your profile or permission set., action=*} Actually what I am trying to do :

5. **[Error 'INVALID_FIELD_FOR_INSERT_UPDATE: Attempting to ... - Salesforce](https://help.salesforce.com/s/articleView?id=000385552&language=en_US&type=1)**
   Check the CSV file and mapping (Data Loader SDL file) for the mapped fields. If any fields attempt to update another object through the relationship field, this may be the problem. Example:


---


---

## Deployment Error - 2025-06-07T21:59:16.753816

**Request ID:** 632603af-36fd-4949-8242-75d1c869cfec  
**Deployment ID:** 0AfGA00001dc2560AA  
**Status:** Failed  
**Total Components:** 1  
**Failed Components:** 1  

### Full Deployment Error Text

**Main Error:** Deployment failed with 1 error(s) out of 1 component(s)

**Component Errors:**

- **UserStory_Account_Contact_Counter (Flow):** field integrity exception: unknown (The inputAssignments field can't use a collection variable.)

### Deployment Package Content

#### Component 1: UserStory_Account_Contact_Counter (Flow)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>61.0</apiVersion>
    <description>As a sales manager, I want the number of Contacts directly associated with an Account to appear on the account record, so I can quickly check the size of the Account</description>
    <label>Account Contact Counter</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value>
            <stringValue>LightningFlowBuilder</stringValue>
        </value>
    </processMetadataValues>
    <processMetadataValues>
        <name>CanvasMode</name>
        <value>
            <stringValue>AUTO_LAYOUT_CANVAS</stringValue>
        </value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <recordLookups>
        <name>Get_Account_Contacts</name>
        <label>Get Account Contacts</label>
        <locationX>176</locationX>
        <locationY>134</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector>
            <targetReference>Update_Account_Contact_Count</targetReference>
        </connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>AccountId</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>varAccountId</elementReference>
            </value>
        </filters>
        <getFirstRecordOnly>false</getFirstRecordOnly>
        <object>Contact</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordLookups>
    <recordUpdates>
        <name>Update_Account_Contact_Count</name>
        <label>Update Account Contact Count</label>
        <locationX>176</locationX>
        <locationY>242</locationY>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Id</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>varAccountId</elementReference>
            </value>
        </filters>
        <inputAssignments>
            <field>Count_of_Contacts__c</field>
            <value>
                <elementReference>Get_Account_Contacts</elementReference>
            </value>
        </inputAssignments>
        <object>Account</object>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector>
            <targetReference>Get_Account_Contacts</targetReference>
        </connector>
    </start>
    <status>Active</status>
    <variables>
        <name>varAccountId</name>
        <dataType>String</dataType>
        <isCollection>false</isCollection>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>
</Flow>
```

### Suggested Fixes (Web Search Results)


#### ✅ Fix for UserStory_Account_Contact_Counter (Flow)

**Error:** field integrity exception: unknown (The inputAssignments field can't use a collection variable.)

**Search Query:** `Salesforce Flow deployment error: field integrity exception: unknown (The inputAssignments field can't use a collection variable.)`

**Suggested Solutions:**

**AI Summary:**
The error occurs because the inputAssignments field in Salesforce Flow cannot use a collection variable. To fix, avoid using collection variables in inputAssignments.

**Relevant Resources:**
1. **[How to resolve field integrity exception error in Salesforce?](https://medium.com/@codebiceps/how-to-resolve-field-integrity-exception-error-in-salesforce-14b18f21e29f)**
   How to resolve field integrity exception error in Salesforce? Image by Field Integrity Exception Error by o-rod on Stackoverflow Two Possible Ways of getting this error in Salesforce 3.   Missing few user level accesses in target org such as enabling Flow User, Knowledge User at User Level in Salesforce. You will face Error: field integrity exception: unknown (The object “”Knowledge__kav” can’t be updated through a flow.) If you are deploying Knowledge related components in salesforce & in targe...

2. **[Field Integrity Exception while deploying Flow - Salesforce Stack Exchange](https://salesforce.stackexchange.com/questions/308332/field-integrity-exception-while-deploying-flow)**
   However , when I try to deploy this to Test org I run into Field Integrity Exception. As a series of tests to find out what is going wrong I removed all the assignments on the main flow so now I just have the main flow which calls another subflow (which has some plugin and invocable apex calls), but I still get the same exception.

3. **[Error 'field integrity exception: unknown' on Opportunity ... - Salesforce](https://help.salesforce.com/s/articleView?id=000382663&language=en_US&type=1)**
   This is commonly caused by a point-in-time copy issue related to performing an action against Roll-Up Summary Fields that either modifies them or triggers recalculation during the sandbox refresh process. As per the sandbox Setup Tips and Considerations documentation: "A sandbox is not a point-in-time snapshot of the exact state of your data.

4. **[salesforce - Debugging "field integrity exception" error when deploying ...](https://stackoverflow.com/questions/61490683/debugging-field-integrity-exception-error-when-deploying-change-set-from-sandb)**
   I ran test classes of the plugins / invocable apex in the target org which are referred from the flow but the same field integrity exception comes while deploying the flow. - Sagnik Commented Jun 18, 2020 at 15:03

5. **[How to Fix FIELD_INTEGRITY_EXCEPTION Error - Automation Champion](https://automationchampion.com/2022/04/18/fix-field_integrity_exception-error/)**
   How to Fix FIELD_INTEGRITY_EXCEPTION Error # How to Fix FIELD\_INTEGRITY\_EXCEPTION Error In my last post How to Fix FIELD\_CUSTOM\_VALIDATION\_EXCEPTION Error, I discussed how to solve the FIELD\_CUSTOM\_VALIDATION\_EXCEPTION error by adding all the required fields to the flow data element. ## What is FIELD\_INTEGRITY\_EXCEPTION Error? For example, while creating a contact via flow if, in the place of AccountId, a user passes an Opportunity record id, then, the user will encounter a FIELD\_INTE...


---


---

## Deployment Error - 2025-06-07T22:00:11.830307

**Request ID:** cb58f623-2c97-4b1b-8223-51f4e74d8fd1  
**Deployment ID:** 0AfGA00001dc25B0AQ  
**Status:** Failed  
**Total Components:** 1  
**Failed Components:** 1  

### Full Deployment Error Text

**Main Error:** Deployment failed with 1 error(s) out of 1 component(s)

**Component Errors:**

- **UserStory_Account_Contact_Counter (Flow):** field integrity exception: unknown (In an Assignment element, “colContacts” isn’t a valid reference for the value when the “varContactCount” variable is set with the Equals operator.)

### Deployment Package Content

#### Component 1: UserStory_Account_Contact_Counter (Flow)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>61.0</apiVersion>
    <description>As a sales manager, I want the number of Contacts directly associated with an Account to appear on the account record, so I can quickly check the size of the Account</description>
    <label>Account Contact Counter</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value>
            <stringValue>LightningFlowBuilder</stringValue>
        </value>
    </processMetadataValues>
    <processMetadataValues>
        <name>CanvasMode</name>
        <value>
            <stringValue>AUTO_LAYOUT_CANVAS</stringValue>
        </value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <assignments>
        <name>Calculate_Contact_Count</name>
        <label>Calculate Contact Count</label>
        <locationX>176</locationX>
        <locationY>242</locationY>
        <assignmentItems>
            <assignToReference>varContactCount</assignToReference>
            <operator>Assign</operator>
            <value>
                <elementReference>colContacts</elementReference>
            </value>
        </assignmentItems>
        <connector>
            <targetReference>Update_Account_Contact_Count</targetReference>
        </connector>
    </assignments>
    <recordLookups>
        <name>Get_Account_Contacts</name>
        <label>Get Account Contacts</label>
        <locationX>176</locationX>
        <locationY>134</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector>
            <targetReference>Calculate_Contact_Count</targetReference>
        </connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>AccountId</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>varAccountId</elementReference>
            </value>
        </filters>
        <getFirstRecordOnly>false</getFirstRecordOnly>
        <object>Contact</object>
        <outputReference>colContacts</outputReference>
    </recordLookups>
    <recordUpdates>
        <name>Update_Account_Contact_Count</name>
        <label>Update Account Contact Count</label>
        <locationX>176</locationX>
        <locationY>350</locationY>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Id</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>varAccountId</elementReference>
            </value>
        </filters>
        <inputAssignments>
            <field>Count_of_Contacts__c</field>
            <value>
                <elementReference>varContactCount</elementReference>
            </value>
        </inputAssignments>
        <object>Account</object>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector>
            <targetReference>Get_Account_Contacts</targetReference>
        </connector>
    </start>
    <status>Active</status>
    <variables>
        <name>colContacts</name>
        <dataType>SObject</dataType>
        <isCollection>true</isCollection>
        <isInput>false</isInput>
        <isOutput>false</isOutput>
        <objectType>Contact</objectType>
    </variables>
    <variables>
        <name>varAccountId</name>
        <dataType>String</dataType>
        <isCollection>false</isCollection>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>
    <variables>
        <name>varContactCount</name>
        <dataType>Number</dataType>
        <isCollection>false</isCollection>
        <isInput>false</isInput>
        <isOutput>false</isOutput>
        <scale>0</scale>
    </variables>
</Flow>
```

### Suggested Fixes (Web Search Results)


#### ✅ Fix for UserStory_Account_Contact_Counter (Flow)

**Error:** field integrity exception: unknown (In an Assignment element, “colContacts” isn’t a valid reference for the value when the “varContactCount” variable is set with the Equals operator.)

**Search Query:** `Salesforce Flow deployment error: field integrity exception: unknown (In an Assignment element, “colContacts” isn’t a valid reference for the value when the “varContactCount” variable is set with the Equals operator.)`

**Suggested Solutions:**

**AI Summary:**
The error indicates "colContacts" is invalid for "varContactCount" in Assignment element. Check field references and variable assignments. Correct the field reference.

❌ No search results found.

---


---

## Deployment Error - 2025-06-07T22:01:10.542214

**Request ID:** 0fa1845c-b19d-4955-86e7-a07177217cca  
**Deployment ID:** 0AfGA00001dc25G0AQ  
**Status:** Failed  
**Total Components:** 1  
**Failed Components:** 1  

### Full Deployment Error Text

**Main Error:** Deployment failed with 1 error(s) out of 1 component(s)

**Component Errors:**

- **UserStory_Account_Contact_Counter (Flow):** field integrity exception: unknown (The formula expression is invalid: It contains an invalid flow element colContacts.)

### Deployment Package Content

#### Component 1: UserStory_Account_Contact_Counter (Flow)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>61.0</apiVersion>
    <description>As a sales manager, I want the number of Contacts directly associated with an Account to appear on the account record, so I can quickly check the size of the Account</description>
    <label>Account Contact Counter</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value>
            <stringValue>LightningFlowBuilder</stringValue>
        </value>
    </processMetadataValues>
    <processMetadataValues>
        <name>CanvasMode</name>
        <value>
            <stringValue>AUTO_LAYOUT_CANVAS</stringValue>
        </value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <formulas>
        <name>ContactCount</name>
        <dataType>Number</dataType>
        <expression>IF(ISNULL({!colContacts}), 0, {!colContacts}.size)</expression>
        <scale>0</scale>
    </formulas>
    <recordLookups>
        <name>Get_Account_Contacts</name>
        <label>Get Account Contacts</label>
        <locationX>176</locationX>
        <locationY>134</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector>
            <targetReference>Update_Account_Contact_Count</targetReference>
        </connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>AccountId</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>varAccountId</elementReference>
            </value>
        </filters>
        <getFirstRecordOnly>false</getFirstRecordOnly>
        <object>Contact</object>
        <outputReference>colContacts</outputReference>
    </recordLookups>
    <recordUpdates>
        <name>Update_Account_Contact_Count</name>
        <label>Update Account Contact Count</label>
        <locationX>176</locationX>
        <locationY>242</locationY>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Id</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>varAccountId</elementReference>
            </value>
        </filters>
        <inputAssignments>
            <field>Count_of_Contacts__c</field>
            <value>
                <elementReference>ContactCount</elementReference>
            </value>
        </inputAssignments>
        <object>Account</object>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector>
            <targetReference>Get_Account_Contacts</targetReference>
        </connector>
    </start>
    <status>Active</status>
    <variables>
        <name>colContacts</name>
        <dataType>SObject</dataType>
        <isCollection>true</isCollection>
        <isInput>false</isInput>
        <isOutput>false</isOutput>
        <objectType>Contact</objectType>
    </variables>
    <variables>
        <name>varAccountId</name>
        <dataType>String</dataType>
        <isCollection>false</isCollection>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>
</Flow>
```

### Suggested Fixes (Web Search Results)


#### ✅ Fix for UserStory_Account_Contact_Counter (Flow)

**Error:** field integrity exception: unknown (The formula expression is invalid: It contains an invalid flow element colContacts.)

**Search Query:** `Salesforce Flow deployment error: field integrity exception: unknown (The formula expression is invalid: It contains an invalid flow element colContacts.)`

**Suggested Solutions:**

**AI Summary:**
The error indicates an invalid formula in the flow. Check the formula for colContacts and ensure it's correctly referenced. Validate field access and permissions.

**Relevant Resources:**
1. **[How to resolve field integrity exception error in Salesforce?](https://medium.com/@codebiceps/how-to-resolve-field-integrity-exception-error-in-salesforce-14b18f21e29f)**
   How to resolve field integrity exception error in Salesforce? Image by Field Integrity Exception Error by o-rod on Stackoverflow Two Possible Ways of getting this error in Salesforce 3.   Missing few user level accesses in target org such as enabling Flow User, Knowledge User at User Level in Salesforce. You will face Error: field integrity exception: unknown (The object “”Knowledge__kav” can’t be updated through a flow.) If you are deploying Knowledge related components in salesforce & in targe...

2. **[Error 'field integrity exception: unknown' on Opportunity ... - Salesforce](https://help.salesforce.com/s/articleView?id=000382663&language=en_US&type=1)**
   This is commonly caused by a point-in-time copy issue related to performing an action against Roll-Up Summary Fields that either modifies them or triggers recalculation during the sandbox refresh process. As per the sandbox Setup Tips and Considerations documentation: "A sandbox is not a point-in-time snapshot of the exact state of your data.

3. **[salesforce - Debugging "field integrity exception" error when deploying ...](https://stackoverflow.com/questions/61490683/debugging-field-integrity-exception-error-when-deploying-change-set-from-sandb)**
   Yes. I have multiple Apex Webservices implemented in the Flow and some changes were made to the Apex Class of one of them but never deployed to Production. I had to check every element of the Flow and compare between Sandbox and Production until I noticed this since SF doesn't give any details. -

4. **[Field Integrity Exception while deploying Flow - Salesforce Stack Exchange](https://salesforce.stackexchange.com/questions/308332/field-integrity-exception-while-deploying-flow)**
   However , when I try to deploy this to Test org I run into Field Integrity Exception. As a series of tests to find out what is going wrong I removed all the assignments on the main flow so now I just have the main flow which calls another subflow (which has some plugin and invocable apex calls), but I still get the same exception.

5. **[How to Fix FIELD_INTEGRITY_EXCEPTION Error - Automation Champion](https://automationchampion.com/2022/04/18/fix-field_integrity_exception-error/)**
   How to Fix FIELD_INTEGRITY_EXCEPTION Error # How to Fix FIELD\_INTEGRITY\_EXCEPTION Error In my last post How to Fix FIELD\_CUSTOM\_VALIDATION\_EXCEPTION Error, I discussed how to solve the FIELD\_CUSTOM\_VALIDATION\_EXCEPTION error by adding all the required fields to the flow data element. ## What is FIELD\_INTEGRITY\_EXCEPTION Error? For example, while creating a contact via flow if, in the place of AccountId, a user passes an Opportunity record id, then, the user will encounter a FIELD\_INTE...


---


---

## Deployment Error - 2025-06-09T10:15:59.984028

**Request ID:** 687092e0-90ca-4827-9294-f7f5013f9c4f  
**Deployment ID:** 0AfGA00001dc25u0AA  
**Status:** Failed  
**Total Components:** 1  
**Failed Components:** 1  

### Full Deployment Error Text

**Main Error:** Deployment failed with 1 error(s) out of 1 component(s)

**Component Errors:**

- **UserStory_Account_Contact_Counter (Flow):** field integrity exception: unknown (The inputAssignments field can't use a collection variable.)

### Deployment Package Content

#### Component 1: UserStory_Account_Contact_Counter (Flow)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>60.0</apiVersion>
    <description>Counts the number of contacts associated with an account and updates the account record</description>
    <label>Account Contact Counter</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value>
            <stringValue>LightningFlowBuilder</stringValue>
        </value>
    </processMetadataValues>
    <processMetadataValues>
        <name>CanvasMode</name>
        <value>
            <stringValue>AUTO_LAYOUT_CANVAS</stringValue>
        </value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <recordLookups>
        <name>Get_Account_Contacts</name>
        <label>Get Account Contacts</label>
        <locationX>176</locationX>
        <locationY>158</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector>
            <targetReference>Update_Account_Contact_Count</targetReference>
        </connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>AccountId</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>recordId</elementReference>
            </value>
        </filters>
        <getFirstRecordOnly>false</getFirstRecordOnly>
        <object>Contact</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordLookups>
    <recordUpdates>
        <name>Update_Account_Contact_Count</name>
        <label>Update Account Contact Count</label>
        <locationX>176</locationX>
        <locationY>278</locationY>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Id</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>recordId</elementReference>
            </value>
        </filters>
        <inputAssignments>
            <field>NumberOfEmployees</field>
            <value>
                <elementReference>Get_Account_Contacts</elementReference>
            </value>
        </inputAssignments>
        <object>Account</object>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector>
            <targetReference>Get_Account_Contacts</targetReference>
        </connector>
    </start>
    <status>Active</status>
    <variables>
        <name>recordId</name>
        <dataType>String</dataType>
        <isCollection>false</isCollection>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>
</Flow>
```

### Suggested Fixes (Web Search Results)


#### ✅ Fix for UserStory_Account_Contact_Counter (Flow)

**Error:** field integrity exception: unknown (The inputAssignments field can't use a collection variable.)

**Search Query:** `Salesforce Flow deployment error: field integrity exception: unknown (The inputAssignments field can't use a collection variable.)`

**Suggested Solutions:**

**AI Summary:**
The error indicates the inputAssignments field cannot use a collection variable in Salesforce Flow. This typically happens due to incorrect data assignment. Ensure correct data types and values are used.

**Relevant Resources:**
1. **[How to resolve field integrity exception error in Salesforce?](https://medium.com/@codebiceps/how-to-resolve-field-integrity-exception-error-in-salesforce-14b18f21e29f)**
   How to resolve field integrity exception error in Salesforce? Image by Field Integrity Exception Error by o-rod on Stackoverflow Two Possible Ways of getting this error in Salesforce 3.   Missing few user level accesses in target org such as enabling Flow User, Knowledge User at User Level in Salesforce. You will face Error: field integrity exception: unknown (The object “”Knowledge__kav” can’t be updated through a flow.) If you are deploying Knowledge related components in salesforce & in targe...

2. **[Field Integrity Exception while deploying Flow - Salesforce Stack Exchange](https://salesforce.stackexchange.com/questions/308332/field-integrity-exception-while-deploying-flow)**
   However , when I try to deploy this to Test org I run into Field Integrity Exception. As a series of tests to find out what is going wrong I removed all the assignments on the main flow so now I just have the main flow which calls another subflow (which has some plugin and invocable apex calls), but I still get the same exception.

3. **[Error 'field integrity exception: unknown' on Opportunity ... - Salesforce](https://help.salesforce.com/s/articleView?id=000382663&language=en_US&type=1)**
   field integrity exception: unknown This is commonly caused by a point-in-time copy issue related to performing an action against Roll-Up Summary Fields that either modifies them or triggers recalculation during the sandbox refresh process.

4. **[salesforce - Debugging "field integrity exception" error when deploying ...](https://stackoverflow.com/questions/61490683/debugging-field-integrity-exception-error-when-deploying-change-set-from-sandb)**
   I ran test classes of the plugins / invocable apex in the target org which are referred from the flow but the same field integrity exception comes while deploying the flow. - Sagnik Commented Jun 18, 2020 at 15:03

5. **[How to Fix FIELD_INTEGRITY_EXCEPTION Error - Automation Champion](https://automationchampion.com/2022/04/18/fix-field_integrity_exception-error/)**
   How to Fix FIELD_INTEGRITY_EXCEPTION Error # How to Fix FIELD\_INTEGRITY\_EXCEPTION Error In my last post How to Fix FIELD\_CUSTOM\_VALIDATION\_EXCEPTION Error, I discussed how to solve the FIELD\_CUSTOM\_VALIDATION\_EXCEPTION error by adding all the required fields to the flow data element. ## What is FIELD\_INTEGRITY\_EXCEPTION Error? For example, while creating a contact via flow if, in the place of AccountId, a user passes an Opportunity record id, then, the user will encounter a FIELD\_INTE...


---


---

## Deployment Error - 2025-06-09T10:20:21.112150

**Request ID:** 6ce1f008-1ca8-4b70-be22-3a185c2121bd  
**Deployment ID:** 0AfGA00001dc2640AA  
**Status:** Failed  
**Total Components:** 1  
**Failed Components:** 1  

### Full Deployment Error Text

**Main Error:** Deployment failed with 1 error(s) out of 1 component(s)

**Component Errors:**

- **UserStory_Account_Contact_Counter (Flow):** field integrity exception: unknown (The inputAssignments field can't use a collection variable.)

### Deployment Package Content

#### Component 1: UserStory_Account_Contact_Counter (Flow)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>60.0</apiVersion>
    <description>Counts the number of contacts associated with an account and updates the account record</description>
    <label>Account Contact Counter</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value>
            <stringValue>LightningFlowBuilder</stringValue>
        </value>
    </processMetadataValues>
    <processMetadataValues>
        <name>CanvasMode</name>
        <value>
            <stringValue>AUTO_LAYOUT_CANVAS</stringValue>
        </value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <recordLookups>
        <name>Get_Account_Contacts</name>
        <label>Get Account Contacts</label>
        <locationX>176</locationX>
        <locationY>158</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector>
            <targetReference>Update_Account_Contact_Count</targetReference>
        </connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>AccountId</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>recordId</elementReference>
            </value>
        </filters>
        <getFirstRecordOnly>false</getFirstRecordOnly>
        <object>Contact</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordLookups>
    <recordUpdates>
        <name>Update_Account_Contact_Count</name>
        <label>Update Account Contact Count</label>
        <locationX>176</locationX>
        <locationY>278</locationY>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Id</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>recordId</elementReference>
            </value>
        </filters>
        <inputAssignments>
            <field>NumberOfEmployees</field>
            <value>
                <elementReference>Get_Account_Contacts</elementReference>
            </value>
        </inputAssignments>
        <object>Account</object>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector>
            <targetReference>Get_Account_Contacts</targetReference>
        </connector>
    </start>
    <status>Active</status>
    <variables>
        <name>recordId</name>
        <dataType>String</dataType>
        <isCollection>false</isCollection>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>
</Flow>
```

### Suggested Fixes (Web Search Results)


#### ✅ Fix for UserStory_Account_Contact_Counter (Flow)

**Error:** field integrity exception: unknown (The inputAssignments field can't use a collection variable.)

**Search Query:** `Salesforce Flow deployment error: field integrity exception: unknown (The inputAssignments field can't use a collection variable.)`

**Suggested Solutions:**

**AI Summary:**
The error indicates the inputAssignments field cannot use a collection variable in Salesforce Flow. This typically happens due to incorrect data assignment. Ensure correct data types and values are used.

**Relevant Resources:**
1. **[How to resolve field integrity exception error in Salesforce?](https://medium.com/@codebiceps/how-to-resolve-field-integrity-exception-error-in-salesforce-14b18f21e29f)**
   How to resolve field integrity exception error in Salesforce? Image by Field Integrity Exception Error by o-rod on Stackoverflow Two Possible Ways of getting this error in Salesforce 3.   Missing few user level accesses in target org such as enabling Flow User, Knowledge User at User Level in Salesforce. You will face Error: field integrity exception: unknown (The object “”Knowledge__kav” can’t be updated through a flow.) If you are deploying Knowledge related components in salesforce & in targe...

2. **[Field Integrity Exception while deploying Flow - Salesforce Stack Exchange](https://salesforce.stackexchange.com/questions/308332/field-integrity-exception-while-deploying-flow)**
   However , when I try to deploy this to Test org I run into Field Integrity Exception. As a series of tests to find out what is going wrong I removed all the assignments on the main flow so now I just have the main flow which calls another subflow (which has some plugin and invocable apex calls), but I still get the same exception.

3. **[Error 'field integrity exception: unknown' on Opportunity ... - Salesforce](https://help.salesforce.com/s/articleView?id=000382663&language=en_US&type=1)**
   field integrity exception: unknown This is commonly caused by a point-in-time copy issue related to performing an action against Roll-Up Summary Fields that either modifies them or triggers recalculation during the sandbox refresh process.

4. **[salesforce - Debugging "field integrity exception" error when deploying ...](https://stackoverflow.com/questions/61490683/debugging-field-integrity-exception-error-when-deploying-change-set-from-sandb)**
   I ran test classes of the plugins / invocable apex in the target org which are referred from the flow but the same field integrity exception comes while deploying the flow. - Sagnik Commented Jun 18, 2020 at 15:03

5. **[How to Fix FIELD_INTEGRITY_EXCEPTION Error - Automation Champion](https://automationchampion.com/2022/04/18/fix-field_integrity_exception-error/)**
   How to Fix FIELD_INTEGRITY_EXCEPTION Error # How to Fix FIELD\_INTEGRITY\_EXCEPTION Error In my last post How to Fix FIELD\_CUSTOM\_VALIDATION\_EXCEPTION Error, I discussed how to solve the FIELD\_CUSTOM\_VALIDATION\_EXCEPTION error by adding all the required fields to the flow data element. ## What is FIELD\_INTEGRITY\_EXCEPTION Error? For example, while creating a contact via flow if, in the place of AccountId, a user passes an Opportunity record id, then, the user will encounter a FIELD\_INTE...


---


---

## Deployment Error - 2025-06-09T10:20:49.169476

**Request ID:** 1d59d7cb-784a-4233-9155-e69999a073d4  
**Deployment ID:** 0AfGA00001dc26E0AQ  
**Status:** Failed  
**Total Components:** 1  
**Failed Components:** 1  

### Full Deployment Error Text

**Main Error:** Deployment failed with 1 error(s) out of 1 component(s)

**Component Errors:**

- **UserStory_Account_Contact_Counter (Flow):** field integrity exception: unknown (In an Assignment element, “contactCollection” isn’t a valid reference for the value when the “contactCount” variable is set with the Equals operator.)

### Deployment Package Content

#### Component 1: UserStory_Account_Contact_Counter (Flow)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>60.0</apiVersion>
    <description>Flow to count contacts associated with an account and update the account record</description>
    <label>Account Contact Counter</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value>
            <stringValue>LightningFlowBuilder</stringValue>
        </value>
    </processMetadataValues>
    <processMetadataValues>
        <name>CanvasMode</name>
        <value>
            <stringValue>AUTO_LAYOUT_CANVAS</stringValue>
        </value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <recordLookups>
        <name>Get_Account_Record</name>
        <label>Get Account Record</label>
        <locationX>176</locationX>
        <locationY>158</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector>
            <targetReference>Get_Related_Contacts</targetReference>
        </connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Id</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>recordId</elementReference>
            </value>
        </filters>
        <getFirstRecordOnly>true</getFirstRecordOnly>
        <object>Account</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordLookups>
    <recordLookups>
        <name>Get_Related_Contacts</name>
        <label>Get Related Contacts</label>
        <locationX>176</locationX>
        <locationY>278</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector>
            <targetReference>Calculate_Contact_Count</targetReference>
        </connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>AccountId</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>recordId</elementReference>
            </value>
        </filters>
        <object>Contact</object>
        <outputReference>contactCollection</outputReference>
    </recordLookups>
    <recordUpdates>
        <name>Update_Account_Contact_Count</name>
        <label>Update Account Contact Count</label>
        <locationX>176</locationX>
        <locationY>518</locationY>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Id</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>recordId</elementReference>
            </value>
        </filters>
        <inputAssignments>
            <field>NumberOfEmployees</field>
            <value>
                <elementReference>contactCount</elementReference>
            </value>
        </inputAssignments>
        <object>Account</object>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector>
            <targetReference>Get_Account_Record</targetReference>
        </connector>
    </start>
    <status>Active</status>
    <assignments>
        <name>Calculate_Contact_Count</name>
        <label>Calculate Contact Count</label>
        <locationX>176</locationX>
        <locationY>398</locationY>
        <assignmentItems>
            <assignToReference>contactCount</assignToReference>
            <operator>Assign</operator>
            <value>
                <elementReference>contactCollection</elementReference>
            </value>
        </assignmentItems>
        <connector>
            <targetReference>Update_Account_Contact_Count</targetReference>
        </connector>
    </assignments>
    <variables>
        <name>recordId</name>
        <dataType>String</dataType>
        <isCollection>false</isCollection>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>
    <variables>
        <name>contactCollection</name>
        <dataType>SObject</dataType>
        <isCollection>true</isCollection>
        <isInput>false</isInput>
        <isOutput>false</isOutput>
        <objectType>Contact</objectType>
    </variables>
    <variables>
        <name>contactCount</name>
        <dataType>Number</dataType>
        <isCollection>false</isCollection>
        <isInput>false</isInput>
        <isOutput>false</isOutput>
        <scale>0</scale>
    </variables>
</Flow>
```

### Suggested Fixes (Web Search Results)


#### ✅ Fix for UserStory_Account_Contact_Counter (Flow)

**Error:** field integrity exception: unknown (In an Assignment element, “contactCollection” isn’t a valid reference for the value when the “contactCount” variable is set with the Equals operator.)

**Search Query:** `Salesforce Flow deployment error: field integrity exception: unknown (In an Assignment element, “contactCollection” isn’t a valid reference for the value when the “contactCount” variable is set with the Equals operator.)`

**Suggested Solutions:**

**AI Summary:**
The error indicates "contactCollection" is invalid for "contactCount" in Assignment element. Check variable references and ensure "contactCollection" is correctly defined.

❌ No search results found.

---


---

## Deployment Error - 2025-06-09T10:21:17.869566

**Request ID:** 1cc89b38-5184-4270-9303-6f21bddb2f93  
**Deployment ID:** 0AfGA00001dc26J0AQ  
**Status:** Failed  
**Total Components:** 1  
**Failed Components:** 1  

### Full Deployment Error Text

**Main Error:** Deployment failed with 1 error(s) out of 1 component(s)

**Component Errors:**

- **UserStory_Account_Contact_Counter (Flow):** field integrity exception: unknown (In an Assignment element, “contactCollection” isn’t a valid reference for the value when the “contactCount” variable is set with the Equals operator.)

### Deployment Package Content

#### Component 1: UserStory_Account_Contact_Counter (Flow)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>60.0</apiVersion>
    <description>Flow to count contacts associated with an account and update the account record</description>
    <label>Account Contact Counter</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value>
            <stringValue>LightningFlowBuilder</stringValue>
        </value>
    </processMetadataValues>
    <processMetadataValues>
        <name>CanvasMode</name>
        <value>
            <stringValue>AUTO_LAYOUT_CANVAS</stringValue>
        </value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <recordLookups>
        <name>Get_Account_Record</name>
        <label>Get Account Record</label>
        <locationX>176</locationX>
        <locationY>158</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector>
            <targetReference>Get_Related_Contacts</targetReference>
        </connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Id</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>recordId</elementReference>
            </value>
        </filters>
        <getFirstRecordOnly>true</getFirstRecordOnly>
        <object>Account</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordLookups>
    <recordLookups>
        <name>Get_Related_Contacts</name>
        <label>Get Related Contacts</label>
        <locationX>176</locationX>
        <locationY>278</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector>
            <targetReference>Calculate_Contact_Count</targetReference>
        </connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>AccountId</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>recordId</elementReference>
            </value>
        </filters>
        <object>Contact</object>
        <outputReference>contactCollection</outputReference>
    </recordLookups>
    <recordUpdates>
        <name>Update_Account_Contact_Count</name>
        <label>Update Account Contact Count</label>
        <locationX>176</locationX>
        <locationY>518</locationY>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Id</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>recordId</elementReference>
            </value>
        </filters>
        <inputAssignments>
            <field>NumberOfEmployees</field>
            <value>
                <elementReference>contactCount</elementReference>
            </value>
        </inputAssignments>
        <object>Account</object>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector>
            <targetReference>Get_Account_Record</targetReference>
        </connector>
    </start>
    <status>Active</status>
    <assignments>
        <name>Calculate_Contact_Count</name>
        <label>Calculate Contact Count</label>
        <locationX>176</locationX>
        <locationY>398</locationY>
        <assignmentItems>
            <assignToReference>contactCount</assignToReference>
            <operator>Assign</operator>
            <value>
                <elementReference>contactCollection</elementReference>
            </value>
        </assignmentItems>
        <connector>
            <targetReference>Update_Account_Contact_Count</targetReference>
        </connector>
    </assignments>
    <variables>
        <name>recordId</name>
        <dataType>String</dataType>
        <isCollection>false</isCollection>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>
    <variables>
        <name>contactCollection</name>
        <dataType>SObject</dataType>
        <isCollection>true</isCollection>
        <isInput>false</isInput>
        <isOutput>false</isOutput>
        <objectType>Contact</objectType>
    </variables>
    <variables>
        <name>contactCount</name>
        <dataType>Number</dataType>
        <isCollection>false</isCollection>
        <isInput>false</isInput>
        <isOutput>false</isOutput>
        <scale>0</scale>
    </variables>
</Flow>
```

### Suggested Fixes (Web Search Results)


#### ✅ Fix for UserStory_Account_Contact_Counter (Flow)

**Error:** field integrity exception: unknown (In an Assignment element, “contactCollection” isn’t a valid reference for the value when the “contactCount” variable is set with the Equals operator.)

**Search Query:** `Salesforce Flow deployment error: field integrity exception: unknown (In an Assignment element, “contactCollection” isn’t a valid reference for the value when the “contactCount” variable is set with the Equals operator.)`

**Suggested Solutions:**

**AI Summary:**
The error indicates "contactCollection" is invalid for "contactCount" in Assignment element. Check variable references and ensure "contactCollection" is correctly defined.

❌ No search results found.

---

