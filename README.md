# sigma-cli: Command-line Interface for Sigma Computing

A modern, powerful command-line tool for interacting with the Sigma Computing REST API.

## Features

✨ **Modern CLI Experience**: Built with Typer and Rich for beautiful, intuitive interface
🔐 **OAuth2 Authentication**: Automatic token management with refresh support
📦 **JSON-First**: Native JSON input/output with syntax highlighting
⚡ **Fast**: Async-ready HTTP client with connection pooling
🎯 **Comprehensive**: Full API coverage with 123 endpoints
📝 **Well-Documented**: Inline help for every command

## Installation

### Prerequisites

- Python 3.13+
- uv package manager

### Install from Source

```bash
# 1. Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and navigate to repository
git clone https://github.com/joncooper/sigma-cli.git
cd sigma-cli

# 3. Create and activate virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# 4. Install sigma-cli
uv pip install -e .
```

After installation, the `sigma` command will be available in your PATH.

### Shell Completion (Optional)

Enable tab completion for zsh:

```bash
# Add to your ~/.zshrc
eval "$(_SIGMA_COMPLETE=zsh_source sigma)"
```

For bash:

```bash
# Add to your ~/.bashrc
eval "$(_SIGMA_COMPLETE=bash_source sigma)"
```

After adding, restart your shell or run `source ~/.zshrc` (or `~/.bashrc`).

## Quick Start

### 1. Configure Credentials

Save your Sigma API credentials for persistent use:

```bash
sigma config \
  --client-id "your-client-id" \
  --secret "your-secret" \
  --base-url "https://aws-api.sigmacomputing.com/v2"
```

Credentials are securely stored in `~/.sigma/config.json` with restricted permissions.

### 2. View Current Configuration

```bash
sigma config --show
```

### 3. Make Your First API Call

```bash
# List all workbooks
sigma workbooks list

# List workbooks as a table
sigma workbooks list --table

# Get a specific workbook
sigma workbooks get <workbook-id>

# List connections
sigma connections list --table
```

## Configuration

sigma-cli supports multiple configuration methods with the following precedence (highest to lowest):

1. **Command-line options** (e.g., `--client-id`, `--secret`)
2. **Environment variables** (`SIGMA_CLIENT_ID`, `SIGMA_SECRET`, `SIGMA_BASE_URL`)
3. **Config file** (`~/.sigma/config.json`)
4. **Defaults**

### Environment Variables

```bash
export SIGMA_CLIENT_ID="your-client-id"
export SIGMA_SECRET="your-secret"
export SIGMA_BASE_URL="https://aws-api.sigmacomputing.com/v2"
```

### .env File Support

Create a `.env` file in your working directory:

```env
SIGMA_CLIENT_ID=your-client-id
SIGMA_SECRET=your-secret
SIGMA_BASE_URL=https://aws-api.sigmacomputing.com/v2
```

sigma-cli will automatically load these variables.

## Usage Examples

### Working with Workbooks

```bash
# List all workbooks
sigma workbooks list

# List with filters
sigma workbooks list --limit 10 --search "Sales"

# Display as table
sigma workbooks list --table

# Get specific workbook
sigma workbooks get wb_abc123

# Create workbook from JSON
sigma workbooks create --json '{"name": "My Workbook"}'

# Create from file
sigma workbooks create --file workbook.json

# Create from stdin
echo '{"name": "My Workbook"}' | sigma workbooks create

# Update workbook
sigma workbooks update wb_abc123 --name "Updated Name"

# Delete workbook
sigma workbooks delete wb_abc123
```

### Working with Connections

```bash
# List all connections
sigma connections list

# List with table view
sigma connections list --table

# Get connection details
sigma connections get conn_abc123

# Test a connection
sigma connections test conn_abc123
```

### Working with Members and Teams

```bash
# List all members
sigma members list --table

# Get member details
sigma members get mem_abc123

# Create a member
sigma members create --email user@example.com --json '{
  "firstName": "Jane",
  "lastName": "Doe",
  "accountType": "Viewer"
}'

# List all teams
sigma teams list --table

# Create a team
sigma teams create --name "Data Analytics Team"

# Add member to team
sigma teams add-member team_abc123 mem_abc123

# Remove member from team
sigma teams remove-member team_abc123 mem_abc123

# List team members
sigma teams members team_abc123 --table
```

### Working with Datasets

```bash
# List all datasets
sigma datasets list --table

# Get dataset details
sigma datasets get ds_abc123

# Get dataset grants
sigma datasets grants ds_abc123

# Create a grant for dataset
echo '{"grantee": "team_abc123", "permission": "view"}' | \
  sigma datasets create-grant ds_abc123
```

