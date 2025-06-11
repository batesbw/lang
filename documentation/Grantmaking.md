# Grantmaking Developer Guide

Version 64.0, Summer ’ 25

```
Last updated: May 23, 2025
```

© Copyright 2000–2025 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other

```
names and marks. Other marks appearing herein may be trademarks of their respective owners.
```

## CONTENTS

- Chapter 1: Introduction to Grantmaking
- Chapter 2: Grantmaking and Budget Management Data Model
- Chapter 3: Grantmaking
- Grantmaking Object Reference
   - ApplicationDecision
   - ApplicationRenderMethod
   - ApplicationReview
   - ApplicationStageDefinition
   - ApplicationTimeline
   - Budget
   - BudgetAllocation
   - BudgetCategory
   - BudgetCategoryValue
   - BudgetParticipant
   - BudgetPeriod
   - FundingAward
   - FundingAwardAmendment
   - FundingAwardParticipant
   - FundingAwardRequirement
   - FundingAwardRqmtSection
   - FundingDisbursement
   - FundingOpportunity
   - FundingOppParticipant
   - IndicatorAssignment
   - IndicatorPerformancePeriod
   - IndividualApplication
   - IndividualApplicationTask
   - IndvApplicationTaskParticipant
   - IndividualApplnParticipant
   - OutcomeActivity
   - PreliminaryApplicationRef
   - Program
- Grantmaking Tooling API Object
   - ApplicationRecordTypeConfig
- Grantmaking Metadata API Types
   - IndustriesSettings



**CHAPTER 1** Introduction to Grantmaking

```
EDITIONS
```
```
Available in: Lightning
Experience
```
```
Available in:
Enterprise , Unlimited ,
and Developer Editions
```
```
Streamline the grant management process for both funders and
applicants. Built on the Salesforce platform, Nonprofit Cloud for
Grantmaking includes everything you need to give grants and
manage your budgets.
Use Grantmaking to:
```
**-** Track organizations and people involved in grants and grant
    applications.
**-** Create funding opportunities that include application details.
**-** Manage reviews and approvals of grant applications and
    budgets.
**-** When used with Experience Cloud, let grant seekers learn about and apply for funding opportunities,
    submit budgets and upload supporting documents.


**CHAPTER 2** Grantmaking and Budget Management

Data Model


```
EDITIONS
```
```
Available in: Lightning
Experience
Available in: Enterprise ,
Performance , and
Unlimited Editions in
Nonprofit Cloud for
Grantmaking
Available in: Enterprise ,
Performance , Unlimited ,
and Developer Editions in
Public Sector Solutions
```
```
Learn about the objects and relationships within the Grantmaking
and Budget Management data model.
The Grantmaking and Budget Management data model provides
a set of objects and fields that you can use to store and manage
information about grants you award and the budgets associated
with them.
```
Grantmaking and Budget Management Data Model


```
To view a larger version, right-click or Ctrl+click the image and select Open Image in New Tab.
```
Grantmaking and Budget Management Data Model


**CHAPTER 3** Grantmaking

```
EDITIONS
```
```
Available in: Lightning
Experience
```
```
Available in:
Enterprise , Unlimited ,
and Developer Editions
```
```
This guide provides information about the objects and APIs that
Grantmaking uses.
```
In this chapter ...

**-** Grantmaking Object
    Reference
**-** Grantmaking Tooling
    API Object
**-** Grantmaking
    Metadata API Types


## Grantmaking Object Reference

```
EDITIONS
```
```
Available in: Lightning
Experience
Available in: Enterprise ,
Performance , and
Unlimited Editions in
Nonprofit Cloud for
Grantmaking
Available in: Enterprise ,
Performance , Unlimited ,
and Developer Editions in
Public Sector Solutions
```
```
The Grantmaking data model provides objects and fields to calculate and manage grants for your
organization.
```
```
ApplicationDecision
Represents a final decision performed for the specified Application. This object is available in
API version 56.0 and later.
ApplicationRenderMethod
Represents how a part of an application can be rendered. This object is available in Grantmaking
API version 61.0 and later.
ApplicationReview
Represents a review performed against a specified Individual Application. This object is available
in API version 56.0 and later.
ApplicationStageDefinition
Represents a stage of an application. This object is available in Grantmaking API version 61.
and later.
ApplicationTimeline
Represents the milestone dates in the application process. This object is available in API version 57.0 and later.
Budget
Tracks an estimate of future revenue or expenses during a specific time period. This object is available in API version 53.0 and later.
BudgetAllocation
Represents a subsection of a Budget that shows where allocated resources are being applied. This object is available in API version
53.0 and later.
BudgetCategory
Represents the purpose of the budget line item. This object is available in API version 57.0 and later.
BudgetCategoryValue
Captures budget values for category and time period. This object is available in API version 57.0 and later.
BudgetParticipant
Represents information about a user or group of participants who have access to a budget. This object is available in API version
59.0 and later.
BudgetPeriod
Defines a distinct time interval in which the estimate applies. This object is available in API version 57.0 and later.
FundingAward
Represents an award given to an individual or organization to facilitate a goal related to the funder’s mission. This object is available
in API version 57.0 and later.
FundingAwardAmendment
Represents a modification to the scope or finances of a previously approved award. This object is available in API version 57.0 and
later.
FundingAwardParticipant
Represents information about a user or group of participants who have access to a funding award. This object is available in API
version 59.0 and later.
```
Grantmaking Grantmaking Object Reference


```
FundingAwardRequirement
Represents a deliverable or milestone for a funding award or funding disbursement. This object is available in API version 57.0 and
later.
FundingAwardRqmtSection
Represents a part of a funding award requirement to be completed or reviewed. This object is available in API version 62.0 and later.
FundingDisbursement
Represents a payment that has been made or scheduled to be made to a funding recipient. This object is available in API version
57.0 and later.
FundingOpportunity
The pool of money available for distribution for a specific purpose. This object is available in API version 57.0 and later.
FundingOppParticipant
Represents information about a user or group of participants who have access to a funding opportunity. This object is available in
API version 60.0 and later.
IndicatorAssignment
Represents the assignment of an indicator definition that's used to measure the performance of an outcome or a related activity
This object is available in API version 59.0 and later.
IndicatorPerformancePeriod
Represents information about a specified time period including the frequency at which indicator results should be calculated and
the baseline value of the indicator. This object is available in API version 59.0 and later.
IndividualApplication
Represents an application form submitted by an individual or organization. This object is available in API version 50.0 and later.
IndividualApplicationTask
Represents a task related to an application. This object is available in Grantmaking API version 61.0 and later.
IndvApplicationTaskParticipant
Represents information about a user or group of participants who have read or write access to an individual application task. This
object is available in API version 61.0 and later.
IndividualApplnParticipant
Represents information about a user or group of participants who have access to a individual application. This object is available in
API version 59.0 and later.
OutcomeActivity
Represents a junction between an outcome and the object that's related to the activity undertaken by an organization to achieve
that outcome. This object is available in API version 59.0 and later.
PreliminaryApplicationRef
Represents the saved applications and pre-screening forms. This object is available in API version 49.0 and later.
Program
Represents information about the enrollment and disbursement of benefits in a program. This object is available in API version 57.
and later.
```
### ApplicationDecision

```
Represents a final decision performed for the specified Application. This object is available in API version 56.0 and later.
```
Grantmaking ApplicationDecision


```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Application system permission
is assigned to users.
```
Fields

```
Field Details
```
```
Type
picklist
```
```
ApplicationDecision
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the decision for the application.
Possible values are:
```
**-** Award
**-** Deny

```
Type
reference
```
```
ApplicationId
```
```
Properties
Create, Filter, Group, Sort, Update
Description
The ID of the application.
This field is a polymorphic relationship field.
Relationship Name
Application
Relationship Type
Lookup
Refers To
IndividualApplication
```
```
Type
textarea
```
```
Comment
```
```
Properties
Create, Nillable, Update
Description
The information about the decision provided on the application.
```
Grantmaking ApplicationDecision


```
Field Details
```
```
Type
reference
```
```
DecisionAuthorityId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The user responsible for the application decision.
This field is a relationship field.
Relationship Name
DecisionAuthority
Relationship Type
Lookup
Refers To
User
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
Description
Name of the preliminary application.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
ID of the owner who owns the record.
```
Grantmaking ApplicationDecision


```
Field Details
```
```
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
PreliminaryApplicationRefId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The ID of the preliminary application reference.
This field is a relationship field.
Relationship Name
PreliminaryApplicationRef
Relationship Type
Lookup
Refers To
PreliminaryApplicationRef
```
### ApplicationRenderMethod

```
Represents how a part of an application can be rendered. This object is available in Grantmaking API version 61.0 and later.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Applications system permission
is assigned to users.
```
Fields

```
Field Details
```
```
Type
textarea
```
```
Description
```
Grantmaking ApplicationRenderMethod


```
Field Details
```
```
Properties
Create, Nillable, Update
Description
The description of the application render method.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last accessed this record indirectly, for example, through
a list view or related record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last viewed this record or list view. If this value is null,
and LastReferenceDate is not null, the user accessed this record or list view indirectly.
```
```
Type
textarea
```
```
MethodName
```
```
Properties
Create, Nillable, Update
Description
The name of the render method associated with the application.
```
```
Type
reference
```
```
MethodRecordId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The record ID of the method that's associated with the application render method.
This field is a polymorphic relationship field.
Relationship Name
MethodRecord
Relationship Type
Lookup
Refers To
OmniProcess, OmniUiCard
```
Grantmaking ApplicationRenderMethod


```
Field Details
```
```
Type
picklist
```
```
MethodType
```
```
Properties
Create, Filter, Group, Restricted picklist, Sort, Update
Description
Specifies the type of method that's used to render components in the application.
Possible values are:
```
**-** FlexCard
**-** Flow
**-** OmniScript

```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the application render method.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
ID of the user who owns the record.
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
picklist
```
```
UsageType
```
```
Properties
Create, Filter, Group, Restricted picklist, Sort, Update
Description
Specifies the usage type of the application render method.
Possible values are:
```
**-** FormFramework This value is available from API version 63.0 and later.

Grantmaking ApplicationRenderMethod


```
Field Details
```
**-** Grantmaking
The default is FormFramework.

