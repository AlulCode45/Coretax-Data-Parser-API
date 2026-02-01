# Setup Coretax Data Parser API di VPS

Panduan lengkap untuk deploy aplikasi Coretax Data Parser API ke VPS (Virtual Private Server).

## 📋 Prasyarat

- VPS dengan Ubuntu 20.04+ atau Debian 10+
- Akses SSH ke VPS
- User dengan sudo privileges
- Domain/subdomain (opsional, bisa menggunakan IP)
- Minimal 1GB RAM dan 10GB storage

## 🔧 Langkah 1: Persiapan Server

### 1.1 Update Sistem

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Install Python 3 dan pip

```bash
# Install Python 3 dan dependencies
sudo apt install python3 python3-pip python3-venv -y

# Verifikasi instalasi
python3 --version
pip3 --version
```

### 1.3 Install Git

```bash
sudo apt install git -y
```

### 1.4 Install Dependencies Sistem untuk PDF Processing

```bash
# Install dependencies untuk pdfplumber
sudo apt install -y \
    build-essential \
    libpoppler-cpp-dev \
    pkg-config \
    python3-dev
```

## 📁 Langkah 2: Setup Aplikasi

### 2.1 Buat User untuk Aplikasi (Opsional tapi Disarankan)

```bash
# Buat user khusus untuk aplikasi
sudo adduser coretax --disabled-password --gecos ""

# Tambahkan ke grup sudo jika perlu
sudo usermod -aG sudo coretax

# Login sebagai user baru
sudo su - coretax
```

### 2.2 Clone atau Upload Aplikasi

**Opsi A: Menggunakan Git**

```bash
cd ~
git clone <repository-url> CoretaxDataParser-API
cd CoretaxDataParser-API
```

**Opsi B: Upload Manual via SCP**

Dari komputer lokal:

```bash
# Upload folder ke VPS
scp -r /path/to/CoretaxDataParser-API user@your-vps-ip:~/

# Atau menggunakan rsync (lebih baik)
rsync -avz -e ssh /path/to/CoretaxDataParser-API/ user@your-vps-ip:~/CoretaxDataParser-API/
```

### 2.3 Setup Virtual Environment

```bash
cd ~/CoretaxDataParser-API

# Buat virtual environment
python3 -m venv venv

# Aktivasi virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Test Aplikasi

```bash
# Test apakah aplikasi berjalan
python3 api.py
```

Akses dari browser: `http://your-vps-ip:8000/docs`

Tekan `Ctrl+C` untuk stop. Jika berhasil, lanjut ke langkah berikutnya.

## 🔄 Langkah 3: Setup Process Manager (Systemd)

Agar aplikasi berjalan otomatis dan restart saat crash/reboot.

### 3.1 Buat Service File

```bash
sudo nano /etc/systemd/system/coretax-api.service
```

Isi dengan konfigurasi berikut (sesuaikan path jika berbeda):

```ini
[Unit]
Description=Coretax Data Parser API
After=network.target

[Service]
Type=simple
User=coretax
WorkingDirectory=/home/coretax/CoretaxDataParser-API
Environment="PATH=/home/coretax/CoretaxDataParser-API/venv/bin"
ExecStart=/home/coretax/CoretaxDataParser-API/venv/bin/python3 /home/coretax/CoretaxDataParser-API/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Catatan:** Jika tidak menggunakan user `coretax`, ganti dengan user Anda (misalnya `ubuntu` atau `root`).

### 3.2 Enable dan Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start otomatis saat boot)
sudo systemctl enable coretax-api

# Start service
sudo systemctl start coretax-api

# Check status
sudo systemctl status coretax-api
```

### 3.3 Command untuk Manage Service

```bash
# Start service
sudo systemctl start coretax-api

# Stop service
sudo systemctl stop coretax-api

# Restart service
sudo systemctl restart coretax-api

# Check status
sudo systemctl status coretax-api

# Lihat logs
sudo journalctl -u coretax-api -f

# Lihat logs terakhir
sudo journalctl -u coretax-api --since today
```

## 🔒 Langkah 4: Setup Firewall

### 4.1 Konfigurasi UFW (Uncomplicated Firewall)

```bash
# Install UFW jika belum ada
sudo apt install ufw -y

# Allow SSH (PENTING! Jangan sampai terkunci)
sudo ufw allow 22/tcp

# Allow port aplikasi (8000)
sudo ufw allow 8000/tcp

# Allow HTTP dan HTTPS jika pakai Nginx
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## 📊 Langkah 5: Monitoring dan Maintenance

### 5.1 Monitor Aplikasi

```bash
# Lihat proses yang berjalan
ps aux | grep uvicorn

