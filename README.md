# IDataProject — RFID-Odoo Integration

**Replace warehouse barcode scanning with UHF RFID. Extensible to toll/highway asset tracking.**

---

## Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose
- Git
- Zebra T1/T2 device (for Phase 3+)

### Setup

```bash
# Clone repository
git clone https://github.com/qspcgonzales-arch/IDataProject.git
cd IDataProject

# Copy environment template
cp .env.example .env

# Start development stack (Odoo 19 + PostgreSQL + Redis)
docker-compose up -d

# Wait for Odoo to be ready (~30 sec)
docker-compose logs -f odoo | grep "HTTP listening"

# Access Odoo
# Web: http://localhost:8069
# Default user: admin / admin
```

See `DEVELOPMENT.md` for detailed setup guides for each component.

---

## Project Structure

```
IDataProject/
├── ARCHITECTURE.md              # System design & data flows
├── DEVELOPMENT.md               # Development workflow & standards
├── SECURITY.md                  # Auth, encryption, threat model
├── API_CONTRACT.md              # OpenAPI spec for RFID endpoints
├── docker-compose.yml           # Local dev environment
├── .env.example                 # Configuration template
├── backend/                     # Odoo custom modules (Python)
│   ├── stock_barcode_rfid/      # Main RFID bridge module
│   ├── stock_barcode_rfid_calibration/  # Phase 4: calibration
│   └── requirements.txt
├── android/                     # Zebra T1/T2 scanner app (Kotlin)
│   ├── README.md                # Android-specific setup
│   ├── build.gradle.kts
│   └── app/src/...
├── docs/                        # Extended documentation
├── tests/                       # Integration & E2E tests
└── .github/workflows/           # CI/CD pipelines
```

---

## Documentation

Start here based on your role:

### **For Everyone**
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Understand the system design, data flows, and decisions (15 min read)
- **[Phase 0 Decisions](IDataProject-Phase0-Decisions.md)** — What we've locked down (hardware, Odoo version, strategies)
- **[12-Week Roadmap Package](ROADMAP_12WEEK_REALISTIC.md)** — Weekly execution plan, gates, critical path, tracker, and contingencies

### **For Backend Developers**
- **[DEVELOPMENT.md](DEVELOPMENT.md)** — Development environment setup, coding standards, testing
- **[API_CONTRACT.md](API_CONTRACT.md)** — Odoo RFID bridge endpoint specs (OpenAPI)
- **[SECURITY.md](SECURITY.md)** — Auth, input validation, audit logging
- **[backend/README.md](backend/README.md)** — Odoo module structure & conventions

### **For Android Developers**
- **[android/README.md](android/README.md)** — Android dev environment and RFID SDK integration
- **[API_CONTRACT.md](API_CONTRACT.md)** — API endpoints the Android app calls
- **[DEVELOPMENT.md](DEVELOPMENT.md)** — Testing strategy, Kotlin conventions

### **For DevOps / Deployment**
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** — Production setup (Phase 7)
- **[docker-compose.yml](docker-compose.yml)** — Local Docker environment
- **[.github/workflows/](.)** — CI/CD pipeline definitions

### **For Troubleshooting**
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** — Common issues & fixes