```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
ApplicationRenderMethodFeed
Feed tracking is available for the object.
ApplicationRenderMethodHistory
History is available for tracked fields of the object.
ApplicationRenderMethodShare
Sharing is available for the object.
```
### ApplicationReview

```
Represents a review performed against a specified Individual Application. This object is available in API version 56.0 and later.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Application system permission
is assigned to users.
```
Fields

```
Field Details
```
```
Type
picklist
```
```
ApplicationCategory
```
```
Properties
Filter, Group, Nillable, Sort
Description
Specifies the category of the application based on the decision period.
Possible values are:
```
**-** Basic
**-** Special

Grantmaking ApplicationReview


```
Field Details
```
```
Type
reference
```
```
ApplicationId
```
```
Properties
Create, Filter, Group, Sort, Update
Description
The individual application associated with the application review.
This field is a polymorphic relationship field.
Relationship Name
Application
Relationship Type
Lookup
Refers To
IndividualApplication
```
```
Type
picklist
```
```
ApplicationRecommendation
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the reviewer's recommended outcome of the application.
Possible values are:
```
**-** Ask for Revisions
**-** Award
**-** Deny

```
Type
reference
```
```
ApplicationStageDefinitionId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The application stage definition that's associated with the application review.
This field is a relationship field.
Relationship Name
ApplicationStageDefinition
Relationship Type
Lookup
Refers To
ApplicationStageDefinition
```
Grantmaking ApplicationReview


```
Field Details
```
```
Type
date
```
```
AssignedDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the application was assigned to the reviewer.
```
```
Type
reference
```
```
AssignedUserId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Identifies the user assigned to perform the review.
This field is a relationship field.
Relationship Name
AssignedUser
Relationship Type
Lookup
Refers To
User
```
```
Type
textarea
```
```
Comment
```
```
Properties
Create, Nillable, Update
Description
The information about the review provided on the application.
```
```
Type
textarea
```
```
Condition
```
```
Properties
Create, Nillable, Update
Description
The condition that's applicable to an applicant.
```
```
Type
int
```
```
DisplayOrder
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The order in which the application review shows on a form.
```
Grantmaking ApplicationReview


```
Field Details
```
```
Type
date
```
```
DueDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The last date by which the application review should be completed.
```
```
Type
date
```
```
EndDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the application review was completed.
```
```
Type
boolean
```
```
IsAssignedToMe
```
```
Properties
Defaulted on create, Filter, Group, Sort
Description
Indicates whether the application review is assigned to the user who's logged in.
The default value is false.
This field is a calculated field.
```
```
Type
boolean
```
```
IsRequired
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the application review is required (true) or not (false).
The default value is false.
```
```
Type
boolean
```
```
IsSubmitted
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the application review has been submitted.
This field is available from API version 58.0 and later.
The default value is true.
```
Grantmaking ApplicationReview


```
Field Details
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
Description
Name of the application being reviewed.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
The owner associated with this application review.
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
ReviewedById
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The user who reviewed the application.
```
Grantmaking ApplicationReview


```
Field Details
```
```
This field is a relationship field.
Relationship Name
ReviewedBy
Relationship Type
Lookup
Refers To
User
```
```
Type
date
```
```
StartDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the application review started.
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the status of the application review.
Possible values are:
```
**-** Canceled
**-** Completed
**-** Draft This value is available from API version 63.0 and later.
**-** In Progress
**-** Not Started

```
Type
date
```
```
SubmissionDate
```
```
Properties
Filter, Group, Nillable, Sort
Description
The date when the applicant submitted the application.
```
```
Type
string
```
```
Title
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The descriptive name for the application review.
```
Grantmaking ApplicationReview


```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
ApplicationReviewFeed
Feed tracking is available for the object.
ApplicationReviewHistory
History is available for tracked fields of the object.
ApplicationReviewOwnerSharingRule
Sharing rules are available for the object.
ApplicationReviewShare
Sharing is available for the object.
```
### ApplicationStageDefinition

```
Represents a stage of an application. This object is available in Grantmaking API version 61.0 and later.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Applications system permission
is assigned to users.
```
Fields

```
Field Details
```
```
Type
textarea
```
```
Description
```
```
Properties
Create, Nillable, Update
Description
The description of the application stage definition.
```
```
Type
reference
```
```
EditTypeAppRenderMethodId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The render method for an editable form or application that's associated with this application
stage definition.
```
Grantmaking ApplicationStageDefinition


```
Field Details
```
```
This field is a relationship field.
Relationship Name
EditTypeAppRenderMethod
Relationship Type
Lookup
Refers To
ApplicationRenderMethod
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last accessed this record indirectly, for example, through
a list view or related record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last viewed this record or list view. If this value is null,
and LastReferenceDate is not null, the user accessed this record or list view indirectly.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the application stage definition.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
ID of the user who owns the record.
This field is a polymorphic relationship field.
Relationship Name
Owner
```
Grantmaking ApplicationStageDefinition


```
Field Details
```
```
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
picklist
```
```
Type
```
```
Properties
Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update
Description
Specifies the type of the application stage definition.
Possible values are:
```
**-** FormFramework This value is available from API version 63.0 and later.
**-** Grantmaking

```
Type
reference
```
```
ViewTypeAppRenderMethodId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The render method for a read-only form or application that's associated with this application
stage definition.
This field is a relationship field.
Relationship Name
ViewTypeAppRenderMethod
Relationship Type
Lookup
Refers To
ApplicationRenderMethod
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
ApplicationStageDefinitionFeed
Feed tracking is available for the object.
ApplicationStageDefinitionHistory
History is available for tracked fields of the object.
ApplicationStageDefinitionShare
Sharing is available for the object.
```
Grantmaking ApplicationStageDefinition


### ApplicationTimeline

```
Represents the milestone dates in the application process. This object is available in API version 57.0 and later.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Application system permission
is assigned to users.
```
Fields

```
Field Details
```
```
Type
date
```
```
ApplicationCloseDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The last date when applicants can apply for a grant.
```
```
Type
date
```
```
ApplicationOpenDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when applicants can start to apply for a grant.
```
```
Type
date
```
```
DecisionReleaseDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the application decision is announced.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
Grantmaking ApplicationTimeline


```
Field Details
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
Name of the application timeline being reviewed.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
ID of the owner who owns the record.
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
picklist
```
```
Type
```
```
Properties
Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update
Description
Specifies which feature this application timeline record belongs to.
Possible values are:
```
**-** Grantmaking

### Budget

```
Tracks an estimate of future revenue or expenses during a specific time period. This object is available in API version 53.0 and later.
```
Grantmaking Budget


```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grants Management or Grantmaking license is enabled, Grants Management or Grantmaking is enabled,
and the Manage Budgets system permission is assigned to users.
```
Fields

```
Field Details
```
```
Type
reference
```
```
AccountId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The account associated with the budget.
This field is available from API version 58.0 and later.
This field is a relationship field.
Relationship Name
Account
Relationship Type
Lookup
Refers To
Account
```
```
Type
currency
```
```
Amount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The total amount of funds for a budget shown in currency format.
```
```
Type
currency
```
```
EstimatedUtilizationAmount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The amount that's estimated to be utilized from the budget.
```
Grantmaking Budget


```
Field Details
```
```
Type
string
```
```
Description
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The description of the budget and its related business processes.
```
```
Type
boolean
```
```
IsSubmitted
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the budget has been submitted. This field is available from API version
58.0 and later.
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
Name of the budget.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
```
Grantmaking Budget


```
Field Details
```
```
Description
ID of the owner who owns the record.
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
ParentBudgetId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
ID of the associated parent budget.
This field is available from API version 56.0 and later.
This field is a relationship field.
Relationship Name
ParentBudget
Relationship Type
Lookup
Refers To
Budget
```
```
Type
date
```
```
PeriodEndDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The end of the date range for which the budget applies.
```
```
Type
string
```
```
PeriodName
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The name of the time period to which the budget applies.
```
```
Type
date
```
```
PeriodStartDate
```
Grantmaking Budget


```
Field Details
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The beginning of the date range for which the budget applies.
```
```
Type
reference
```
```
ProgramId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The program associated with the budget.
This field is available from API version 58.0 and later.
This field is a relationship field.
Relationship Name
Program
Relationship Type
Lookup
Refers To
Program
```
```
Type
double
```
```
Quantity
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The quantity used to track a budget for non-currency projects. For example, this could be
number of hours or number of resources.
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The status of the budget.
Possible values are:
```
**-** Active
**-** Archived
**-** Planned

```
Type
picklist
```
```
Type
```
Grantmaking Budget


```
Field Details
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Categorizes the budget by how it will be used.
Possible values are:
```
**-** Department
**-** Program
**-** Project

```
Type
currency
```
```
UtilizedAmount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The amount that has already been utilized from the budget.
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
BudgetFeed
Feed tracking is available for the object.
BudgetHistory
History is available for tracked fields of the object.
BudgetOwnerSharingRule
Sharing rules are available for the object.
BudgetShare
Sharing is available for the object.
```
### BudgetAllocation

```
Represents a subsection of a Budget that shows where allocated resources are being applied. This object is available in API version 53.0
and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
Grantmaking BudgetAllocation


```
Special Access Rules
This object is available only if the Grants Management or Grantmaking license is enabled, Grants Management or Grantmaking is enabled,
and the Manage Budgets system permission is assigned to users.
```
Fields

```
Field Details
```
```
Type
currency
```
```
Amount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The total amount of allocated funds.
```
```
Type
reference
```
```
BudgetCategoryValueId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The budget category value that's associated with the grants allocation.
This field is a relationship field.
Relationship Name
BudgetCategoryValue
Relationship Type
Lookup
Refers To
BudgetCategoryValue
```
```
Type
reference
```
```
BudgetId
```
```
Properties
Create, Filter, Group, Sort
Description
The budget that this allocation is related to.
This field is a relationship field.
Relationship Name
Budget
Relationship Type
Master-Detail
Refers To
Budget
```
Grantmaking BudgetAllocation


```
Field Details
```
```
Type
reference
```
```
FundingDisbursementId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The funding disbursement associated with the budget allocation.
This field is available from API version 58.0 and later.
This field is a relationship field.
Relationship Name
FundingDisbursement
Relationship Type
Lookup
Refers To
FundingDisbursement
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
A descriptive name for the allocation.
```
```
Type
double
```
```
Quantity
```
```
Properties
Create, Filter, Nillable, Sort, Update
```
Grantmaking BudgetAllocation


