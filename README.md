# file-server-auto-https

A CLI tool for creating file servers with automatic HTTPS using Cloudflare DNS. This tool automatically generates subdomains on your domain and configures Cloudflare's Flexible SSL for secure access.

## Features

- Automatic subdomain generation for your domain
- Cloudflare DNS management
- Public and local IP detection
- Flexible SSL through Cloudflare
- Rich CLI interface with detailed feedback

## Prerequisites

- Python 3.8 or higher
- A Cloudflare account
- A domain managed by Cloudflare
- Cloudflare API credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/file-server-auto-https.git
cd file-server-auto-https
```

2. Install dependencies:
```bash
pip install -e .
```

## Configuration

Create a `.env` file in the project root with your Cloudflare credentials:

```env
CLOUDFLARE_EMAIL=your-email@example.com
CLOUDFLARE_API_KEY=your-api-key
CLOUDFLARE_ZONE_ID=your-zone-id  # Zone ID for your domain
BASE_DOMAIN=your-domain.com
```

To find your Zone ID:
1. Log into your Cloudflare dashboard
2. Select your domain
3. The Zone ID is shown in the Overview tab's API section

## Usage

The tool provides a CLI interface with various commands:

### Create DNS Record

Create a new subdomain pointing to your server:

```bash
# Basic usage (auto-detects public IP)
file-server dns create

# Specify custom IP
file-server dns create --ip 1.2.3.4

# Use local IP instead of public
file-server dns create --no-use-public-ip

# Specify custom subdomain
file-server dns create --subdomain myserver

# Custom subdomain length (for random generation)
file-server dns create --length 12

# Disable Cloudflare proxying
file-server dns create --no-proxied
```

### List DNS Records

View existing DNS records:

```bash
# List records created by this tool
file-server dns list-records

# List all DNS records in the zone
file-server dns list-records --show-all
```

### Delete DNS Record

Delete a DNS record by its ID:

```bash
# Delete a record (get ID from list-records command)
file-server dns delete RECORD_ID
```

### Command Options

#### Create
- `--ip`: Specify IP address manually
- `--use-public-ip`: Use public IP (default: True)
- `--subdomain`: Specify custom subdomain
- `--length`: Length of random subdomain (default: 8)
- `--proxied`: Enable/disable Cloudflare proxying (default: True)

#### List
- `--show-all`: Show all records, not just those created by this tool

## Development

### Running Tests

The project uses pytest for testing. To run the tests:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=file_server_auto_https

# Run specific test file
pytest tests/test_generate_dns_record.py
```

### Test Structure

- `test_generate_dns_record.py`: Tests for DNS record generation
  - Subdomain generation
  - DNS record creation
  - Error handling
  - Configuration validation

## SSL/TLS

This project uses Cloudflare's Flexible SSL:
- HTTPS between visitors and Cloudflare
- HTTP between Cloudflare and your server
- No need to generate/manage SSL certificates
- Enabled automatically when `proxied=True`

## Troubleshooting

### DNS Record Not Appearing
If your DNS record isn't appearing in Cloudflare:

1. Check your credentials:
   ```bash
   # List existing records to verify API access
   file-server dns list-records --show-all
   ```

2. Verify the API response:
   The create command now shows the raw API response for debugging.

3. Common issues:
   - Incorrect Zone ID
   - API key permissions (needs DNS Write access)
   - Rate limiting
   - Invalid subdomain format

If you're still having issues, check the error messages in the command output for more details.

## License

GPL-3.0