### Working with Files and Workspaces

```bash
# List files
sigma files list --path "/My Folder" --table

# Get file info
sigma files get inode_abc123

# List workspaces
sigma workspaces list --table

# Create workspace
sigma workspaces create --name "Analytics Workspace"

# Get workspace members
sigma workspaces members ws_abc123
```

### Working with Tags and User Attributes

```bash
# List tags
sigma tags list --table

# Create a tag
sigma tags create --name "Production" --color "#FF0000"

# Assign tag to a document
sigma tags assign tag_abc123 inode_abc123

# List user attributes
sigma user-attributes list --table

# Create user attribute
sigma user-attributes create --name "Department" --json '{
  "description": "User department",
  "dataType": "string"
}'
```

### Working with Grants

```bash
# List all grants
sigma grants list --table

# Get grant details
sigma grants get grant_abc123

# Create a grant
echo '{
  "grantee": "team_abc123",
  "permission": "view",
  "resource": "workbook_abc123"
}' | sigma grants create

# Delete a grant
sigma grants delete grant_abc123
```

### Working with Account Types

```bash
# List account types
sigma account-types list

# List as table
sigma account-types list --table

# Get permissions for an account type
sigma account-types permissions at_abc123
```

### Authentication

```bash
# Get a fresh access token
sigma auth token

# Get token (compact output)
sigma auth token --compact
```

### Raw API Requests

For endpoints not yet wrapped in specific commands, use the `raw` command:

```bash
# GET request
sigma raw GET /v2/workbooks

# GET with query parameters
sigma raw GET /v2/workbooks --params '{"limit": 5}'

# POST request with JSON
sigma raw POST /v2/workbooks --json '{"name": "Test"}'

# POST from file
sigma raw POST /v2/workbooks --file data.json

# POST from stdin
echo '{"name": "Test"}' | sigma raw POST /v2/workbooks

# Other HTTP methods
sigma raw PUT /v2/workbooks/wb_123 --json '{"name": "Updated"}'
sigma raw PATCH /v2/workbooks/wb_123 --json '{"name": "Patched"}'
sigma raw DELETE /v2/workbooks/wb_123
```

## JSON Input/Output

sigma-cli is designed for JSON-first workflows:

### JSON Input Methods

1. **Command-line string**: `--json '{"key": "value"}'`
2. **File**: `--file data.json`
3. **Stdin**: `echo '{"key": "value"}' | sigma ...`

### JSON Output Modes

```bash
# Pretty-printed with syntax highlighting (default)
sigma workbooks list

# Compact output
sigma workbooks list --compact

# Pipe to jq for processing
sigma workbooks list --compact | jq '.entries[0]'
```

## Advanced Usage

### Piping and Chaining

```bash
# Get all workbooks and filter with jq
sigma workbooks list --compact | jq '.entries[] | select(.name | contains("Sales"))'

# Create workbook from template
cat template.json | jq '.name = "New Name"' | sigma workbooks create

# Get workbook ID and delete it
WORKBOOK_ID=$(sigma workbooks list --compact | jq -r '.entries[0].workbookId')
sigma workbooks delete $WORKBOOK_ID
```

### Override Configuration Per-Command

```bash
# Use different credentials for one command
sigma workbooks list \
  --client-id "other-client-id" \
  --secret "other-secret"

# Use different API endpoint
sigma workbooks list --base-url "https://azure-api.sigmacomputing.com/v2"
```

### Scripting

```bash
#!/bin/bash

# Export all workbooks
for wb_id in $(sigma workbooks list --compact | jq -r '.entries[].workbookId'); do
  sigma workbooks get "$wb_id" > "workbooks/${wb_id}.json"
done

# Bulk create from directory
for file in workbooks/*.json; do
  sigma workbooks create --file "$file"
done
```

## Available Commands

sigma-cli organizes commands by resource type. All 123+ API endpoints are accessible via command groups or the `raw` command.

### Core Commands

- `sigma config` - Configure credentials and settings
- `sigma version` - Show version information
- `sigma raw` - Make raw HTTP requests to any endpoint

### Authentication & User Management

- `sigma auth` - Authentication commands
  - `token` - Get access token

- `sigma members` - Manage organization members
  - `list`, `get`, `create`, `update`, `delete`, `teams`

- `sigma teams` - Manage teams
  - `list`, `get`, `create`, `update`, `delete`, `members`, `add-member`, `remove-member`

- `sigma account-types` - Manage account types
  - `list`, `permissions`

- `sigma whoami` - Get current user information

### Content & Workbooks

- `sigma workbooks` - Manage workbooks
  - `list`, `get`, `create`, `update`, `delete`