```
Field Details
```
```
Description
The total quantity amount allocated for non-currency projects.
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The status of the budget allocation.
Possible values are:
```
**-** Allocated
**-** Committed
**-** Finalized

```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
BudgetAllocationFeed
Feed tracking is available for the object.
BudgetAllocationHistory
History is available for tracked fields of the object.
```
### BudgetCategory

```
Represents the purpose of the budget line item. This object is available in API version 57.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Budgets system permission
is assigned to users.
```
Grantmaking BudgetCategory


Fields

```
Field Details
```
```
Type
reference
```
```
BudgetId
```
```
Properties
Create, Filter, Group, Sort
Description
The parent budget that's associated with the budget category.
This field is a relationship field.
Relationship Name
Budget
Relationship Type
Master-Detail
Refers To
Budget
```
```
Type
string
```
```
Description
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The description of the budget category.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
```
Grantmaking BudgetCategory


```
Field Details
```
```
Description
The name of the budget category.
```
```
Type
string
```
```
Reason
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The reason why an item is being included in the budget.
```
```
Type
double
```
```
SequenceNumber
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The number assigned to a budget category that's used to edit or show a category.
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
BudgetCategoryFeed
Feed tracking is available for the object.
BudgetCategoryHistory
History is available for tracked fields of the object.
```
### BudgetCategoryValue

```
Captures budget values for category and time period. This object is available in API version 57.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Budgets system permission
is assigned to users.
```
Grantmaking BudgetCategoryValue


Fields

```
Field Details
```
```
Type
currency
```
```
ActualAmount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The actual amount of the budget that was used.
This field is available from API version 59.0 and later.
```
```
Type
double
```
```
ActualQuantity
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The actual quantity of the budget that was used.
This field is available from API version 59.0 and later.
```
```
Type
currency
```
```
Amount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The planned amount for the budget.
```
```
Type
reference
```
```
BudgetCategoryId
```
```
Properties
Create, Filter, Group, Sort
Description
The ID that's associated with this budget category value.
This field is a relationship field.
Relationship Name
BudgetCategory
Relationship Type
Master-Detail
Refers To
BudgetCategory
```
```
Type
reference
```
```
BudgetDivisionId
```
Grantmaking BudgetCategoryValue


```
Field Details
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The budget period that's associated with the budget category value.
This field is a relationship field.
Relationship Name
BudgetDivision
Relationship Type
Lookup
Refers To
BudgetPeriod
```
```
Type
string
```
```
Comments
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The comments about how the budget was used.
This field is available from API version 59.0 and later.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
Description
The name of this budget category value.
```
Grantmaking BudgetCategoryValue


```
Field Details
```
```
Type
double
```
```
Quantity
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The planned quantity for the budget. Use when establishing budgets for non-currency
projects.
```
```
Type
currency
```
```
VarianceAmount
```
```
Properties
Filter, Nillable, Sort
Description
The amount over or under the planned budget that was used.
This field is available from API version 59.0 and later.
This field is a calculated field.
```
```
Type
double
```
```
VarianceQuantity
```
```
Properties
Filter, Nillable, Sort
Description
The quantity over or under the planned budget that was used.
This field is available from API version 59.0 and later.
This field is a calculated field.
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
BudgetCategoryValueFeed
Feed tracking is available for the object.
BudgetCategoryValueHistory
History is available for tracked fields of the object.
```
### BudgetParticipant

```
Represents information about a user or group of participants who have access to a budget. This object is available in API version 59.0
and later.
```
Grantmaking BudgetParticipant


```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), update(), upsert()
```
Special Access Rules

```
Example: This object is accessible only when the Grantmaking license is on, Grantmaking is active, Compliant Data Sharing is
on, and users have the Managed Funding Awards system permission.
```
Fields

```
Field Details
```
```
Type
reference
```
```
BudgetId
```
```
Properties
Create, Filter, Group, Sort
Description
The budget associated with the budget participant.
This field is a relationship field.
Relationship Name
Budget
Relationship Type
Master-Detail
Refers To
Budget
```
```
Type
string
```
```
Comments
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The comments about why the participant has access to the budget.
```
```
Type
boolean
```
```
IsParticipantActive
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the budget participant is currently active (true) or not (false).
```
Grantmaking BudgetParticipant


```
Field Details
```
```
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
Description
The name of the budget participant.
```
```
Type
reference
```
```
ParticipantId
```
```
Properties
Create, Filter, Group, Sort
Description
The participant associated with the budget.
This field is a polymorphic relationship field.
Relationship Name
Participant
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
ParticipantRoleId
```
```
Properties
Create, Filter, Group, Sort, Update
```
Grantmaking BudgetParticipant


```
Field Details
```
```
Description
The participant role associated with the budget participant.
This field is a relationship field.
Relationship Name
ParticipantRole
Relationship Type
Lookup
Refers To
ParticipantRole
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
BudgetParticipantFeed
Feed tracking is available for the object.
BudgetParticipantHistory
History is available for tracked fields of the object.
```
### BudgetPeriod

```
Defines a distinct time interval in which the estimate applies. This object is available in API version 57.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Budgets system permission
is assigned to users.
```
Fields

```
Field Details
```
```
Type
reference
```
```
BudgetId
```
Grantmaking BudgetPeriod


```
Field Details
```
```
Properties
Create, Filter, Group, Sort
Description
The parent budget that's associated with the budget period.
This field is a relationship field.
Relationship Name
Budget
Relationship Type
Master-Detail
Refers To
Budget
```
```
Type
boolean
```
```
IsSubmitted
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the budget has been submitted. This field is available from API version
59.0 and later.
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the budget period.
```
Grantmaking BudgetPeriod


```
Field Details
```
```
Type
date
```
```
PeriodEndDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the budget period ends.
```
```
Type
date
```
```
PeriodStartDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The start date of the budget period.
```
```
Type
double
```
```
SequenceNumber
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The order in which the budget period is shown.
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
BudgetPeriodFeed
Feed tracking is available for the object.
BudgetPeriodHistory
History is available for tracked fields of the object.
```
### FundingAward

```
Represents an award given to an individual or organization to facilitate a goal related to the funder’s mission. This object is available in
API version 57.0 and later.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
Grantmaking FundingAward


```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Funding Awards system
permission is assigned to users.
```
Fields

```
Field Details
```
```
Type
currency
```
```
Amount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The total award amount.
```
```
Type
string
```
```
AwardNumber
```
```
Properties
Autonumber, Defaulted on create, Filter, Sort
Description
The unique identifier of the funding award in the customer's org.
```
```
Type
reference
```
```
AwardeeId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The entity related to the funding award. The account can be an organization (business
account) or individual (person account) that receives the funding.
This field is a relationship field.
Relationship Name
Awardee
Relationship Type
Lookup
Refers To
Account
```
```
Type
reference
```
```
BudgetId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The budget that's used to track the use of the award funding.
```
Grantmaking FundingAward


```
Field Details
```
```
This field is a relationship field.
Relationship Name
Budget
Relationship Type
Lookup
Refers To
Budget
```
```
Type
reference
```
```
ContactId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The individual receiving the funding award.
This field is a relationship field.
Relationship Name
Contact
Relationship Type
Lookup
Refers To
Contact
```
```
Type
reference
```
```
ContractId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The contract associated with the funding award.
This field is available from API version 59.0 and later.
This field is a relationship field.
Relationship Name
Contract
Relationship Type
Lookup
Refers To
Contract
```
```
Type
dateTime
```
```
DecisionDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
```
Grantmaking FundingAward


```
Field Details
```
```
Description
The date and time of the decision about the funding award.
```
```
Type
dateTime
```
```
EndDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The date and time when the contract related to the award ends.
```
```
Type
reference
```
```
FundingOpportunityId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The funding opportunity that's associated with the award.
This field is a relationship field.
Relationship Name
FundingOpportunity
Relationship Type
Lookup
Refers To
FundingOpportunity
```
```
Type
reference
```
```
IndividualApplicationId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The individual application that's related to the award.
This field is a relationship field.
Relationship Name
IndividualApplication
Relationship Type
Lookup
Refers To
IndividualApplication
```
```
Type
dateTime
```
```
LastReferencedDate
```
Grantmaking FundingAward


```
Field Details
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the funding award.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
ID of the owner who owns the record.
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
ParentFundingAwardId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The parent funding award for this funding award.
This field is a relationship field.
```
Grantmaking FundingAward


```
Field Details
```
```
Relationship Name
ParentFundingAward
Relationship Type
Lookup
Refers To
FundingAward
```
```
Type
reference
```
```
ProgramId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The program associated with the funding award.
This field is available from API version 58.0 and later.
This field is a relationship field.
Relationship Name
Program
Relationship Type
Lookup
Refers To
Program
```
```
Type
dateTime
```
```
StartDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The date and time when the contract related to the award begins.
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the current status of the award.
Possible values are:
```
**-** Active
**-** Cancelled
**-** Completed

Grantmaking FundingAward


```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
FundingAwardFeed
Feed tracking is available for the object.
FundingAwardHistory
History is available for tracked fields of the object.
FundingAwardOwnerSharingRule
Sharing rules are available for the object.
FundingAwardShare
Sharing is available for the object.
```
### FundingAwardAmendment

```
Represents a modification to the scope or finances of a previously approved award. This object is available in API version 57.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Funding Awards system
permission is assigned to users.
```
Fields

```
Field Details
```
```
Type
currency
```
```
AdjustedAwardAmount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The actual amount that's approved for adjustment in the funding award amount.
```
```
Type
dateTime
```
```
AdjustedEndDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
```
Grantmaking FundingAwardAmendment


```
Field Details
```
```
Description
The actual date of adjustment to the end date of the funding award.
```
```
Type
picklist
```
```
ApprovalStatus
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the approval status of the requested adjustment.
Possible values are:
```
**-** Approved
**-** In Review
**-** New
**-** Rejected

```
Type
textarea
```
```
Comments
```
```
Properties
Create, Nillable, Update
Description
The comment about the approval or rejection of the adjustment request.
```
```
Type
reference
```
```
ContractId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The amended contract related to this funding award amendment.
This field is available from API version 59.0 and later.
This field is a relationship field.
Relationship Name
Contract
Relationship Type
Lookup
Refers To
Contract
```
```
Type
reference
```
```
FundingAwardId
```
Grantmaking FundingAwardAmendment


```
Field Details
```
```
Properties
Create, Filter, Group, Sort
Description
The funding award that's associated with the contract that's adjusted.
This field is a relationship field.
Relationship Name
FundingAward
Relationship Type
Master-Detail
Refers To
FundingAward
```
```
Type
boolean
```
```
IsSubmitted
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the amendment to the funding award has been submitted (true) or not
(false).
This field is available from API version 58.0 and later.
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
```
Grantmaking FundingAwardAmendment


```
Field Details
```
```
Description
The name of amendment for the funding award.
```
```
Type
currency
```
```
ProposedAwardAmount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The amount of adjustment requested in the award amount.
```
```
Type
dateTime
```
```
ProposedEndDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The requested change to the End Date of the funding award.
```
```
Type
textarea
```
```
Reason
```
```
Properties
Create, Nillable, Update
Description
The reason for the adjustment requested in the contract.
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the status of the adjustment request.
Possible values are:
```
**-** Approved
**-** Draft
**-** Rejected
**-** Submitted

```
Type
picklist
```
```
Type
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
```
Grantmaking FundingAwardAmendment


```
Field Details
```
```
Description
Specifies the type of adjustment.
Possible values are:
```
**-** Administrative
**-** Amount
**-** Scope
**-** Timeline

```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
FundingAwardAmendmentFeed
Feed tracking is available for the object.
FundingAwardAmendmentHistory
History is available for tracked fields of the object.
```
### FundingAwardParticipant

```
Represents information about a user or group of participants who have access to a funding award. This object is available in API version
59.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Funding Awards system
permission is assigned to users.
```
Fields

```
Field Details
```
```
Type
string
```
```
Comments
```
Grantmaking FundingAwardParticipant


```
Field Details
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The comments about why the participant has access to the funding award.
```
```
Type
reference
```
```
FundingAwardId
```
```
Properties
Create, Filter, Group, Sort
Description
The funding award associated with the funding award participant.
This field is a relationship field.
Relationship Name
FundingAward
Relationship Type
Master-Detail
Refers To
FundingAward
```
```
Type
boolean
```
```
IsParticipantActive
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the funding award participant is currently active (true) or not (false).
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
Grantmaking FundingAwardParticipant


