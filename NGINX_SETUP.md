# Setup Nginx untuk Coretax Data Parser API (Opsional)

Panduan setup Nginx sebagai reverse proxy untuk Coretax Data Parser API. Setup ini **opsional** tapi **sangat disarankan** untuk production karena:

- ✅ Bisa menggunakan domain name
- ✅ Support HTTPS/SSL
- ✅ Better performance dan caching
- ✅ Load balancing (jika multiple instances)
- ✅ Rate limiting
- ✅ Static file serving lebih efisien

## 📋 Prasyarat

- VPS sudah setup sesuai [VPS_SETUP.md](VPS_SETUP.md)
- Aplikasi sudah berjalan di port 8000
- Domain/subdomain (opsional, bisa pakai IP)

## 🔧 Langkah 1: Install Nginx

```bash
# Update package list
sudo apt update

# Install Nginx
sudo apt install nginx -y

# Check status
sudo systemctl status nginx

# Enable auto-start on boot
sudo systemctl enable nginx
```

## 📝 Langkah 2: Konfigurasi Nginx

### 2.1 Buat Konfigurasi untuk Aplikasi

```bash
sudo nano /etc/nginx/sites-available/coretax-api
```

### Opsi A: Konfigurasi Tanpa Domain (Menggunakan IP)

```nginx
server {
    listen 80;
    server_name _;  # Terima semua request

    client_max_body_size 50M;  # Limit upload size

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings untuk upload file besar
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;
    }
}
```