- `sigma datasets` - Manage datasets
  - `list`, `get`, `grants`, `create-grant`, `update-grant`, `delete-grant`

- `sigma files` - Manage files
  - `list`, `get`, `create`, `update`, `delete`

- `sigma workspaces` - Manage workspaces
  - `list`, `get`, `create`, `update`, `delete`, `members`

### Data Infrastructure

- `sigma connections` - Manage data connections
  - `list`, `get`, `test`

### Permissions & Organization

- `sigma grants` - Manage grants and permissions
  - `list`, `get`, `create`, `update`, `delete`

- `sigma user-attributes` - Manage user attributes
  - `list`, `get`, `create`, `update`, `delete`

- `sigma tags` - Manage tags
  - `list`, `create`, `update`, `delete`, `assign`

### Getting Help

```bash
# General help
sigma --help

# Command group help
sigma workbooks --help
sigma members --help
sigma grants --help

# Specific command help
sigma workbooks list --help
sigma teams create --help
```

## API Coverage

sigma-cli provides access to the entire Sigma Computing REST API (123+ endpoints) across 24 resource types:

**✅ Fully Implemented:**
- Account Types (2 endpoints)
- Authentication (1 endpoint)
- Connections (21 endpoints)
- Datasets (8 endpoints)
- Files (5 endpoints)
- Grants (4 endpoints)
- Members (10 endpoints)
- Tags (5 endpoints)
- Teams (10 endpoints)
- User Attributes (11 endpoints)
- Workbooks (48 endpoints)
- Workspaces (9 endpoints)

**📦 Via Raw Command:**
- Allowed IPs (Beta)
- Credentials
- Data Models
- Favorites
- Query Export
- Shared Templates
- Templates
- Tenants (Beta)
- Translations

For any endpoint, use `sigma raw` for direct access:
```bash
sigma raw GET /v2/templates
sigma raw POST /v2/favorites --json '{"inodeId": "..."}'
```

## Architecture

```
src/sigma_cli/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point for python -m sigma_cli
├── cli.py               # Main CLI app with Typer
├── auth.py              # OAuth2 authentication handler
├── client.py            # HTTP client wrapper
├── config.py            # Configuration management
├── openapi.py           # OpenAPI spec parser
├── commands/            # Command modules
│   ├── account_types.py
│   ├── auth_cmd.py
│   ├── connections.py
│   └── workbooks.py
└── utils/               # Utilities
    ├── json_utils.py    # JSON input/output
    └── output.py        # Rich formatting
```

## Development

### Adding New Commands

1. Create a new module in `src/sigma_cli/commands/`
2. Define commands using Typer
3. Register in `src/sigma_cli/cli.py`

Example:

```python
# src/sigma_cli/commands/datasets.py
import typer
from sigma_cli.client import SigmaClient
from sigma_cli.config import get_config

app = typer.Typer()

@app.command("list")
def list_datasets():
    """List all datasets."""
    cfg = get_config()
    client = SigmaClient(cfg)
    response = client.get("/v2/datasets")
    print_json(response)
```

```python
# In src/sigma_cli/cli.py
from sigma_cli.commands import datasets

app.add_typer(datasets.app, name="datasets", help="Manage datasets")
```

### Testing

```bash
# Install in development mode
uv pip install -e .

# Run CLI directly
sigma --help

# Or via Python module
python -m sigma_cli --help
```

## Troubleshooting

### Authentication Errors

If you see "Missing credentials" errors:

1. Check your configuration: `sigma config --show`
2. Verify environment variables: `env | grep SIGMA`
3. Re-configure: `sigma config --client-id ... --secret ...`

### Network Errors

Ensure you're using the correct base URL for your Sigma cloud:

- AWS: `https://aws-api.sigmacomputing.com/v2`
- Azure: `https://azure-api.sigmacomputing.com/v2`
- GCP: `https://gcp-api.sigmacomputing.com/v2`

### Token Expiration

Tokens are automatically refreshed. If you experience issues:

```bash
# Force a new token
sigma auth token
```

## Security

- Credentials are stored in `~/.sigma/config.json` with 0600 permissions (owner read/write only)
- Tokens are cached in memory and automatically refreshed
- Never commit credentials to version control
- Use environment variables or config file for CI/CD

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file.

## Support

For issues or questions:

- GitHub Issues: [joncooper/sigma-cli](https://github.com/joncooper/sigma-cli/issues)
- Sigma Documentation: [help.sigmacomputing.com](https://help.sigmacomputing.com)
- Sigma API Reference: [help.sigmacomputing.com/reference](https://help.sigmacomputing.com/reference)

## Acknowledgments

Built with:
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [httpx](https://www.python-httpx.org/) - HTTP client
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
