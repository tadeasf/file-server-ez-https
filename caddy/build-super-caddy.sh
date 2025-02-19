#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Clean up existing files
echo -e "${YELLOW}Cleaning up existing files...${NC}"
rm -f super-caddy Caddyfile

# Load environment variables
if [ -f "../.env" ]; then
    source "../.env"
elif [ -f ".env" ]; then
    source ".env"
else
    echo -e "${RED}Error: .env file not found in current or parent directory${NC}"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for xcaddy
if ! command_exists xcaddy; then
    echo -e "${YELLOW}xcaddy not found. Attempting to install...${NC}"
    
    # Check for paru
    if command_exists paru; then
        paru -S xcaddy
    # Check for yay
    elif command_exists yay; then
        yay -S xcaddy
    else
        echo -e "${RED}Error: Neither paru nor yay found. Please install xcaddy manually${NC}"
        exit 1
    fi
fi

# Check AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${YELLOW}Warning: AWS credentials not found in environment${NC}"
    echo -e "If you plan to use AWS services, please set:"
    echo -e "  - AWS_ACCESS_KEY_ID"
    echo -e "  - AWS_SECRET_ACCESS_KEY"
fi

# Build Caddy
echo -e "${GREEN}Building Super Caddy...${NC}"
xcaddy build \
  --output super-caddy \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/mholt/caddy-webdav \
  --with github.com/mholt/caddy-dynamicdns \
  --with github.com/mholt/caddy-ratelimit \
  --with github.com/caddyserver/cache-handler \
  --with github.com/darkweak/storages/redis/caddy \
  --with github.com/caddy-dns/route53 \
  --with github.com/caddyserver/transform-encoder \
  --with github.com/tdewolff/minify/v2 \
  --with github.com/ueffel/caddy-imagefilter

# Create log directory if it doesn't exist
echo -e "${GREEN}Setting up log directory...${NC}"
if [ ! -d /var/log/caddy ]; then
    if sudo mkdir -p /var/log/caddy; then
        sudo chown -R $USER:$USER /var/log/caddy
        echo -e "${GREEN}Created and configured log directory${NC}"
    else
        echo -e "${RED}Error: Failed to create log directory. Please create it manually:${NC}"
        echo -e "sudo mkdir -p /var/log/caddy"
        echo -e "sudo chown -R \$USER:\$USER /var/log/caddy"
        exit 1
    fi
fi

# Create Caddyfile
echo -e "${GREEN}Creating Caddyfile...${NC}"
cat > Caddyfile <<EOL
{
    email ${CLOUDFLARE_EMAIL}
    log {
        output file /var/log/caddy/access.log
        format json
    }

    # Debug options (comment out in production)
    debug
    
    # Cache configuration
    cache {
        redis {
            url localhost:6379
        }
        ttl 3600s
        allowed_http_verbs GET HEAD
    }
}

# Global configurations for Cloudflare DNS
(cloudflare) {
    tls {
        dns cloudflare {
            api_token {env.CLOUDFLARE_API_KEY}
        }
    }
}

# Example domain configuration
${BASE_DOMAIN} {
    import cloudflare

    # Enable Prometheus metrics
    metrics /metrics

    # File server for current directory
    file_server {
        root .
        browse
    }

    # Enable caching for this site
    cache

    # Rate limiting
    rate_limit {
        zone global {
            events 10
            window 1s
        }
    }

    # Security headers
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "1; mode=block"
        # Remove Server header
        -Server
    }
}
EOL

echo -e "${GREEN}Setup complete!${NC}"

# Format Caddyfile
echo -e "${GREEN}Formatting Caddyfile...${NC}"
./super-caddy fmt --overwrite Caddyfile

# Run Caddy
echo -e "${GREEN}Starting Caddy server...${NC}"
sudo ./super-caddy run -c Caddyfile

