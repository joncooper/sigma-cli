# sigma-cli Examples

Practical examples for common sigma-cli use cases.

## Table of Contents

- [Setup and Configuration](#setup-and-configuration)
- [Workbook Management](#workbook-management)
- [Connection Management](#connection-management)
- [Data Export and Backup](#data-export-and-backup)
- [Automation Scripts](#automation-scripts)
- [Advanced Workflows](#advanced-workflows)

## Setup and Configuration

### Initial Setup

```bash
# Configure credentials interactively
sigma config \
  --client-id "your-client-id-here" \
  --secret "your-secret-here" \
  --base-url "https://aws-api.sigmacomputing.com/v2"

# Verify configuration
sigma config --show
```

### Using Environment Variables

```bash
# Set credentials via environment
export SIGMA_CLIENT_ID="your-client-id"
export SIGMA_SECRET="your-secret"
export SIGMA_BASE_URL="https://aws-api.sigmacomputing.com/v2"

# Now all commands will use these credentials
sigma workbooks list
```

### Using .env File

```bash
# Create .env file
cat > .env <<EOF
SIGMA_CLIENT_ID=your-client-id
SIGMA_SECRET=your-secret
SIGMA_BASE_URL=https://aws-api.sigmacomputing.com/v2
EOF

# Commands automatically load .env
sigma workbooks list
```

## Workbook Management

### List and Search Workbooks

```bash
# List all workbooks
sigma workbooks list

# List as table
sigma workbooks list --table

# Search by name
sigma workbooks list --search "Sales Dashboard"

# Limit results
sigma workbooks list --limit 10

# Combine filters
sigma workbooks list --search "Sales" --limit 5 --table
```

### Create Workbooks

```bash
# Create from command line
sigma workbooks create --name "My New Workbook"

# Create with JSON
sigma workbooks create --json '{
  "name": "Q4 Analysis",
  "description": "Quarterly analysis workbook"
}'

# Create from file
cat > workbook.json <<EOF
{
  "name": "Customer Analytics",
  "description": "Customer behavior analysis"
}
EOF
sigma workbooks create --file workbook.json

# Create from stdin
echo '{"name": "Test Workbook"}' | sigma workbooks create
```

### Update and Delete

```bash
# Get workbook ID
WORKBOOK_ID="wb_abc123def456"

# Update workbook name
sigma workbooks update $WORKBOOK_ID --name "Updated Name"

# Update with JSON
sigma workbooks update $WORKBOOK_ID --json '{
  "name": "New Name",
  "description": "Updated description"
}'

# Delete workbook
sigma workbooks delete $WORKBOOK_ID
```

## Connection Management

### List Connections

```bash
# List all connections
sigma connections list

# List as table
sigma connections list --table

# Search connections
sigma connections list --search "postgres"

# Include archived connections
sigma connections list --archived
```

### Test Connections

```bash
# Get connection ID
CONNECTION_ID="conn_abc123"

# Get connection details
sigma connections get $CONNECTION_ID

# Test connection
sigma connections test $CONNECTION_ID
```

## Data Export and Backup

### Export All Workbooks

```bash
#!/bin/bash
# export-workbooks.sh

# Create backup directory
mkdir -p backups/workbooks
cd backups/workbooks

# Get all workbook IDs and export
sigma workbooks list --compact | \
  jq -r '.entries[].workbookId' | \
  while read wb_id; do
    echo "Exporting $wb_id..."
    sigma workbooks get "$wb_id" > "${wb_id}.json"
  done

echo "Export complete!"
```

### Export Connections

```bash
#!/bin/bash
# export-connections.sh

mkdir -p backups/connections
cd backups/connections

sigma connections list --compact | \
  jq -r '.entries[].connectionId' | \
  while read conn_id; do
    echo "Exporting $conn_id..."
    sigma connections get "$conn_id" > "${conn_id}.json"
  done
```

### Restore from Backup

```bash
#!/bin/bash
# restore-workbooks.sh

cd backups/workbooks

for file in *.json; do
  echo "Restoring $file..."
  sigma workbooks create --file "$file"
done
```

## Automation Scripts

### Daily Workbook Report

```bash
#!/bin/bash
# daily-workbook-report.sh

# Get workbook count
TOTAL=$(sigma workbooks list --compact | jq '.total')

# Get recent workbooks (last page)
RECENT=$(sigma workbooks list --limit 5 --compact | \
  jq -r '.entries[] | "\(.name) - Updated: \(.updatedAt)"')

# Send report
cat <<EOF | mail -s "Daily Sigma Workbook Report" admin@example.com
Total Workbooks: $TOTAL

Recently Updated:
$RECENT
EOF
```

### Connection Health Check

```bash
#!/bin/bash
# connection-health-check.sh

echo "Testing all connections..."

sigma connections list --compact | \
  jq -r '.entries[] | "\(.connectionId) \(.name)"' | \
  while read conn_id name; do
    echo -n "Testing '$name'... "

    if sigma connections test "$conn_id" &>/dev/null; then
      echo "✓ OK"
    else
      echo "✗ FAILED"
    fi
  done
```

### Bulk Workbook Creation

```bash
#!/bin/bash
# bulk-create-workbooks.sh

# Create workbooks from CSV
cat workbooks.csv | tail -n +2 | while IFS=, read name description; do
  echo "Creating workbook: $name"

  sigma workbooks create --json "{
    \"name\": \"$name\",
    \"description\": \"$description\"
  }"

  sleep 1  # Rate limiting
done
```

## Advanced Workflows

### Find and Update Workbooks

```bash
#!/bin/bash
# rename-sales-workbooks.sh

# Find all workbooks with "Sales" in name
sigma workbooks list --search "Sales" --compact | \
  jq -r '.entries[] | "\(.workbookId) \(.name)"' | \
  while read wb_id name; do
    # Add "FY2024" prefix
    new_name="FY2024 - $name"
    echo "Renaming '$name' to '$new_name'"

    sigma workbooks update "$wb_id" --name "$new_name"
  done
```

### Workbook Audit Trail

```bash
#!/bin/bash
# workbook-audit.sh

# Create audit report
echo "Workbook Audit Report - $(date)"
echo "================================"

sigma workbooks list --compact | \
  jq -r '.entries[] | [
    .name,
    .createdBy,
    .createdAt,
    .updatedBy,
    .updatedAt
  ] | @tsv' | \
  column -t -s $'\t' -N "Name,Created By,Created At,Updated By,Updated At"
```

### Pipe to Other Tools

```bash
# Export workbooks to CSV
sigma workbooks list --compact | \
  jq -r '.entries[] | [.workbookId, .name, .createdAt] | @csv' > workbooks.csv

# Filter with jq
sigma workbooks list --compact | \
  jq '.entries[] | select(.name | contains("Dashboard"))'

# Count workbooks by creator
sigma workbooks list --compact | \
  jq -r '.entries[].createdBy' | \
  sort | uniq -c | sort -rn

# Get most recently updated workbook
sigma workbooks list --compact | \
  jq -r '.entries | sort_by(.updatedAt) | reverse | .[0] | .name'
```

### Using Raw API Endpoints

```bash
# Get member details
sigma raw GET /v2/members

# Create a team
sigma raw POST /v2/teams --json '{
  "name": "Data Analytics Team",
  "description": "Team for data analysts"
}'

# Update organization settings
sigma raw PATCH /v2/organizations/org_123 --json '{
  "name": "Updated Org Name"
}'

# Get workbook with specific version
sigma raw GET /v2/workbooks/wb_123 --params '{
  "version": "v1.2.3"
}'
```

### Multi-Environment Workflows

```bash
#!/bin/bash
# sync-workbooks.sh

# Export from staging
SIGMA_BASE_URL="https://aws-api.sigmacomputing.com/v2" \
SIGMA_CLIENT_ID="staging-client-id" \
SIGMA_SECRET="staging-secret" \
sigma workbooks list --compact > staging-workbooks.json

# Compare with production
SIGMA_BASE_URL="https://aws-api.sigmacomputing.com/v2" \
SIGMA_CLIENT_ID="prod-client-id" \
SIGMA_SECRET="prod-secret" \
sigma workbooks list --compact > prod-workbooks.json

# Show differences
diff <(jq -r '.entries[].name' staging-workbooks.json | sort) \
     <(jq -r '.entries[].name' prod-workbooks.json | sort)
```

### JSON Template Processing

```bash
# Use jq to modify template before creating
cat workbook-template.json | \
  jq '.name = "Customized Name" | .description = "Auto-generated"' | \
  sigma workbooks create

# Batch create with variations
for region in us-east us-west eu-west; do
  cat template.json | \
    jq --arg region "$region" '.name = "\($region) Dashboard"' | \
    sigma workbooks create
done
```

### Error Handling in Scripts

```bash
#!/bin/bash
# robust-workbook-create.sh

set -e  # Exit on error

create_workbook() {
  local name="$1"

  if sigma workbooks create --name "$name" > /tmp/result.json 2>&1; then
    local wb_id=$(jq -r '.workbookId' /tmp/result.json)
    echo "✓ Created: $name (ID: $wb_id)"
    return 0
  else
    echo "✗ Failed: $name"
    cat /tmp/result.json
    return 1
  fi
}

# Create with error handling
create_workbook "Dashboard 1" || echo "Continuing despite error..."
create_workbook "Dashboard 2" || echo "Continuing despite error..."
```

## Performance Tips

### Pagination

```bash
# Process large result sets with pagination
process_all_workbooks() {
  local page=""

  while true; do
    # Get page of results
    local response=$(sigma workbooks list --limit 100 \
      ${page:+--page "$page"} --compact)

    # Process entries
    echo "$response" | jq -r '.entries[] | .name'

    # Check for next page
    page=$(echo "$response" | jq -r '.nextPage // empty')

    # Exit if no more pages
    [ -z "$page" ] && break
  done
}

process_all_workbooks
```

### Parallel Processing

```bash
# Process workbooks in parallel
sigma workbooks list --compact | \
  jq -r '.entries[].workbookId' | \
  xargs -P 5 -I {} sigma workbooks get {} > {}.json
```

### Rate Limiting

```bash
# Add delays to respect rate limits
sigma workbooks list --compact | \
  jq -r '.entries[].workbookId' | \
  while read wb_id; do
    sigma workbooks get "$wb_id"
    sleep 0.5  # 500ms delay between requests
  done
```

## Integration Examples

### With GitHub Actions

```yaml
# .github/workflows/sigma-backup.yml
name: Daily Sigma Backup

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install sigma-cli
        run: uv pip install -e .

      - name: Backup workbooks
        env:
          SIGMA_CLIENT_ID: ${{ secrets.SIGMA_CLIENT_ID }}
          SIGMA_SECRET: ${{ secrets.SIGMA_SECRET }}
        run: |
          mkdir -p backups
          sigma workbooks list --compact > backups/workbooks-$(date +%Y%m%d).json

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: sigma-backups
          path: backups/
```

### With Cron

```bash
# Add to crontab
# Daily backup at 2 AM
0 2 * * * cd /path/to/project && ./backup-sigma.sh >> /var/log/sigma-backup.log 2>&1

# Weekly report on Mondays at 9 AM
0 9 * * 1 cd /path/to/project && ./weekly-report.sh | mail -s "Weekly Sigma Report" admin@example.com
```

## Debugging

### Verbose Output

```bash
# Show full error details
sigma workbooks list 2>&1 | tee debug.log

# Inspect raw responses
sigma raw GET /v2/workbooks --pretty > response.json
cat response.json
```

### Testing Authentication

```bash
# Get a token to verify auth works
sigma auth token

# Use the token manually
TOKEN=$(sigma auth token --compact | jq -r '.access_token')
curl -H "Authorization: Bearer $TOKEN" \
     https://aws-api.sigmacomputing.com/v2/workbooks
```

## Best Practices

1. **Always use `--compact` for scripting** to get clean JSON output
2. **Store credentials securely** using `sigma config` or environment variables
3. **Add error handling** in scripts with proper exit codes
4. **Use pagination** for large result sets
5. **Respect rate limits** with sleep delays
6. **Test in staging** before running on production
7. **Keep backups** of important configurations
8. **Use version control** for automation scripts
9. **Document your workflows** with comments
10. **Monitor and log** automated jobs

## Need Help?

- Run `sigma --help` for command overview
- Run `sigma COMMAND --help` for specific command help
- See the full documentation in `docs/sigma-cli-README.md`
- Check the Sigma API reference: https://help.sigmacomputing.com/reference
