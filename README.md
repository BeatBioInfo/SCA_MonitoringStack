# Monitoring Stack — Prometheus, Grafana, Loki, Alloy

A complete observability stack built from scratch during the SCA DevOps Bootcamp (Week 9).
Follows the *build from the docs* approach — every config file in this repo traces back to an official documentation page.

## What's inside

A Docker Compose setup running seven services on one private network:

- **pay-api** — a Flask application instrumented with the `prometheus_client` library, exposing Counter, Histogram, and Gauge metrics at `/metrics`
- **traffic-generator** — a small shell script that continuously hits `pay-api` so there's live data to graph
- **node-exporter** — system-level metrics (CPU, memory, disk, network) on port 9100
- **prometheus** — pull-based metrics database scraping three targets every 15s (port 9090)
- **grafana** — visualization layer (port 3000)
- **loki** — log aggregation (port 3100)
- **alloy** — log collector; uses the Docker socket to discover containers and ship their logs to Loki

## Architecture

```
                    ┌──────────────┐
                    │   Grafana    │  :3000
                    └──────┬───────┘
                           │ queries
              ┌────────────┴────────────┐
              │                         │
      ┌───────▼──────┐          ┌───────▼──────┐
      │  Prometheus  │ :9090    │     Loki     │ :3100
      └───────▲──────┘          └───────▲──────┘
              │ scrapes                 │ push
              │                         │
        ┌─────┴──────┐             ┌────┴─────┐
        │  pay-api   │ :5000       │  Alloy   │
        │  node-exp  │ :9100       └────┬─────┘
        └────────────┘                  │ reads
                                 ┌──────▼───────┐
                                 │ Docker sock  │
                                 └──────────────┘
```

## Getting started

### Prerequisites

- Docker and Docker Compose v2
- 2 GB RAM minimum (4 GB recommended)

### Run it

```bash
docker compose up -d --build
```

First run takes 2–4 minutes while Docker pulls images and builds `pay-api`.

### Verify

```bash
docker compose ps
```

All seven containers should show `Up`.

Then open in a browser:

| URL                          | What you should see                           |
|------------------------------|-----------------------------------------------|
| `http://<host>:5000`         | "Welcome to Pay-API"                          |
| `http://<host>:5000/metrics` | Raw Prometheus metrics                        |
| `http://<host>:9100/metrics` | Node Exporter system metrics                  |
| `http://<host>:9090`         | Prometheus UI → Status → Targets → three UP   |
| `http://<host>:3000`         | Grafana (login: `admin` / `admin`)            |

## Project layout

```
monitoring-stack/
├── docker-compose.yml          # Orchestrates all seven services
├── config/
│   ├── prometheus.yml          # Scrape config: 3 targets
│   ├── loki-config.yml         # Loki: filesystem storage, single instance
│   └── alloy-config.alloy      # 4-stage log pipeline: discover → relabel → collect → ship
├── pay-api/
│   ├── app.py                  # Flask app with Counter, Histogram, Gauge metrics
│   ├── requirements.txt
│   └── Dockerfile
└── traffic-generator/
    └── generate-traffic.sh     # Generates ~5 req/s to pay-api
```

## First PromQL queries to try

Once the stack is running, go to `http://<host>:9090` and try:

```promql
up                                           # 1 for each reachable target
rate(http_requests_total[5m])                # requests per second, by endpoint/status
payment_success_total                        # counter of successful payments
(node_memory_MemTotal_bytes - node_memory_MemFree_bytes) / 1024 / 1024
                                             # memory usage in MB
```

## References used

- Prometheus: https://prometheus.io/docs/prometheus/latest/getting_started/
- Node Exporter guide: https://prometheus.io/docs/guides/node-exporter/
- `prometheus_client` (Python): https://prometheus.github.io/client_python/
- Grafana + Prometheus: https://grafana.com/docs/grafana/latest/datasources/prometheus/
- Loki Docker install: https://grafana.com/docs/loki/latest/setup/install/docker/
- Alloy + Docker discovery: https://grafana.com/docs/alloy/latest/reference/components/discovery/discovery.docker/

## Notes

- This is a lab setup. `auth_enabled: false` on Loki, default `admin/admin` on Grafana, and public-access security group rules are for learning only — never for production.
- Data in the `prometheus-data`, `grafana-data`, and `loki-data` named volumes survives `docker compose down` but is wiped by `docker compose down -v`.