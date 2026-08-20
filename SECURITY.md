# IDataProject — Security Baseline

**Status:** Framework documented (Aug 19–20). Security controls are implemented progressively from Aug 31 onward as endpoints are built.  
**Last Updated:** 2026-08-18

---

## Security Principles

1. **Defense in depth:** Multiple layers of validation (client-side, server-side, database)
2. **Least privilege:** API keys grant only RFID scan ingestion, not full Odoo access
3. **Audit everything:** All scans logged with operator, device, timestamp, result
4. **Fail securely:** On errors, deny access (not open)
5. **No secrets in code:** Use environment variables, secrets manager

---

## Data Classification

| Data | Sensitivity | Protection | Retention |
|------|-------------|-----------|-----------|
| EPC (tag ID) | Medium | Encrypted in transit, indexed in DB | Per company retention policy |
| Session ID | Medium | HTTPS only, session-scoped | Auto-expire 24 hours |
| API key | High | Android Keystore, never logged | Rotate every 90 days |
| Operator ID | Medium | Audit logged with each scan | Per company retention policy |
| RSSI/signal | Low | Cleartext (no PII) | Auto-archive after 30 days |
| Inventory qty | Medium | Access controlled by Odoo ACL | Per company retention policy |

---

## Authentication & Authorization

### API Key Lifecycle

**Generation (admin):**
1. Admin creates API key in Odoo Settings → Users → [operator user] → "API Keys"
2. Odoo generates: `key_<32-char-random>` + secret (shown once)
3. Key stored in Odoo database (hashed with SHA-256)
4. Secret shared with operator (printed QR code for easy scanning into Android app)

**Validation (every request):**
```python
# backend/stock_barcode_rfid/controllers/security.py

def validate_api_key(request, api_key):
    """Validate API key, return (is_valid, user_id)."""
    if not api_key or len(api_key) < 20:
        return False, None

    # Hash the key and look up in database
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    api_key_rec = env['ir.api.key'].search([
        ('key_hash', '=', key_hash),
        ('state', '=', 'active'),
        ('expiration_date', '>=', fields.Datetime.now()),
    ], limit=1)

    if not api_key_rec:
        _logger.warning(f"Invalid or expired API key attempt: {api_key[:8]}...")
        return False, None

    # Rate limiting: check # of requests in last minute
    one_min_ago = fields.Datetime.now() - timedelta(minutes=1)
    req_count = env['stock.barcode.rfid.request_log'].search_count([
        ('api_key_id', '=', api_key_rec.id),
        ('create_date', '>=', one_min_ago),
    ])

    if req_count > 100:  # Max 100 requests/min
        _logger.warning(f"Rate limit exceeded for key {api_key_rec.id}: {req_count} requests in 1min")
        return False, None

    return True, api_key_rec.user_id.id
```

**Expiration (automatic):**
- Keys expire after 90 days
- Operator prompted to re-generate in Android app settings
- Expired keys still work for 7-day grace period (log warning)
- After grace period: 401 Unauthorized

**Revocation (admin):**
- Admin can immediately revoke a key (e.g., lost device)
- Key marked `state = 'revoked'`, validation fails
- Operator loses access, must request new key

### Authorization Scopes

API key permissions (Odoo OAuth-style):

```
read:stock.barcode_rfid       # Can read own scan logs
write:stock.barcode_rfid      # Can POST scans
read:stock.lot                # Can look up lot IDs
```

Only these scopes granted; full Odoo admin access NOT included.

---

## Input Validation

### EPC Format Validation

```python
def validate_epc(epc):
    """Validate EPC is 96-bit hex (24 chars)."""
    errors = []

    if not isinstance(epc, str):
        errors.append("EPC must be string")
    elif len(epc) != 24:
        errors.append(f"EPC must be 24 hex chars, got {len(epc)}")
    
    try:
        int(epc, 16)  # Validate hex
    except ValueError:
        errors.append(f"EPC contains non-hex characters: {epc}")

    if errors:
        raise exceptions.ValidationError("; ".join(errors))
```

### Session ID Validation

```python
def validate_session_id(session_id):
    """Validate session ID format."""
    if not re.match(r'^barcode_session_[a-f0-9]{8}$', session_id):
        raise exceptions.ValidationError(
            f"Invalid session ID format: {session_id}. "
            f"Expected: barcode_session_<8-hex>"
        )
```

### RSSI Range Validation

```python
def validate_rssi(rssi):
    """Validate RSSI is in reasonable range (-100 to 0 dBm)."""
    if not isinstance(rssi, int) or rssi < -100 or rssi > 0:
        raise exceptions.ValidationError(
            f"RSSI must be integer in range [-100, 0], got {rssi}"
        )
```

### SQL Injection Prevention

Never concatenate user input into SQL queries:

```python
# ❌ WRONG
query = f"SELECT * FROM stock_lot WHERE name = '{epc}'"
env.cr.execute(query)

# ✓ CORRECT (Odoo ORM handles escaping)
lot = env['stock.lot'].search([('name', '=', epc)])

# ✓ CORRECT (raw SQL with parameterized query)
env.cr.execute("SELECT * FROM stock_lot WHERE name = %s", (epc,))
```

---

## Data Security

### In Transit

**HTTPS/TLS:**
- All prod traffic encrypted (TLS 1.2+)
- Certificate pinned in Android app (prevent MITM)
- Dev environment: HTTP allowed (localhost only)

**Certificate Pinning (Android):**
```kotlin
// app/src/main/kotlin/com/idataproject/network/OdooClient.kt

class OdooClient(private val certificatePin: String) {
    private val certificatePinner = CertificatePinner.Builder()
        .add("odoo.warehouse.internal", "sha256/" + certificatePin)
        .build()

    private val httpClient = OkHttpClient.Builder()
        .certificatePinner(certificatePinner)
        .build()
}
```

### At Rest

**Database:**
- PostgreSQL data encrypted at rest (LUKS volume encryption in prod)
- Sensitive fields encrypted with `AES-256-GCM`:

```python
# backend/stock_barcode_rfid/models/__init__.py

class IrApiKey(models.Model):
    _inherit = 'ir.api.key'

    key_hash = fields.Char('Key Hash', encrypt=True)  # Odoo field encryption
```

**Android:**
- API keys stored in **Android Keystore** (hardware-backed encryption if available)
- Keystore requires fingerprint/PIN to unlock (operator authentication)

```kotlin
// app/src/main/kotlin/com/idataproject/storage/SecurePreferences.kt

class SecurePreferences(private val context: Context) {
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

    fun saveApiKey(key: String) {
        val cipher = Cipher.getInstance(KeyProperties.KEY_ALGORITHM_AES + "/" + 
            KeyProperties.BLOCK_MODE_GCM + "/" + KeyProperties.ENCRYPTION_PADDING_NONE)
        cipher.init(Cipher.ENCRYPT_MODE, keyStore.getKey("idata_key", null) as SecretKey)
        
        val encryptedKey = cipher.doFinal(key.toByteArray())
        context.getSharedPreferences("idata_secure", Context.MODE_PRIVATE)
            .edit()
            .putString("api_key", Base64.encodeToString(encryptedKey, Base64.DEFAULT))
            .apply()
    }
}
```

---

## Audit & Logging

Every RFID scan logged with full context:

```python
# Model: stock.barcode.rfid (audit table)

class StockBarcodeRFID(models.Model):
    _name = 'stock.barcode.rfid'

    epc = fields.Char('EPC', required=True)
    lot_id = fields.Many2one('stock.lot')
    session_id = fields.Char('Session ID')
    operator_id = fields.Many2one('res.users')
    device_id = fields.Char('Device ID')  # Zebra serial
    rssi = fields.Integer('RSSI (dBm)')
    timestamp_ms = fields.BigInteger('Client Timestamp (ms)')
    server_receive_time = fields.Datetime('Server Receive Time')
    is_duplicate = fields.Boolean('Marked as Duplicate')
    duplicate_of_id = fields.Many2one('stock.barcode.rfid')
    status = fields.Selection([
        ('queued', 'Queued'),
        ('relayed', 'Relayed to Barcode UI'),
        ('buffered', 'Buffered (no active session)'),
    ])

    _sql_constraints = [
        ('unique_scan', 'UNIQUE(epc, session_id, create_date)', 
         'Cannot have identical EPC scans within 2 seconds'),
    ]
```

**Retention:**
- Scans archived after 30 days to cold storage (S3, backup tape)
- Operator can request data deletion (GDPR compliance, handled via Odoo privacy module)

**Log Aggregation:**
- All logs sent to centralized log sink (ELK, Splunk, or Datadog)
- Structured logging: JSON format, no bare exceptions

```python
import logging
import json

logger = logging.getLogger(__name__)

# Log scan event
logger.info(json.dumps({
    "event": "rfid_scan_received",
    "epc": epc,
    "lot_id": lot_id,
    "session_id": session_id,
    "operator_id": operator_id,
    "rssi": rssi,
    "is_duplicate": is_duplicate,
    "timestamp": datetime.now().isoformat(),
}))
```

---

## Threat Model

### Threat: Unauthorized EPCs injected into inventory count

**Attack:** Bad actor POSTs fake EPCs to manipulate stock quantity.

**Mitigations:**
- ✓ API key authentication (only authorized users can submit)
- ✓ Session validation (EPC only accepted if active Barcode session exists)
- ✓ EPC validation via rfid.tag.mapping lookup (EPC must resolve to a known product mapping)
- ✓ Audit trail (every scan logged with operator + device)
- ✓ Rate limiting (suspicious bulk submissions detected)

**Residual risk:** Compromised API key (Low: key expires 90 days, Keystore encryption)

### Threat: Cross-user scan hijacking (operator A's scans attributed to operator B)

