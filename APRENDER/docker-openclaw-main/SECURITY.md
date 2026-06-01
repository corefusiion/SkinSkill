# 🔒 Security Hardening Checklist

Based on the [OpenClaw Security Guide](https://docs.openclaw.ai) — Top 10 vulnerabilities and fixes.

---

## Three Deployment Scenarios

This guide covers three distinct setups. Choose your scenario:

| | 🏠 Local Basic | 🏠🔒 Local Maximum | ☁️ Cloud VPS |
|---|---|---|---|
| **Physical access** | Yes | Yes | No |
| **Network exposure** | LAN only | LAN only | Public IP |
| **Attack surface** | Low | Low | High |
| **SSH hardening** | Optional | Required | **Critical** |
| **Firewall** | Optional | Required | **Required** |
| **Fail2Ban** | Skip | Optional | **Required** |
| **VPN/Tailscale** | Nice to have | Recommended | **Highly recommended** |
| **Disk encryption** | Optional | Recommended | Provider-dependent |

---

## 🏠 Local Server — Basic Security (Home / Office)

You have physical access to the machine. It sits behind your router/firewall.

### Threat model:
- Other devices on your LAN
- Someone with physical access
- Malware on your network

### What this Docker setup does automatically:
```
✅ Gateway bind: loopback (127.0.0.1 on host side)
✅ DM policy: pairing (users must be approved)
✅ Logging enabled (audit trail)
✅ Config permissions: chmod 600 (secrets protected)
✅ Docker container isolation (non-root user)
✅ No privilege escalation (no-new-privileges)
✅ Secrets via environment variables (not in config files)
```

### Recommended extras:
```bash
# Block port 18789 from outside your LAN (most routers do this by default)
# Just make sure you DON'T have port forwarding enabled for 18789

# Enable automatic security updates (Ubuntu/Debian)
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 🏠🔒 Local Server — Maximum Security

Same physical access, but you want **enterprise-grade** protection.

### 🛡️ Full hardening:

#### 1. Network Isolation (Firewall)
```bash
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.1.0/24 to any port 22  # SSH only from your LAN
sudo ufw deny 18789/tcp                              # Block gateway externally
sudo ufw --force enable
```

#### 2. SSH Hardening (Key-Only Auth)
```bash
# Generate key on your local machine
ssh-keygen -t ed25519 -C "local-admin"
ssh-copy-id user@server-local-ip

# Disable password + root login
sudo sed -i "s/#PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
sudo sed -i "s/PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
sudo sed -i "s/PermitRootLogin yes/PermitRootLogin no/" /etc/ssh/sshd_config
sudo systemctl restart sshd
```

#### 3. Docker with AppArmor
```yaml
# Add to docker-compose.yml:
services:
  openclaw:
    security_opt:
      - no-new-privileges:true
      - apparmor:docker-default
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp:size=512M,noexec,nosuid
```

#### 4. Tailscale for Remote Access
```bash
# Zero-trust network — no open ports needed
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Access only via Tailscale IP
sudo ufw default deny incoming
sudo ufw allow in on tailscale0
```

---

## ☁️ Cloud VPS (Hetzner, DigitalOcean, AWS, etc.)

Your server has a **public IP**. It's under constant attack from automated scanners.

### 🚨 Required security (do ALL of these):

#### 1. Firewall (UFW)
```bash
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw deny 18789/tcp     # Block gateway port externally
sudo ufw --force enable
```

#### 2. SSH Key-Only Authentication
⚠️ **Do this in order or you WILL lose access!**

```bash
# Step 1: On your LOCAL machine, generate a key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Step 2: Copy your public key to the server
ssh-copy-id user@your-server-ip

# Step 3: TEST key login from a NEW terminal (don't close the current one!)
ssh user@your-server-ip

# Step 4: Only after confirming key login works:
sudo sed -i "s/PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
sudo systemctl restart sshd
```

#### 3. Fail2Ban (Anti Brute-Force)
```bash
sudo apt-get install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

#### 4. Remote Access via Tailscale (recommended)
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Access via Tailscale IP only
```

---

## OpenClaw-Specific Hardening

These apply to **all** scenarios:

### Vulnerability Status

| # | Vulnerability | Fix | Status |
|---|--------------|-----|--------|
| 1 | Gateway exposed on 0.0.0.0:18789 | Bind to loopback only | ✅ Default |
| 2 | DM policy allows all users | Set dmPolicy to `pairing` | ✅ Default |
| 3 | Sandbox disabled by default | Docker container isolation | ✅ Docker |
| 4 | Credentials in plaintext | Environment variables + chmod 600 | ✅ Entrypoint |
| 5 | Prompt injection via web content | Wrap untrusted content in safety tags | ⚠️ Manual |
| 6 | Dangerous commands unblocked | Block rm -rf, curl pipes, git push --force | ⚠️ AGENTS.md |
| 7 | No network isolation | Docker network with `internal: true` option | ✅ Compose |
| 8 | Elevated tool access granted | Restrict MCP tools to minimum needed | ⚠️ Manual |
| 9 | No audit logging enabled | Logging + diagnostics enabled | ✅ Default |
| 10 | Weak/default pairing codes | Pairing mode with rate limiting | ✅ Default |

### What This Docker Setup Does Automatically:
- **Gateway binds to loopback** — not exposed to the internet
- **Credentials via env vars** — never stored in plaintext config
- **Config file permissions** — chmod 600 on startup
- **Non-root user** — container runs as `openclaw` user
- **No new privileges** — `security_opt: no-new-privileges`
- **Logging enabled** — info level + diagnostics by default
- **DM pairing mode** — users must be approved before chatting

---

## 🔍 Quick Security Audit

### Inside the container:
```bash
docker compose exec openclaw bash

# Check config permissions
stat -c '%a' ~/.openclaw/openclaw.json
# Expected: 600

# Check gateway binding
grep -o '"bind":"[^"]*"' ~/.openclaw/openclaw.json
# Expected: "bind":"lan"

# Check DM policy
grep -o '"dmPolicy":"[^"]*"' ~/.openclaw/openclaw.json
# Expected: "dmPolicy":"pairing"

# Run OpenClaw's built-in doctor
openclaw doctor
```

### On the host (VPS only):
```bash
# Check firewall
sudo ufw status

# Check SSH config
grep "PasswordAuthentication" /etc/ssh/sshd_config

# Check fail2ban
sudo fail2ban-client status sshd

# Check open ports
ss -tlnp | grep -E '18789|22'
```

---

## 📁 Config File Locations

**Inside the container:**

```
/home/openclaw/
├── .openclaw/                     # Main config directory
│   ├── openclaw.json              # ⚠️ CRITICAL - Contains tokens and settings
│   ├── credentials/               # OAuth tokens, refresh tokens
│   └── agents/
│       └── main/
│           └── sessions/
│               └── sessions.json  # Active sessions, conversation history
├── workspace/                     # Agent workspace
│   ├── AGENTS.md                  # ⚠️ Agent security rules
│   ├── SOUL.md                    # Agent personality
│   ├── TOOLS.md                   # Tool configuration
│   └── skills/                    # Custom skills
└── logs/                          # Persistent logs
```

---

## ⚠️ What NEVER to Do

❌ **NEVER commit `.env` to git**
```bash
# If you accidentally committed:
git rm --cached .env
git commit -m "Remove .env from repo"
git push

# And revoke all API keys immediately!
```

❌ **NEVER expose port 18789 publicly**
```yaml
# WRONG:
ports:
  - "0.0.0.0:18789:18789"  # ❌ Exposed to the world

# CORRECT:
ports:
  - "127.0.0.1:18789:18789"  # ✅ Local only
```

❌ **NEVER run the container as root**
```yaml
# WRONG:
user: root  # ❌ Security risk

# CORRECT:
user: openclaw  # ✅ Non-root (already the default)
```

---

## 📚 Resources

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [OpenClaw Website](https://openclaw.ai)
- [Discord Community](https://discord.gg/clawd)
- [GitHub](https://github.com/openclaw/openclaw)
