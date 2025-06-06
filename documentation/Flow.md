Flow
====

Represents the metadata associated with a flow that encompasses the flow's structure, logic, and run-time behavior. It allows you to build dynamic applications that guide users through interactive screens, automate processes, and connect with various Salesforce and external services. This includes managing data operations like creating, updating, or deleting records, handling complex decisions, looping through collections, and invoking actions like Apex or external services to extend functionality. A flow contains options for API versioning, various execution environments, and detailed configuration of elements to design powerful automation solutions.

Where possible, we changed non-inclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

Here are the limitations related to how you can use Metadata API to work with flows:

*   You can’t use Metadata API to access a flow installed from a managed package unless the flow is a template.
*   Spaces in a flow file name can lead to errors when you deploy the flow. You can include spaces at the beginning or end of a name, but these spaces are removed when you deploy the flow.
*   You can deploy changes to an active flow if in a non-production org, such as a scratch or sandbox org. To deploy changes in a production org, you must enable the **Deploy processes and flows as active** preference. After you deploy changes to an active flow, the flow’s detail page shows a new flow version that’s active. The new version includes your changes.
*   You can delete a flow version if it isn’t active and doesn’t have any paused interviews. If the flow version has paused interviews, wait for those interviews to resume and finish, or delete them.

Don’t edit the metadata of retrieved Process Builder processes, such as flow components whose processType is Workflow or InvocableProcess. If you deploy process metadata that you edited, you can’t open the process in the target org.

Declarative Metadata File Suffix and Directory Location
-------------------------------------------------------

Flows are stored in the Flow directory of the corresponding package directory. The file name matches the flow’s unique full name, and the extension is .flow.

Version
-------

The flow Metadata API is available in API version 24.0 and later.

Flow
----

This metadata type represents a valid definition of a flow. This type extends the [Metadata](/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm "The base class for all metadata types. You can’t edit this object. A component is an instance of a metadata type.") metadata type and inherits its fullName field.

Field Name

Field Type

Description

actionCalls