**Attack:** Attacker intercepts or replays scan POSTs from operator A.

**Mitigations:**
- ✓ TLS encryption (HTTPS only)
- ✓ Certificate pinning (prevent MITM)
- ✓ Session ID binding (scan only valid for the operator who started session)
- ✓ Timestamp validation (reject replay attacks with old timestamps)

**Residual risk:** Compromised device (Keystore breach). Mitigation: PIN/fingerprint unlock.

### Threat: DoS attack on /stock_barcode_rfid/scan endpoint

**Attack:** Attacker floods endpoint with 10k requests/sec.

**Mitigations:**
- ✓ Rate limiting (100 req/min per API key)
- ✓ Nginx request throttling (200 req/sec global)
- ✓ Request queuing (Celery/RQ for async processing)

**Residual risk:** Sophisticated DDoS (botnet). Mitigation: WAF (Cloudflare, AWS Shield).

### Threat: EPC prediction/enumeration (attacker brute-forces valid EPCs)

**Attack:** Attacker tries sequential EPCs to find valid ones.

**Mitigations:**
- ✓ EPC format validation (must be valid hex)
- ✓ Session binding (only valid within active session)
- ✓ rfid.tag.mapping validation (only EPCs that resolve to a mapped product are accepted without operator review)
- ✓ Rate limiting (slows enumeration)

**Residual risk:** Low. EPCs are 24 hex chars (2^96 possible values); enumeration infeasible.

---

## Secrets Management

### Environment Variables (Dev)

**Never commit secrets to Git:**

```bash
# ✓ .env.example (safe template, committed)
ODOO_ADMIN_PASSWD=<CHANGE_ME>
POSTGRES_PASSWORD=<CHANGE_ME>
ODOO_API_KEY_SAMPLE=key_abc123xyz  # Fake key for testing

# .env (actual secrets, gitignored)
ODOO_ADMIN_PASSWD=SuperSecure!Passwd123
POSTGRES_PASSWORD=PostgresSecret456
```

**Commit hooks prevent secrets:**
```bash
# .git/hooks/pre-commit
#!/bin/bash
if git diff --cached | grep -E "POSTGRES_PASSWORD|ODOO_ADMIN|api_key.*="; then
    echo "ERROR: Secrets detected in commit. Use .env.example instead."
    exit 1
fi
```

### Production Secrets (Phase 7)

Use **Odoo's built-in secret manager** or external vault:

```python
# Production setup: use AWS Secrets Manager or HashiCorp Vault

from odoo.addons.base.models.res_config import general_settings

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    odoo_api_key_master = fields.Char(
        'Master API Key',
        help='Fetched from AWS Secrets Manager in prod',
    )

    @api.model
    def _get_secret(self, key_name):
        """Fetch secret from vault, never cache in code."""
        import boto3
        client = boto3.client('secretsmanager', region_name='us-east-1')
        response = client.get_secret_value(SecretId=key_name)
        return response['SecretString']
```

---

## Compliance & Standards

- **OWASP Top 10:** Mitigated for A01 (Broken Access Control), A03 (Injection), A07 (Identification & Auth Failure)
- **PCI-DSS:** If storing payment card data: N/A for Phase 1 (inventory only)
- **GDPR:** Operator data (user ID, device ID) deleted per Odoo privacy module
- **SOC 2:** Audit logs, access control, encryption (add SOC 2 certification process in Phase 7)

---

## Security Checklist (Sep 2 — Before API is wired to Android)

- [ ] Odoo API key generation/validation implemented
- [ ] Rate limiting configured (100 req/min per key)
- [ ] HTTPS enabled on Odoo instance (self-signed OK for dev, real cert for prod)
- [ ] Input validation tested (EPC, session ID, RSSI)
- [ ] Android Keystore integration tested (API key encryption)
- [ ] Audit logging working (every scan in stock.barcode.rfid)
- [ ] Secrets removed from Git (git-secrets installed, test commit blocked)
- [ ] SQL injection tests passed (manual + automated)
- [ ] OWASP ZAP scan run, no critical findings
- [ ] Android app code obfuscation enabled (ProGuard/R8)

---

## Security Review Schedule

- **After Sep 2 auth endpoint is live:** Internal security review (code inspection, pen test) → document findings
- **After Oct 9 security pass:** External security sign-off (3rd-party firm or senior audit)
- **Post-pilot production rollout:** Continuous monitoring (SIEM alerts, vulnerability scanning)

---

## Reporting Security Issues

**Do not open public GitHub issues for security vulnerabilities.**

Contact: security@idataproject.internal (or admin email)

Include:
- Vulnerability description
- Steps to reproduce
- Potential impact
- Proof-of-concept (if safe)

**Response time:** 24 hours acknowledgment, 7 days fix assessment.

---

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Android Security & Privacy: https://developer.android.com/privacy-and-security
- Odoo Security: https://www.odoo.com/documentation/17.0/applications/general/iot/devices/security_concerns.html
- TLS/HTTPS: https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html