### Opsi B: Konfigurasi dengan Domain

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;  # Ganti dengan domain Anda

    client_max_body_size 50M;  # Limit upload size

    # Logging
    access_log /var/log/nginx/coretax-api.access.log;
    error_log /var/log/nginx/coretax-api.error.log;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;
    }

    # Optional: Serve static files directly (jika ada)
    location /static/ {
        alias /home/coretax/CoretaxDataParser-API/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2.2 Enable Konfigurasi

```bash
# Buat symbolic link ke sites-enabled
sudo ln -s /etc/nginx/sites-available/coretax-api /etc/nginx/sites-enabled/

# Hapus default config jika tidak diperlukan
sudo rm /etc/nginx/sites-enabled/default

# Test konfigurasi
sudo nginx -t

# Jika OK, reload nginx
sudo systemctl reload nginx
```

## 🔒 Langkah 3: Setup SSL/HTTPS dengan Let's Encrypt (Sangat Disarankan)

### 3.1 Install Certbot

```bash
# Install Certbot dan plugin Nginx
sudo apt install certbot python3-certbot-nginx -y
```

### 3.2 Dapatkan SSL Certificate

**Untuk domain:**

```bash
# Ganti dengan email dan domain Anda
sudo certbot --nginx -d api.yourdomain.com

# Follow the prompts:
# - Enter email address
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (pilih Yes)
```

Certbot akan otomatis:

- Generate SSL certificate
- Update konfigurasi Nginx
- Setup auto-renewal

### 3.3 Test Auto-Renewal

```bash
# Dry run untuk test renewal
sudo certbot renew --dry-run
```

### 3.4 Konfigurasi Setelah SSL (Auto-generated oleh Certbot)

Certbot akan menambahkan konfigurasi seperti ini:

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;
    }
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}
```

## 🔐 Langkah 4: Konfigurasi Security Headers (Opsional tapi Disarankan)

Edit konfigurasi dan tambahkan security headers:

```bash
sudo nano /etc/nginx/sites-available/coretax-api
```

Tambahkan di dalam blok `location /`:

```nginx
location / {
    # ... konfigurasi proxy yang sudah ada ...

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

## ⚡ Langkah 5: Optimasi Nginx (Opsional)

### 5.1 Edit Main Config

```bash
sudo nano /etc/nginx/nginx.conf
```

Sesuaikan nilai-nilai berikut di dalam blok `http`:

```nginx
http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;  # Hide Nginx version

    # Upload size
    client_max_body_size 50M;
    client_body_buffer_size 128k;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    # ... rest of config ...
}
```

### 5.2 Tambahkan Rate Limiting ke Site Config

```bash
sudo nano /etc/nginx/sites-available/coretax-api
```

Tambahkan di dalam `location /`:

```nginx
location / {
    # Rate limiting: 10 requests per second, burst 20
    limit_req zone=api_limit burst=20 nodelay;

    # ... rest of proxy config ...
}
```

### 5.3 Test dan Reload

```bash
# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

## 🌐 Langkah 6: Update Firewall

```bash
# Jika pakai UFW
sudo ufw allow 'Nginx Full'

# Atau allow port spesifik
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Bisa block direct access ke port 8000 dari luar
sudo ufw delete allow 8000/tcp

# Check status
sudo ufw status
```

## 📊 Langkah 7: Testing

### Test HTTP (tanpa SSL)

```bash
# Test dari VPS
curl http://localhost/

# Test dari luar
curl http://your-vps-ip/docs
curl http://api.yourdomain.com/docs  # Jika pakai domain
```

### Test HTTPS (dengan SSL)

```bash
# Test SSL
curl https://api.yourdomain.com/

# Test dengan verbose untuk lihat SSL info
curl -v https://api.yourdomain.com/

# Upload test
curl -X POST "https://api.yourdomain.com/parse" \
  -F "file=@/path/to/invoice.pdf"
```

### Test di Browser

- **HTTP**: `http://your-vps-ip/docs`
- **HTTPS**: `https://api.yourdomain.com/docs`

## 🔍 Monitoring dan Logs

### Check Nginx Status

```bash
# Status service
sudo systemctl status nginx

# Test config
sudo nginx -t

# Reload config tanpa downtime
sudo systemctl reload nginx

# Restart (ada downtime singkat)
sudo systemctl restart nginx
```

### View Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/coretax-api.access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/coretax-api.error.log

# Search for specific IP
sudo grep "192.168.1.1" /var/log/nginx/access.log
```

### Log Analysis

```bash
# Top 10 IP addresses
sudo awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Most accessed endpoints
sudo awk '{print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Count status codes
sudo awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn
```

## 🔧 Troubleshooting

### Nginx Tidak Start

```bash
# Check detailed error
sudo systemctl status nginx -l
sudo journalctl -u nginx -n 50

# Check config
sudo nginx -t

# Check if port already used
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

### 502 Bad Gateway Error

```bash
# Check if backend app is running
sudo systemctl status coretax-api
curl http://127.0.0.1:8000/

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check SELinux (jika pakai CentOS/RHEL)
sudo setsebool -P httpd_can_network_connect 1
```

### SSL Certificate Issues

```bash
# Check certificate expiry
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal

# Test renewal
sudo certbot renew --dry-run
```

### Permission Denied

```bash
# Check Nginx user
ps aux | grep nginx

# Fix permissions (jika perlu)
sudo chown -R www-data:www-data /var/log/nginx/
```

## 🔄 Maintenance

### Update Nginx

```bash
sudo apt update
sudo apt upgrade nginx -y
sudo systemctl restart nginx
```

### Rotate Logs

Nginx uses logrotate by default. Check config:

```bash
cat /etc/logrotate.d/nginx
```

Manual rotation:

```bash
sudo logrotate -f /etc/logrotate.d/nginx
```

## 📱 Setup untuk Multiple Domains/Apps (Advanced)

Jika ingin host multiple apps:

```bash
# App 1
sudo nano /etc/nginx/sites-available/app1
# ... config for app1.com -> http://127.0.0.1:8000

# App 2
sudo nano /etc/nginx/sites-available/app2
# ... config for app2.com -> http://127.0.0.1:8001

# Enable both
sudo ln -s /etc/nginx/sites-available/app1 /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/app2 /etc/nginx/sites-enabled/

sudo nginx -t
sudo systemctl reload nginx
```

## 🎯 Konfigurasi Lengkap dengan Semua Optimasi

```nginx
# Rate limiting zone (tambahkan di nginx.conf atau di file ini)
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Upload limits
    client_max_body_size 50M;
    client_body_buffer_size 128k;

    # Logging
    access_log /var/log/nginx/coretax-api.access.log;
    error_log /var/log/nginx/coretax-api.error.log;

    # Main application
    location / {
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;

        # Proxy settings
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    }
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}
```

## 📚 Referensi

- [Nginx Official Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [FastAPI Behind a Proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/)

---

**Dibuat:** Februari 2026  
**Versi:** 1.0