```
Field Details
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
Description
The name of the funding award participant.
```
```
Type
reference
```
```
ParticipantId
```
```
Properties
Create, Filter, Group, Sort
Description
The participant associated with the funding award.
This field is a polymorphic relationship field.
Relationship Name
Participant
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
ParticipantRoleId
```
```
Properties
Create, Filter, Group, Sort, Update
Description
The participant role associated with the funding award participant.
This field is a relationship field.
Relationship Name
ParticipantRole
Relationship Type
Lookup
Refers To
ParticipantRole
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
```
Grantmaking FundingAwardParticipant


```
FundingAwardParticipantFeed
Feed tracking is available for the object.
FundingAwardParticipantHistory
History is available for tracked fields of the object.
```
### FundingAwardRequirement

```
Represents a deliverable or milestone for a funding award or funding disbursement. This object is available in API version 57.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Funding Awards system
permission is assigned to users.
```
Fields

```
Field Details
```
```
Type
reference
```
```
ActionPlanTemplateId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The action plan template that's related to the funding award requirement and that's used
for funding requirement forms.
This field is a relationship field.
This field is available from API version 64.0 and later.
Relationship Name
ActionPlanTemplate
Refers To
ActionPlanTemplate
```
```
Type
picklist
```
```
ApprovalStatus
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
```
Grantmaking FundingAwardRequirement


```
Field Details
```
```
Description
Specifies the approval status the information that's submitted against the requirements.
Possible values are:
```
**-** Approved
**-** In Review
**-** New
**-** Rejected

```
Type
reference
```
```
AssignedContactId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The contact who is responsible for submitting the requirement.
This field is a relationship field.
Relationship Name
AssignedContact
Relationship Type
Lookup
Refers To
Contact
```
```
Type
reference
```
```
AssignedUserId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The user who submits the funding requirement.
This field is a relationship field.
Relationship Name
AssignedUser
Relationship Type
Lookup
Refers To
User
```
```
Type
textarea
```
```
Description
```
```
Properties
Create, Nillable, Update
```
Grantmaking FundingAwardRequirement


```
Field Details
```
```
Description
The description of the funding requirement.
```
```
Type
dateTime
```
```
DueDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The last date and time of submitting the requirement.
```
```
Type
reference
```
```
FundingAwardId
```
```
Properties
Create, Filter, Group, Sort
Description
Funding award that's associated with the funding requirement.
This field is a relationship field.
Relationship Name
FundingAward
Relationship Type
Master-Detail
Refers To
FundingAward
```
```
Type
reference
```
```
FundingDisbursementId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The funding disbursement that's associated with the requirement. The funds are disbursed
only after the requirements are fulfilled.
This field is a relationship field.
Relationship Name
FundingDisbursement
Relationship Type
Lookup
Refers To
FundingDisbursement
```
```
Type
boolean
```
```
IsSubmitted
```
Grantmaking FundingAwardRequirement


```
Field Details
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the requirement for the funding award has been submitted (true) or
not (false).
This field is available from API version 58.0 and later.
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last accessed this record indirectly, for example, through
a list view or related record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last viewed this record or list view. If this value is null,
and LastReferenceDate is not null, the user accessed this record or list view indirectly.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the funding requirement.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
ID of the owner of this object.
This field is a polymorphic relationship field.
Relationship Name
Owner
```
Grantmaking FundingAwardRequirement


```
Field Details
```
```
Refers To
Group, User
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the status of the funding requirement.
Possible values are:
```
**-** Approved
**-** Delayed
**-** In Progress
**-** Open
**-** Rejected
**-** Submitted

```
Type
dateTime
```
```
SubmittedDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The actual date and time when the requirement was submitted.
```
```
Type
picklist
```
```
Type
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the type of funding requirement.
Possible values are:
```
**-** Combined Report
**-** Contract
**-** Financial Report
**-** Narrative Report

```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
```
Grantmaking FundingAwardRequirement


```
FundingAwardRequirementFeed
Feed tracking is available for the object.
FundingAwardRequirementHistory
History is available for tracked fields of the object.
FundingAwardRqmtSectionOwnerSharingRule
Sharing rules are available for the object.
```
### FundingAwardRqmtSection

```
Represents a part of a funding award requirement to be completed or reviewed. This object is available in API version 62.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Funding Awards system
permission is assigned to users.
```
Fields

```
Field Details
```
```
Type
reference
```
```
ApplicationStageDefinitionId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The application stage definition associated with the funding award requirement section.
This field is a relationship field.
Relationship Name
ApplicationStageDefinition
Relationship Type
Lookup
Refers To
ApplicationStageDefinition
```
```
Type
reference
```
```
AssignedUserId
```
Grantmaking FundingAwardRqmtSection


```
Field Details
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The user assigned to complete the funding award requirement section.
This field is a relationship field.
Relationship Name
AssignedUser
Relationship Type
Lookup
Refers To
User
```
```
Type
string
```
```
Description
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The description of the funding award requirement section.
```
```
Type
int
```
```
DisplayOrder
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The order in which the funding award requirement section shows on the form.
```
```
Type
date
```
```
DueDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the funding award requirement section is due.
```
```
Type
dateTime
```
```
EndDateTime
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The date and time when the funding award requirement section ends.
```
Grantmaking FundingAwardRqmtSection


```
Field Details
```
```
Type
reference
```
```
FundingAwardRequirementId
```
```
Properties
Create, Filter, Group, Sort
Description
The parent funding award requirement associated with the funding award requirement
section.
This field is a relationship field.
Relationship Name
FundingAwardRequirement
Relationship Type
Master-detail
Refers To
FundingAwardRequirement (the master object)
```
```
Type
boolean
```
```
IsAssignedToMe
```
```
Properties
Defaulted on create, Filter, Group, Sort
Description
Indicates whether the requirement section is assigned to the logged in user (true) or not
(false). This field can be used to filter the sections assigned to the user.
The default value is false.
This field is a calculated field.
```
```
Type
boolean
```
```
IsRequired
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the funding award requirement section is required (true) or not (false).
The default value is false.
```
```
Type
boolean
```
```
IsSubmitted
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the funding award requirement section has been submitted (true) or not
(false).
The default value is false.
```
Grantmaking FundingAwardRqmtSection


```
Field Details
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last accessed this record indirectly, for example, through
a list view or related record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last viewed this record or list view. If this value is null,
and LastReferenceDate is not null, the user accessed this record or list view indirectly.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the funding award requirement section
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
ID of the owner of this object.
This field is a polymorphic relationship field.
Relationship Name
Owner
Refers To
Group, User
```
```
Type
dateTime
```
```
StartDateTime
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The date and time when the funding award requirement section starts.
```
Grantmaking FundingAwardRqmtSection


```
Field Details
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the status of the funding award requirement section.
Possible values are:
```
**-** Canceled
**-** Completed
**-** In Progress
**-** Not Started

```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
FundingAwardRqmtSectionHistory
History is available for tracked fields of the object.
FundingAwardRequirementFeed
Feed tracking is available for the object.
FundingAwardRqmtSectionOwnerSharingRule
Sharing rules are available for the object.
FundingAwardRqmtSectionShare
Sharing is available for the object.
```
### FundingDisbursement

```
Represents a payment that has been made or scheduled to be made to a funding recipient. This object is available in API version 57.0
and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Funding Awards system
permission is assigned to users.
```
Grantmaking FundingDisbursement


Fields

