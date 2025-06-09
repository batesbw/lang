**NEVER** put a DML statement inside of a loop

**NEVER** put a SOQL query inside of a loop

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
