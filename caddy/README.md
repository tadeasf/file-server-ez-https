# Super Caddy Builder

This repository contains instructions for building a custom Caddy server with enhanced functionality through carefully selected plugins.

## Prerequisites

1. Install xcaddy using your package manager:
```bash
# Arch Linux / Manjaro (using paru)
paru -S xcaddy
```

2. Install Redis for caching:
```bash
# Arch Linux / Manjaro
sudo pacman -S redis

# Start Redis service
sudo systemctl enable redis
sudo systemctl start redis

# Verify Redis is running
redis-cli ping
# Should return "PONG"
```

## Building Custom Caddy

Run the following command to build a custom Caddy binary with all recommended plugins:

```bash
xcaddy build \
  --output super-caddy \
  # Core Functionality
  --with github.com/caddy-dns/cloudflare \
  --with github.com/mholt/caddy-webdav \
  --with github.com/greenpau/caddy-security \
  --with github.com/mholt/caddy-dynamicdns \
  --with github.com/mholt/caddy-ratelimit \
  # Enhanced Security & Authentication
  # Performance & Caching
  --with github.com/caddyserver/cache-handler \
  # CDN & Proxy Features
  --with github.com/caddy-dns/route53 \
  # Content & Optimization
  --with github.com/caddyserver/transform-encoder \
  --with github.com/tdewolff/minify/v2 \
  --with github.com/ueffel/caddy-imagefilter
```

## Cache Configuration

The server uses Redis for caching responses. The default configuration:

```caddy
cache {
    redis {
        url localhost:6379
    }
    ttl 3600s
    api {
        basepath /cache-api
        prometheus
    }
    regex {
        exclude /api/.*
    }
}
```

You can access cache statistics and management through the API at `/cache-api`.

## Usage

After building, your custom Caddy binary will be available as `super-caddy` in the current directory.

Run it directly:
```bash
./super-caddy
```

Or move it to your system's binary location:
```bash
sudo mv super-caddy /usr/local/bin/caddy
```

## Basic Reverse Proxy Setup

For a basic reverse proxy setup without plugin configuration, use this minimal Caddyfile:

```caddy
example.com {
    reverse_proxy localhost:8080
}
```

## Required Plugin Configuration

If you plan to use specific plugins, here are the minimum required configurations:

### Security Plugins

#### Caddy Security (if using authentication)
```caddy
example.com {
    authenticate with auth0 {
        auth_url https://example.auth0.com/authorize
        token_url https://example.auth0.com/oauth/token
        client_id your_client_id
        client_secret your_client_secret
    }
    reverse_proxy localhost:8080
}
```

### Monitoring

#### Prometheus Metrics
```caddy
example.com {
    metrics /metrics
    reverse_proxy localhost:8080
}
```

### Cloud Integration

#### AWS/Route53 (if using AWS services)
```caddy
{
    aws_credentials {
        # Either configure environment variables:
        # AWS_ACCESS_KEY_ID
        # AWS_SECRET_ACCESS_KEY
        # Or use AWS credentials file
    }
}
```

#### Cloudflare DNS (if using Cloudflare DNS challenges)
```caddy
{
    acme_dns cloudflare {
        api_token your_cloudflare_token
    }
}
```