```
Field Details
```
```
Type
currency
```
```
Amount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The total amount that's disbursed to the awardee.
```
```
Type
dateTime
```
```
DisbursementDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The actual date and time of funds disbursement.
```
```
Type
reference
```
```
FundingAwardId
```
```
Properties
Create, Filter, Group, Sort
Description
The funding award that's associated with the funding disbursement.
This field is a relationship field.
Relationship Name
FundingAward
Relationship Type
Master-Detail
Refers To
FundingAward
```
```
Type
boolean
```
```
IsApproved
```
```
Properties
Defaulted on create, Filter, Group, Sort
Description
Indicates whether the funding disbursement is approved (true) or not (false).
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
Grantmaking FundingDisbursement


```
Field Details
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The autogenerated name of the funding disbursement.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
The owner of the record.
This field is a polymorphic relationship field.
This field is available from API version 63.0 and later.
Relationship Name
Owner
Refers To
Group, User
```
```
Type
picklist
```
```
PaymentMethodType
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the payment method for funds disbursement.
Possible values are:
```
**-** Cash

Grantmaking FundingDisbursement


```
Field Details
```
**-** Check
**-** EFT
**-** Wire

```
Type
string
```
```
PaymentNumber
```
```
Properties
Autonumber, Defaulted on create, Filter, Sort
Description
The unique identifier of the payment related to the funds disbursement.
```
```
Type
dateTime
```
```
ScheduledDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The scheduled date and time to disburse the funds.
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the approval status of the funds disbursement.
Possible values are:
```
**-** Approved
**-** Cancelled
**-** Paid
**-** Pending Approval
**-** Processing
**-** Returned
**-** Scheduled

```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
FundingDisbursementShare
Sharing is available for the object.
```
Grantmaking FundingDisbursement


```
FundingDisbursementOwnerSharingRule
Sharing rules are available for the object.
FundingDisbursementFeed
Feed tracking is available for the object.
FundingDisbursementHistory
History is available for tracked fields of the object.
```
### FundingOpportunity

```
The pool of money available for distribution for a specific purpose. This object is available in API version 57.0 and later.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Funding Awards system
permission is assigned to users.
```
Fields

```
Field Details
```
```
Type
reference
```
```
ActionPlanTemplateId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The action plan template that represents the application sections for this funding opportunity.
Relationship Name
ActionPlanTemplate
Refers To
ActionPlanTemplate
```
```
Type
textarea
```
```
ApplicationInstructions
```
```
Properties
Create, Nillable, Update
Description
The instructions on how to apply for the funding opportunity.
```
Grantmaking FundingOpportunity


```
Field Details
```
```
Type
reference
```
```
ApplicationTimelineId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The application timeline associated with the opportunity that describes the milestones in
the application process.
This field is a relationship field.
Relationship Name
ApplicationTimeline
Relationship Type
Lookup
Refers To
ApplicationTimeline
```
```
Type
reference
```
```
BudgetTemplateId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The budget that's used as a template by the applicants when they apply for the funding
opportunity.
This field is a relationship field.
Relationship Name
BudgetTemplate
Relationship Type
Lookup
Refers To
Budget
```
```
Type
textarea
```
```
Description
```
```
Properties
Create, Nillable, Update
Description
The description about the opportunity in terms of the minimum award requirements and
expected outcome.
```
```
Type
dateTime
```
```
EndDate
```
Grantmaking FundingOpportunity


```
Field Details
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The date and time when the acceptance of funding opportunity applications ended.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
currency
```
```
MaximumFundingAmount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The maximum fund amount that's awarded.
```
```
Type
currency
```
```
MinimumFundingAmount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The minimum fund amount that's awarded.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the funding opportunity.
```
```
Type
reference
```
```
OwnerId
```
Grantmaking FundingOpportunity


```
Field Details
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
ID of the owner who owns the record.s
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
ParentFundingOpportunityId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The associated parent funding opportunity.
This field is available from API version 59.0 and later.
This field is a relationship field.
Relationship Name
ParentFundingOpportunity
Relationship Type
Lookup
Refers To
FundingOpportunity
```
```
Type
reference
```
```
ProgramId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The program associated with the funding opportunity.
This field is available from API version 58.0 and later.
This field is a relationship field.
Relationship Name
Program
Relationship Type
Lookup
```
Grantmaking FundingOpportunity


```
Field Details
```
```
Refers To
Program
```
```
Type
dateTime
```
```
StartDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The date and time when the acceptance of funding opportunity applications started.
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the status of the funding opportunity.
Possible values are:
```
**-** Active
**-** Cancelled
**-** Completed
**-** Planned

```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
FundingOpportunityFeed
Feed tracking is available for the object.
FundingOpportunityHistory
History is available for tracked fields of the object.
FundingOpportunityOwnerSharingRule
Sharing rules are available for the object.
FundingOpportunityShare
Sharing is available for the object.
```
### FundingOppParticipant

```
Represents information about a user or group of participants who have access to a funding opportunity. This object is available in API
version 60.0 and later.
```
Grantmaking FundingOppParticipant


```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Funding Awards system
permission is assigned to users.
```
Fields

```
Field Details
```
```
Type
string
```
```
Comments
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The comments about why the participant has access to the funding opportunity.
```
```
Type
reference
```
```
FundingOpportunityId
```
```
Properties
Create, Filter, Group, Sort
Description
The funding opportunity associated with the funding opportunity participant.
This field is a relationship field.
Relationship Name
FundingOpportunity
Relationship Type
Master-Detail
Refers To
FundingOpportunity
```
```
Type
boolean
```
```
IsParticipantActive
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
```
Grantmaking FundingOppParticipant


```
Field Details
```
```
Description
Indicates whether the funding opportunity participant is currently active (true) or not
(false).
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
Description
The name of the funding opportunity participant.
```
```
Type
reference
```
```
ParticipantId
```
```
Properties
Create, Filter, Group, Sort
Description
The participant associated with the funding opportunity.
This field is a polymorphic relationship field.
Relationship Name
Participant
Relationship Type
Lookup
Refers To
Group, User
```
Grantmaking FundingOppParticipant


```
Field Details
```
```
Type
reference
```
```
ParticipantRoleId
```
```
Properties
Create, Filter, Group, Sort, Update
Description
The participant role associated with the funding opportunity participant.
This field is a relationship field.
Relationship Name
ParticipantRole
Relationship Type
Lookup
Refers To
ParticipantRole
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
FundingOppParticipantFeed
Feed tracking is available for the object.
FundingOppParticipantHistory
History is available for tracked fields of the object.
```
### IndicatorAssignment

```
Represents the assignment of an indicator definition that's used to measure the performance of an outcome or a related activity This
object is available in API version 59.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available in products:
```
**-** That include the Outcome Management and Grantmaking licenses.
**-** Where Outcome Management and Grantmaking are enabled.

Grantmaking IndicatorAssignment


**-** The Manage Applications, Manage Funding Awards, Manage Outcomes, and Use Grantmaking system permissions are assigned to
    users.

Fields

```
Field Details
```
```
Type
reference
```
```
FundingAwardId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The funding award that the indicator assignment measures.
This field is a relationship field.
Relationship Name
FundingAward
Relationship Type
Lookup
Refers To
FundingAward
```
```
Type
reference
```
```
FundingOpportunityId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The funding opportunity that the indicator assignment measures.
This field is a relationship field.
Relationship Name
FundingOpportunity
Relationship Type
Lookup
Refers To
FundingOpportunity
```
```
Type
picklist
```
```
IndicatorAssignmentType
```
```
Properties
Create, Filter, Group, Sort, Update
Description
Specifies the object that the indicator assignment measures.
Possible values are:
```
Grantmaking IndicatorAssignment


```
Field Details
```
**-** Outcome
**-** Program

```
Type
reference
```
```
IndicatorDefinitionId
```
```
Properties
Create, Filter, Group, Sort
Description
The indicator definition that's associated with the indicator assignment.
This field is a relationship field.
Relationship Name
IndicatorDefinition
Relationship Type
Master-detail
Refers To
IndicatorDefinition (the master object)
```
```
Type
reference
```
```
IndividualApplicationId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The individual application that the indicator assignment measures.
This field is a relationship field.
Relationship Name
IndividualApplication
Relationship Type
Lookup
Refers To
IndividualApplication
```
```
Type
picklist
```
```
IntendedDirection
```
```
Properties
Create, Filter, Group, Nillable, Restricted picklist, Sort, Update
Description
Specifies the intended direction of change in the behavior, knowledge, skills, status, or level
of functioning that's detailed in the parent indicator definition.
Possible values are:
```
**-** Decrease

Grantmaking IndicatorAssignment


```
Field Details
```
**-** Increase
**-** Maintain

```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last accessed this record indirectly, for example, through
a list view or related record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last viewed this record or list view. If this value is null,
and LastReferenceDate is not null, the user accessed this record or list view indirectly.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the indicator assignment.
```
```
Type
reference
```
```
OutcomeId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The outcome that the indicator assignment measures.
This field is a relationship field.
Relationship Name
Outcome
Relationship Type
Lookup
Refers To
Outcome
```
```
Type
reference
```
```
OwnerId
```
Grantmaking IndicatorAssignment


```
Field Details
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
The owner of this indicator assignment.
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
ProgramId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The program that the indicator assignment measures.
This field is a relationship field.
Relationship Name
Program
Relationship Type
Lookup
Refers To
Program
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Sort, Update
Description
Specifies the status of the indicator assignment.
Possible values are:
```
**-** Active
**-** Canceled
**-** Completed
**-** Planned

Grantmaking IndicatorAssignment


```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
IndicatorAssignmentFeed
Feed tracking is available for the object.
IndicatorAssignmentHistory
History is available for tracked fields of the object.
IndicatorAssignmentOwnerSharingRule
Sharing rules are available for the object.
IndicatorAssignmentShare
Sharing is available for the object.
```
### IndicatorPerformancePeriod

```
Represents information about a specified time period including the frequency at which indicator results should be calculated and the
baseline value of the indicator. This object is available in API version 59.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available in products:
```
**-** That include the Outcome Management and Grantmaking licenses.
**-** Where Outcome Management and Grantmaking are enabled.
**-** The Manage Applications, Manage Funding Awards, Manage Outcomes, and Use Grantmaking system permissions are assigned to
    users.

Fields

```
Field Details
```
```
Type
textarea
```
```
BaselineDescription
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The description of the baseline value.
```
Grantmaking IndicatorPerformancePeriod


```
Field Details
```
```
Type
double
```
```
BaselineValue
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The value of the indicator assignment at the beginning of the indicator performance period.
```
```
Type
textarea
```
```
Description
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The description of the indicator performance period.
```
```
Type
reference
```
```
FundingAwardRequirementId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The funding award requirement that's associated with the indicator performance period.
This field is a relationship field.
Relationship Name
FundingAwardRequirement
Relationship Type
Lookup
Refers To
FundingAwardRequirement
```
```
Type
reference
```
```
IndicatorAssignmentId
```
```
Properties
Create, Filter, Group, Sort
Description
The indicator assignment that is associated with the indicator performance period.
This field is a relationship field.
Relationship Name
IndicatorAssignment
Relationship Type
Master-detail
Refers To
IndicatorAssignment (the master object)
```
Grantmaking IndicatorPerformancePeriod


```
Field Details
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last accessed this record indirectly, for example, through
a list view or related record.
```
```
Type
date
```
```
LastResultMeasurementDate
```
```
Properties
Filter, Group, Nillable, Sort
Description
The date when the last result value was measured.
This field is a calculated field.
```
```
Type
double
```
```
LastResultValue
```
```
Properties
Filter, Nillable, Sort
Description
The result value from the most recently measured indicator result.
This field is a calculated field.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last viewed this record or list view. If this value is null,
and LastReferenceDate is not null, the user accessed this record or list view indirectly.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the indicator performance period.
```
```
Type
picklist
```
```
TargetProgress
```
Grantmaking IndicatorPerformancePeriod


```
Field Details
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the progress of the target within the time period.
Possible values are:
```
**-** At Risk
**-** Complete
**-** Not Met
**-** Not Started
**-** On Track

```
Type
double
```
```
TargetValue
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The target value of the indicator assignment within the time period.
```
```
Type
reference
```
```
TimePeriodId
```
```
Properties
Create, Filter, Group, Sort, Update
Description
The time period that is associated with the indicator performance period.
This field is a relationship field.
Relationship Name
TimePeriod
Relationship Type
Lookup
Refers To
TimePeriod
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
IndicatorPerformancePeriodFeed
Feed tracking is available for the object.
IndicatorPerformancePeriodHistory
History is available for tracked fields of the object.
```
Grantmaking IndicatorPerformancePeriod


### IndividualApplication

```
Represents an application form submitted by an individual or organization. This object is available in API version 50.0 and later.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
Fields

