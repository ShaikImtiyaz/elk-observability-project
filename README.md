# End-to-End Observability Lab: FastAPI + Elastic Stack + OpenTelemetry

A hands-on observability learning project built locally on macOS using Docker Compose and Python. The goal is to practice collecting application logs, traces, and metrics, then searching and visualizing them with the Elastic Stack.

## Project status

### Completed
- [x] Elasticsearch 8.17.0 runs locally in Docker.
- [x] Kibana 8.17.0 runs locally in Docker.
- [x] FastAPI demo application starts.
- [x] `/health`, `/api/orders`, and `/api/payments` endpoints are implemented.
- [x] Application JSON log file is created at `logs/api.jsonl`.
- [x] Git repository has been initialized locally.

### In progress
- [ ] Configure Logstash to ingest the FastAPI JSON logs into Elasticsearch.
- [ ] Verify that API log documents are searchable in Elasticsearch and Kibana.
- [ ] Add OpenTelemetry instrumentation to FastAPI.
- [ ] Add an OpenTelemetry Collector and verify trace/metric export compatibility with the local Elastic setup.

### Planned
- [ ] Build a Kibana dashboard for API request volume, status codes, errors, and latency.
- [ ] Add log/metric collection with Filebeat or Elastic Agent.
- [ ] Add alerting and troubleshooting scenarios.
- [ ] Add automation and deployment documentation.

> Status note: Logstash ingestion was being troubleshot when this README was written. OpenTelemetry integration is planned and should not be considered complete until it is tested end to end.

## Architecture

Current intended flow:

```text
FastAPI application
  └── JSON logs: logs/api.jsonl
        └── Logstash
              └── Elasticsearch
                    └── Kibana
```

Planned telemetry flow:

```text
FastAPI + OpenTelemetry SDK
  └── OTLP (gRPC :4317 / HTTP :4318)
        └── OpenTelemetry Collector
              └── Supported Elastic-compatible export path
                    └── Elasticsearch / Kibana
```

The OpenTelemetry export configuration must be tested against the exact versions and configuration in this lab; direct OTLP ingestion by Elasticsearch should not be assumed.

## Prerequisites

- macOS (tested workflow intended for Apple Silicon)
- Docker Desktop
- Python 3.12 or another version supported by the installed dependencies
- Git
- A GitHub account if you want to publish the repository

## Project structure

```text
elk-observability-project/
├── app/                  # FastAPI application
├── docs/                 # Project notes and documentation
├── filebeat/             # Planned Filebeat configuration
├── logs/                 # Local JSON application logs
├── logstash/
│   └── pipeline/         # Logstash pipeline configuration
├── otel/                 # OpenTelemetry Collector configuration (planned/in progress)
├── scripts/              # Helper scripts
├── compose.yaml           # Elasticsearch, Kibana, and added services
├── README.md
└── .gitignore
```

Some folders may be empty while their stages are in progress.

## Start Elasticsearch and Kibana

From the project directory:

```bash
docker compose -f compose.yaml up -d
docker compose -f compose.yaml ps
```

Check Elasticsearch:

```bash
curl http://localhost:9200
```

Open Kibana in your browser:

- http://localhost:5601

## Run the FastAPI application

Activate the project's virtual environment:

```bash
cd ~/elk-observability-project
source .venv/bin/activate
```

Create the log directory if needed:

```bash
mkdir -p logs
```

Install the application dependencies if needed:

```bash
python -m pip install fastapi "uvicorn[standard]"
```

Start the application:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal, test the endpoints:

```bash
curl http://localhost:8000/health
curl -i http://localhost:8000/api/orders
curl -i http://localhost:8000/api/payments
```

Generate several sample requests:

```bash
for i in {1..10}; do
  curl -s http://localhost:8000/api/orders
  echo
  curl -s http://localhost:8000/api/payments
  echo
done
```

Inspect the JSON log file:

```bash
tail -n 5 logs/api.jsonl
```

## Logstash troubleshooting

Check the Logstash container:

```bash
docker compose -f compose.yaml ps
docker logs --tail 100 elk-logstash
```

The earlier pipeline startup failure was caused by `file_completed_log_path` trying to create a file inside a read-only mounted log directory. The attempted fix was to remove these two options from `logstash/pipeline/logstash.conf`:

```text
file_completed_action => "log"
file_completed_log_path => "/usr/share/logstash/logs/completed.log"
```

After changing the pipeline, recreate Logstash:

```bash
docker compose -f compose.yaml up -d --force-recreate logstash
docker logs --tail 100 elk-logstash
```

Check for indices and documents:

```bash
curl -s "http://localhost:9200/_cat/indices?v"
curl -s "http://localhost:9200/api-logs-*/_search?pretty&size=3"
```

If the index is missing, inspect the Logstash logs before changing additional configuration. The current file input uses read mode, so continuous log tailing still needs to be configured and verified.

## Git and GitHub

Before publishing, review `.gitignore` and make sure local logs, virtual environments, secrets, and generated data are not committed. See the GitHub section in the project setup notes or use these commands:

```bash
git status
git add README.md .gitignore app compose.yaml logstash filebeat scripts docs otel
git status
git commit -m "Document observability lab setup"
```

Create an empty repository on GitHub (do not initialize it with a README if you already have this local README). Then connect and push, replacing `YOUR_GITHUB_USERNAME` with your username and `elk-observability-project` with the repository name if different:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/elk-observability-project.git
git push -u origin main
```

If `origin` already exists, inspect it first:

```bash
git remote -v
```

If needed, update it rather than adding a duplicate:

```bash
git remote set-url origin https://github.com/YOUR_GITHUB_USERNAME/elk-observability-project.git
git push -u origin main
```

## Safety and repository hygiene

- Do not commit `.venv/`, `.env` files, passwords, API keys, certificates, local log files, Elasticsearch data, or other secrets.
- Keep the local Elasticsearch/Kibana ports bound to `127.0.0.1` for this learning setup.
- This project is for local learning, not a production deployment.
- Confirm all configurations and data paths before running destructive Docker volume commands. Do not remove the `esdata` volume unless you intentionally want to delete local Elasticsearch data.

## Learning objectives

By completing this project, you will practice:

- Structured application logging
- Log ingestion and parsing with Logstash
- Searching and visualizing logs with Elasticsearch and Kibana
- OpenTelemetry instrumentation and OTLP
- Collector pipelines and telemetry export
- Dashboard design, alerting, and troubleshooting
- Git-based version control and project documentation