# Monitor resource usage
htop

# Install htop jika belum ada
sudo apt install htop -y
```

### 5.2 Log Files

```bash
# Lihat logs real-time
sudo journalctl -u coretax-api -f

# Lihat 100 baris terakhir
sudo journalctl -u coretax-api -n 100

# Lihat logs dengan filter waktu
sudo journalctl -u coretax-api --since "1 hour ago"
sudo journalctl -u coretax-api --since "2024-01-01" --until "2024-01-02"
```

### 5.3 Update Aplikasi

```bash
# Stop service
sudo systemctl stop coretax-api

# Navigate ke folder aplikasi
cd ~/CoretaxDataParser-API

# Backup jika perlu
cp -r ~/CoretaxDataParser-API ~/CoretaxDataParser-API.backup

# Pull update (jika dari git)
git pull

# Atau upload file baru via SCP

# Aktivasi virtual environment
source venv/bin/activate

# Update dependencies jika ada perubahan
pip install -r requirements.txt --upgrade

# Start service lagi
sudo systemctl start coretax-api

# Check status
sudo systemctl status coretax-api
```

## 🌐 Langkah 6: Akses Aplikasi

### Tanpa Nginx (Akses Langsung)

Aplikasi bisa diakses langsung di:

- **API Docs**: `http://your-vps-ip:8000/docs`
- **API Endpoint**: `http://your-vps-ip:8000/parse`
- **Health Check**: `http://your-vps-ip:8000/`

### Dengan Nginx (Opsional)

Lihat panduan [NGINX_SETUP.md](NGINX_SETUP.md) untuk konfigurasi reverse proxy dengan domain dan SSL.

## 🔍 Troubleshooting

### Service Tidak Bisa Start

```bash
# Check status lengkap
sudo systemctl status coretax-api -l

# Lihat logs error
sudo journalctl -u coretax-api -n 50

# Check apakah port sudah dipakai
sudo netstat -tulpn | grep 8000
# atau
sudo lsof -i :8000
```

### Port Sudah Digunakan

```bash
# Cari proses yang menggunakan port 8000
sudo lsof -i :8000

# Kill proses (ganti PID dengan yang sesuai)
sudo kill -9 PID
```

### Permission Denied

```bash
# Pastikan ownership file benar
sudo chown -R coretax:coretax ~/CoretaxDataParser-API

# Atau jika tidak pakai user coretax
sudo chown -R $USER:$USER ~/CoretaxDataParser-API
```

### Dependencies Error

```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Memory Issues

```bash
# Check memory usage
free -h

# Buat swap file jika RAM kurang (1GB)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 🔐 Security Best Practices

1. **Jangan gunakan root user** untuk menjalankan aplikasi
2. **Gunakan SSH key** authentication, disable password auth
3. **Update sistem** secara berkala
4. **Setup fail2ban** untuk proteksi brute force
5. **Gunakan HTTPS** dengan SSL certificate (via Nginx + Let's Encrypt)
6. **Limit upload size** di nginx untuk prevent abuse
7. **Setup monitoring** dengan tools seperti Netdata atau Prometheus

### Install Fail2Ban (Opsional)

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📝 Testing API dari Command Line

### Menggunakan curl

```bash
# Test health check
curl http://your-vps-ip:8000/

# Upload single PDF
curl -X POST "http://your-vps-ip:8000/parse" \
  -F "file=@/path/to/your/invoice.pdf"

# Upload multiple PDFs
curl -X POST "http://your-vps-ip:8000/parse" \
  -F "file=@/path/to/invoice1.pdf" \
  -F "file=@/path/to/invoice2.pdf"
```

### Menggunakan Python requests

```python
import requests

# Single file
with open('invoice.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://your-vps-ip:8000/parse', files=files)
    print(response.json())

# Multiple files
files = [
    ('file', open('invoice1.pdf', 'rb')),
    ('file', open('invoice2.pdf', 'rb'))
]
response = requests.post('http://your-vps-ip:8000/parse', files=files)
print(response.json())
```

## 📚 Referensi Tambahan

- [FastAPI Deployment Documentation](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [Nginx Setup Guide](NGINX_SETUP.md) (Opsional)

## 🆘 Bantuan

Jika mengalami masalah, check:

1. Logs: `sudo journalctl -u coretax-api -n 100`
2. Service status: `sudo systemctl status coretax-api`
3. Firewall: `sudo ufw status`
4. Port usage: `sudo netstat -tulpn | grep 8000`
5. Disk space: `df -h`
6. Memory: `free -h`

---

**Dibuat:** Februari 2026  
**Versi:** 1.0