```
Field Details
```
```
Type
reference
```
```
AccountId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The ID of the applicant’s account.
This is a relationship field.
Relationship Name
Account
Relationship Type
Lookup
Refers To
Account
```
```
Type
reference
```
```
ApplicationCaseId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The ID of a case that relates to this application.
This is a relationship field.
Relationship Name
ApplicationCase
Relationship Type
Lookup
Refers To
Case
```
```
Type
textarea
```
```
ApplicationChangeOverview
```
Grantmaking IndividualApplication


```
Field Details
```
```
Properties
Create, Nillable, Update
Description
The Einstein-generated historical overview of the changes between application versions.
Available in API versions 62.0 and later. Einstein Generative AI for Public Sector Solutions
must be enabled.
```
```
Type
string
```
```
ApplicationName
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Descriptive name for the application. This field is available if you enabled Public Sector
Solutions or Grantmaking in Setup.
Available from API version 57.0 and later.
```
```
Type
textarea
```
```
ApplicationOverview
```
```
Properties
Create, Nillable, Update
Description
The Einstein-generated historical overview of application stages, data changes, and processing
actions.
Available in API versions 62.0 and later. Einstein Generative AI for Public Sector Solutions
must be enabled.
```
```
Type
string
```
```
ApplicationReferenceNumber
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The custom reference number assigned to the application. This field is available if you enabled
Health Cloud, Public Sector Solutions, or Grantmaking in Setup.
```
```
Type
picklist
```
```
ApplicationType
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The type of the application.
Possible values are:
```
Grantmaking IndividualApplication


```
Field Details
```
**-** Change Of Circumstance—Available in API versions 62.0 and later with Public
    Sector Solutions.
**-** ChangeOfCircumstance—Available in API versions 60.0 and 61.0 with Public
    Sector Solutions.
**-** New
**-** Recertification—Available in API version 60.0 and later with Public Sector
    Solutions.
**-** Renewal

```
Type
dateTime
```
```
AppliedDate
```
```
Properties
Create, Filter, Sort, Update
Description
The date on which the application was received from the applicant.
```
```
Type
dateTime
```
```
ApprovedDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The date on which the application was approved.
```
```
Type
reference
```
```
BudgetId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The budget associated with the individual application. This field is available if you enabled
Public Sector Solutions or Grantmaking in Setup.
Available from API version 57.0 and later.
This field is a relationship field.
Relationship Name
Budget
Relationship Type
Lookup
Refers To
Budget
```
```
Type
picklist
```
```
Category
```
Grantmaking IndividualApplication


```
Field Details
```
```
Properties
Create, Filter, Group, Sort, Update
Description
The service category of the application.
Possible values are:
```
**-** License
**-** Permit
**-** Grant Application
**-** Letter of Intent

```
Type
reference
```
```
ContactId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The contact associated with the individual application.
This field is a relationship field.
Relationship Name
Contact
Relationship Type
Lookup
Refers To
Contact
```
```
Type
string
```
```
Description
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Text description provided by the applicant.
```
```
Type
reference
```
```
FundingOpportunityId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The funding opportunity associated with the individual application. This field is available if
you enabled Public Sector Solutions or Grantmaking in Setup.
Available in API version 57.0 and later.
This field is a relationship field.
```
Grantmaking IndividualApplication


```
Field Details
```
```
Relationship Name
FundingOpportunity
Relationship Type
Lookup
Refers To
FundingOpportunity
```
```
Type
textarea
```
```
FundingRequestPurpose
```
```
Properties
Create, Nillable, Update
Description
Description of what the individual application funds are used for. This field is available if you
enabled Public Sector Solutions or Grantmaking in Setup.
Available in API version 57.0 and later.
```
```
Type
picklist
```
```
InternalStatus
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Status of the individual application in Salesforce CRM.
Available in API version 57.0 and later.
Possible values are:
```
**-** Invited
**-** In Progress
**-** Submitted
**-** Application Accepted
**-** Revision Requested
**-** In Review
**-** Approved
**-** Denied

```
Type
boolean
```
```
IsOwnerEditable
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Whether the owner ID of this record can be changed.
The default value is 'false'.
```
Grantmaking IndividualApplication


```
Field Details
```
```
Type
boolean
```
```
IsSubmitted
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the individual application has been submitted. This field is available if you
enabled Public Sector Solutions or Grantmaking in Setup.
Available in API version 58.0 and later.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when a user most recently viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when a user most recently viewed this record. If this value is null, this
record might only have been referenced (LastReferencedDate) and not viewed.
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
Description
The auto-generated unique ID for this application.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
The ID of the user that owns this record.
This is a polymorphic relationship field.
Relationship Name
Owner
```
Grantmaking IndividualApplication


```
Field Details
```
```
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
RecordTypeId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The record associated to the application.
This is a relationship field.
Relationship Name
RecordType
Relationship Type
Lookup
Refers To
RecordType
```
```
Type
currency
```
```
RequestedAmount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
Amount requested in the individual application. This field is available if you enabled Public
Sector Solutions or Grantmaking in Setup.
Available in API version 57.0 and later.
```
```
Type
dateTime
```
```
RequirementsCompleteDate
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The date when the applicant fulfilled all the requirements for approval.
```
```
Type
reference
```
```
SavedApplicationRefId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Reference Id of the saved application.
```
Grantmaking IndividualApplication


```
Field Details
```
```
This is a relationship field.
Relationship Name
SavedApplicationRef
Relationship Type
Lookup
Refers To
PreliminaryApplicationRef
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The submission and approval status of the application.
Possible values are:
```
**-** Invited
**-** In Progress
**-** Submitted
**-** Application Accepted
**-** Revision Requested
**-** In Review
**-** Approved
**-** Denied

```
Type
boolean
```
```
WasReturned
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Whether a submitted application was sent back to the applicant due to errors.
The default value is 'false'.
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
IndividualApplicationChangeEvent (API Version 55.0)
Change events are available for the object.
IndividualApplicationFeed
Feed tracking is available for the object.
```
Grantmaking IndividualApplication


```
IndividualApplicationHistory
History is available for tracked fields of the object.
IndividualApplicationOwnerSharingRule
Sharing rules are available for the object.
IndividualApplicationShare
Sharing is available for the object.
```
### IndividualApplicationTask

```
Represents a task related to an application. This object is available in Grantmaking API version 61.0 and later.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Funding Awards system
permission is assigned to users.
```
Fields

```
Field Details
```
```
Type
reference
```
```
ApplicationStageDefinitionId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The application stage definition associated with the individual application task.
This field is a relationship field.
Relationship Name
ApplicationStageDefinition
Relationship Type
Lookup
Refers To
ApplicationStageDefinition
```
```
Type
string
```
```
Description
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
```
Grantmaking IndividualApplicationTask


```
Field Details
```
```
Description
Describes the details of the task to be completed.
```
```
Type
date
```
```
DueDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the individual application task must be completed.
```
```
Type
date
```
```
DueDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the individual application task must be completed.
```
```
Type
dateTime
```
```
EndDateTime
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The date and time when the individual application task ends.
```
```
Type
reference
```
```
IndividualApplicationId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The individual application associated with the individual application task.
This field is a relationship field.
Relationship Name
IndividualApplication
Relationship Type
Lookup
Refers To
IndividualApplication
```
```
Type
boolean
```
```
IsRequired
```
Grantmaking IndividualApplicationTask


```
Field Details
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the individual application task is required (true) or not (false).
The default value is false.
```
```
Type
boolean
```
```
IsSubmitted
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the individual application task has been submitted.
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last accessed this record indirectly, for example, through
a list view or related record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last viewed this record or list view. If this value is null,
and LastReferenceDate is not null, the user accessed this record or list view indirectly.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the individual application task.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
```
Grantmaking IndividualApplicationTask


```
Field Details
```
```
Description
ID of the user who owns the record.
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
PreliminaryApplicationRefId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The parent funding award for this funding award.
This field is a relationship field.
Relationship Name
PreliminaryApplicationRef
Relationship Type
Lookup
Refers To
PreliminaryApplicationRef
```
```
Type
url
```
```
SavedApplicationUrl
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The URL of a saved application that's associated with the individual application task.
```
```
Type
int
```
```
SequenceNumber
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The sequence in which the individual application task must be performed.
```
```
Type
dateTime
```
```
StartDateTime
```
Grantmaking IndividualApplicationTask