[FlowActionCall](#FlowActionCall)\[\]

An array of nodes that defines calls to action. This field is available in API version 31.0 and later.

apexPluginCalls

[FlowApexPluginCall](#FlowApexPluginCall)\[\]

An array of nodes that defines calls to Apex plug-ins.

apiVersion

number

The API version that defines the execution behavior of the flow. This field is available in API version 50.0 and later. Flows created before API version 50.0 show an API version of 0 on the Flows list view in Setup. To show the correct API version number, create another version of the flow, and set the API version for running the flow to 49.0 or later.

areMetricsLoggedToDataCloud

boolean

Indicates whether the flow's metrics are logged to Data Cloud. The default value is false. This field is available in API version 63.0 and later.

assignments

[FlowAssignment](#FlowAssignment)\[\]

An array of assignment nodes.

choices

[FlowChoice](#FlowChoice)\[\]

An array of static choice options.

collectionProcessors

[FlowCollectionProcessor](#FlowCollectionProcessor)\[\]

An array of nodes that process collections. This field is available in API version 50.0 and later.

constants

[FlowConstant](#FlowConstant)\[\]

An array of constants.

customErrors

[FlowCustomError](#FlowCustomError)\[\]

An array of custom errors.

customProperties

[FlowCustomProperty](#FlowCustomProperty)\[\]

An array of custom properties that specify flow properties such as the option to show a progress indicator in a screen flow. This field is available in API version 63.0 and later.

decisions

[FlowDecision](#FlowDecision)\[\]

An array of decision nodes.

description

string

Description of the flow.

dynamicChoiceSets

[FlowDynamicChoiceSet](#FlowDynamicChoiceSet)\[\]

An array that constructs a set of choice options based on a database lookup.

environments

FlowEnvironment (enumeration of type string)

The environment in which the flow can run. Valid values are:

*   Default—The flow can run from a Visualforce component, Lightning page, flow action, or custom Aura component.
*   Offline—The flow can run only offline. Flow types that support offline flows must set this value. This value is available in API version 62.0 and later.
*   Slack—The flow can run in Slack and the default environment. You specify the Slack flow environment when you save the flow.

This field is available in API version 55.0 and later.

exitRules

[FlowExitRule](#FlowExitRule)\[\]

An array of exit rules that determine when to end the flow for a user in a segment-triggered flow. This field is available in API version 61.0 and later.

experiments

[FlowExperiment](#FlowExperiment)\[\]

An array of experiments. This field is available in API version 61.0 and later.

formulas

[FlowFormula](#FlowFormula)\[\]

An array of formulas.

fullName

string

Required. Inherited from the Metadata component. Name of the file in Metadata API.

A unique name for the flow that contains only underscores and alphanumeric characters. The name must be unique across the org, begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores.

To deploy or retrieve a version, you can specify the version number. For example, sampleFlow-3 specifies version 3 of the flow whose unique name is sampleFlow. If you don’t specify a version number, the flow is the latest version.

In API version 43.0 and earlier, this field included the version number. In API version 44 and later, this field no longer includes the version number.

interviewLabel

string

Label for the interview. This label helps users and administrators differentiate interviews from the same flow.

In the user interface, this label appears in the Paused Flow Interviews component on the user’s Home tab and in the list of paused flow interviews in Setup.

isAdditionalPermissionRequiredToRun

boolean

Override the default behavior and restrict access to enabled profiles or permission sets by setting this property to true. The default value is false. This field is available in API version 47.0 and later.

isTemplate

boolean

Indicates whether the process or flow is a template. The default value is false. When installed from managed packages, subscribers can’t view or clone processes or flows because of intellectual property (IP) protection. But when those processes and flows are templates, subscribers can open them in a builder, clone them, and customize the clones. This field is available in API version 45.0 and later.

label

string

Required. Label for the flow.

loops

[FlowLoop](#FlowLoop)\[\]

An array of nodes for iterating through collections. This field is available in API version 30.0 and later.

migratedFromWorkflowRuleName

string

The name of the workflow rule that the flow was migrated from. This field is available in API version 54.0 and later.

orchestratedStages

[FlowOrchestratedStage](#subtype_FlowOrchestratedStage)\[\]

An array of stage nodes in an orchestration. This field is available in API version 53.0 and later.

processMetadataValues

[FlowMetadataValue](#FlowMetadataValue)\[\]

Metadata values for the flow.

This field is available in API version 31.0 and later.

processType

FlowProcessType (enumeration of type string)

The type of the flow, as determined by the active version, or the latest version, if there’s no active version. Valid values are:

*   ActionableEventManagementFlow—A flow that triggers an actionable event orchestration process in the background and automatically executes different types of actions based on the event type. This value is available in API version 62.0 and later.
*   ActionCadenceAutolaunchedFlow—A flow that’s executed when a user completes a cadence step. This value is available in API version 56.0 and later.
*   ActionCadenceStepFlow—A screen flow used as a cadence step. This value is available in API version 56.0 and later.
*   ActivityObjectMatchingFlow—A flow that launches when Einstein Activity Capture detects and captures a new activity, such as an email. This type of flow runs in the background without user interaction. This value is available with Sync Email as Salesforce Activity in API version 64.0 and later.
*   Appointments—A flow for Lightning Scheduler. This value is available in API version 44.0 and later.
*   ApprovalWorkflow—An orchestration that’s used for an approval process. This value is available in API version 63.0 and later.
*   AutoLaunchedFlow—A flow that doesn’t require user interaction.
*   CheckoutFlow—A flow used in Lightning B2B Commerce to create a checkout in a store. This value is available in API version 48.0 and later.
*   ContactRequestFlow—A flow that lets customers request to be contacted by customer support. This flow is used to create contact request records. This value is available in API version 45.0 and later.
*   CustomerLifecycle—A Salesforce Surveys flow that lets you associate survey questions with different stages in customer lifecycles. This value is available in API version 49.0 and later and only when the Customer Lifecycle Designer license is enabled.
*   CustomEvent—A process that is invoked when it receives a platform event message. In the UI, it’s an event process. This value is available in API version 41.0 and later.
*   DataCaptureFlow— In the UI, Data Capture flows configure the Form tab in the Field Service mobile app. When the Data Capture flow is launched, its Flow metadata is publicly available in JavaScript format. This value is available in API version 62.0 and later.
*   DcvrFrameworkDataCaptureFlow—A screen flow that presents assessment questions from Discovery Framework. Launches when invoked by a user on a mobile device. This type of flow collects or displays information, requires user interaction, and works offline or online. This value is available in API version 62.0 and later.
*   EvaluationFlow—A flow for evaluating custom entry and exit conditions in an orchestration. Uses the isOrchestrationConditionMet output variable and discards values from any other output variables. This value is available in API version 54.0 and later.
*   FieldServiceMobile—A flow for the Field Service mobile app. This value is available in API version 39.0 and later.
*   FieldServiceWeb—A flow for embedded Appointment Booking. Its UI label is Field Service Embedded Flow. This value is available in API version 41.0 and later.
*   Flow—A flow that requires user interaction because it contains one or more screens or local actions, choices, or dynamic choices. In the UI and Salesforce Help, it’s a screen flow. Screen flows can be launched from the UI, such as with a flow action, Lightning page, or web tab.
*   FSCLending—A flow for Financial Services Cloud Mortgage. This value is available in API version 46.0 and later.
*   IdentityUserRegistrationFlow—A flow to handle user registration and updates for single sign-on with the authentication provider framework. Available in API version 64.0 and later.
*   IndicatorResultFlow—A flow for Outcome Management that calculates and creates indicator results for a selected indicator performance period. This value is available with the Outcome Management license in API version 60.0 and later.
*   IndividualObjectLinkingFlow—A flow that associates individuals with interactions such as voice calls, messaging sessions, or case-related emails. This value is available in API version 58.0 and later.
*   InvocableProcess—A process that another process or the Invocable Actions resource in REST API invokes. This value is available in API version 38.0 and later.
*   Journey—An audience-driven flow for Marketing Cloud. This value is available in API version 57.0 and later.
*   LoginFlow—A flow for login. This value is available in API version 51.0 and later.
*   LoyaltyManagementFlow—A flow for the Loyalty Management app that’s invokable by loyalty program processes. This value is available in API version 54.0 and later.
*   Orchestrator—An orchestration that organizes flows into groups of steps contained in a series of stages. This value is available in API version 53.0 and later.
*   PromptFlow—A flow for Prompt Builder. Pass data between Prompt Builder and the flow. This value is available in API version 60.0 and later.
*   RecommendationStrategy—Build recommendations for your users. A recommendation launches its assigned flow. This value is available in API version 54.0 and later. See [Flow Builder Strategies](https://help.salesforce.com/s/articleView?id=sf.nba_building_flow_builder_strategy.htm&language=en_US "HTML (New Window)").
*   RoutingFlow—A flow for Salesforce Omni-Channel routing and other business logic. This value is available in API version 52.0 and later.
*   Survey—A flow for Salesforce Surveys. From the UI, this type of flow is created in Survey Builder. This value is available in API version 42.0 and later.
*   SurveyEnrich—A Salesforce Surveys flow that uses the Survey Data Mapper. From the UI, this type of flow is created in the Survey Builder and requires an associated survey flow type. This value is available in API version 49.0 or later and only when the Customer Lifecycle Designer license is enabled.
*   Workflow—A process that is invoked when a record is created or edited. In the UI and Salesforce Help, it’s a record change process.

Across flow versions, you can change the type only from Flow to AutoLaunchedFlow or vice versa. Before you change the flow type, make sure that the flow contains only the elements, resources, and functionality that the new flow type supports.

These values are reserved for future or Salesforce internal use.

*   ActionCadenceFlow
*   ActionPlan
*   AppProcess
*   ApprovalWorkflow
*   CartAsyncFlow
*   DigitalForm
*   JourneyBuilderIntegration
*   LoginFlow
*   ManagedContentFlow
*   OrchestrationFlow
*   SalesEntryExperienceFlow
*   TransactionSecurityFlow
*   UserProvisioningFlow

This field is available in API version 31.0 and later.

recordCreates

[FlowRecordCreate](#FlowRecordCreate)\[\]

An array of nodes for creating records in the database.

recordDeletes

[FlowRecordDelete](#FlowRecordDelete)\[\]

An array of nodes for deleting records in the database.

recordLookups

[FlowRecordLookup](#FlowRecordLookup)\[\]

An array of nodes for looking up records in the database.

recordRollbacks

[FlowRecordRollback](#FlowRecordRollback)\[\]

An array of nodes for rolling back transactions in the screen flow. This field is available in API version 52.0 and later.

recordUpdates

[FlowRecordUpdate](#FlowRecordUpdate)\[\]

An array of nodes for updating records in the database.

runInMode

FlowRunInMode (enumeration of type string)

The context that the flow runs in. Valid values are:

*   DefaultMode—How the flow is launched determines whether the flow runs in user context or in system context. In the UI, this value appears as **User or System Context—Depends on How Flow is Launched**.
*   SystemModeWithSharing—The flow respects org-wide default settings, role hierarchies, sharing rules, manual sharing, teams, and territories. The flow doesn’t respect object permissions, field-level access, or other permissions of the running user. In the UI, this value appears as **System Context with Sharing—Enforces Record-Level Access**.
*   SystemModeWithoutSharing—The flow can access all data. In the UI, this value appears as **System Context without Sharing—Access All Data**. This value is available in API version 49.0 and later.

This field is available in API version 48.0 and later.

screens

[FlowScreen](#FlowScreen)\[\]

An array of screen nodes.

segment

string

Reserved for future use.

stages

[FlowStage](#FlowStage)\[\]

An array of stage resources that you can use throughout the flow. This field is available in API version 42.0 and later.

start

[FlowStart](#FlowStart)\[\]

The flow’s Start element, which specifies how and when the flow starts. This field is available in API version 47.0 and later.

startElementReference

string

Specifies which node or element is the starting point in the flow.

This field isn’t used in flows created or saved in Flow Builder in Winter ’20 and later. Those flows use the start field instead to specify how the flow starts.

status

FlowVersionStatus (enumeration of type string)

The activation status of the flow. Valid values are:

*   Active
*   Draft—In the UI, this status appears as Inactive.
*   Obsolete—In the UI, this status appears as Inactive.
*   InvalidDraft—In the UI, this status appears as Draft.

steps

[FlowStep](#FlowStep)\[\]

An array of step nodes.

subflows

[FlowSubflow](#FlowSubflow)\[\]

An array of subflows. This field is available in API version 25.0 and later.

textTemplates

[FlowTextTemplate](#FlowTextTemplate)\[\]

An array of text templates.

timeZoneSidKey

string

The ID that defines the time zone in which the flow runs. This field is available in API version 56.0 and later.

transforms

[FlowTransform](#FlowTransform)\[\]

An array of data transformations. This field is available in API version 59.0 and later.

triggerOrder

int

The run order of a record-triggered flow, from 1 to 2,000. See [Guidelines for Defining the Run Order of Record-Triggered Flows for an Object](https://help.salesforce.com/s/articleView?id=flow_concepts_trigger_guidelines.htm&type=5&language=en_US "HTML (New Window)") in Salesforce Help. This field is available in API version 54.0 and later.

variables

[FlowVariable](#FlowVariable)\[\]

An array of variable definitions.

waits

[FlowWait](#FlowWait)\[\]

An array of wait nodes. This field is available in API version 32.0 and later.

FlowActionCall
--------------

Defines a call to an action from the flow. It extends [FlowNode](#FlowNode).

This metadata type is available in API version 31.0 and later.

Field Name

Field Type

Description

actionCallPaths

[ActionCallPath](#FlowStep)\[\]

Reserved for future use.

actionName

string

Required. Name for the action. Must be unique across actions with the same actionType.

actionType

InvocableActionType (enumeration of type string)

Required. The action type. Valid values are:

*   activateSessionPermSet—Activates a session-based permission set for the running user.
*   addMessageToChat—Adds a message to an existing Salesforce Anywhere chat. This value is available in API version 49.0 and later.
*   addMessageToQuipChat—Adds a Quip message to an existing chat room. This value is available in API version 46.0 and later.
*   addMessageToQuipDocument—Adds a Quip message to an existing Quip document, spreadsheet, or slide. This value is available in API version 46.0 and later.
*   addQuipDocumentToFolder—Adds an existing Quip document, spreadsheet, or slide to an existing folder. This value is available in API version 46.0 and later.
*   addUsersToChat—Adds users to an existing Salesforce Anywhere chat. This value is available in API version 49.0 and later.
*   addUsersToQuipDocument—Adds users, identified by their email addresses, to an existing Quip document, spreadsheet, or slide. This value is available in API version 46.0 and later.
*   addUsersToQuipChat—Adds users, identified by their email addresses, to an existing Quip chat room. This value is available in API version 46.0 and later.
*   answerQuestionsWithSalesforceDocumentation—Searches Salesforce documentation to provide answer to questions, as well as links to relevant articles.
*   analyticsSendDigestAsSlackMsg—Sends an Analytics digest to a Slack channel. This value is available in API version 64.0 and later.
*   attachQuipDocumentToRecord—Attaches a Quip document, spreadsheet, or slide to a Salesforce record. This value is available in API version 46.0 and later.
*   apex—Invokes an Apex method that has the @invocableMethod annotation.
*   archiveKnowledgeArticles—Archives a list of published Knowledge articles. This value is available in API version 45.0 and later.
*   assignKnowledgeArticles—Mass assigns knowledge articles from article list views. This value is available in API version 44.0 and later.
*   automateRefund—Initiate a refund to the customer. This value is available in API version 60.0 and later.
*   buildIdentityVerification—Calls an action that builds the identity verification context using the identity verification process definition specified in IdVerfProcessDefinition and information passed into the flow. Stores the result in the VerificationContext variable. This value is available in API version 55.0 and later.
*   cdpPublishCalculatedInsight—Run the calculated insight in Data Cloud. Available in API version 60.0 and later.
*   cdpPublishSegment—Publish a segment in Data Cloud. Available in API version 60.0 and later.
*   cdpRefreshDataStream—Refresh a data stream in Data Cloud. Available in API version 60.0 and later.
*   cdpRunIdentityResolution—Runs a Data Cloud identity resolution process. This value is available in API version 57.0 and later.
*   chat—Creates a Salesforce Anywhere chat. This value is available in API version 49.0 and later.
*   chatterPost—Posts to Chatter.
*   choosePricebook—Selects a price book.
*   contactRequestAction—Creates a contact request record. This value is available in API version 45.0 and later.
*   component—Invokes the Lightning component that implements the lightning:availableForFlowActions interface and that is referenced by actionName. This value is available in API version 43.0 and later.
*   contentWorkspaceEnableFolders—Enables folders in a library.
*   copyQuipDocument—Creates a copy of an existing Quip document, spreadsheet, or slide, and gives it a new title. This value is available in API version 46.0 and later.
*   createDraftFromOnlineKnowledgeArticle—Creates a draft from a published knowledge article. This value is available in API version 45.0 and later.
*   createFieldGnrnPromptTmplResp—Creates a field generation prompt template response. This value is available in API version 62.0 and later.
*   createInvoiceFromFulfillmentOrder—Creates an invoice from a purchase order. Available to B2B Commerce. This value is available in API version 49.0 and later.
*   createQuipChat—Creates a Quip chat room. This value is available in API version 46.0 and later.
*   createQuipDocument—Creates a Quip document, spreadsheet, or slide. This value is available in API version 46.0 and later.
*   createQuipFolder—Creates a Quip folder. This value is available in API version 46.0 and later.
*   customNotificationAction—Sends a custom notification. This value is available in API version 46.0 and later.
*   dataCloudIngestionApi—Send data to Data Cloud using Ingestion API. This value is available in API version 61.0 and later.
*   deactivateSessionPermSet—Deactivates a session-based permission set for the running user.
*   deleteKnowledgeArticle—Deletes a draft version (translation or master-language) or an entire archived knowledge article. This value is available in API version 46.0 and later.
*   dynamicSendSurveyInvitation—Sends customized notifications to users about important events or updates to the records that they’re working on. This value is available in API version 51.0 and later.
*   editQuipDocument—Modifies the contents of an existing Quip document, spreadsheet, or slide. This value is available in API version 46.0 and later.
*   einsteinDecidePath—Determines a user's level of email engagement using Einstein Engagement Frequency or Einstein Engagment Scoring, and route users through the flow based on that engagement. This value is available in API version 64.0 and later.
*   emailAlert—Sends an email by referencing a workflow email alert
*   emailSimple—Sends an email by using flow resources
*   exploreConversation—Retrieves insights from a conversation. This value is available in API version 61.0 and later.
*   externalConnector—Executes a process or method exposed via a connector to an external system. This value is available in API version 63.0 and later.
*   externalService—Invokes an External Service operation that makes an HTTP request to an external system made available by an External Service schema registered through Setup. This value is available in API version 46.0 and later.
*   findMatchingIndividuals—Finds contact, lead, or employee records that match a search term.
*   flow—Invokes an autolaunched flow. This action type isn’t available for flows with a processType of Flow or AutolaunchedFlow. To invoke an autolaunched flow from one of those types, use FlowSubflow. This value is available in API version 32.0 and later.
*   generateAiAgentResponse—Generates a response from the AI agent based on input and instructions to support intelligent, conversational experiences. This value is available in API version 63.0 and later.
*   generateAnalyticsAssetsContent—Generates Analytics assets content. This value is available in API version 64.0 and later.
*   generateVerificationCode—Sends a verification code to the customer's email to verify their identity. This value is available in API version 63.0 and later.
*   getActivitySummary—Gets a summary of activity data associated with a specified record, including emails, calls, and meetings. This value is available in API version 60.0 and later.
*   getArticleSmartLinkUrl—Gets the Smart Link URL of the Salesforce Knowledge article. Smart links go to the right article and version, even when a new version is published or the URL name changes. This value is available in API version 54.0 and later.
*   getResourcesForMnlScheduling—Recommends resources to use to manually schedule the start of a care visit or recurring visits. You must enable Home Health to use this action. This value is available in API version 61.0 and later.
*   getVerificationData—Calls an invocable action to get verification data for selectedPrimaryVerificationContext and adds the results to selectedPrimaryVerificationContext. This value is available in API version 54.0 and later.
*   goToCadenceStep—Jumps to the specified step in the Sales cadence. This value is available in API version 57.0 and later.
*   internalTestAction—Reserved for internal use.
*   internalTestConnectApiAction—Reserved for internal use.
*   limitRepetitions—Limit the number of times the same recommendation or offer appears on the same record or for the same user during a time period in a recommendation strategy flow. This value is available in API version 55.0 and later.
*   lockRecord—Lock or unlock a workflow-enabled or approval-enabled record for editing during an approval and specify who can edit the record while it's locked.
*   massUpdateAccountForecast—Bulk updates forecasts asynchronously. This value is available in API version 48.0 and later.
*   massUpdateSalesAgreement—Bulk updates sales agreements asynchronously. This value is available in API version 48.0 and later.
*   processDataUsingGenAi—Using Einstein generative AI, performs NLP to summarize text, extract key phrases, analyze sentiment, and unlock valuable insights. This value is available in API version 61.0 and later.
*   publishActionableOrchSrcEvent—Publishes events triggered by an external system. This value is available in API version 62.0 and later.
*   publishKnowledgeArticles—Mass publishes knowledge articles from article list views. This value is available in API version 44.0 and later.
*   quickAction—Invokes a [QuickAction](/docs/atlas.en-us.api_meta.meta/api_meta/meta_quickaction.htm "Represents a specified create or update quick action for an object that then becomes available in the Chatter publisher. For example, you can create an action that, on the detail page of an account, allows a user to create a contact related to that account from the Chatter feed on that page. QuickAction can be created on objects that permit custom fields.").
*   rescheduleRecurringHomeVisits—Reschedules all the home visits based on the recurrence pattern and scheduling policy provided. This value is available in API version 60.0 and later.
*   restoreKnowledgeArticleVersion—Restores an archived version of a knowledge article. This value is available in API version 45.0 and later.
*   scheduleGroupVisits—Create visiting records for patient home visits by bundling them into a group and scheduling either a single start-of-care visit or a series of recurring visits associated with the bundled records. This value is available in API version 60.0 and later.
*   sendAlert—Sends Salesforce Anywhere alerts to users. This value is available in API version 49.0 and later.
*   sendNotification—Sends an available notification type. This value is available in API version 54.0 and later.
*   sendSurveyInvitation—Sends email survey invitations to leads, contacts, and users in your org based on an action, such as when a customer support case closes. This value is available in API version 47.0 and later.
*   pardotSlackCompletionActionNotification—Sends a user a Slack notification when a prospect completes an activity in Account Engagement.
*   performSurveySentimentAnalysis—Perform survey sentiment analysis to create or update the AI Sentiment Result records. This value is available in API version 55.0 and later.
*   processDataUsingGenAi—Using Einstein Generative AI, perform Natural Language Processing (NLP) to summarize text, extract key phrases, analyze sentiment, and unlock valuable insights. This value is available in API version 61.0 and later.
*   skillsBasedRouting—Creates a [PendingServiceRouting](https://developer.salesforce.com/docs/atlas.en-us.256.0.object_reference.meta/object_reference/sforce_api_objects_pendingservicerouting.htm "HTML (New Window)") record used for Omni-Channel skills-based routing. This value is available in version 44.0 and later.
*   slackArchiveChannel—Archives a Slack channel in a Slack workspace. This value is available in API version 54.0 and later.
*   slackCheckUsersAreConnectedToSlack—Indicates whether a collection of Salesforce users is connected to a given Slack app. This value is available in API version 54.0 and later.
*   slackCreateChannel—Creates a Slack channel in a Slack workspace. This value is available in API version 54.0 and later.
*   slackGetConversationInfo—Retrieves the name of a Slack channel or group direct message and finds out whether it’s archived. This value is available in API version 54.0 and later.
*   slackInviteUsersToChannel—Adds users who are connected to a given Slack app to a Slack channel or group direct message. This value is available in API version 54.0 and later.
*   slackPinMessage—Pin or unpin a message in a Slack channel or group direct message. This value is available in API version 54.0 and later.
*   slackPostMessage—Send a message to a Slack channel or group direct message. This value is available in API version 54.0 and later.
*   slackSendMessageToLaunchFlow—Send a message to a Slack channel, direct message, or the Messages tab of a Slack app that includes a button that a recipient can use to launch a screen flow. This value is available in API version 55.0 and later.
*   slackUpdateMessage—Edits a message that was previously sent to a Slack channel or group direct message. This value is available in API version 54.0 and later.
*   submitKnowledgeArticleForTranslation—Submits a published or draft knowledge article for translation. This value is available in API version 46.0 and later.
*   submit—Submits a record for approval.
*   transformNlpActionResult—Transform an AI Natural Language Processing (NLP) result created by using Einstein Generative AI into an Apex Object record. This value is available in API version 61.0 and later.
*   verifyCustomerCode—Verifies the code entered by the customer to complete identity verification. This value is available in API version 63.0 and later.

These values are used in Omnichannel Inventory. If no version is specified, the value is available in API version 51.0 and later.

*   ociCreateReservation—Creates one or more inventory reservations at a location or location group.
*   ociFulfillReservation—Fulfills one or more inventory reservations at a location.
*   ociGetAvailability—Gets inventory availability data for one or more products at one or more inventory locations or location groups.
*   ociReleaseReservation—Releases one or more inventory reservations.
*   ociTransferReservation—Transfers one or more inventory reservations between locations or location groups.

These values are used in the B2B Commerce Checkout Flow. If no version is specified, the value is available in API version 47.0 and later.

*   updateCheckoutSessionStateAction—Updates the checkout session next state for checkout flows. This value is available in API version 49.0 and later.
*   priceCart—Requests prices for all items in a cart during B2B Commerce checkout. This value is available in API version 47.0 and later.
*   checkoutSessionAction—Initiates or retrieves an existing Checkout Session for Checkout Flows. Available to B2B Commerce. This value is available in API version 49.0 and later.
*   cancelCartAsyncOperation—Cancels a WebCart’s async operation. Available to B2B Commerce. This value is available in API version 49.0 and later.
*   calcCartPromotionsAction—Requests a full cart promotion calculation of all applicable line items in the Web Cart during B2B Commerce checkout. This value is available in API version 52.0 and later.
*   checkCartInventoryAction—Requests an inventory for all items in a Web Cart during B2B Commerce checkout. This value is available in API version 47.0 and later.
*   calcCartShipmentAction—Calculates the shipping cost for all items in a Web Cart during B2B Commerce checkout. This value is available in API version 47.0 and later.
*   cartToOrderAction—Creates a Salesforce Standard Order in draft mode. This value is available in API version 47.0 and later.
*   activateOrderAction—Activates a draft order, which creates an order summary. This value is available in API version 47.0 and later.

These values are used in the B2B Commerce and D2C Commerce.

*   recordTaxReversal—Reverses the recorded tax transactions in an external system. This value is available in API version 62.0 and later.
*   recordTaxTransaction—Records tax transactions from an order summary to an external system. This value is available in API version 62.0 and later.

For values used in Business Rules Engine, see [Flow for Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.256.0.industries_reference.meta/industries_reference/bre_flow_metadata_api.htm "HTML (New Window)").

These values are used in the Commerce Checkout Flow. If no version is specified, the value is available in API version 55.0 and later.

*   addCartItem—Adds an item to a cart during Commerce checkout.
*   createCart—Creates a cart during Commerce checkout.
*   deleteCart—Deletes a cart during Commerce checkout.

These values are used in Salesforce CMS Workflows and Approvals. If no version is specified, the value is available in API version 58.0 and later.

*   managedContentPublishVariant—Publishes a content variant associated with a flow. This value is available in API version 59.0 and later.
*   managedContentRoleStepInteractive—Assigns a content variant review to a CMS role.
*   managedContentUnpublishVariant—Unpublishes a published content variant associated with a flow. This value is available in API version 59.0 and later.
*   managedContentVariantSetLockStatus—Sets the locked status of a content variant.
*   managedContentVariantSetReadyStatus—Sets the ready for publication status of a content variant.

For values used in Digital Lending, see [Flow for Digital Lending.](https://developer.salesforce.com/docs/atlas.en-us.256.0.industries_reference.meta/industries_reference/digital_lending_flow_metadata_api.htm "HTML (New Window)")

These values are used in Order Management. If no version is specified, the value is available in API version 48.0 and later.

*   addOrderItemSummarySubmit—Adds order item summaries to an order summary. This value is available in API version 54.0 and later.
*   adjustOrderItemSummariesPreview—Previews the expected results of applying a price adjustment to order item summaries from an order summary without actually applying it. This value is available in API version 49.0 and later.
*   adjustOrderItemSummariesSubmit—Applies a price adjustment to order item summaries from an order summary. This value is available in API version 49.0 and later.
*   authorizePayment—Authorizes a card payment. This value is available in API version 55.0 and later.
*   cancelFulfillmentOrderItem—Removes items from a fulfillment order.
*   cancelOrderItemSummariesPreview—Previews the expected results of canceling order item summaries from an order summary without actually canceling them.
*   cancelOrderItemSummariesSubmit—Cancels order item summaries from an order summary.
*   confirmHeldFulfillmentOrderCapacity—Confirms held fulfillment order capacity. This value is available in API version 55.0 and later.
*   createCreditMemoOrderSummary—Creates a credit memo for an order summary.
*   createFulfillmentOrder—Creates one or more fulfillment orders and fulfillment order products for an order delivery group summary, which defines a recipient and delivery method.
*   createFulfillmentOrders—Creates fulfillment orders and fulfillment order products for multiple order delivery group summaries, each of which defines a recipient and delivery method. This value is available in API version 51.0 and later.
*   createInvoiceFromChangeOrders—Creates an invoice for one or more change orders. This value is available in API version 56.0 and later.
*   createInvoiceFromFulfillmentOrder—Creates an invoice for a fulfillment order.
*   createOrderPaymentSummary—Creates an order payment summary for an authorization or payments belonging to an order summary.
*   createOrderSummary—Creates an order summary for an order.
*   createReturnOrder—Creates a return order and return order items for an order.
*   ensureFundsOrderSummaryAsync—Triggers an asynchronous background process to ensure funds through a payment provider for an invoice belonging to an order summary.
*   ensureRefundsOrderSummaryAsync—Triggers an asynchronous background process to ensure refunds through a payment provider for an invoice belonging to an order summary.
*   getFulfillmentOrderCapacityValues—Gets fulfillment order capacity information. This value is available in API version 55.0 and later.
*   holdFulfillmentOrderCapacity—Holds fulfillment order capacity. This value is available in API version 55.0 and later.
*   orderRoutingFindRoutesWithFewestSplits—Evaluates ordered product quantities against available inventory to determine the smallest combination of locations that can fulfill the order. This value is available in API version 51.0 and later.
*   orderRoutingFindRoutesWithFewestSplitsUsingOCI—Evaluates ordered product quantities against available inventory at specified location groups and locations to determine the smallest combination of locations that can fulfill the order. This value is available in API version 54.0 and later.
*   orderRoutingRankByAverageDistance—Calculates the average distance from sets of inventory locations to an order recipient, and returns the sets sorted by that average distance. This value is available in API version 51.0 and later.
*   releaseHeldFulfillmentOrderCapacity—Releases held fulfillment order capacity. This value is available in API version 55.0 and later.
*   returnOrderItemSummariesPreview—Previews the expected results of returning order item summaries from an order summary without actually returning them.
*   returnOrderItemSummariesSubmit—Returns order item summaries from an order summary.
*   returnReturnOrderItems—Processes return order line items.

For values used in Financial Services Cloud, see [Flow for Financial Services Cloud](https://developer.salesforce.com/docs/atlas.en-us.256.0.financial_services_cloud_object_reference.meta/financial_services_cloud_object_reference/fsc_meta_visual_workforce.htm "HTML (New Window)").

For values used in Fundraising for Nonprofit Cloud, see Flow for Fundraising.

For values used in Health Cloud, see [Flow for Health Cloud](https://developer.salesforce.com/docs/atlas.en-us.256.0.health_cloud_object_reference.meta/health_cloud_object_reference/health_cloud_flow_metadata_api.htm "HTML (New Window)").

For values used in Insurance Brokerage, see [Flow for Insurance Brokerage](https://developer.salesforce.com/docs/atlas.en-us.256.0.insurance_developer_guide.meta/insurance_developer_guide/insurance_brokerage_flow_metadata_api.htm "HTML (New Window)").

For values used in Insurance Policy Administration, see [Flow for Insurance Policy Administration](https://developer.salesforce.com/docs/atlas.en-us.256.0.insurance_developer_guide.meta/insurance_developer_guide/insurance_policy_administration_flow_metadata_api.htm "HTML (New Window)").

For values used in Life Sciences Cloud, see [Flow for Life Sciences Cloud](https://developer.salesforce.com/docs/atlas.en-us.256.0.life_sciences_dev_guide.meta/life_sciences_dev_guide/life_sciences_flow_metadata_api.htm "HTML (New Window)").

For values used in Manufacturing Cloud, see [Flow for Manufacturing Cloud](https://developer.salesforce.com/docs/atlas.en-us.256.0.mfg_api_devguide.meta/mfg_api_devguide/mfg_flow_metadata_api.htm "HTML (New Window)").

These values are used in Rebate Management.

*   addRebateMemberList—Adds a list of members to a rebate program. This value is available in API version 51.0 and later.
*   calculateProjectedRebateAmount—Calculates the projected rebate amount for rebate types associated with a specified transaction ID. This value is available in API version 54.0 and later.
*   calculateRebateAmountAndUpsertPayout—Calculates the rebate amount and upserts the rebate payout for the specified aggregate record. This value is available in API version 51.0 and later.
*   getBenefitAndCalculateRebateAmount— Gets benefit details, and optionally calculates the rebate amount for the specified aggregate record. This value is available in API version 51.0 and later.
*   getEligibleProgramRebateTypes—Retrieves the eligible program rebate types for a mapped object. This value is available in API version 52.0 and later.
*   generateRebatePayoutPeriods—Generates payout periods for a rebate program based on the frequency specified in the program. This value is available in API version 51.0 and later.
*   processRebatesBatchCalculationJob—Processes a rebate batch calculation job from the Data Processing Engine. This value is available in API version 51.0 and later.
*   processProgramRebateTypeProducts—Insert or delete records in the Program Rebate Type Product object. This value is available in API version 53.0 and later.
*   rebatesProcessCSV—Processes an uploaded CSV file using Bulk API 2.0 and converts the file’s data into records in the target object. This value is available in API version 51.0 and later.
*   upsertCustomRebatePayout—Upserts the custom calculated rebate payout for the specified aggregate record. This value is available in API version 51.0 and later.

For values used in Referral Marketing, see Flow for Referral Marketing.

These values are used in Loyalty Management.

*   adjustPoints—Adjusts loyalty points for a specified program member or journal transaction. This value is available in API version 51.0 and later.
*   assignTierBenefits— Assigns Member Benefits to a member tier for benefits that are associated with a Benefit Action. This value is available in API version 51.0 and later.
*   cancelAccrual—Cancels a specific set of accrual transactions.
*   creditPoints—Credits loyalty points to a specified program member’s balance. This value is available in API version 51.0 and later.
*   cancelRedemption—Reverts a specific set of redemption transactions. This value is available in API version 51.0 and later.
*   changeTier—Changes the tier for a specified program member. This value is available in API version 51.0 and later.
*   changeTierWhenNoErrors—Changes tier for a specified loyalty program member only when all the input parameters meet the criteria. This value is available in API version 51.0 and later.
*   debitPoints—Debits loyalty points to a specified program member’s balance. This value is available in API version 51.0 and later.
*   executeMemberBenefit—Processes the benefit action associated with the benefit, which is assigned to a loyalty program member. This value is available in API version 51.0 and later.
*   generateMemberReferralCode—Generates a unique 8-character referral code for a loyalty program member. This value is available in API version 57.0 and later.
*   getMemberActiveSegments—Retrieve active Data Cloud market segments that a loyalty program member is a part of.
*   getTier—Gets the current tier for a specified program member. This value is available in API version 51.0 and later.
*   getPointsBalance—Gets the loyalty points balance for a specified program member. This value is available in API version 51.0 and later.
*   getLoyaltyPromotion—Gets active loyalty promotions based on a transaction journal. This value is available in API version 53.0 and later.
*   getLoyaltyPromotionBasedOnSalesforceCDP—Gets promotions for a member based on the market segment the member belongs to. This value is available in API version 53.0 and later.
*   issueVoucher—Issues a voucher for a member or contract. This value is available in API version 51.0 and later.
*   mergeLoyaltyProgramMembership—Merges two active loyalty program member records that both belong to the same loyalty program. This value is available in API version 56.0 and later.
*   transferMemberPointsToGroups—Transfers points from an individual member or a corporate member to the member’s associated group. This value is available in API version 53.0 and later.
*   updateProgressForCumulativePromotionUsage—Updates the progress a member has made towards attaining a cumulative type promotion. This value is available in API version 53.0 and later.
*   unmergeLoyaltyProgramMembership—Unmerges loyalty program member records that have a Merged status. The action unmerges memberships in the Merged status from the previously merged membership. This value is available in API version 56.0 and later.
*   runProgramProcess—Triggers an active loyalty program process. This value is available in API version 56.0 and later.
*   runProgramProcessForTransactionJournal—Triggers an active loyalty program process whose process type is TransactionJournal. This value is available in API version 54.0 and later.

These values are for Decision Table.

*   decisionTableAction—Runs an active decision table definition. This value is available in API version 51.0 and later.
*   refreshDecisionTable—Refreshes the decision table cache. This value is available in API version 51.0 and later.

These values are for the Batch Management jobs.

*   batchJobAction—Runs the batch management jobs definitions. This value is available in API version 51.0 and later.
*   submitFailedRecordsBatchJob—Resubmits an existing batch job with failed records for processing. This value is available in API version 52.0 and later.

This value is for Data Processing Engine.

*   dataProcessingEngineAction—Runs the data processing engine definitions. This value is available in API version 51.0 and later.

This value is used for Einstein Visit Recommendation.

*   saveRecommendationDecision—Save visit and task recommendation decisions. This value is available in API version 51.0 and later.

These values are used in flows for Engagement.

*   createEngagementsDetailsRep—Creates a JSON representation. Use the details of Engagement Interaction, Messaging Session, and Voice Call records; the related Engagement Topic and Note records; and transcripts to create the representation.
*   getConversationTranscripts—Gets the list of transcripts of the conversations between an agent and a customer.
*   getEngagements—Gets engagement interaction, messaging session, and voice call records associated with a specified account record.
*   getRecordDetails—Gets the details of specified records, including the name of the parent record.

These values are used in Field Service. If no version is specified, the value is available in API version 52.0 and later.

*   addWorkPlans—Creates work plan and work step objects from the work plan library.
*   addWorkSteps—Creates work step objects from the work plan library.
*   deleteWorkPlans—Deletes all the work plans and work steps associated with a work order or work order line item.
*   generateWorkPlans—Generates work plans based off rules defined in the work plan library.

For values used in Intelligent Form Reader, see Flow for Intelligent Form Reader.

For values used in Intelligent Document Reader, see Flow for Intelligent Document Reader.

This value is used in Public Sector Solutions.

*   createBenefitDisbursement—Creates a benefit disbursement for an eligible benefit assignment. This value is available in API version 57.0 and later.
*   runRecordAggrBatchProcDef—Runs a Data Processing Engine definition to process an asynchronous batch job that creates or updates record aggregation results. This value is available in API version 59.0 and later.

For values used in Net Zero Cloud, see Flow for Net Zero Cloud.

For values used in Asset Lifecycle, see [Flow for Asset Lifecycle](https://developer.salesforce.com/docs/atlas.en-us.256.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/asset_lifecycle_flow_metadata_api.htm "HTML (New Window)").

For values used in Salesforce Pricing, see [Flow for Salesforce Pricing](https://developer.salesforce.com/docs/atlas.en-us.256.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/pricing_flow_metadata_api.htm "HTML (New Window)").

For values used in Dynamic Revenue Orchestrator, see [Flow for Dynamic Revenue Orchestrator](https://developer.salesforce.com/docs/atlas.en-us.256.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_flow_metadata_api.htm "HTML (New Window)").

For values used in Product Discovery, see [Flow for Product Discovery](https://developer.salesforce.com/docs/atlas.en-us.256.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_discovery_flow_metadata_api.htm "HTML (New Window)").

For values used in Rate Management, see [Flow for Rate Management](https://developer.salesforce.com/docs/atlas.en-us.256.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rate_management_flow_metadata_api.htm "HTML (New Window)").

For values used in Quote and Order Capture, see [Flow for Quote and Order Capture](https://developer.salesforce.com/docs/atlas.en-us.256.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/qoc_flow_metadata_api.htm "HTML (New Window)").

For values used in Billing, see [Flow for Billing](https://developer.salesforce.com/docs/atlas.en-us.256.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_flow_metadata_api.htm "HTML (New Window)").

For values used in Usage Management, see [Flow for Usage Management](https://developer.salesforce.com/docs/atlas.en-us.256.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/usage_management_flow_metadata_api.htm "HTML (New Window)").

This value is used in Einstein generative AI features.

*   generatePromptResponse—Generates a response based on the large language model (LLM) response for the specified prompt template and inputs. This value is available in API version 60.0 and later.

These values are used in Einstein Bots. If no version is specified, the value is available in API version 56.0 and later.

*   getDataCategoryDetails—Gets the labels and API names for a specified data category associated with the Knowledge object and its child categories.
*   getDataCategoryGroups—Gets the labels and API names of the active data category groups associated with the Knowledge object that’s visible to the current user.
*   searchKnowledgeArticles—Searches for knowledge articles with specified search terms, language, data category group, and data category.

These values are reserved for future use.

*   thanks
*   metricRefresh
*   exportSurveyResponses
*   rpa

This value is used for Einstein Initiate Language Processing Action.

*   initiateNaturalLangProcessing—Create a record for the AI natural language processing result and initiate text processing by using the service specified in the related record. This value is available in API version 60.0 and later.

These value are used in Einstein Work summaries.

*   getCaseInfoToSummarize—Gets case field details like subject, description, comments, emails, and conversation transcripts for use with prompt templates in Prompt Studio. This value is available in API version 63.0 and later.
*   getConvTrscpForRecord—Gets the conversation transcript associated with a VoiceCall, MessagingSession, or LiveChatTranscript record. This value is available in API version 63.0 and later.

This value is used in Media Cloud.

*   vlocity\_cmt\_\_MediaIntegrationProcedureInvocable—Call an Integration Procedure from a Salesforce Flow to process media content. This value is available in API version 60.0 and later.

These values are used in the Get Forecast Guidance flow.

*   getForecastContext— Gets the forecast context for a specified user. This value is available in API version 61.0 and later.
*   getForecastOpportunities — Gets forecast opportunities for a user that matches the specified criteria. This value is available in API version 61.0 and later.

This value is used in the Get Opportunity Details flow.

*   getRecPrioData— Gets the record data and field metadata required to prioritize records. This value is available in API version 62.0 and later.

This value is used in Einstein Case Classification flow.

*   applyCaseClassificationRecommendations—takes a Case ID as input and outputs a case SObject with recommendations applied. This value is available in API version 57.0 and later.

These values are used in the Activities: Match Email to Records flow. Sync Email as Salesforce Activity must be enabled.

*   associateRecordsWithActivity—Updates the specified email message to associate it with specified account, contact, lead, opportunity, and user records. This value is available in API version 63.0 and later.
*   getAcctOpptyFromEmailAddr—Gets an account record associated with one of the specified contacts or unmatched email addresses and also gets an opportunity record related to the account. This value is available in API version 63.0 and later.
*   getContcLeadsFromEmailAddr—Matches email addresses to contact and lead records related to specified active user records. This value is available in API version 63.0 and later.
*   getUsersFromEmailAddresses—Gets user records with email addresses that match those specified in the To, From, or CC address field after a sent email is captured by Einstein Activity Capture. This value is available in API version 63.0 and later.

These values are used in the Identity User Registration flow.

*   generateUserData—Generates placeholder user data for the fields that are required to create a user. Available in API version 64.0 and later.
*   getUserDataFromJsonString—Gets an attribute value from a JSON object that has been serialized into a string. Use this action to retrieve user information from the identity provider's ID token and user info response. Available in API version 64.0 and later.

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after this action call.

dataTypeMappings

[FlowDataTypeMapping](#FlowDataTypeMapping)\[\]

An array of data type mappings for input and output values that have the generic sObject data type. This field is available in API version 48.0 and later.

einsteinDecidePath

string

Reserved for future use.

faultConnector

[FlowConnector](#FlowConnector)

Specifies which node to execute if the action call results in an error.

flowTransactionModel

FlowTransactionModel (enumeration of type string)

Required. Specifies the transactional model for flows that execute invocable actions. Valid values are:

*   Automatic— Creates a transaction if the invocable action supports it and there’s pending DML.
*   CurrentTransaction— Keeps the invocable action running in the same transaction.
*   NewTransaction— Creates a transaction before the invocable action is executed.

This field is available in API version 51.0 and later.

inputParameters

[FlowActionCallInputParameter](#FlowActionCallInputParameter)\[\]

An array of input parameters from the flow to the action.

isWaitUntilCompleted

boolean

Specifies whether to pause the flow until the action is completed. This field is available in API version 61.0 and later.

nameSegment

string

Specifies the name of the versioned action. Supported only when nameSegment is specified. This field is available in API version 58.0 to 61.0. This field is deprecated in API version 62.0 and later.

offset

int

Specify the number of months, days, hours, or minutes to pause the flow while it waits for the action to be completed. This field is available in API version 61.0 and later.

offsetUnit

FlowScheduledPathOffsetUnit (enumeration of type string)

Specify the time unit used to wait when the async action executes. Possible values are:

*   Months
*   Days
*   Hours
*   Minutes

This field is available in API version 61.0 and later.

outputParameters

[FlowActionCallOutputParameter](#FlowActionCallOutputParameter)\[\]

An array of output parameters from the action to the flow.

storeOutputAutomatically

boolean

Indicates whether the action’s output parameters are automatically available in the flow without creating any variables. When the value is true, you can reference an output parameter by specifying the API name of the Action element in the flow. The default value is false. When the value is false, create variables manually to store output values from the action.

This field is available in API version 48.0 and later.

timeoutConnector

[FlowConnector](#FlowConnector)

Specifies which node to execute if an async action execution is timed out. This field is available in API version 62.0 and later.

versionSegment

int

Specifies the version of the versioned action. By default, the value is 1. Supported only when versionSegment is specified. This field is available in API version 58.0 to 61.0. This field is deprecated in API version 62.0 and later.

versionString

string

Reserved for future use.

FlowActionCallInputParameter
----------------------------

Defines an input parameter from the flow to the action. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 31.0 and later.

Field Name

Field Type

Description

name

string

Required. Unique name for the input parameter.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the input parameter.

FlowActionCallOutputParameter
-----------------------------

Defines an output parameter from the action to the flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 31.0 and later.

Field Name

Field Type

Description

assignToReference

string

Required. Specifies the variable to which you want to assign the output parameter value.

name

string

Required. Unique name for the output parameter.

FlowApexPluginCall
------------------

Defines a call to an Apex plug-in from the flow. It extends [FlowNode](#FlowNode) and inherits all its fields.

Field Name

Field Type

Description

apexClass

string

Required. The name of the Apex class.

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after this Apex plug-in call.

faultConnector

[FlowConnector](#FlowConnector)

Specifies which node to execute if the Apex plug-in call results in an error.

inputParameters

[FlowApexPluginCallInputParameter](#FlowApexPluginCallInputParameter)\[\]

An array of input parameters from the flow to the Apex plug-in.

outputParameters

[FlowApexPluginCallOutputParameter](#FlowApexPluginCallOutputParameter)\[\]

An array of output parameters from the Apex plug-in to the flow.

FlowApexPluginCallInputParameter
--------------------------------

Defines an input parameter from the flow to the Apex plug-in. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

name

string

Required. Unique name for the input parameter.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the input parameter.

FlowApexPluginCallOutputParameter
---------------------------------

Defines an output parameter from the Apex plug-in to the flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

assignToReference

string

Required. Specifies the variable to which you want to assign the output parameter value.

name

string

Required. Unique name for the output parameter.

FlowAssignment
--------------

Defines an assignment node that can dynamically change the value of a variable in the flow. It extends [FlowNode](#FlowNode) and inherits all of its fields.

Field Name

Field Type

Description

assignmentItems

[FlowAssignmentItem](#FlowAssignmentItem)\[\]

An array of assignment operations that’s executed in the given order, starting from the index 0.

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after this assignment node.

FlowAssignmentItem
------------------

Defines an operation to apply to a variable. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

assignToReference

string

Reference to the variable to which you want to apply the specified operator.

operator

[FlowAssignmentOperator](#FlowAssignmentOperator) (enumeration of type string)

Operation to apply to the variable reference in the assignToReference field. For valid values, see [FlowAssignmentOperator](#FlowAssignmentOperator).

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value that you want the operator to apply to the variable reference in the assignToReference field.

FlowAssignmentOperator
----------------------

An enumeration of type string that specifies the operation to apply to the variable in the assignToReference field. See “[Flow Operators in Assignment Elements](https://help.salesforce.com/articleView?id=flow_ref_operators_assignment.htm&language=en_US "HTML (New Window)")” in Salesforce Help.

These values are valid.

Enumeration Value

Description

Add

When the assignToReference field is a variable of type number or currency, this operator adds the value to the variable.

When the assignToReference field is a variable of type date, this operator adds the value in days to the variable.

When the assignToReference field is a variable of type string, this operator appends the value to the end of the string.

When the assignToReference field is a variable of type picklist, this operator appends the value to the end of the last item in the picklist.

When the assignToReference field is a variable of type multipicklist, this operator appends the value to the end of the last item in the multi-select picklist. To instead add an item to the end of the multi-select picklist, use the AddItem operator.

When the assignToReference field is the $Flow.ActiveStages global variable, this operator appends the value as a new item at the end of $Flow.ActiveStages.

When the assignToReference field is a collection variable, this operator appends the value to the end of the collection. Support for a collection variable as the value is available in API version 43.0 and later, but only via Metadata API. From Flow Builder, you can’t save an Assignment element that contains a collection variable in the Value column for the Add operator.

The Add operator isn’t supported when the assignToReference field is a variable of type boolean, dateTime, or sObject.

AddAtStart

Supported only when the assignToReference field is a collection variable or the $Flow.ActiveStages global variable. Adds the value as a new item at the beginning of the collection. When the value is a collection variable, the operator adds all items at the beginning of the collection. This operator is available in API version 43.0 and later.

AddItem

Supported only when the assignToReference field is a variable of type multipicklist. Adds the value to the picklist, including the semicolon that’s required to mark a value as a separate item. This operator is available in API version 34.0 and later.

Assign

Assigns the value to the variable in the assignToReference field.

AssignCount

Supported only when the value is a collection variable or the $Flow.ActiveStages global variable. Counts the number of stages or items in the collection, and assigns that number to the variable in the assignToReference field. Corresponds to equals count in the user interface. This operator is available in API version 43.0 and later.

RemoveAfterFirst

Supported only when the assignToReference field is a collection variable or the $Flow.ActiveStages global variable. Finds the first instance of the value within the variable in the assignToReference field. Removes everything after that first instance from the variable. This operator is available in API version 43.0 and later.

RemoveAll

Supported only when the assignToReference field is a collection variable or the $Flow.ActiveStages global variable. Removes all instances of the value from the variable in the assignToReference field. When the value is a collection variable, the operator removes all instances of each item from the variable in the assignToReference field. This operator is available in API version 43.0 and later.

RemoveBeforeFirst

Supported only when the assignToReference field is a collection variable or the $Flow.ActiveStages global variable. Finds the first instance of the value within the variable in the assignToReference field. Removes everything before that first instance from the variable. This operator is available in API version 43.0 and later.

RemoveFirst

Supported only when the assignToReference field is a collection variable or the $Flow.ActiveStages global variable. Removes the first instance of the value from the variable in the assignToReference field. This operator is available in API version 43.0 and later.

RemovePosition

Supported only when the assignToReference field is a collection variable or the $Flow.ActiveStages global variable. Removes the item at the specified position. For example, if the collection contains three items, such as Red, Green, and Blue, and the value is 2, the second item, Green, is removed from the collection variable. This operator is available in API version 43.0 and later.

Make sure that the value at run time is a positive integer within the range of the number of items in the collection variable.

RemoveUncommon

Supported only when assignToReference and value are both collection variables. Keeps items that are in both collections and removes the rest from the collection variable in the assignToReference field. This operator is available in API version 43.0 and later.

Subtract

Supported only when the assignToReference field is a variable of type currency, date, or number.

When the assignToReference field is a variable of type number or currency, this operator subtracts the value from the variable.

When the assignToReference field is a variable of type date, this operator subtracts the value in days from the variable.

FlowBaseElement
---------------

Base class for all flow elements that require contextual information in metadata values. This class is an abstract class. FlowBaseElement is available in API version 32.0 and later.

Field Name

Field Type

Description

processMetadataValues

[FlowMetadataValue](#FlowMetadataValue)\[\]

Contextual information for the element.

FlowChoice
----------

A choice resource is a standalone choice option that you can reference or reuse throughout the flow. It extends [FlowElement](#FlowElement) and inherits all of its fields.

Field Name

Field Type

Description

choiceIcon

[FlowIcon](#FlowIcon)

The icon to display for the choice in the screen. This field is available in API version 64.0 and later.

choiceText

string

Required. Choice label to display in the screen.

dataType

FlowDataType (enumeration of type string)

Required. Valid types are:

*   Currency
*   Date
*   Number
*   String
*   Boolean

userInput

[FlowChoiceUserInput](#FlowChoiceUserInput)

Enables the choice to allow user input when the choice is selected. Not supported for choices in multi-select fields.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Actual value that’s used during flow execution, for example, in assignments, calls to Apex plug-ins, and record elements. If null, this choice always has the value of null.

FlowChoiceUserInput
-------------------

Allows the choice to include a user input field that appears when the user selects a choice. User input isn’t supported for choices in multi-select fields. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

isRequired

boolean

Indicates whether users are required to enter something into the field when they select the choice.

promptText

string

Text that’s displayed to prompt the user for input at runtime. Supports merge fields.

validationRule

[FlowInputValidationRule](#FlowInputValidationRule)

A rule used at runtime to validate the user input.

FlowCollectionProcessor
-----------------------

Defines a node that processes the contents of a collection, depending on the collectionProcessorType. FlowCollectionProcessor is available in API version 50.0 and later. FlowCollectionProcessor extends FlowNode and inherits all its fields.

Field Name

Field Type

Description

assignNextValueToReference

string

The name of the variable that’s assigned to the next value of the collection.

collectionProcessorType

FlowCollectionProcessorType

The type of the collection processor. Valid values are:

*   SortCollectionProcessor—This value is available in API version 50.0 and later.
*   RecommendationMapCollectionProcessor— This value is available in API version 53.0 and later.
*   FilterCollectionProcessor— This value is available in API version 53.0 and later.

collectionReference

string

The collection being sorted, filtered, or assigned to recommendations.

conditionLogic

string

Defines how the filtering conditions are evaluated. Valid values are:

*   And
*   Or
*   Custom logic, such as (1 AND (2 OR 3))
*   Formula

conditions

[FlowCondition](#FlowCondition)\[\]

An array of conditions for the input collection.

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after processing the collection.

formula

string

The formula expression that filters the input collection. If the formula evaluates to true, the record is added to the output collection.

limit

int

The maximum number of records to include in the generated collection. There’s no default value. All items of the collection are kept if it’s greater than the size of the collection.

If sortField and sortOrder are also specified, the records are sorted before the limit takes effect.

This field is available in API version 51.0 and later.

This field is nillable in API version 51.0 and later.

mapItems

[FlowCollectionMapItem](#FlowCollectionMapItem)\[\]

The rules to map each field of the collection variable.

outputSObjectType

string

The sObject type of the output collection.

sortOptions

[FlowCollectionSortOption](#FlowCollectionSortOption)\[\]

An array of options to sort the items in the collection. This field is available in API version 51.0 and later.

FlowCollectionSortOption
------------------------

Sets the sorting field, sort order, and placement of empty or null values in the sorted collection. This metadata type is available in API version 51.0 and later.

Field Name

Field Type

Description

doesPutEmptyStringAndNullFirst

boolean

Place empty or null values first in the sorted list by setting this value to true. The default value is false.

sortField

string

Determines the sorting of records that meet the filter criteria. Required for record collections and collections of Apex-defined variables.

If the collection is a primitive data type, such as a list of string or integer values, sortField isn’t supported.

sortOrder

SortOrder (enumeration of type string)

The order that the collection is sorted in. Valid values are:

*   Asc—Ascending
*   Desc—Descending

FlowCustomError
---------------

Defines a custom error element to roll back a change that triggered a flow and inform the user exactly what caused the error. It extends [FlowNode](#FlowNode) and inherits all its fields.

Field Name

Field Type

Description

description

string

Describes the error message.

connector

[FlowConnector](#FlowConnector)

Required. Which node to execute after completing the current node.

customErrorMessages

[FlowCustomErrorMessage](#FlowCustomErrorMessage)\[\]

An array of custom error messages.

FlowCustomErrorMessage
----------------------

Defines a custom error message for a custom error element. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

errorMessage

string

Required. Specifies the custom error message.

fieldSelection

string

References the erroneous field that’s associated with the custom error message.

isFieldError

boolean

Required. When this field is set to true, indicates that the custom error message displays inline on a field. When it is set to false, it displays in a window on a record page. The default value is false.

FlowCondition
-------------

Defines a condition for a rule. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

aggregationOperator

string

Operation to apply to the variable reference in the assignToReference field. The valid value is:

*   Count

conditionLogic

string

Specifies logic for the conditions. Value can be:

*   and—Evaluates to true only if all its conditions evaluate to true
*   or—Evaluates to true if any of its conditions evaluate to true

conditionType

FlowWaitConditionType (enumeration of type string)

The type of condition that a requirement in an automation is used for. Valid values are:

*   Container
*   EntryCondition
*   ExitCondition

conditions

[FlowCondition](#FlowCondition)\[\]

An array of conditions that must be true for the flow to execute the rule.

leftValueReference

string

Required. Unique name of the element that serves as the left side of the condition expression.

operator

FlowComparisonOperator (enumeration of type string)

Required. Comparison operators in conditions for flow elements and resources. Valid values are:

*   Contains
*   EndsWith
*   EqualTo
*   GreaterThan
*   GreaterThanOrEqualTo
*   HasError—This value is available in API version 64.0 and later.
*   In— This value is available in API version 56.0 and later.
*   IsBlank—A text value with zero characters or with only whitespace. Use to determine whether a text field or variable is blank. For other data type values, use to determine whether a field or variable is null. This value is available in API version 61.0 and later.
*   IsChanged— This value is available in API version 52.0 and later.
*   IsEmpty—An empty collection. This value is available in API version 61.0 and later.
*   IsNull—A value that is either not set or references no value. Use to determine whether a field or variable value is set to no value.
*   LessThan
*   LessThanOrEqualTo
*   None— Save a flow with an incomplete condition, so you can finish building the flow later. This value is available in API version 58.0 and later.
*   NotEqualTo
*   NotIn— This value is available in API version 56.0 and later.
*   StartsWith
*   WasSelected— Requires a choice on the left side.
*   WasSet— This value is available in API version 30.0 and later.
*   WasVisited— Requires a node on the left side.

See [Flow Operators](https://help.salesforce.com/s/articleView?id=platform.flow_ref_operators.htm&language=en_US).

rightValue

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Unique name of an element or the actual value, such as text or a number, for the right side of the condition expression.

FlowCustomProperty
------------------

Defines the name and value of a custom property in a flow. This metadata type is available in API version 63.0 and later.

Field Name

Field Type

Description

name

string

Required. Unique name for the custom property associated with the flow.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the custom property associated with the flow. When the FlowCustomProperty’s name is set to ScreenProgressIndicator, valid values are:

*   “Location":"Top","Type":"Simple”
*   "Location":"Footer","Type":"Simple"
*   "Location":"Top","Type":"Path”

FlowActionCallPath
------------------

A path determines which node of the flow is executed after the Einstein Decision element. A path defines and links to the subsequent node. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

connector

[FlowConnector](#FlowConnector)

Required. Which node to execute after completing the current node.

pathName

string

Required. Unique name for the path.

FlowConnector
-------------

Connectors determine the order in which the nodes of the flow are executed. A connector defines and links to the subsequent node. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

isGoTo

boolean

Make the connector a Go To Connector by setting this value to true. The default value is false. This value is available in API version 53.0 and later. See [Flow Connectors](https://help.salesforce.com/s/articleView?id=sf.flow_ref_connectors.htm&language=en_US).

targetReference

string

Required. Which node to execute after completing the current node.

FlowCollectionMapItem
---------------------

Defines the rule to assign a value to the field reference. This metadata type is available in API version 51.0 and later.

Field Name

Field Type

Description

assignToFieldReference

string

Required. Specifies the reference to the field to which the specified operator is applied.

operator

[FlowAssignmentOperator](#FlowAssignmentOperator) (enumeration of type string)

Required. Applies to the variable reference in the assignToFieldReference field.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Required. Defines the value that the operator applies to the variable reference in the assignToFieldReference field.

FlowDataTypeMapping
-------------------

This data type mapping defines the specific sObject data type for input and out values that have the generic sObject data type. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 48.0 and later.

Field Name

Field Type

Description

apexClass

string

The name of the Apex class. This field is available in API version 61.0 and later.

typeName

string

Required. API name of the input or output variable. The T\_\_ prefix is required for input variables. The U\_\_ prefix is required for output variables. For example, T\_\_inputCollection represents the API name of the input variable inputCollection.

typeValue

string

API name of the specific sObject data type that this value maps to. For example, Account.

FlowConstant
------------

A constant resource defines a fixed value that can be used throughout your flow. It extends [FlowElement](#FlowElement) and inherits all its fields.

Field Name

Field Type

Description

dataType

FlowDataType (enumeration of type string)

Required. Valid types are:

*   Currency
*   Date
*   Number
*   String
*   Boolean

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Default value of the constant. This field can’t have merge fields, nor can it reference another resource besides $GlobalConstant.EmptyString.

FlowDecision
------------

A node that evaluates a set of rules and routes the flow execution based on the first rule that evaluates to true. It extends [FlowNode](#FlowNode) and inherits all its fields.

Field Name

Field Type

Description

defaultConnector

[FlowConnector](#FlowConnector)

Specifies which node to execute if none of the rules evaluate to true.

defaultConnectorLabel

string

Label for the default connector.

rules

[FlowRule](#FlowRule)\[\]

An array of rules for the decision. The rules are evaluated in the order that they’re listed, and the connector of the first true rule is used. If no rules are true, then the default connector is used. In Flow Builder, rules are referred to as decision outcomes.

FlowDynamicChoiceSet
--------------------

Retrieves data or metadata from an object and dynamically generates a set of choices at run time. It extends [FlowElement](#FlowElement) and inherits all its fields. Depending on the fields that are set, this element represents a record choice or a picklist choice.

*   A record choice dynamically generates choices based on records that meet specified filter criteria. If a dynamic choice doesn’t have the picklistField and picklistObject parameters set, it’s a record choice and it can’t have a data type of Picklist or Multipicklist.
*   A picklist choice dynamically generates choices based on the available values for a picklist or multi-select picklist field. If a dynamic choice has the picklistField and picklistObject parameters set, it’s a picklist choice and it must have a data type of Picklist or Multipicklist.

Field Name

Field Type

Description

collectionReference

string

The collection that’s used to generate choices. This field is available in API version 54.0 and later.

dataType

FlowDataType (enumeration of type string)

Required. Valid types are:

*   Boolean
*   Currency
*   Date
*   Multipicklist—Picklist choices only
*   Number
*   Picklist—Picklist choices only
*   Record
*   String

Picklist and Multipicklist are available in API version 35.0 and later. Record is available in API version 54.0 and later.

displayField

string

Required for record choices. Specifies the object field. The values of the object field are displayed to the user as choice labels for selecting a record.

For example, for an account, if you want the dynamically generated choices to be displayed as the account names from the records that are retrieved from the database, specify Name in displayField.

Not supported for picklist choices. Picklist choices always display the labels for the retrieved picklist values.

filters

[FlowRecordFilter](#FlowRecordFilter)\[\]

An array of filters to apply to the records retrieved from the database. For example, filter accounts to include only the accounts that were created in the past three months.

Not supported for picklist choices.

limit

int

Maximum number of choices to include in the generated set of choices. Maximum and default: 200.

If sortField and sortOrder are also specified, the records are sorted before the limit takes effect.

This field is available in API version 25.0 and later.

This field is nillable in API version 45.0 and later.

object

string

Required for record choices. The object whose fields you want to retrieve from the database and use to generate the set of choices. For example, use “Account” to dynamically generate choices from the information in account records in the database.

Not supported for picklist choices.

outputAssignments

[FlowOutputFieldAssignment](#FlowOutputFieldAssignment)\[\]

An array that assigns fields from the user-selected record to variables that can be used elsewhere in the flow. For example, when the user selects an account name from the dynamically generated list of choice options, outputAssignments can assign the ID and AnnualRevenue from the user-selected account to variables that you specify.

Not supported for picklist choices.

picklistField

string

Required for picklist choices. The field whose available values you want to retrieve from the database and use to generate the picklist choice. For example, use “Industry” to dynamically generate one choice for each available value on the Industry picklist field.

Not supported for record choices.

This field is available in API version 35.0 and later.

picklistObject

string

Required for picklist choices. The object whose field metadata you want to retrieve from the database and use to generate the picklist choice. For example, use “Account” to dynamically generate choices from a picklist field on the Account object.

Not supported for record choices.

This field is available in API version 35.0 and later.

sortField

string

Field that’s used for sorting records that meet the filter criteria. If this field isn’t specified, the returned records aren’t sorted.

You can only sort records by fields that have the Sort API field property, as specified in [SOAP API](https://developer.salesforce.com/docs/atlas.en-us.256.0.api.meta/api/ "HTML (New Window)").

Not supported for picklist choices.

This field is available in API version 25.0 and later.

sortOrder

SortOrder (enumeration of type string)

Order in which to sort the records. If this field isn’t specified, then the results aren’t sorted.

Valid values are:

*   Asc—Ascending
*   Desc—Descending

Not supported for picklist choices.

This field is available in API version 25.0 and later.

valueField

string

Stored value for the choice, which can differ from what is displayed to the user as the choice options (displayField). For example, the displayField could be the account “Name” while the valueField is the account “Id.”

Not supported for picklist choices. Picklist choices always store the API value for the retrieved picklist values.

FlowElement
-----------

Base class for all flow elements. This class is an abstract class. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

description

string

Description of the flow element.

name

string

Unique name of the flow element.

FlowElementReferenceOrValue
---------------------------

Defines a reference to an existing element or a particular value that you specify. Make sure that you specify only _one_ of the fields.

Field Name

Field Type

Description

apexValue

string

Use this field to specify a JSON response value of an Apex-defined record. Use this field only for FlowScreenFieldInputParameter and FlowActionCallInputParameter. If you want to specify a different data type or element reference, don’t use this field.

booleanValue

boolean

Use this field to specify a boolean value. If you want to specify a different data type or element reference, don’t use this field.

complexValue

string

When complexValueType is specified, use this field to specify flow resources and fields in the data structure. Use these fields to describe the data structure:

*   fieldReference—The list of field API names.
*   objectType—The object type, sObject or Apex.
*   type—The API name of the sObject or Apex class.
*   elementReference—The API name of the flow resource that contains the list of fields specified in fieldReference.

This field is available in API version 63.0 and later.

complexValueType

FlowComplexValueType (enumeration of type string)

Use this field to specify the type of data structure to reference. Valid values are:

*   JoinDefinition—When InnerJoin is specified in transformType, indicates flow resources for source and target collections, join keys, selected fields to join. and field mappings in a join transformation.
*   FieldReference—Use this field to define the flow resource and its fields referenced in the flow.

This field is available in API version 63.0 and later. Use complexValue to specify the data structure.

dateTimeValue

dateTime

Use this field to specify a dateTime value. If you want to specify a different data type or element reference, don’t use this field. This field is available in API version 30.0 and later.

dateValue

date

Use this field to specify a date value. If you want to specify a different data type or element reference, don’t use this field.

elementReference

string

Use this field to specify the name of an existing flow resource. If you want to specify a value instead of an element reference, don’t use this field.

formulaDataType

FlowDataType (enumeration of type string)

Use this field to specify the formula result’s data type of the transformed data. Corresponds to the target data field in Flow Builder. This field requires the formulaExpression field. This field is available in API version 59.0 and later. See [FlowTransform](#FlowTransform)

Valid values are:

*   Apex
*   Boolean
*   Currency
*   Date
*   DateTime
*   Number
*   String
*   sObject—This value corresponds to a record variable.

formulaExpression

string

Use this field to specify the formula expression that transforms the data in the flow. In Flow Builder, it corresponds to the target data field in the Transform element. This field requires the formulaDataType field. This field is available in API version 59.0 and later. See [FlowTransform](#FlowTransform).

numberValue

double

Use this field to specify a double value. If you want to specify a different data type or element reference, don’t use this field.

setupReference

string

Use this field to specify the name of an existing setup reference. Required for Omni-Channel elements. If you want to specify a value instead of a setup reference, don’t use this field. Required when setupReferenceType is specified.

setupReferenceType

string

Use this field to specify the type of setup reference. Required when setupReference is specified.

sobjectValue

string

Use this field to specify a JSON response value of an sObject record. Use this field only for FlowScreenFieldInputParameter and FlowActionCallInputParameter. If you want to specify a different data type or element reference, don’t use this field.

stringValue

string

Use this field to specify a string value. If you want to specify a different data type or element reference, don’t use this field.

When the [FlowMetadataValue](#FlowMetadataValue)'s name field is set to SendNoApproverEmails, valid values are true or false and are case-insensitive.

When the [FlowMetadataValue](#FlowMetadataValue)'s name field is set to BuilderType or OriginalBuilderType, the valid value is LightningFlowBuilder. The value is reserved for internal use.

transform

FlowInlineTransform

Use this field to specify a value for an inline data transformation. This field is available in API version 62.0 and later.

transformValueReference

string

Reserved for future use.

FlowExitRule
------------

Defines the conditions and logic that enables an exit rule to evaluate to true. It extends [FlowElement](#FlowElement) and inherits all of its fields.

Field Name

Field Type

Description

conditions

[FlowCondition](#FlowCondition)\[\]

An array of conditions for the exit rule.

label

string

Required. Label for the exit rule.

logicalOperator

string

Required. Logical operator in conditions for the exit rule. Valid values are:

*   and—Evaluates to true only if all its conditions evaluate to true
*   or—Evaluates to true if any of its conditions evaluate to true

ruleOrder

int

Indicates how the exit rule is ordered against other exit rules. The ruleOrder value must be unique within the flow.

FlowExperiment
--------------

A node that routes the flow execution based on a specified experiment distribution percentage. It extends [FlowNode](#FlowNode) and inherits all its fields. This metadata type is available in API version 61.0 and later.

Field Name

Field Type

Description

duration

int

The amount of time that the experiment runs. This field is available in API version 64.0 and later.

durationUnit

string

The unit of measurement for experiment duration. Valid values are:

*   Minutes
*   Hours
*   Days
*   Weeks
*   Months

This field is available in API version 64.0 and later.

paths

[FlowExperimentPath](#FlowExperimentPath)\[\]

An array of flow experiment paths.

testGroupPercentage

int

Specifies the distribution percentage of the test group. A valid number in the range 0-99. This field is available in API version 64.0 and later.

type

FlowExperimentType

Required. The type of experiment. Valid value is:

*   Random

FlowExperimentPath
------------------

Defines an experiment path. It extends [FlowElement](#FlowElement) and inherits all its fields. This metadata type is available in API version 61.0 and later.

Field Name

Field Type

Description

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after this experiment path.

label

string

Required. Label for the path.

percentage

int

Required. The distribution percentage for this path.

FlowFormula
-----------

Calculates a value using functions and elements in the flow. It extends [FlowElement](#FlowElement) and inherits all its fields.

Field Name

Field Type

Description

dataType

FlowDataType (enumeration of type string)

The data type for the formula. Valid values are:

*   Boolean
*   Currency
*   Date
*   DateTime
*   Number
*   String

dataType defaults to Number if it isn’t defined in a formula.

This field is available in API version 31.0 and later.

expression

string

Required. Salesforce formula expression. The return value must match the data type. For API version 30.0 and earlier, the return value must be numeric.

scale

int

Scale of the return value, specifically, the number of digits to the right of the decimal point. Available only when the data type is Number or Currency. Corresponds to the Decimal Places field in Flow Builder.

FlowIcon
--------

Allows a resource to include an icon. This metadata type is available in API version 64.0 and later.

Field Name

Field Type

Description

iconName

String

The name of the selected Salesforce Lightning Design System icon. This field is available in API version 64.0 and later.

FlowInputFieldAssignment
------------------------

Assigns the value for a record field based on a resource or static value. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

field

string

Required. The name of the field to assign a value to when a record is created or updated.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

The value to assign to the field.

FlowInputValidationRule
-----------------------

Validation rules verify that the data entered by the user meets the specified requirements. If the validation rule evaluates to false, then the specified error message is displayed.

Field Name

Field Type

Description

errorMessage

string

Required. The error message to display when formulaExpression is false.

formulaExpression

string

Required. A formula that’s used to validate the user input.

FlowLoop
--------

A construct for iterating through a collection. It extends [FlowNode](#FlowNode) and inherits all its fields. FlowLoop is available in API version 30.0 and later.

Field Name

Field Type

Description

assignNextValueToReference

string

The variable that’s assigned to the current value in the collection before navigating to the target of nextValueConnector.

collectionReference

string

The collection being looped through.

iterationOrder

iterationOrder (enumeration of type string)

Valid values are:

*   Asc—Iterate through the collection in the order the values are listed (first to last).
*   Desc—Iterate through the collection in the reverse order the values are listed (last to first).

nextValueConnector

[FlowConnector](#FlowConnector)

A reference to the next element in the collection.

noMoreValuesConnector

[FlowConnector](#FlowConnector)

The element to navigate to when all entries in the collection have been iterated through.

FlowMetadataValue
-----------------

Defines contextual information that can be passed between elements in a flow. Flow metadata values can be used in an application that produces or consumes flows. FlowMetadataValue is available in API version 31.0 and later.

Field Name

Field Type

Description

name

string

Required. Name for the metadata value. This name doesn’t need to be unique across all elements.

To specify that an approval orchestration send no email notifications to approvers, use SendNoApproverEmails .

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Reference or value for the metadata value.

FlowNode
--------

A node is a type of element that’s visible in the flow diagram. It extends [FlowElement](#FlowElement) and inherits all its fields.

Field Name

Field Type

Description

elementSubtype

FlowElementSubtype (enumeration of type string)

Reserved for internal use.

label

string

Name of the node. This non-unique label is different from the unique name of the node, which is inherited from [FlowElement](#FlowElement).

locationX

int

Required. Horizontal location of the node, in pixels from the left. In API version 64.0 and later, if a flow is saved in auto-layout, this field is set to 0.

locationY

int

Required. Vertical location of the node, in pixels from the top. In API version 64.0 and later, if a flow is saved in auto-layout, this field is set to 0.

FlowOrchestratedStage
---------------------

A stage node that contains steps in an orchestration. It extends [FlowNode](https://developer.salesforce.com/docs/atlas.en-us.256.0.api_meta.meta/api_meta/meta_visual_workflow.htm#FlowNode) and inherits all its fields. This metadata type is available in API version 53.0 and later.

Field Name

Field Type

Description

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after this stage.

exitActionInputParameters

[FlowStageStepExitActionInputParameter](#subtype_FlowStageStepExitActionInputParameter)\[\]

An array of input parameters from the stage to the evaluation flow. These parameters specify an exit condition for the stage.

exitActionName

string

The name of the evaluation flow used as an exit condition for the stage.

exitActionOutputParameters

[FlowStageStepExitActionOutputParameter](#subtype_FlowStageStepExitActionOutputParameter)\[\]

An array of output parameters from the evaluation flow to the stage. These parameters specify an exit condition for the stage.

exitActionType

InvocableActionType (enumeration of type string)

The type of the evaluation flow for the custom exit condition. Valid values are:

*   createFieldGnrnPromptTmplResp
*   EvaluationFlow
*   exploreConversation
    
    This value is available in API version 61.0 and later.
    

exitConditionLogic

string

Defines how the stage exit conditions are evaluated. Valid values are:

*   And
*   Or
*   Custom logic, such as (1 AND (2 OR 3))
*   Formula

exitConditions

[FlowCondition](#FlowCondition)\[\]

An array of requirements that must be met to exit the stage.

faultConnector

[FlowConnector](#FlowConnector)

Not used.

runAsUser

boolean

Indicates whether an asynchronous background step is run in the context of the user who completed the most recently completed interactive step.

stageSteps

[FlowStageStep](#subtype_FlowStageStep)\[\]

An array of stage step resources.

FlowOutputFieldAssignment
-------------------------

Assigns a record field’s value to a variable that can be used elsewhere in the flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

assignToReference

string

Required. Reference to the variable where you want to store the value of the record field.

field

string

Required. Name of the field whose value is to be assigned after a record lookup.

FlowRelatedRecordLookup (Beta)
------------------------------

This feature is a pilot or beta service that is subject to the Beta Services Terms at [Agreements - Salesforce.com](https://www.salesforce.com/company/legal/agreements/ "HTML (New Window)") or a written Unified Pilot Agreement if executed by Customer, and applicable terms in the [Product Terms Directory](https://ptd.salesforce.com/ "HTML (New Window)"). Use of this pilot or beta service is at the Customer's sole discretion.

Finds records in the database that are related to the records specified in FlowRecordLookup and stores their field values in the flow. Corresponds to a Get Records element in Flow Builder. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

filterLogic

string

The filter logic that’s applied to the filter condition requirements. To require all conditions, use AND. To require any conditions, use OR. For custom condition logic, enter the entire logic string. For example, 1 AND 2 OR (3 AND 4).

filters

[FlowRecordFilter](#FlowRecordFilter)\[\]

An array that specifies the criteria used to select the record from the database.

If the filters return more than one record, they’re sorted according to the specified sortField and sortOrder. If outputReference specifies a non-collection record variable or if getFirstRecordOnly is true, only the first record in the sorted list is selected.

If sortField or sortOrder isn’t specified, records aren’t returned in any particular order. If outputReference specifies a non-collection record variable or if getFirstRecordOnly is true, only the first record in the unsorted list is selected.

getFirstRecordOnly

boolean

Indicates whether to store field values for only one record, even when multiple records meet the filter criteria. Supported only when storeOutputAutomatically is true. When storeOutputAutomatically is false, what determines whether one or multiple records are stored is whether outputReference specifies a record variable or a record collection variable.

limit

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Specifies the maximum number of records to store. Valid values are between 2 and 20,000. Supported only when getFirstRecordOnly is false.

queriedFields

strings\[\]

An array that specifies which fields from the selected record are saved to the specified record variable.

relatedObject

string

Name of the related object from which to select related records.

relatedRecords

[FlowRelatedRecordLookup](#FlowRelatedRecordLookup)\[\]

An array that specifies the related records to look up in the database.

relationshipField

string

Specifies the API name of the relationship field used to link the object to its related object. This field is required for retrieving related records.

sortField

string

The field that’s used for sorting the records that meet the filter criteria. If this field isn’t specified, the returned records aren’t sorted.

You can only sort records by fields that have the Sort API field property, as specified in [SOAP API](https://developer.salesforce.com/docs/atlas.en-us.256.0.api.meta/api/ "HTML (New Window)").

sortOrder

SortOrder (enumeration of type string)

Order in which to sort the records. If this field isn’t specified, then the results aren’t sorted.

Valid values are:

*   Asc—Ascending
*   Desc—Descending

FlowRecordCreate
----------------

Create a record in the database using values from the flow. It extends [FlowNode](#FlowNode) and inherits all its properties.

The flow record create, lookup, update, and delete operations are different from the CRUD-based metadata calls [create()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_create.htm#meta_create "Deprecated. Adds one or more new metadata components to your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use createMetadata() instead."), [retrieve()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_retrieve.htm#meta_retrieve "The retrieve() call retrieves XML file representations of components in an organization."), [update()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_update.htm#meta_update "Deprecated. Updates one or more components in your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use updateMetadata() or renameMetadata() instead."), and [delete()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_delete.htm#meta_delete "Deprecated. Deletes one or more components from your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use deleteMetadata() instead."). The flow record methods apply to record operations from within a flow, which aren’t the same as doing any metadata calls to CRUD setup entities.

Field Name

Field Type

Description

assignRecordIdToReference

string

Reference to the variable where you want to store the ID after the record is created.

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after creating the record.

doesUpsert

boolean

Indicates whether the element creates or updates records. The default value is false, indicating that the element only creates records. This field is available in API version 62.0 and later.

doesUpsertAllOrNone

boolean

Indicates whether the element creates or updates records only if all records are created or updated successfully. If set to true and a record fails, then the transaction rolls back and no records are created or updated.

If set to false, the transaction creates or updates only the records that are successful. The default value is true. This field is available in API version 62.0 and later.

faultConnector

[FlowConnector](#FlowConnector)

Specifies which node to execute if the attempt to create a record results in an error.

filterLogic

string

The filter logic applied to the filter condition requirements. To require all conditions, use AND. To require any conditions, use OR. For custom condition logic, enter the entire logic string. For example, 1 AND 2 OR (3 AND 4).

This field is available in API version 61.0 and later.

filters

[FlowRecordFilter](#FlowRecordFilter)\[\]

An array that specifies the criteria to select which records to create or update in the database.

This field is available in API version 61.0 and later.

inputAssignments

[FlowInputFieldAssignment](#FlowInputFieldAssignment)\[\]

An array that assigns values to the specified fields of the record being created.

inputReference

string

Specifies the record variable whose field values are used to populate the new record’s fields.

object

string

Required. The object type that the element creates.

operationMultMatchingRecords

string

The operation to perform if multiple matching records are found. Valid values are:

*   None
*   UpdateAllRecords
*   UpdateLatestRecord

This field is available in API version 61.0 and later.

operationOneMatchingRecord

string

The operation to perform if one matching record is found. Valid values are:

*   None
*   UpdateAllRecords

This field is available in API version 61.0 and later.

operationZeroMatchingRecords

string

The operation to perform if no matching records are found. Valid values are:

*   None

This field is available in API version 61.0 and later.

storeOutputAutomatically

boolean

Indicates whether the record ID is automatically available in the flow without creating any variables. When the value is true, you can reference the record ID by specifying the API name of the Create Records element in the flow. The default value is false. When the value is false, create a variable to store the record ID.

This field is available in API version 48.0 and later.

upsertExternalIdField

string

If doesUpsert is true, specifies the external ID field on the record. You can provide a value for this property or for the Upsert Standard ID Field property, but not both. This field is available in API version 62.0 and later.

upsertStandardIdField

string

If doesUpsert is true, specifies the standard ID field like Account ID on the object. You can provide a value for this property or for the Upsert External ID Field property, but not both. This field is available in API version 62.0 and later.

FlowRecordDelete
----------------

Deletes one or more records in the database. It extends [FlowNode](#FlowNode) and inherits all its fields.

The flow record create, lookup, update, and delete operations are different from the CRUD-based metadata calls [create()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_create.htm#meta_create "Deprecated. Adds one or more new metadata components to your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use createMetadata() instead."), [retrieve()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_retrieve.htm#meta_retrieve "The retrieve() call retrieves XML file representations of components in an organization."), [update()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_update.htm#meta_update "Deprecated. Updates one or more components in your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use updateMetadata() or renameMetadata() instead."), and [delete()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_delete.htm#meta_delete "Deprecated. Deletes one or more components from your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use deleteMetadata() instead."). The flow record methods apply to record operations from within a flow, which aren’t the same as doing any metadata calls to CRUD setup entities.

Field Name

Field Type

Description

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after deleting the record.

faultConnector

[FlowConnector](#FlowConnector)

Specifies which node to execute if the attempt to delete a record results in an error.

filters

[FlowRecordFilter](#FlowRecordFilter)\[\]

An array that specifies the criteria used to select which records to delete from the database. For example, delete accounts whose last activity was older than a specified date.

inputReference

string

Specifies the record variable whose record ID is used to identify which record to delete in the database.

object

string

Required. The name of the object whose records are deleted.

FlowRecordFilter
----------------

Sets the criteria for searching records in the database. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields.

Field Name

Field Type

Description

field

string

Required. The field to be used for filtering records.

operator

FlowRecordFilterOperator (enumeration of type string)

Required. Valid values are:

*   EqualTo
*   NotEqualTo
*   GreaterThan
*   LessThan
*   GreaterThanOrEqualTo
*   LessThanOrEqualTo
*   StartsWith
*   EndsWith
*   Contains
*   IsNull

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Reference or value used with the field and operator to filter records.

FlowRecordLookup
----------------

Finds records in the database and stores their field values in the flow. Corresponds to a Get Records element in Flow Builder. It extends [FlowNode](#FlowNode) and inherits all its fields.

The flow record create, lookup, update, and delete operations are different from the CRUD-based metadata calls [create()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_create.htm#meta_create "Deprecated. Adds one or more new metadata components to your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use createMetadata() instead."), [retrieve()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_retrieve.htm#meta_retrieve "The retrieve() call retrieves XML file representations of components in an organization."), [update()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_update.htm#meta_update "Deprecated. Updates one or more components in your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use updateMetadata() or renameMetadata() instead."), and [delete()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_delete.htm#meta_delete "Deprecated. Deletes one or more components from your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use deleteMetadata() instead."). The flow record methods apply to record operations from within a flow, which aren’t the same as doing any metadata calls to CRUD setup entities.

Field Name

Field Type

Description

assignNullValuesIfNoRecordsFound

boolean

Specifies that all values are set to null when no record is found. Supported only when storeOutputAutomatically is false.

This field is available in API version 30.0 and later.

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after getting records from the database.

faultConnector

[FlowConnector](#FlowConnector)

Specifies which node to execute if the attempt to get records results in an error.

filterLogic

string

The filter logic that’s applied to the filter condition requirements. To require all conditions, use AND. To require any conditions, use OR. For custom condition logic, enter the entire logic string. For example, 1 AND 2 OR (3 AND 4). This field is available in API version 50.0 and later.

filters

[FlowRecordFilter](#FlowRecordFilter)\[\]

An array that specifies the criteria used to select the record from the database.

If the filters return more than one record, they’re sorted according to the specified sortField and sortOrder. If outputReference specifies a non-collection record variable or if getFirstRecordOnly is true, only the first record in the sorted list is selected.

If sortField or sortOrder isn’t specified, records aren’t returned in any particular order. If outputReference specifies a non-collection record variable or if getFirstRecordOnly is true, only the first record in the unsorted list is selected.

getFirstRecordOnly

boolean

Indicates whether to store field values for only one record, even when multiple records meet the filter criteria. Supported only when storeOutputAutomatically is true. When storeOutputAutomatically is false, what determines whether one or multiple records are stored is whether outputReference specifies a record variable or a record collection variable.

This field is available in API version 47.0 and later.

limit

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Specifies the maximum number of records to store. Valid values are between 2 and 20,000. Supported only when getFirstRecordOnly is false.

This field is available in API version 63.0 and later.

object

string

Name of the object from which to select the record.

outputAssignments

[FlowOutputFieldAssignment](#FlowOutputFieldAssignment)\[\]

An array that assigns fields from the selected record to variables that can be used elsewhere in the flow. Supported only when storeOutputAutomatically is false.

outputReference

string

Specifies the record variable or record collection variable that stores the queried fields’ values. Supported only when storeOutputAutomatically is false.

queriedFields

string\[\]

An array that specifies which fields from the selected record are saved to the specified record variable.

relatedRecords (beta)

[FlowRelatedRecordLookup](#FlowRelatedRecordLookup)\[\]

An array that specifies the related records to look up in the database.

sortField

string

The field that’s used for sorting the records that meet the filter criteria. If this field isn’t specified, the returned records aren’t sorted.

You can only sort records by fields that have the Sort API field property, as specified in [SOAP API](https://developer.salesforce.com/docs/atlas.en-us.256.0.api.meta/api/ "HTML (New Window)").

This field is available in API version 25.0 and later.

sortOrder

SortOrder (enumeration of type string)

Order in which to sort the records. If this field isn’t specified, then the results aren’t sorted.

Valid values are:

*   Asc—Ascending
*   Desc—Descending

This field is available in API version 25.0 and later.

storeOutputAutomatically

boolean

Indicates whether the returned records’ field values are automatically available in the flow without creating any variables. When the value is true, the flow can reference a field by specifying the name of the Get Records element and the record field, such as Get\_Contacts.AccountId. Supported only when processType is Flow or AutoLaunchedFlow.

This field is available in API version 47.0 and later.

FlowRecordRollback
------------------

Rolls back the current transaction and cancels its pending record changes. Corresponds to the Roll Back Records element in Flow Builder. Available only in screen flows.

FlowRecordRollback extends [FlowNode](#FlowNode) and inherits all its fields. This metadata type is available in API version 52.0 and later.

Field Name

Field Type

Description

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after rolling back the current transaction.

FlowRecordUpdate
----------------

Finds records in the database and updates them with values from the flow. It extends [FlowNode](#FlowNode) and inherits all its fields.

The flow record create, lookup, update, and delete operations are different from the CRUD-based metadata calls [create()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_create.htm#meta_create "Deprecated. Adds one or more new metadata components to your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use createMetadata() instead."), [retrieve()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_retrieve.htm#meta_retrieve "The retrieve() call retrieves XML file representations of components in an organization."), [update()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_update.htm#meta_update "Deprecated. Updates one or more components in your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use updateMetadata() or renameMetadata() instead."), and [delete()](/docs/atlas.en-us.api_meta.meta/api_meta/meta_delete.htm#meta_delete "Deprecated. Deletes one or more components from your organization asynchronously. This call is removed as of API version 31.0 and is available in earlier versions only. Use deleteMetadata() instead."). The flow record methods apply to record operations from within a flow, which aren’t the same as doing any metadata calls to CRUD setup entities.

Field Name

Field Type

Description

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after completing the record update.

faultConnector

[FlowConnector](#FlowConnector)

Specifies which node to execute if the attempt to update a record results in an error.

filters

[FlowRecordFilter](#FlowRecordFilter)\[\]

An array that specifies the criteria used to select the records to update in the database.

inputAssignments

[FlowInputFieldAssignment](#FlowInputFieldAssignment)\[\]

An array that assigns values to the specified fields of the record being updated.

inputReference

string

Specifies the record variable whose field values are used to update the record’s fields.

object

string

Required. Name of the object whose records are updated.

FlowRule
--------

Defines the conditions and logic that enables a rule to evaluate to true. It extends [FlowElement](#FlowElement) and inherits all of its fields.

Field Name

Field Type

Description

conditionLogic

string

Specifies logic for the conditions. Value can be:

*   and—Evaluates to true if all of its conditions are true.
*   or—Evaluates to true if any conditions are true.
*   Advanced logic like 1 AND (2 OR 3)—Evaluates to true if the first condition is true and either the second or third condition is true.
    
    When you use advanced logic, the string can contain up to 1,000 characters.
    

conditions

[FlowCondition](#FlowCondition)\[\]

An array of conditions for the rule.

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute if this rule evaluates to true in a decision first.

doesRequireRecordChangedToMeetCriteria

boolean

If set to true, conditions evaluate to true only if the record didn’t meet the required conditions before the triggering update but now meets the conditions after the update. This field is available in API version 50.0 and later.

label

string

Required. Label for the connector.

FlowSchedule
------------

Specifies when and how frequently to run the flow. This metadata type is available in API version 47.0 and later.

Field Name

Field Type

Description

frequency

FlowStartFrequency (enumeration of type string)

Specifies how frequently to run the flow. Valid values are:

*   Once
*   Daily
*   Weekly
*   OnActivate—This value is available in API version 49.0 and later.

startDate

date

The date when the flow runs, or when the flow’s run schedule starts recurring.

startTime

time

The time of day when the flow runs, based on the org’s default time zone.

FlowScheduledPath
-----------------

Defines a scheduled path. It extends [FlowElement](#FlowElement) and inherits all its fields. This metadata type is available in API version 51.0 and later.

Field Name

Field Type

Description

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after this scheduled path.

label

string

Label for the scheduled path.

maxBatchSize

int

The maximum number of scheduled path interviews to execute in a single batch, from 1 to 200. Default is 200.

offsetNumber

int

Number of months, days, hours, or minutes to offset the time that the scheduled path executes. Negative values offset the time to execute before the provided time. Positive values offset the time to execute after the provided time.

offsetUnit

FlowScheduledPathOffsetUnit (enumeration of type string)

Specify the time unit used to offset when the scheduled path executes. Possible values are:

*   Months—This value is available in API version 56.0 and later.
*   Days
*   Hours
*   Minutes

pathType

FlowScheduledPathType (enumeration of type string)

The type of scheduled path. null is used for time-triggered and record-triggered paths. The default value is null.

*   AsyncAfterCommit—The scheduled path runs asynchronously after a save.

recordField

string

Field used to determine when the scheduled path executes. The field’s object is defined in [FlowStart](#FlowStart).

timeSource

FlowScheduledPathTimeSource (enumeration of type string)

Specify if a field or event is used to determine when the scheduled path executes. Possible values are:

*   RecordField
*   RecordTriggerEvent

FlowScreen
----------

Screens capture information from users and display information to users. It extends [FlowNode](#FlowNode) and inherits all its fields.

Field Name

Field Type

Description

actions

[FlowScreenAction](#FlowScreenAction)\[\]

An array of screen actions.

This field is available in API version 59.0 and later.

allowBack

boolean

Indicates whether to show (true) or hide (false) the **Previous** button on the screen at runtime. When true, the **Previous** button appears only if the user visited a previous screen in the flow path and if showFooter for the screen is set to true. Set this field to false when revisiting the previous screen triggers an action that you don’t want repeated, such as a credit card transaction.

This field is available in API version 26.0 and later.

Default: true

You can set either allowBack or allowFinish to false, but not both.

allowFinish

boolean

Indicates whether to show (true) or hide (false) the **Finish** button on the screen at runtime. When true, the **Finish** button appears only if the screen element is the end of a flow path, and if showFooter for the screen is set to true. The default value is true.

Set to false if user is required to go back to a previous screen to continue or complete the flow. For example, don’t include a **Finish** button on a screen that tells the user to go back and make corrections on a previous screen.

You can set allowBack or allowFinish to false, but not both.

This field is available in API version 26.0 and later.

allowPause

boolean

Indicates whether to show (true) or hide (false) the **Pause** button on the screen at runtime. The default value is true.

A flow screen displays the **Pause** button if all these conditions are true.

*   **Let users pause flows** is enabled in the organization’s process automation settings.
*   allowPause for the screen is set to true.
*   If the flow is embedded in a Visualforce page, the <flow:interview> component has its showAllowPause attribute set to true.
*   The showFooter field for the screen is set to true.

This field is available in API version 33.0 and later.

backButtonLabel

string

A label for the Back button.

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after the screen node.

fields

[FlowScreenField](#FlowScreenField)\[\]

An array of fields to display on the screen.

helpText

string

Text that appears if the end user clicks a link for help text.

Supports merge fields in API version 26.0 and later.

nextOrFinishButtonLabel

string

A label for the Next or Finish button.

pauseButtonLabel

string

A label for the Pause button.

pausedText

string

A confirmation message that appears when an end user clicks **Pause**.

This field is available in API version 33.0 and later.

rules

Reserved for future use.

showFooter

boolean

Indicates whether to show (true) or hide (false) the screen’s footer at Lightning runtime. Classic runtime isn’t supported. The default value is true.

The footer includes navigation actions for the screen. If showFooter is hidden, use Lightning components on the screen to show navigation actions.

This field is available in API version 42.0 and later.

showHeader

boolean

Indicates whether to show (true) or hide (false) the screen’s header at Lightning runtime. Classic runtime isn’t supported. The default value is true.

The header includes access to help text for the screen. If showHeader is hidden, use Lightning components on the screen to show help text.

This field is available in API version 42.0 and later.

stageReference

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

The API name of the stage resource that’s associated with the screen.

triggers

[FlowScreenTrigger](#FlowScreenTrigger)\[\]

An array of triggers configured for a flow screen field or a flow screen field attribute.

This field is available in API version 59.0 and later.

FlowScreenAction
----------------

Defines an action that can be triggered by one or more flow screen components.

This metadata type is available in API version 59.0 and later.

Field Name

Field Type

Description

actionName

string

Required. The API name of the flow screen action.

actionType

InvocableActionType (enumeration of type string)

Required. The flow screen action type. Valid values are:

*   flow—Invokes an autolaunched flow.

inputParameters

[FlowScreenActionInputParameter](#FlowScreenActionInputParameter)\[\]

An array of input parameters from the flow to the flow screen action.

label

string

Requiired. The label of the flow screen action.

nameSegment

string

The API name of the flow screen action.

versionSegment

int

The version number for the screen action.

versionString

string

Specifies the version of the screen action to be invoked.

This field is available in API version 63.0 and later.

FlowScreenActionInputParameter
------------------------------

Defines an iput parameter for a flow screen action. It extends [FlowScreenFieldInputParameter](#FlowScreenFieldInputParameter) and inherits all its fields.

This metadata type is available in API version 59.0 and later.

Field Name

Field Type

Description

name

string

Required. Unique name of the input parameter of a flow screen action.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the valueof an input parameter for a flow screen action.

FlowScreenField
---------------

Represents a screen component. FlowScreenField extends [FlowElement](#FlowElement) and inherits all its fields.

Field Name

Field Type

Description

choiceReferences

string\[\]

An array of references to FlowChoices or FlowDynamicChoiceSets. The resulting choice options appear in the order specified in this array, where the element at index 0 provides the top-most choice option. Supported for these types of screen components.

*   RadioButtons
*   DropdownBox
*   MultiSelectCheckboxes
*   MultiSelectPicklist

Multi-select checkboxes and multi-select picklist fields are available in API version 26.0 and later.

dataType

FlowDataType (enumeration of type string)

Data type of the screen component. Only supported for the InputField, RadioButtons, and DropdownBox types of screen components. Valid data types are:

*   Boolean
*   Currency
*   Date
*   DateTime
*   Number
*   String

Boolean input fields, which appear as checkbox fields at runtime, are available in API version 26.0 and later.

Only the string data type is supported for multi-select checkboxes and multi-select picklist fields. Multi-select fields are available in API version 26.0 and later.

Date/time input fields are available in API version 43.0 and later.

dataTypeMappings

[FlowDataTypeMapping](#FlowDataTypeMapping)\[\]

Reserved for future use.

defaultSelectedChoiceReference

string

The name of the FlowChoice element to use as the default value for the screen component. Supported for these types of screen components.

*   RadioButtons
*   DropdownBox
*   MultiSelectCheckboxes
*   MultiSelectPicklist

For DropdownBox field types only, if defaultSelectedChoiceReference is empty or null, the reference at index 0 of choiceReferences is used as the default value.

You can specify only one FlowChoice element as the default value for multi-select checkboxes and multi-select picklist fields. Multi-select fields are available in API version 26.0 and later.

defaultValue

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

The value that is used by default when the screen component requires users to provide input. Only supported for InputField, LargeTextArea, and PasswordField.

extensionName

string

The name of the Lightning component to display. This field is available in API version 42.0 and later.

fields

[FlowScreenField](#FlowScreenField)\[\]

An array of columns to display in a section, or an array of fields to display in a column. This field is available in API version 49.0 and later.

fieldText

string

Field label that is displayed on the screen. Supports merge fields.

fieldType

FlowScreenFieldType (enumeration of type string)

Required. The type of field to display on a flow screen. Valid values are:

*   DisplayText
*   InputField
*   LargeTextArea
*   PasswordField
*   RadioButtons
*   DropdownBox
*   MultiSelectCheckboxes—This value is available in API version 26.0 and later.
*   MultiSelectPicklist—This value is available in API version 26.0 and later.
*   ComponentInstance—This value is available in API version 42.0 and later.
*   ComponentChoice and ComponentInput—This value is available in API version 48.0 and later for the Survey processType value only.
*   Region— Specifies that a screen field in a section is a column. This value is available in API version 51.0 and later.
*   RegionContainer—Specifies that a screen field is a section. This value is available in API version 51.0 and later.
*   ObjectProvided—Specifies that a screen field is a field from a Salesforce object. This value is available in API version 51.0 and later.

At runtime, each multi-select field stores its field value as a concatenation of the user-selected choice values, separated by semicolons. Any semicolons in the selected choice values are removed when added to the multi-select field value.

helpText

string

Text that appears if the end user clicks the help icon (![info](https://developer.salesforce.com/docs/resources/img/en-us/256.0?doc_id=help%2Fimages%2Fvpm_info_up.png&folder=api_meta)) for the screen component.

Supports merge fields in API version 26.0 and later.

inputParameters

[FlowScreenFieldInputParameter](#FlowScreenFieldInputParameter)\[\]

An array of input parameters. Supported only when fieldType is ComponentInstance.

This field is available in API version 42.0 and later.

inputsOnNextNavToAssocScrn

FlowScreenFieldInputsRevisited (enumeration of type string)

Controls whether the flow remembers the input value if the user moves to any screen and then returns to the screen component. Valid values are:

*   UseStoredValues—Uses values from when the user last visited this screen.
*   ResetValues—Refreshes inputs to incorporate changes elsewhere in the flow.

The default value is UseStoredValues.

This property applies to screen components in API version 51.0 and later and to record fields on flow screens in API version 57.0 and later.

isRequired

boolean

Indicates whether the user must select a choice or provide input. Not supported for DisplayText or boolean inputField.

isVisible

boolean

objectFieldReference

string

Specifies the Salesforce object field for an ObjectProvided field.

outputParameters

[FlowScreenFieldOutputParameter](#FlowScreenFieldOutputParameter)\[\]

An array of output parameters. Supported only when fieldType is ComponentInstance and when storeOutputAutomatically is false.

This field is available in API version 42.0 and later.

regionContainerType

FlowRegionContainerType (enumeration of type string)

Stores information about a section component header. Possible values include:

*   SectionWithHeader
*   SectionWithoutHeader

Available only when the component type is Section. This field is available in API version 55.0 and later.

scale

int

Controls the number of digits to the right of the decimal point up to 17 places. If you leave this field blank or set it to zero, only whole numbers appear when your flow runs.

Available only when the data type is Number or Currency. Corresponds to the Decimal Places field in Flow Builder.

sourceTemplateApiName

string

The API name of the template specified by the provider. This field is available in API version 62.0 and later.

sourceTemplateProviderType

string

The API name of the source that provides the template. This field is available in API version 62.0 and later.

storeOutputAutomatically

boolean

Indicates whether the screen component’s output parameters are automatically available in the flow without creating any variables. When the value is true, you can reference an output parameter by specifying the name of the screen component and the output parameter, such as Mailing\_Address.City.

Supported only when fieldType is ComponentInstance.

This field is available in API version 47.0 and later.

styleProperties

[FlowScreenFieldStyleProperties](#FlowScreenFieldStyleProperties)

Specifies the style properties of a screen component.

This field is available in API version 64.0 and later.

validationRule

[FlowInputValidationRule](#FlowInputValidationRule)

A rule that’s used to validate the user input when the screen component is of type InputField, LargeTextArea, or PasswordField.

visibilityRule

[FlowVisibilityRule](#FlowVisibilityRule)

A condition-based rule that’s used to render or hide the screen component.

This field is available in API version 47.0 and later.

FlowScreenFieldInputParameter
-----------------------------

Defines an input parameter from the flow to the extension. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. FlowScreenFieldInputParameter is available in API version 42.0.

Field Name

Field Type

Description

name

string

Required. Unique name for the input parameter.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the input parameter.

FlowScreenFieldOutputParameter
------------------------------

Defines an output parameter from the extension to the flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. FlowScreenFieldOutputParameter is available in API version 42.0.

Field Name

Field Type

Description

assignToReference

string

Required. Specifies the variable to which you want to assign the output parameter value.

name

string

Required. Unique name for the output parameter.

FlowScreenFieldStyleProperties
------------------------------

Defines how a screen component looks on a screen element at run time.

This metadata type is available in API version 64.0 and later.

Field Name

Field type

Description

width

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

The number of columns the width of the screen component fills up in a screen element's 12-column wide spatial grid. Valid values are numbers 1 through 12.

verticalAlignment

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

The vertical alignment of the screen component. Valid values are top, middle, bottom.

FlowScreenTrigger
-----------------

Defines an event handler for a flow screen component.

This metadata type is available in API version 59.0 and later.

Field Name

Field Type

Description

eventName

string

Required. The API name of the event from eventSource that the trigger listens for.

eventSource

string

Required. The screen field, screen field attribute, action, or action attribute where eventName takes place.

handlers

[FlowScreenTriggerHandler](#FlowScreenTriggerHandler)\[\]

An array of flow screen handlers to conditionally run when the configured event is recevied.

FlowScreenTriggerHandler
------------------------

Defines conditions for a flow screen trigger handler.

This metadata type is available in API version 59.0 and later.

Field Name

Field Type

Description

conditionLogic

string

Specifies logic for the conditions. Valid values are:

*   and—Evaluates to true only if all its conditions evaluate to true
*   or—Evaluates to true if any of its conditions evaluate to true
*   Advanced logic like 1 AND (2 OR 3)—Evaluates to true if the first condition is true and either the second or third condition if true.
    
    When you use advanced logic, the string must consist of 1,000 or fewer characters.
    

This field is available in API version 63.0 and later.

conditions

[FlowCondition](#FlowCondition)\[\]

An array of conditions that must be true to trigger the handler.

This field is available in API version 63.0 and later.

screenActionName

string

Required. The API name of the FlowScreenAction to run when conditions are met.

FlowStage
---------

A section of your flow that can be represented in the UI, such as with breadcrumbs. It extends [FlowElement](#FlowElement) and inherits all its fields.

When an interview starts, any stages where isActive is true are added to the $Flow.ActiveStages global variable, which holds a collection of stages. Each stage’s stageOrder determines the order they’re added in. The stage with the lowest stageOrder is assigned to the $Flow.CurrentStage global variable.

Field Name

Field Type

Description

isActive

boolean

Indicates whether the stage is active by default.

label

string

A user-friendly label for this stage.

stageOrder

int

Indicates how the stage is ordered against other stages. The stageOrder value must be unique within the flow.

FlowStageStep
-------------

A step resource defines a step within a stage node. This metadata type is available in API version 53.0 and later.

Field Name

Field Type

Description

actionName

string

Required. Name of the flow associated with the step.

actionType

InvocableActionType (enumeration of type string)

Required. The type of the step. Valid values are:

*   createFieldGnrnPromptTmplResp—This value is available in API version 62.0 and later.
*   exploreConversation—This value is available in API version 61.0 and later.
*   stepBackground
*   stepInteractive
*   stepMuleSoft

assignees

[FlowStageStepAssignee](#subtype_FlowStageStepAssignee)

An array of users, groups, or queues that are assigned to complete the interactive step.

canAssigneeEdit

boolean

Reserved for future use.

entryActionInputParameters

[FlowStageStepEntryActionInputParameter](#subtype_FlowStageStepEntryActionInputParameter)\[\]

An array of input parameters from the step to the evaluation flow that are used as an entry condition for the step.

entryActionName

string

The name of the evaluation flow used as an entry condition for the step.

entryActionOutputParameters

[FlowStageStepEntryActionOutputParameter](#subtype_FlowStageStepEntryActionOutputParameter)\[\]

An array of output parameters from the evaluation flow to the step used to determine if the step can be started.

entryActionType

InvocableActionType (enumeration of type string)

The type of the evaluation flow used as a custom entry condition for the step. Valid values are:

*   EvaluationFlow
*   exploreConversation—This value is available in API version 61.0 and later.

entryConditionLogic

string

Defines how the entry requirements for a step are evaluated. Valid values are:

*   And
*   Or
*   Custom logic, such as (1 AND (2 OR 3))
*   Formula

entryConditions

[FlowCondition](#FlowCondition)\[\]

An array of requirements that must be met to start the step.

exitActionInputParameters

[FlowStageStepExitActionInputParameter](#subtype_FlowStageStepExitActionInputParameter)\[\]

An array of input parameters from the step to the evaluation flow. These parameters specify an exit condition for the step.

exitActionName

string

The name of the step exit evaluation flow.

exitActionOutputParameters

[FlowStageStepExitActionOutputParameter](#subtype_FlowStageStepExitActionOutputParameter)\[\]

An array of output parameters from the evaluation flow to the step. These parameters specify an exit condition for the step.

exitActionType

InvocableActionType (enumeration of type string)

The type of the evaluation flow used as a custom exit condition for the step. The only possible value are:

*   EvaluationFlow
*   exploreConversation—This value is available in API version 61.0 and later.

.

exitConditionLogic

string

Defines how the exit requirements for an interactive step are evaluated. Valid values are:

*   And
*   Or
*   Custom logic, such as (1 AND (2 OR 3))
*   Formula

exitConditions

[FlowCondition](#FlowCondition)\[\]

An array of requirements to be met for exiting an interactive step.

inputParameters

[FlowStageStepInputParameter](#subtype_FlowStageStepInputParameter)\[\]

An array of input parameters from the step to its associated flow.

label

string

Required. The label for the step.

outputParameters

[FlowStageStepOutputParameter](#subtype_FlowStageStepOutputParameter)\[\]

An array of output parameters from a flow to its associated step.

requiresAsyncProcessing

boolean

Not used in API version 63.0.

shouldLock

boolean

Reserved for future use.

stepSubtype

FlowElementSubtype (enumeration of type string)

Reserved for internal use.

FlowStageStepAssignee
---------------------

An assignee associated with an Interactive step. Applicable only for interactive steps. This metadata type is available in API version 53.0 and later.

Field Name

Field Type

Description

assignee

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Names of the user, group, or queue assigned to the interactive step.

assigneeType

FlowStageStepAssigneeType (enumeration of type string)

Required. The type of the assignee associated with the interactive step. Valid values are:

*   Group
*   Queue
*   User
*   invalid— This value is available in API version 61.0 and later.

FlowStageStepEntryActionInputParameter
--------------------------------------

Defines an input parameter from the step to its associated evaluation flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 53.0 and later.

Field Name

Field Type

Description

name

string

Required. The unique name for the input parameter of the evaluation flow used by a step as an entry condition.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the input parameter of the evaluation flow used by a step as an entry condition.

FlowStageStepEntryActionOutputParameter
---------------------------------------

Defines an output parameter from an evaluation flow used to determine if the step meets entry criteria. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 53.0 and later.

Field Name

Field Type

Description

assignToReference

string

Reserved for future use.

name

string

Required. A unique name for the output parameter of the evaluation flow used by a step as an entry condition. Valid values are:

*   isOrchestrationConditionMet

FlowStageStepExitActionInputParameter
-------------------------------------

Defines an input parameter from the stage or step to its associated evaluation flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 53.0 and later.

Field Name

Field Type

Description

name

string

Required. A unique name for the input parameter of the evaluation flow used by a stage or step as an exit condition.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the input parameter of the evaluation flow used by a stage or step as an exit condition.

FlowStageStepExitActionOutputParameter
--------------------------------------

Defines an output parameter from an evaluation flow used to determine if the stage or step meets exit criteria. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 53.0 and later.

Field Name

Field Type

Description

assignToReference

string

Reserved for future use.

name

string

Required. A unique name for the output parameter of the evaluation flow used by a stage or step as an exit condition. The only possible value is isOrchestrationConditionMet.

FlowStageStepInputParameter
---------------------------

Defines an input parameter from the step to the flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 53.0 and later.

Field Name

Field Type

Description

name

string

Required. Unique name for the input parameter for a flow associated with the step.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the input parameter of the flow associated with a step.

FlowStageStepOutputParameter
----------------------------

Defines an output parameter from the step to the flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 53.0 and later.

Field Name

Field Type

Description

assignToReference

string

Reserved for future use.

name

string

Required. Unique name for the output parameter for a flow associated with the step.

FlowStart
---------

Represents the flow’s Start element, which specifies how the flow starts. In an autolaunched flow, the Start element also defines when and how frequently to run the flow. To run the flow only for specific records, the Start element can define filter criteria.

FlowStart extends [FlowNode](#FlowNode) and inherits all its fields except name and label. This metadata type is available in API version 47.0 and later.

Field Name

Field Type

Description

capabilityTypes

[FlowCapability](#FlowCapability)\[\]

An array of capabilities that can pass data with the flow. Only one capability is supported in API version 60.0 and later. This field is available in API version 60.0 and later.

connector

[FlowConnector](#FlowConnector)

Specifies which element to execute first.

dataGraph

string

The data graph associated with the flow. Reference fields from this data graph throughout the flow. This field is available in API version 61.0 and later.

dataTypeMappings

[FlowDataTypeMapping](#FlowDataTypeMapping)\[\]

An array of data type mappings for input and output values that have the generic sObject data type. This field is available in API version 63.0 and later.

doesRequireRecordChangedToMeetCriteria

boolean

If set to true, conditions evaluate to true only if the record didn’t meet the required conditions before the triggering update but now meets the conditions after the update. This field is available in API version 50.0 and later.

entryType

FlowEntryType (enumeration of type string)

Specifies when a unified individual can join a flow. Valid values are:

*   AfterCompletion—Unified individuals can join the flow only after they complete all previous flow runs of the same flow definition.
*   Always—Unified individuals can always join the flow.

This field is available in API version 60.0 and later.

eventName

string

The name of the automation event that triggers the automation event-triggered flow. Valid values are:

*   trgrOnSmsSubscription
*   trgrOnEmailSubscription
*   trgrOnOrderPlacement
*   The API name of a form
*   The API name of an external service

This field is available in API version 61.0 and later.

eventType

InvocableActionType (enumeration of type string)

The type of the automation event that triggers the automation event-triggered flow. Valid values are:

*   exploreConversation—This value is available in API version 61.0 and later.
*   externalEvent
*   processWebStoreUserRgstr
*   trgrOnEmailBounceEngagement
*   trgrOnEmailLinkClickEngagement
*   trgrOnEmailOpenEngagement
*   trgrOnEmailSubscription
*   trgrOnFormSubmission
*   trgrOnOrderPlacement
*   trgrOnSmsDeliveryFailureEngagement
*   trgrOnSmsLinkClickEngagement
*   trgrOnSmsResponseEngagement
*   trgrOnSmsSubscription
*   trgrOnWebCartAbandoned
*   trgrOnWhatsAppDeliveredEngagement
*   trgrOnWhatsAppDlvrFailureEngmt
*   trgrOnWhatsAppLinkClickEngmt
*   trgrOnWhatsAppReadEngagement
*   trgrOnWhatsAppResponseEngmt
*   trgrOnWhatsAppSubscription

filterFormula

string

A formula that’s used to filter what records execute the flow during a save. Available only in record-triggered flows. This field is available in API version 55.0 and later.

filterLogic

string

The filter logic that’s applied to the filter condition requirements. To require all conditions, use AND. To require any conditions, use OR. For custom condition logic, enter the entire logic string, for example 1 AND 2 OR (3 AND 4). This field is available in API version 50.0 and later.

filters

[FlowRecordFilter](#FlowRecordFilter)\[\]

An array of filters to apply when retrieving records from the database. For example, filter accounts to include only the records that haven’t been updated in the last 4 weeks.

flowRunAsUser

string

Specifies who to run the flow as. Possible values are:

*   TriggeringUser—Run the flow as the user that triggered the flow.
*   DefaultWorkflowUser—Run the flow as the default workflow user.

This field is available in API version 60.0 and later.

form

string

Required only for form-triggered flows. The content key value for the form used to trigger the flow. This field is available in API version 59.0 and later.

inputs

[FlowStartInputParameter](#FlowStartInputParameter)\[\]

An array of inputs to the Start element.

object

string

The object whose records you want to retrieve from the database. A flow interview starts for each record that meets the filter conditions.

publishSegment

boolean

Indicates whether to republish the segment and update segment membership before the flow runs or on the segment’s Data Cloud publish schedule. When the value is true, the segment is immediately republished before the flow runs, and ignores the segment's publish schedule. When the value is false, the segment is republished on the segment's Data Cloud publish schedule, but the segment isn't republished if the schedule is set to Do not refresh.

The default value is false.

This field is available in API version 60.0 and later.

recordTriggerType

RecordTriggerType (enumeration of type string)

Specifies what type of record changes can start the flow. Possible values are:

*   Create—When a record is created.
*   Update—When a record is updated.
*   CreateAndUpdate—When a record is created and updated.
*   Delete—When a record is deleted. This value is available in API version 50.0 and later.
*   None—For flows that aren’t record-triggered flows. This value is available in API version 55.0 and later.

Available only when triggerType is RecordBeforeSave or DataCloudDataChange. This field is available in API version 48.0 and later.

schedule

[FlowSchedule](#FlowSchedule)

Required when triggerType is Scheduled. Specifies when and how frequently the flow runs.

scheduledPaths

[FlowScheduledPath](#FlowScheduledPath)\[\]

Specifies the flow’s scheduled paths. This field is available in API version 51.0 and later.

segment

string

The segment used to trigger the flow. This field is available in API version 56.0 and later.

TimeZoneSidKey

string

Reserved for future use.

triggeringDataGraph

string

The API name of the data graph that includes the data model object that triggers the automation event-triggered flow. This field is available in API version 63.0 and later.

triggeringDataModelObjectPath

string

The Data Cloud path to the data model object that triggers the automation event-triggered flow. This field is available in API version 63.0 and later.

triggerType

FlowTriggerType (enumeration of type string)

Specifies what causes the flow to run. If you exclude this field, the flow has no trigger and starts only when a user or app launches the flow. Possible values are:

*   AutomationEvent—The flow starts when an automation event such as an SMS subscription occurs. This value is available in API version 62.0 and later.
*   Capability—When capabilityTypes is set, the flow starts when the capability is run. This value is available in API version 60.0 and later.
*   DataCloudDataChange— The flow starts when data model object (DMO) or calculated insight object (CIO) conditions are met. This value is available in API version 59.0 and later.
*   DataGraphDataChange— The flow starts when conditions are met in the specified data graph field. This value is available in API version 63.0 and later.
*   EventDrivenJourney—Reserved for internal use.
*   ExternalSystemChange
*   —The flow starts when a relevant change is detected in an external system. This value is available in API version 62.0 and later.
*   PlatformEvent—The flow starts when a platform event message is received. This value is available in API version 49.0 and later.
*   RecordAfterSave—The flow starts after a record is saved. This value is available in API version 49.0 and later.
*   RecordBeforeDelete—Deleting a record triggers an autolaunched flow before the record is deleted from the database. This value is available in API version 50.0 and later.
*   RecordBeforeSave—Creating and/or updating a record triggers an autolaunched flow to make more updates to that record before it’s saved to the database. This value is available in API version 48.0 and later.
*   Scheduled—The flow starts at the scheduled time. This value is available in API version 47.0 and later.
*   ScheduledJourney— The flow starts only at the scheduled time and frequency. This value is available in API version 49.0 and later.
*   Segment— At the scheduled time, the flow send emails to individuals included in the chosen segment. This value is available in API version 56.0 and later.

Available only when processType is AutoLaunchedFlow or PromptFlow. This field is available in API version 47.0 and later.

FlowCapability
--------------

Defines the data structure of a capability. When the capability is invoked, it triggers the flow to run and data is passed between the flow and capability. It extends [FlowElement](#FlowElement) and inherits all of its fields. This metadata type is available in API version 60.0 and later.

Field Name

Field Type

Description

capabilityName

string

Required. The specified capability that the flow integrates with. The valid format is Name://Name, for example, PromptBuilder://SalesEmail

inputs

[FlowCapabilityInput](#FlowCapabilityInput)\[\]

An array of capability inputs. The flow sets the input values and passes the data to the capability.

FlowCapabilityInput
-------------------

Defines the data structure of a capability input. It extends [FlowElement](#FlowElement) and inherits all of its fields. This metadata type is available in API version 60.0 and later.

Field Name

Field Type

Description

capabilityInputName

string

Required. The input name is the same for the capability and the flow.

dataType

string

The data type of the capability input. Valid types are:

*   Boolean—This value is available in API version 61.0 and later.
*   Currency—This value is available in API version 61.0 and later.
*   Date—This value is available in API version 61.0 and later.
*   Number—This value is available in API version 61.0 and later.
*   sObject—This value corresponds to a record variable. This value is available in API version 60.0 and later.
*   String—This value is available in API version 61.0 and later.

isCollection

boolean

Required. Indicates whether the input is a collection of values. The default value is false.

FlowStartInputParameter
-----------------------

Defines an input parameter to the flow Start element. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 62.0 and later.

Field Name

Field Type

Description

name

string

Required. The unique name for the input parameter to the Start element.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the input parameter to the Start element.

FlowStep
--------

Steps function as placeholders when you’re building a flow. It extends [FlowNode](#FlowNode) and inherits all its fields.

Field Name

Field Type

Description

connectors

[FlowConnector](#FlowConnector)\[\]

Specifies which node to execute after the step node.

FlowSubflow
-----------

A subflow element references another flow, which it calls at run time. The flow that contains the subflow element is referred to as the parent flow. FlowSubflow extends [FlowNode](#FlowNode) and inherits all its fields. It’s available in API version 25.0 and later.

Field Name

Field Type

Description

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute after the subflow.

flowName

string

References the flow to call at runtime. The value must be an API name of a flow and it can’t contain an appended hyphen and version number.

inputAssignments

[FlowSubflowInputAssignment](#FlowSubflowInputAssignment)\[\]

An array of input variable assignments that are set at the start of the flow.

outputAssignments

[FlowSubflowOutputAssignment](#FlowSubflowOutputAssignment)\[\]

An array of output variable assignments that are set at the end of the flow.

storeOutputAutomatically

boolean

Indicates whether the subflow’s output parameters are automatically available in the flow without creating any variables. When the value is true, you can reference an output parameter by specifying the API name of the subflow in the flow. When the value is false, create variables manually to store output values from the subflow. The default value is false.

This field is available in API version 49.0 and later.

FlowSubflowInputAssignment
--------------------------

Assigns an element or value from the parent flow to a variable in the referenced flow. Input assignments occur when the subflow calls the referenced flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. It’s available in API version 25.0 and later.

Field Name

Field Type

Description

name

string

Required. Unique name for the variable in the referenced flow.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value to assign to the variable.

FlowSubflowOutputAssignment
---------------------------

Assigns the value of a variable from the referenced flow to a variable in the parent flow. Output assignments occur when the referenced flow is finished running. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. It’s available in API version 25.0 and later.

Field Name

Field Type

Description

assignToReference

string

Unique name for the variable in the parent flow.

name

string

Required. Unique name for the variable in the referenced flow.

FlowTransform
-------------

Defines a node that can dynamically transform the value of source data to target data in the flow. It extends [FlowNode](#FlowNode) and inherits all of its fields. This metadata type is available in API version 59.0 and later.

Field Name

Field Type

Description

apexClass

string

The Apex class of the target data after transformation if its data type is Apex.

connector

[FlowConnector](#FlowConnector)\[\]

Specifies which node to execute after this data transformation.

dataType

FlowDataType (enumeration of type string)

Required. Specifies the data type of the transformed data. In Flow Builder, it corresponds to the target data in the Transform element. Valid types are:

*   Apex
*   Boolean—This value is available in API version 62.0.
*   Currency—This value is available in API version 62.0.
*   Date—This value is available in API version 62.0.
*   DateTime—This value is available in API version 62.0.
*   Number—This value is available in API version 62.0.
*   String—This value is available in API version 62.0.
*   sObject—This value corresponds to a record variable.

isCollection

boolean

Indicates whether the variable is a collection of values. The default value is false.

objectType

string

Object type of this variable resource if its data type is sObject.

scale

int

Controls the number of digits to the right of the decimal point up to 17 places. If you leave this field blank or set it to zero, only whole numbers appear when your flow runs.

Corresponds to the Decimal Places field in Flow Builder.

storeOutputAutomatically

boolean

Reserved for future use.

transformValues

[FlowTransformValue](#FlowTransformValue)\[\]

An array of values for data transformation

FlowTransformValue
------------------

Defines the values for transforming specific data in the flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 59.0 and later.

Field Name

Field Type

Description

transformValueActions

[FlowTransformValueAction](#FlowTransformValueAction)\[\]

An array of actions for data transformation

transformValueName

string

Reserved for future use.

transformValueLabel

string

Reserved for future use.

transformValueDescription

string

Reserved for future use.

FlowTransformValueAction
------------------------

Defines the data and actions to transform in the flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. This metadata type is available in API version 59.0 and later.

Field Name

Field Type

Description

actionName

string

Reserved for future use.

actionType

InvocableActionType (enumeration of type string)

Reserved for future use.

actionVersionString

string

Reserved for future use.

assignToReference

string

Reserved for future use.

inputParameters

[FlowTransformValueActionInputParameter](#FlowTransformValueActionInputParameter)\[\]

An array of input parameters for data transformation. This field is available in API version 60.0 and later.

outputFieldApiName

string

The API name of the field for transformed data in a data transformation mapping. In Flow Builder, it corresponds to the target data field in the Transform element.

transformType

FlowTransformValueActionType (enumeration of type string)

Required. The type of transformation from source data to target data. Valid types are:

*   Count—Calculates the number of items in a source collection.
*   GetItemByIndex—Reserved for future use.
*   InnerJoin—Joins selected data from two source collections that are stored in a target collection in a flow. This value is available in API version 63.0 and later. See complexValueType on [FlowElementReferenceOrValue](#FlowElementReferenceOrValue).
*   InvocableAction—Reserved for future use.
*   Map—Specifies a mapping between the datasets in flows. In Flow Builder, it corresponds to the mapping between source data fields and target data fields.
*   Sum—Adds the numeric values of a field on each item in a collection.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the transformed data. In Flow Builder, the value of this field corresponds to the result of the target data field in the Transform element.

FlowTransformValueActionInputParameter
--------------------------------------

Defines the input parameters of the source data for data transformation. This metadata type is available in API version 60.0 and later.

Field Name

Field Type

Description

name

string

A key that specifies the configuration of input parameters for this data transformation when transformType is set to Sum or Count. Valid values are:

*   aggregationField—The field on each item in a source collection that’s used to calculate the transformed value.
*   aggregationValues—The source collection that’s used to calculate the transformed value.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the specified key in name.

FlowTextTemplate
----------------

Defines a text template that can be used throughout the flow. It extends [FlowElement](#FlowElement) and inherits all its fields.

Field Name

Field Type

Description

isViewedAsPlainText

boolean

If set to true, the flow resource remembers the View as Plain Text setting used for the text template after the flow resource is saved. If set to false, the flow resource uses the View as Rich Text setting.

The default value is false.

text

string

Actual text of the template. Supports merge fields.

FlowVariable
------------

With variables, creates updatable values to use in the flow. FlowVariable extends [FlowElement](#FlowElement) and inherits all its fields.

Field Name

Field Type

Description

apexClass

string

The Apex class of this variable if its data type is Apex. This field is available in API version 46.0 and later.

dataType

FlowDataType (enumeration of type string)

Required. Valid types are:

*   Apex—This value is available in API version 46.0 and later.
*   Boolean
*   Currency
*   Date
*   DateTime—This value is available in API version 30.0 and later.
*   Number
*   Multipicklist—This value is available in API version 34.0 and later.
*   Picklist—This value is available in API version 34.0 and later.
*   String
*   sObject—This value corresponds to a record variable.

isCollection

boolean

Indicates whether the variable is a collection of values. This field is available in API version 30.0 and later. In API version 32.0 and later, a collection variable can be of any data type.

The default value is False.

isInput

boolean

Indicates whether the variable can be set at the start of the flow using URL parameters, Visualforce controllers, or subflow inputs. This field is available in API version 25.0 and later.

Default value:

*   False for a variable created in API version 25.0 and later or in the Flow Builder in Summer ’12 and later.
*   True for a variable created in API version 24.0 or in Flow Builder in Spring ’12 and earlier.

Disabling input or output access for an existing variable can break the functionality of applications and pages that call the flow and access the variable. For example, you can access variables from URL parameters, processes, and other flows.

isOutput

boolean

Indicates whether the variable’s value can be accessed from Visualforce controllers and other flows. This field is available in API version 25.0 and later.

Default value:

*   False for a variable created in API version 25.0 and later or in the Flow Builder in Summer ’12 and later.
*   True for a variable created in API version 24.0 or in Flow Builder in Spring ’12 and earlier.

Disabling input or output access for an existing variable can break the functionality of applications and pages that call the flow and access the variable. For example, you can access variables from URL parameters, processes, and other flows.

objectType

string

Object type of this variable if its data type is sObject.

scale

int

Controls the number of digits to the right of the decimal point up to 17 places. If you leave this field blank or set it to zero, only whole numbers appear when your flow runs.

Corresponds to the Decimal Places field in Flow Builder.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Default value of this variable.

Default values aren’t supported if the variable’s data type is Picklist or Multipicklist.

FlowVisibilityRule
------------------

Visibility rules render a flow screen component when visibility rule conditions are met. Hides a flow screen component when visibility rule conditions aren’t met. This metadata type is available in API version 47.0 and later.

Field Name

Field Type

Description

conditionLogic

string

Specifies logic for the conditions. Value can be:

*   and—Evaluates to true only if all its conditions evaluate to true.
*   or—Evaluates to true if any of its conditions evaluate to true.
*   Advanced logic like 1 AND (2 OR 3)—Evaluates to true if the first condition is true and either the second or third condition is true.
    
    When you use advanced logic, the string must consist of 1,000 or fewer characters.
    

conditions

[FlowCondition](#FlowCondition)\[\]

An array of conditions that must be true for the flow to wait for this event.

FlowWait
--------

Waits for one or more defined events to occur. FlowWait extends [FlowNode](#FlowNode) and inherits all its fields. FlowWait is available in API version 32.0 and later.

Field Name

Field Type

Description

defaultConnector

[FlowConnector](#FlowConnector)

Specifies which node to execute if the conditions are false for every event in the Wait element.

defaultConnectorLabel

string

Label for the default connector.

faultConnector

[FlowConnector](#FlowConnector)

Specifies which node to execute if the attempt to wait results in an error. If any of the wait events fail, the flow takes the fault connector.

timeZoneId

string

Reserved for future use.

waitEvents

[FlowWaitEvent](#FlowWaitEvent)\[\]

An array of events that the Wait element is waiting for.

If the conditions for every event evaluate to false, the defaultConnector is used.

FlowWaitEvent
-------------

An event that a FlowWait element is waiting for. FlowWaitEvent extends [FlowElement](#FlowElement) and inherits all its fields. FlowWaitEvent is available in API version 32.0 and later.

Field Name

Field Type

Description

conditionLogic

string

Specifies logic for the conditions. Value can be:

*   and—Evaluates to true only if all its conditions evaluate to true
*   or—Evaluates to true if any of its conditions evaluate to true
*   Advanced logic like 1 AND (2 OR 3)—Evaluates to true if the first condition is true and either the second or third condition is true
    
    When you use advanced logic, the string must consist of 1,000 or fewer characters.
    

associatedElement

string

The API name of the event that resumes the flow. This field is available in API version 60.0 and later.

conditions

[FlowCondition](#FlowCondition)\[\]

An array of conditions that must be true for the flow to wait for this event.

automationEventName

string

Name of the automation event that the Wait element is waiting for.

automationEventType

InvocableActionType (enumeration of type string)

The type of the automation event that triggers the Wait element is waiting for. Valid values are:

*   exploreConversation—This value is available in API version 61.0 and later.
*   trgrOnSmsSubscription
*   trgrOnEmailSubscription
*   trgrOnOrderPlacement
*   trgrOnFormSubmission

connector

[FlowConnector](#FlowConnector)

Specifies which node to execute if this event is the first event that occurs.

eventType

string

Required. The event’s type. The type determines which input parameters are available to define this event. Valid values are:

*   AlarmEvent—This event is an alarm based off an absolute date/time value.
*   DateRefAlarmEvent—This event is an alarm based off a date/time field on a record.

extendUntil

Time

Reserved for future use.

filters

[FlowRecordFilter](#FlowRecordFilter)\[\]

An array of filters to apply when retrieving records from the database. For example, filter accounts to include only the records that haven’t been updated in the last 4 weeks. This field is available in API version 60.0 and later.

filterlogic

string

The filter logic that’s applied to the filter condition requirements. To require all conditions, use AND. To require any conditions, use OR. For custom condition logic, enter the entire logic string, for example 1 AND 2 OR (3 AND 4). This field is available in API version 60.0 and later.

inputParameters

[FlowWaitEventInputParameter](#FlowWaitInputParameter)\[\]

An array of the event’s input parameters. The parameter values are set by using values from the flow.

interactionType

FlowWaitInteractionType (enumeration of type string)

Specifies what type of event can resume the flow. Possible values are:

*   SmsResponse—An SMS response event
*   WhatsappResponse—A WhatsApp response event

This field is available in API version 62.0 and later.

label

string

Required. Label for the wait event.

object

string

The object that contains the event you want to use to resume the flow. This field is available in API version 60.0 and later.

offset

int

Reserved for future use.

offsetUnit

FlowScheduledPathOffsetUnit (enumeration of type string)

Reserved for future use.

outputParameters

[FlowWaitEventOutputParameter](#FlowWaitOutputParameter)\[\]

An array of the event’s output parameters. The parameter values are assigned from the event to variables in the flow.

recordTriggerType

RecordTriggerType

Specifies what type of record changes can resume the flow. Possible values are:

*   Create—When a related record is created
*   Update—When a related record is updated
*   CreateAndUpdate—When a related record is created and updated

This field is available in API version 60.0 and later.

FlowWaitEventInputParameter
---------------------------

An input parameter for FlowWaitEvent. The parameter’s value is set by using values from the flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. FlowWaitEventInputParameter is available in API version 32.0 and later.

Field Name

Field Type

Description

name

string

Unique name for the input parameter.

value

[FlowElementReferenceOrValue](#FlowElementReferenceOrValue)

Defines the value of the input parameter.

FlowWaitEventOutputParameter
----------------------------

An output parameter for FlowWaitEvent. The parameter’s value is assigned to a variable in the flow so that it can be referenced in another part of the flow. It extends [FlowBaseElement](#FlowBaseElement) and inherits all its fields. FlowWaitEventOutputParameter is available in API version 32.0 and later.

Field Name

Field Type

Description

assignToReference

string

Required. Specifies the variable to which you want to assign the output parameter value.

name

string

Required. Unique name for the output parameter.

Upgrade Flow Files to API Version 44.0 or Later
-----------------------------------------------

In API version 43.0 and earlier, the Flow object’s fullName field included the flow’s version number. Starting in API version 44, the field no longer includes the version number. Before you deploy using API version 44.0 via Metadata API or Salesforce CLI, make sure that:

*   The flows directory doesn’t include any unused flow versions.
*   For each active flow, the status field is Active. Any flow without a status value is deployed or retrieved with a status value of Draft.
*   The flowDefinitions directory is empty.

For Metadata API only.

*   The package.xml file is set to API version 44.0.
*   For the latest version of each flow, the file name doesn’t include a version number. For example, change myflow-3.flow to myflow.flow.

For Salesforce CLI only.

*   The sfdx-project.json file is set to "sourceApiVersion": "44.0".
*   For the latest version of each flow, the file name doesn’t include a version number. For example, change myflow-1.flow-meta.xml to myflow.flow-meta.xml.

As part of this upgrade, flow definitions are no longer necessary when you deploy or retrieve via Metadata API. If you deploy with flow definitions, the active version numbers in the flow definitions override the status fields in the flows. For example, the active version number in the flow definition is version 3, and the latest version of the flow is version 4 with the status field as Active. After you deploy your flow, the active version is version 3.

After you finished this upgrade, you can integrate with a version control system without worrying about flow file names changing. To reduce deployment issues when you push the source code into a scratch org, make sure that you don’t reuse an existing scratch org.

For more information, see [Deploy Processes and Flows as Active](https://help.salesforce.com/s/articleView?id=sf.flow_distribute_deploy_active.htm&language=en_US) in _Salesforce Help_.

Declarative Metadata Sample Definition
--------------------------------------

Here’s a sample XML definition of a flow.

Wildcard Support in the Manifest File
-------------------------------------

This metadata type supports the wildcard character \* (asterisk) in the package.xml manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm "The deploy() and retrieve() calls are used to deploy and retrieve a .zip file. Within the .zip file is a project manifest (package.xml) that lists what to retrieve or deploy, and one or more XML components that are organized into folders.").

#### See Also

*   [_Salesforce Help_: Deploy Processes and Flows as Active](https://help.salesforce.com/s/articleView?id=sf.flow_distribute_deploy_active.htm&language=en_US)