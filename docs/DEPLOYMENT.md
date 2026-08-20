# Deployment Guide

**Status:** Placeholder — production deployment is out of scope for the pilot phase.  
**Planned:** Post-pilot production rollout (after Oct 16 go/no-go decision).

---

## Current Dev Deployment

Use `docker-compose up -d` for local development. See `DEVELOPMENT.md` for the full quick-start.

## Pilot Deployment (Oct 12–16)

The pilot runs on the same Docker Compose stack, deployed to a warehouse-local machine or cloud VM with the following additions:
- HTTPS via a real TLS certificate (not self-signed)
- `workers = 4` in `backend/odoo.conf`
- Firewall rules limiting `/stock_barcode_rfid/*` to the Android device IP range

## Production Rollout (Post-Pilot)

Full production deployment guide will be written after pilot UAT sign-off. Topics will include:
- Zone-by-zone rollout checklist
- Multi-worker Odoo configuration
- PostgreSQL backup schedule
- API key rotation procedure
- Certificate pinning update flow for Android fleet

---

*This document will be written during the post-pilot production rollout phase.*