```
Field Details
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The date and time when the individual application task starts.
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
Specifies the status of the individual application task.
Possible values are:
```
**-** Cancelled
**-** Completed
**-** In Progress
**-** Not Started

```
Type
picklist
```
```
Type
```
```
Properties
Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update
Description
Specifies the type of the individual application task.
Possible values are:
```
**-** Grantmaking

```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
IndividualApplicationTaskFeed
Feed tracking is available for the object.
IndividualApplicationTaskHistory
History is available for tracked fields of the object.
IndividualApplicationTaskShare
Sharing is available for the object.
```
Grantmaking IndividualApplicationTask


### IndvApplicationTaskParticipant

```
Represents information about a user or group of participants who have read or write access to an individual application task. This object
is available in API version 61.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Applications system permission
is assigned to users.
```
Fields

```
Field Details
```
```
Type
string
```
```
Comments
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The reasons why a participant is involved in an individual application task.
```
```
Type
reference
```
```
IndividualApplicationTaskId
```
```
Properties
Create, Filter, Group, Sort
Description
The individual application task associated with the individual application task participant.
This field is a relationship field.
Relationship Name
IndividualApplicationTask
Relationship Type
Master-Detail
Refers To
IndividualApplicationTask (the master object)
```
```
Type
boolean
```
```
IsParticipantActive
```
Grantmaking IndvApplicationTaskParticipant


```
Field Details
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates if the participant is currently active.
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last accessed this record indirectly, for example, through
a list view or related record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last viewed this record or list view. If this value is null,
and LastReferenceDate is not null, the user accessed this record or list view indirectly.
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
Description
The name of the individual application task participant.
```
```
Type
reference
```
```
ParticipantId
```
```
Properties
Create, Filter, Group, Sort
Description
The participant associated with the individual application task.
This field is a polymorphic relationship field.
Relationship Name
Participant
Relationship Type
Lookup
```
Grantmaking IndvApplicationTaskParticipant


```
Field Details
```
```
Refers To
Group, User
```
```
Type
reference
```
```
ParticipantRoleId
```
```
Properties
Create, Filter, Group, Sort, Update
Description
The participant role associated with the individual application task participant.
This field is a relationship field.
Relationship Name
ParticipantRole
Relationship Type
Lookup
Refers To
ParticipantRole
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
IndvApplicationTaskParticipantFeed
Feed tracking is available for the object.
IndvApplicationTaskParticipantHistory
History is available for tracked fields of the object.
```
### IndividualApplnParticipant

```
Represents information about a user or group of participants who have access to a individual application. This object is available in API
version 59.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Funding Awards system
permission is assigned to users.
```
Grantmaking IndividualApplnParticipant


Fields

