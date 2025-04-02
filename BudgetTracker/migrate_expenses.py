import boto3

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")

# Define old and new tables
old_table = dynamodb.Table('ExpensesTable')
new_table = dynamodb.Table('ExpensesTableV2')  # New table with correct schema

# Scan old table
response = old_table.scan()
items = response.get('Items', [])

# Migrate data with fixed transaction_id
for item in items:
    # ✅ Identify incorrect transaction_id key
    incorrect_key = next((key for key in item.keys() if key.strip() == "transaction_id"), None)

    if incorrect_key:
        item['transaction_id'] = item.pop(incorrect_key).strip()  # ✅ Rename & fix spaces
    else:
        print(f"⚠️ Skipping item with missing transaction_id: {item}")
        continue  # Skip the item if transaction_id is missing

    # ✅ Insert item into the new table
    new_table.put_item(Item=item)

print(f"✅ Successfully migrated {len(items)} records to ExpensesTableV2.")
