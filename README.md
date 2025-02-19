# File Server with Auto HTTPS

A Python-based file server that automatically sets up HTTPS using Caddy v2 as a reverse proxy and Cloudflare DNS management.

## Features

- 🔒 Automatic HTTPS via Caddy v2
- 🌐 Public and local IP address support
- 🎯 Random or custom subdomain generation
- 📁 Directory listing control
- 🔄 CORS support for cross-origin requests
- 🚦 Graceful start/stop handling
- 🛡️ Cloudflare integration with flexible SSL modes

## Installation

### 1. Install the Python package
```bash
pip install file-server-auto-https
```

### 2. Install Caddy v2
Follow the [official Caddy installation guide](https://caddyserver.com/docs/install).

## Configuration

### 1. Create a `.env` file with your Cloudflare credentials:

```env
CLOUDFLARE_EMAIL=your.email@example.com
CLOUDFLARE_API_KEY=your_api_key
CLOUDFLARE_ZONE_ID=your_zone_id
BASE_DOMAIN=your.domain.com
```

### 2. Configure Caddy (optional)

Default configuration is provided, but you can customize it:

```json
{
  "apps": {
    "http": {
      "servers": {
        "srv0": {
          "listen": [":443"],
          "routes": [
            {
              "handle": [{
                "handler": "reverse_proxy",
                "upstreams": [{"dial": "localhost:8000"}]
              }]
            }
          ]
        }
      }
    }
  }
}
```

## Usage

### Basic File Server (HTTP Only)

```bash
# Serve current directory on port 8000
file-server serve

# Serve specific directory with custom port
file-server serve /path/to/directory --port 8080

# Disable directory listing
file-server serve --no-directory-listing
```

### Secure Server with Caddy (HTTPS)

```bash
# Start with automatic HTTPS
file-server serve --with-caddy

# Use specific domain
file-server serve --with-caddy --domain mysite.example.com

# Custom Caddy config
file-server serve --with-caddy --caddy-config /path/to/config.json
```

### Cloudflare Integration

#### 1. Create DNS Record
```bash
# Create with auto-generated subdomain
file-server dns create

# Create with specific subdomain
file-server dns create --subdomain myserver

# Create with specific IP and Cloudflare proxy settings
file-server dns create --ip 1.2.3.4 --proxied --ttl 3600
```

#### 2. List DNS Records
```bash
# List records created by this tool
file-server dns list

# List all DNS records
file-server dns list --show-all
```

#### 3. Delete DNS Record
```bash
file-server dns delete RECORD_ID
```

## API Usage

### Basic File Server
```python
from file_server_auto_https import FileServer

# Start a basic file server
with FileServer("./", port=8000) as server:
    print(f"Server running at {server.url}")
```

### With Caddy Integration
```python
from file_server_auto_https import FileServer, CaddyManager

# Start file server with Caddy reverse proxy
with FileServer("./", port=8000) as server:
    with CaddyManager(target_port=8000, domain="mysite.example.com") as caddy:
        print(f"Server running at https://{caddy.domain}")
```

### Cloudflare DNS Management
```python
from file_server_auto_https import CloudflareClient, DNSRecord

# Create a DNS record
client = CloudflareClient()
record = DNSRecord(
    name="myserver.example.com",
    content="1.2.3.4",
    proxied=True
)
result = client.create_dns_record(record)
```

## Cloudflare SSL/TLS Modes

The server supports different Cloudflare SSL modes:

### Flexible SSL (Default)
- HTTPS between visitor and Cloudflare
- HTTP between Cloudflare and your server
- No SSL certificate required on your server
- Only works on port 443
- Uses Caddy as reverse proxy

```bash
file-server serve --with-caddy --ssl-mode flexible
```

### Full SSL
- HTTPS everywhere
- Requires SSL certificate (automatically handled by Caddy)
- More secure than Flexible

```bash
file-server serve --with-caddy --ssl-mode full
```

### Full (Strict) SSL
- HTTPS everywhere with certificate validation
- Most secure option
- Requires valid SSL certificate (automatically handled by Caddy)

```bash
file-server serve --with-caddy --ssl-mode strict
```

## Development

### Running Tests
```bash
pytest tests/
```

### Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