```
Field Details
```
```
Type
string
```
```
Comments
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The comments about why the participant has access to the individual application.
```
```
Type
reference
```
```
IndividualApplicationId
```
```
Properties
Create, Filter, Group, Sort
Description
The individual application associated with the individual application participant.
This field is a relationship field.
Relationship Name
IndividualApplication
Relationship Type
Master-Detail
Refers To
IndividualApplication
```
```
Type
boolean
```
```
IsParticipantActive
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the individual application participant is currently active (true) or not
(false).
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
Grantmaking IndividualApplnParticipant


```
Field Details
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
Description
The name of the individual application participant.
```
```
Type
reference
```
```
ParticipantId
```
```
Properties
Create, Filter, Group, Sort
Description
The participant associated with the individual application.
This field is a polymorphic relationship field.
Relationship Name
Participant
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
ParticipantRoleId
```
```
Properties
Create, Filter, Group, Sort, Update
Description
The participant role associated with the individual application participant.
This field is a relationship field.
Relationship Name
ParticipantRole
Relationship Type
Lookup
Refers To
ParticipantRole
```
Grantmaking IndividualApplnParticipant


```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
IndividualApplnParticipantFeed
Feed tracking is available for the object.
IndividualApplnParticipantHistory
History is available for tracked fields of the object.
```
### OutcomeActivity

```
Represents a junction between an outcome and the object that's related to the activity undertaken by an organization to achieve that
outcome. This object is available in API version 59.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available in products:
```
**-** That include the Outcome Management and Grantmaking licenses.
**-** Where Outcome Management and Grantmaking are enabled.
**-** The Manage Applications, Manage Funding Awards, Manage Outcomes, and Use Grantmaking system permissions are assigned to
    users.

Fields

```
Field Details
```
```
Type
reference
```
```
BenefitId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The benefit that's associated with the outcome.
This field is a relationship field.
Relationship Name
Benefit
Relationship Type
Lookup
```
Grantmaking OutcomeActivity


```
Field Details
```
```
Refers To
Benefit
```
```
Type
reference
```
```
FundingAwardId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The funding award that's associated with the outcome.
This field is a relationship field.
Relationship Name
FundingAward
Relationship Type
Lookup
Refers To
FundingAward
```
```
Type
reference
```
```
FundingOpportunityId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The funding opportunity that's associated with the outcome.
This field is a relationship field.
Relationship Name
FundingOpportunity
Relationship Type
Lookup
Refers To
FundingOpportunity
```
```
Type
reference
```
```
GoalDefinitionId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The goal definition that's associated with the outcome. This field is available from API version
60.0 and later.
This field is a relationship field.
Relationship Name
GoalDefinition
```
Grantmaking OutcomeActivity


```
Field Details
```
```
Relationship Type
Lookup
Refers To
GoalDefinition
```
```
Type
reference
```
```
IndividualApplicationId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The individual application that's associated with the outcome.
This field is a relationship field.
Relationship Name
IndividualApplication
Relationship Type
Lookup
Refers To
IndividualApplication
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last accessed this record indirectly, for example, through
a list view or related record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last viewed this record or list view. If this value is null,
and LastReferenceDate is not null, the user accessed this record or list view indirectly.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the outcome activity.
```
Grantmaking OutcomeActivity


```
Field Details
```
```
Type
picklist
```
```
OutcomeActivityType
```
```
Properties
Create, Filter, Group, Sort, Update
Description
Specifies the type of activity that’s associated with the outcome
Possible values are:
```
**-** Benefit
**-** Goal Definition This value is available from API version 60.0 and later.
**-** Program

```
Type
reference
```
```
OutcomeId
```
```
Properties
Create, Filter, Group, Sort
Description
The outcome that's associated with the outcome.
This field is a relationship field.
Relationship Name
Outcome
Relationship Type
Master-detail
Refers To
Outcome (the master object)
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
The owner of the record.
This field is a polymorphic relationship field.
This field is available from API version 63.0 and later.
Relationship Name
Owner
Refers To
Group, User
```
```
Type
reference
```
```
ProgramId
```
Grantmaking OutcomeActivity


```
Field Details
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The program that's associated with the outcome.
This field is a relationship field.
Relationship Name
Program
Relationship Type
Lookup
Refers To
Program
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
OutcomeActivityShare
Sharing is available for the object.
OutcomeActivityOwnerSharingRule
Sharing rules are available for the object.
OutcomeActivityFeed
Feed tracking is available for the object.
OutcomeActivityHistory
History is available for tracked fields of the object.
```
### PreliminaryApplicationRef

```
Represents the saved applications and pre-screening forms. This object is available in API version 49.0 and later.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Application system permission
is assigned to users.
```
Grantmaking PreliminaryApplicationRef


Fields

```
Field Details
```
```
Type
reference
```
```
ApplicantId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
ID of the applicant for the application.
This field is a relationship field.
Relationship Name
Applicant
Relationship Type
Lookup
Refers To
Contact
```
```
Type
picklist
```
```
ApplicationCategory
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The category of the application
```
```
Type
string
```
```
ApplicationName
```
```
Properties
Create, Filter, Group, Sort, Update
Description
Name of the preliminary application.
```
```
Type
picklist
```
```
ApplicationType
```
```
Properties
Create, Filter, Group, Restricted picklist, Sort, Update
Description
Type of application.
Possible values are:
```
**-** BusinessLicenseApplication—Business License Application
**-** BusinessPrescreening—License Requirement Assessment
**-** IndividualApplication—Individual Application

Grantmaking PreliminaryApplicationRef


```
Field Details
```
```
Type
reference
```
```
BusinessAccountNameId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
ID of the account related to the application.
This field is a relationship field.
Relationship Name
BusinessAccountName
Relationship Type
Lookup
Refers To
Account
```
```
Type
boolean
```
```
IsSubmitted
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
Indicates whether the application was submitted.
The default value is false.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed a record related to this record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp for when the current user last viewed this record.
```
```
Type
string
```
```
Name
```
```
Properties
Autonumber, Defaulted on create, Filter, idLookup, Sort
```
Grantmaking PreliminaryApplicationRef


```
Field Details
```
```
Description
Name of the preliminary application.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
Description
ID of the owner who owns the record.
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
url
```
```
SavedApplicationUrl
```
```
Properties
Create, Filter, Group, Sort, Update
Description
Relative path of the saved application.
```
```
Type
date
```
```
SubmissionDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the application was submitted.
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
PreliminaryApplicationRefFeed
Feed tracking is available for the object.
PreliminaryApplicationRefHistory
History is available for tracked fields of the object.
PreliminaryApplicationRefOwnerSharingRule
Sharing rules are available for the object.
```
Grantmaking PreliminaryApplicationRef


```
PreliminaryApplicationRefShare
Sharing is available for the object.
```
### Program

```
Represents information about the enrollment and disbursement of benefits in a program. This object is available in API version 57.0 and
later.
```
```
Supported Calls
create(), delete(), describeLayout(), describeSObjects(), getDeleted(), getUpdated(), query(),
retrieve(), search(), undelete(), update(), upsert()
```
Fields

```
Field Details
```
```
Type
double
```
```
ActiveEnrolleeCount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The count of program enrollees with IsActive on ProgramEnrollment selected. Data
Processing Engine calculates this field if you activate the Program Management Data
Processing Engine Definition templates in Setup. You can schedule this calculation to run
on a regular basis.
```
```
Type
textarea
```
```
AdditionalContext
```
```
Properties
Create, Nillable, Update
Description
The additional context about the program.
```
```
Type
double
```
```
CurrentMonthDisbCount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The count of benefits disbursed in the current month. Data Processing Engine calculates this
field if you activate the Program Management Data Processing Engine Definition templates
in Setup. You can schedule this calculation to run on a regular basis.
```
```
Type
double
```
```
CurrentYearDisbCount
```
Grantmaking Program


```
Field Details
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The count of benefits disbursed in the current year. Data Processing Engine calculates this
field if you activate the Program Management Data Processing Engine Definition templates
in Setup. You can schedule this calculation to run on a regular basis.
```
```
Type
date
```
```
EndDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the program ends.
```
```
Type
dateTime
```
```
LastReferencedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last accessed this record indirectly, for example, through
a list view or related record.
```
```
Type
dateTime
```
```
LastViewedDate
```
```
Properties
Filter, Nillable, Sort
Description
The timestamp when the current user last viewed this record or list view. If this value is null,
and LastReferenceDate is not null, the user accessed this record or list view.
```
```
Type
string
```
```
Name
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of the program.
```
```
Type
reference
```
```
OwnerId
```
```
Properties
Create, Defaulted on create, Filter, Group, Sort, Update
```
Grantmaking Program


```
Field Details
```
```
Description
The user who owns the object.
This field is a polymorphic relationship field.
Relationship Name
Owner
Relationship Type
Lookup
Refers To
Group, User
```
```
Type
reference
```
```
ParentProgramId
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The associated parent program.
This field is available from API version 59.0 and later.
This field is a relationship field.
Relationship Name
ParentProgram
Relationship Type
Lookup
Refers To
Program
```
```
Type
double
```
```
PreviousMonthDisbCount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The count of benefits disbursed in the previous month. Data Processing Engine calculates
this field if you activate the Program Management Data Processing Engine Definition
templates in Setup. You can schedule this calculation to run on a regular basis.
```
```
Type
double
```
```
PreviousYearDisbCount
```
```
Properties
Create, Filter, Nillable, Sort, Update
```
Grantmaking Program


```
Field Details
```
```
Description
The count of benefits disbursed in the previous year. Data Processing Engine calculates this
field if you activate the Program Management Data Processing Engine Definition templates
in Setup. You can schedule this calculation to run on a regular basis.
```
```
Type
date
```
```
StartDate
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The date when the program begins.
```
```
Type
picklist
```
```
Status
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The status of the program.
Possible values are:
```
**-** Active
**-** Cancelled
**-** Completed
**-** Planned
This field is accessible if you enabled Data Protection and Privacy in Setup.

```
Type
string
```
```
Summary
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The summary of the program.
```
```
Type
double
```
```
TotalEnrolleeCount
```
```
Properties
Create, Filter, Nillable, Sort, Update
Description
The total count of enrollees in the program. Data Processing Engine calculates this field if
you activate the Program Management Data Processing Engine Definition templates in Setup.
You can schedule this calculation to run on a regular basis.
```
Grantmaking Program


```
Field Details
```
```
Type
picklist
```
```
UsageType
```
```
Properties
Create, Filter, Group, Nillable, Restricted picklist, Sort, Update
Description
Specifies the usage type of the program.
Possible value is ProgramManagement.
```
```
Associated Objects
This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object.
Otherwise, they’re available in the specified API version and later.
ProgramFeed
Feed tracking is available for the object.
ProgramHistory
History is available for tracked fields of the object.
ProgramOwnerSharingRule
Sharing rules are available for the object.
```
## Grantmaking Tooling API Object

```
EDITIONS
```
```
Available in: Lightning
Experience
```
```
Available in: Enterprise ,
Performance , and
Unlimited Editions in
Nonprofit Cloud for
Grantmaking
Available in: Enterprise ,
Performance , Unlimited ,
and Developer Editions in
Public Sector Solutions
```
```
Tooling API exposes metadata used in developer tooling that you can access through REST or SOAP.
Tooling API’s SOQL capabilities for many metadata types allow you to retrieve smaller pieces of
metadata.
For more information about Tooling API objects and to find a complete reference of all the supported
objects, see Introducing Tooling API.
```
### ApplicationRecordTypeConfig

```
Represents the configuration that maps object record types to an application. This object is
available in API version 57.0 and later.
```
### ApplicationRecordTypeConfig

```
Represents the configuration that maps object record types to an application. This object is available
in API version 57.0 and later.
```
```
Important: Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain
terms to avoid any effect on customer implementations.
```
```
Supported SOAP API Calls
create(), delete(), describeSObjects(), query(), retrieve(), update(), upsert()
```
Grantmaking Grantmaking Tooling API Object


```
Supported REST API Methods
DELETE, GET,HEAD,PATCH, POST,Query
```
```
Special Access Rules
This object is available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage Application system permission
is assigned to users.
```
Fields

```
Field Details
```
```
Type
picklist
```
```
ApplicationUsageType
```
```
Properties
Create, Filter, Group, Restricted picklist, Sort, Update
Description
Count of application records used by Grantmaking.
Possible values are:
```
**-** BA—Benefit Assistance
**-** CCM—Composable Case Management
**-** EDU—Education Cloud
**-** Grantmaking
**-** HC—Health Cloud
**-** ERM—Others
**-** LPI—Public Sector Solutions

```
Type
string
```
```
DeveloperName
```
```
Properties
Create, Filter, Group, Nillable, Sort, Update
Description
The unqiue name for ApplicationRecordTypeConfig.
The unique name of the object in the API. This name can contain only underscores and
alphanumeric characters, and must be unique in your org. It must begin with a letter, not
include spaces, not end with an underscore, and not contain two consecutive underscores.
In managed packages, this field prevents naming conflicts on package installations. With
this field, a developer can change the object’s name in a managed package and the changes
are reflected in a subscriber’s organization. Label is Record Type Name. This field is
automatically generated, but you can supply your own value if you create the record using
the API.
```
Grantmaking ApplicationRecordTypeConfig


```
Field Details
```
```
Note: When creating large sets of data, always specify a unique DeveloperName
for each record. If no DeveloperName is specified, performance may slow while
Salesforce generates one for each record.
```
```
Type
picklist
```
```
Language
```
```
Properties
Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update
Description
The language of the ApplicationRecordTypeConfig.
Possible values are:
```
**-** The language of the account record type configuration.
**-** da—Danish
**-** de—German
**-** en_US—English
**-** es—Spanish
**-** es_MX—Spanish (Mexico)
**-** fi—Finnish
**-** fr—French
**-** it—Italian
**-** ja—Japanese
**-** ko—Korean
**-** nl_NL—Dutch
**-** no—Norwegian
**-** pt_BR—Portuguese (Brazil)
**-** ru—Russian
**-** sv—Swedish
**-** th—Thai
**-** zh_CN—Chinese (Simplified)
**-** zh_TW—Chinese (Traditional)

```
Type
string
```
```
MasterLabel
```
```
Properties
Create, Filter, Group, Sort, Update
Description
Label for the ApplicationRecordTypeConfig. In the UI, this field is Application Record Type
Configuration.
```
Grantmaking ApplicationRecordTypeConfig


```
Field Details
```
```
Type
picklist
```
```
ObjectName
```
```
Properties
Create, Filter, Group, Restricted picklist, Sort, Update
Description
Objects used by Grantmaking.
Possible values are:
```
**-** IndividualApplication—Individual Application

```
Type
string
```
```
RecordTypeName
```
```
Properties
Create, Filter, Group, idLookup, Sort, Update
Description
The name of record type that was created for Individual Application.
```
## Grantmaking Metadata API Types

```
Metadata API enables you to access some types and feature settings that you can customize in the user interface. For more information
about Metadata API.
Find a complete reference of existing metadata types, see Metadata API Developer Guide.
```
### IndustriesSettings

```
Represents the settings for Grantmaking
```
### IndustriesSettings

```
Represents the settings for Grantmaking
This type extends the metadata type and inherits its fullName field.
In the package manifest, all organization settings metadata types are accessed using the Settings name.
```
```
File Suffix and Directory Location
IndustriesSettings are stored in a single file named Industries.settings in the settings directory.
```
```
Version
Industries settings for Grantmaking are available in API version 59.0 and later.
```
Grantmaking Grantmaking Metadata API Types


```
Special Access Rules
Unless noted otherwise, these settings are available only if the Grantmaking license is enabled, Grantmaking is enabled, and the Manage
Application system permission is assigned to users.
```
```
Fields
Industries settings for Grantmaking are available in API version 59.0 and later.
```
```
Field Description
Type
```
```
Field Name
```
```
Indicates whether the Compliant Data Sharing feature is enabled for
the Budget object. The default is false. Available only if the
Grantmaking license is enabled and Grantmaking is enabled.
```
```
enableCompliantDataSharingForBudget boolean
```
```
Indicates whether the Compliant Data Sharing feature is enabled for
the Individual Application object. The default is false. Available
only if the Grantmaking license is enabled and Grantmaking is enabled.
```
```
enableCompliantDataSharingForIndividualApplication boolean
```
```
Indicates whether the Compliant Data Sharing feature is enabled for
the Funding Award object. The default is false. Available only if
the Grantmaking license is enabled and Grantmaking is enabled.
```
```
enableCompliantDataSharingForFundingAward boolean
```
```
Indicates whether the Grantmaking feature is enabled. The default
is false. This option can’t be disabled (false) once it’s enabled
```
```
enableGrantmaking boolean
```
```
(true). Only requires that the Grantmaking license is enabled in the
org.
```
```
Declarative Metadata Sample Definition
The following is an example of an Industries.Settings metadata file.
```
```
<?xmlversion="1.0"encoding="UTF-8"?>
<IndustriesSettingsxmlns="http://soap.sforce.com/2006/04/metadata">
<enableGrantmaking>true</enableGrantmaking>
<enableCompliantDataSharingForBudget>true</enableCompliantDataSharingForBudget>
```
```
<enableCompliantDataSharingForIndividualApplication>true</enableCompliantDataSharingForIndividualApplication>
```
```
<enableCompliantDataSharingForFundingAward>true</enableCompliantDataSharingForFundingAward>
</IndustriesSettings>                                                                                                                                       
```
```
The following is an example package.xml that references the previous definition.
```
```
<?xmlversion="1.0"encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
<types>
<members>Industries</members>
<name>Settings</name>
</types>
```
Grantmaking IndustriesSettings


```
<version>54.0</version>
</Package>
```
Grantmaking IndustriesSettings


