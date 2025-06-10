## Performance Rules

### DML Operations in Loops
- **Rule**: Do not place Create Records, Update Records, or Delete Records elements inside Loop elements
- **Reason**: Each DML operation counts against governor limits. In a loop, this can quickly exceed the 150 DML operations limit per transaction
- **Solution**: Collect records in variables/collections within the loop, then perform bulk DML operations outside the loop

### SOQL Queries in Loops  
- **Rule**: Do not place Get Records elements inside Loop elements
- **Reason**: Each SOQL query counts against governor limits. In a loop, this can quickly exceed the 100 SOQL queries limit per transaction
- **Solution**: Query all needed records before the loop starts, then filter or process the collection within the loop

## Examples

### ❌ Incorrect - DML in Loop
```
Loop Element (iterating through Accounts)
  └─ Update Records (updating each Account individually)
```

### ✅ Correct - Bulk DML Outside Loop
```
Assignment Element (build collection of Accounts to update)
Loop Element (iterating through source data)
  └─ Assignment Element (add Account to collection variable)
Update Records (bulk update the collection)
```

### ❌ Incorrect - SOQL in Loop
```
Loop Element (iterating through Account IDs)
  └─ Get Records (query Contacts for each Account)
```

### ✅ Correct - Query Before Loop
```
Get Records (query all needed Contacts upfront)
Loop Element (iterating through Contact collection)
  └─ Assignment/Decision Elements (process each Contact)
```

## Deployment and Validation Errors

### You can't use the outputAssignments field with the storeOutputAutomatically field. Remove the value for the outputAssignments field and try again.
- **Reason**: This error occurs when a Flow element has both:
outputAssignments field populated with manual assignments
storeOutputAutomatically field set to true
These two approaches are mutually exclusive in Salesforce Flows - you cannot use both simultaneously.
- **Solution**: Option 1: Automatic Storage (storeOutputAutomatically)
When storeOutputAutomatically="true":
Salesforce automatically creates variables to store the output values
Variable names are auto-generated based on the component API names
No manual outputAssignments needed
Option 2: Manual Assignments (outputAssignments)
When using outputAssignments:
You manually specify which variables receive which values
You have full control over variable names and assignments
storeOutputAutomatically should be false or omitted