### **External Reference**
- **[Spider's RFID — RFID Odoo Integration Best Practices](https://www.spidersrfid.com/en/articles/rfid-odoo-integration-best-practices)** — Additional implementation guidance and integration best practices

---

## Roadmap & Phases

The tracker sheet is the source of truth for execution status and dates. This roadmap reflects the current tracker schedule, not the earlier generic phase framework.

| Window | Scope | Status |
|---|---|---|
| Aug 19-Aug 22 | Hardware validation gate (iData SDK functional on emulator + real device) | Planned/Complete by gate |
| Aug 24-Sep 10 | Foundation + widened integration (Odoo scaffold, Android scaffold, scan bridge, injection POC) | Planned |
| Sep 11-Sep 24 | Live RFID hardware loop hardening + gate confirmation | Planned |
| Sep 28-Oct 8 | Calibration + offline queue validation + accuracy gate | Planned |
| Oct 12-Oct 20 | Pilot readiness + UAT + production checklist gate | Planned |
| Oct 21-Oct 28 | Pilot shadow-run + final go/no-go sign-off | Planned |

**Current:** 12-week plan is active from Aug 19 to Oct 28 with explicit go/no-go gates and contingency pivots.

See [ROADMAP_12WEEK_REALISTIC.md](ROADMAP_12WEEK_REALISTIC.md) for the full weekly roadmap and decision gates.  
Execution tracker: [TRACKER_12WEEK.csv](TRACKER_12WEEK.csv)  
Gate details: [GATES_AND_CHECKPOINTS.md](GATES_AND_CHECKPOINTS.md)  
Critical path: [MILESTONES_CRITICAL_PATH.md](MILESTONES_CRITICAL_PATH.md)  
Contingencies: [CONTINGENCY_AND_ROLLBACK.md](CONTINGENCY_AND_ROLLBACK.md)

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | Odoo | 19.0 |
| Backend Language | Python | 3.10+ |
| Database | PostgreSQL | 15 |
| Caching | Redis | 7 |
| Mobile | Kotlin | 1.9+ |
| Mobile SDK | iData T1UHF SDK | Latest |
| Deployment | Docker & Compose | Latest |
| CI/CD | GitHub Actions | — |

---

## Success Metrics

✓ **Accuracy:** ≥99% of tags read correctly in calibrated zone  
✓ **Speed:** 60–70% faster inventory counting vs. barcode  
✓ **Stability:** <0.1% scan loss during live warehouse use  
✓ **Uptime:** 99.5% during warehouse operating hours  

See [ARCHITECTURE.md](ARCHITECTURE.md#success-metrics) for details.

---

## Key Decisions

- **Odoo Version:** 19.0 (latest, deployed)
- **EPC Mapping:** EPC → stock.lot.name via Barcode Nomenclature rule
- **Encoding:** Hybrid (in-house + pre-encoded supplier tags)
- **Workflow Priority:** Start with Inventory Adjustments (cycle counts)
- **Hardware:** iData T1UHF RFID handheld scanner (primary focus product)
- **Architecture:** Monorepo (backend + android in one repo, shared infrastructure)

See [Phase 0 Decisions](IDataProject-Phase0-Decisions.md) for full rationale.

---

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes & Test Locally
```bash
# Backend: run Odoo tests
cd backend
python -m pytest tests/ -v

# Android: run build & unit tests
cd ../android
./gradlew test
```

### 3. Commit with Clear Messages
```bash
git commit -m "feat(stock_barcode_rfid): add EPC validation

- Implement 96-bit EPC hex format validation
- Add unit tests for invalid inputs
- Closes #42"
```

### 4. Push & Create Pull Request
```bash
git push origin feature/your-feature-name
```

See [DEVELOPMENT.md](DEVELOPMENT.md#development-workflow) for full workflow.

---

## Code Review Checklist

Before your PR is merged:

- [ ] All tests pass locally + CI green
- [ ] Code follows style guide (PEP 8 for Python, Google Android style for Kotlin)
- [ ] No secrets or credentials committed
- [ ] Security: input validation, rate limiting, auth checks
- [ ] Documentation: docstrings, non-obvious logic commented
- [ ] Performance: no N+1 queries, no main-thread blocking
- [ ] Backwards compatible (no breaking API changes)

---

## Common Tasks

### Run Tests
```bash
# Backend (Odoo)
cd backend && python -m pytest tests/ -v

# Android
cd android && ./gradlew test

# Integration tests
cd tests && python -m pytest test_rfid_bridge_e2e.py -v
```

### Start Development Server
```bash
docker-compose up -d
# Odoo available at http://localhost:8069
```

### Check Logs
```bash
# Odoo logs
docker-compose logs -f odoo

# All services
docker-compose logs -f
```

### Update Environment
```bash
cp .env.example .env
# Edit .env with your values
docker-compose restart odoo
```

---

## Troubleshooting

**Odoo won't start?**
```bash
docker-compose logs odoo | tail -50
```

**PostgreSQL connection error?**
```bash
docker-compose restart postgres
sleep 5
docker-compose restart odoo
```

**Android build failing?**
```bash
cd android && ./gradlew clean build --info
```

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more.

---

## Security

⚠️ **IMPORTANT:** Never commit secrets (passwords, API keys) to Git.

- Use `.env` for local development (gitignored)
- Use environment variables or a secrets manager in production
- See [SECURITY.md](SECURITY.md) for full details

---

## Contributing

1. **Read [ARCHITECTURE.md](ARCHITECTURE.md)** first to understand the system
2. **Follow [DEVELOPMENT.md](DEVELOPMENT.md)** for coding standards
3. **Run tests before committing** (see "Common Tasks" above)
4. **Create a Pull Request** with clear description
5. **Address code review feedback** and CI checks

---

## Support

- **Questions?** Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) first
- **Security issue?** Email: security@idataproject.internal (do NOT open public issue)
- **Bug report?** Open a GitHub Issue with steps to reproduce
- **Feature request?** Discuss in team channel first, then GitHub Discussions

---

## License

Apache 2.0 — See LICENSE file

---

## Project Status

| Aspect | Status | Notes |
|--------|--------|-------|
| Architecture | ✅ Locked | Phase 0 complete |
| Backend | 🔲 In Development | Phase 1 starts |
| Android | 🔲 Not Started | Phase 1-3 |
| Testing | 🔲 Scaffolding | CI/CD stubs only |
| Documentation | ✅ Complete | ARCHITECTURE, DEVELOPMENT, SECURITY, API_CONTRACT |
| Deployment | 🔲 Phase 7 | Docker Compose ready for dev |

---

**Last Updated:** 2026-08-20  
**Next Milestone:** Gate 0.5 (iData SDK functional validation by Aug 22)
