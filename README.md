<h1>Multi-Tenant Observability Stack with Grafana Alloy</h1>

<p>This repository contains a fully containerized, multi-tenant observability stack. It demonstrates how to collect logs, metrics, and traces from isolated application workloads and route them securely to dedicated multi-tenant backends using <nw-concept>Grafana Alloy</nw-concept> as a high-performance telemetry pipeline.</p>

<h2>🏗️ Architecture Overview</h2>
<p>The architecture is divided into three distinct layers:</p>
<ul>
  <li><strong>Telemetry Generators (Applications):</strong> Two Python microservices instrumented with <nw-concept>OpenTelemetry</nw-concept> SDKs. They export telemetry in the <nw-concept>OTLP</nw-concept> format.</li>
  <li><strong>Routing Agent (Collector):</strong> <nw-concept>Grafana Alloy</nw-concept> receives the incoming OTLP traffic. It reads the <nw-code-block inline="true" language="text">service.namespace</nw-code-block> resource attribute and injects the corresponding tenant ID into the HTTP header.</li>
  <li><strong>Multi-Tenant Storage (Backends):</strong> <nw-concept>Mimir</nw-concept> (metrics), <nw-concept>Loki</nw-concept> (logs), and <nw-concept>Tempo</nw-concept> (traces) enforce tenant isolation using the <nw-code-block inline="true" language="text">X-Scope-OrgID</nw-code-block> HTTP header.</li>
</ul>

<h2>📂 Project Structure</h2>
<pre>
.
├── apps/
│   ├── backend/
│   │   ├── app.py              # Simulates batch-processor telemetry
│   │   ├── Dockerfile          # Lowercase "D" for BuildKit compatibility
│   │   └── requirements.txt    # OpenTelemetry Python SDK libraries
│   └── frontend/
│       ├── app.py              # Simulates frontend-api HTTP telemetry
│       ├── Dockerfile          # Container build definition
│       └── requirements.txt    # Pinned dependency versions
├── config/
│   ├── alloy.config            # Grafana Alloy processing pipeline
│   ├── loki.yaml               # Loki local storage & multi-tenancy rules
│   ├── mimir.yaml              # Mimir TSDB & active tenant rules
│   ├── tempo.yaml              # Tempo OTLP receiver endpoints & trace blocks
│   └── grafana-datasources.yaml # Automated datasource provisioning
└── docker-compose.yaml         # Complete 7-service orchestration blueprint
</pre>

<h2>⚙️ Configuration & Tenant Boundaries</h2>
<p>Isolation boundaries are defined in the configurations through the following configurations:</p>
<ul>
  <li><strong>Mimir & Tempo:</strong> Activated with <nw-code-block inline="true" language="yaml">multitenancy_enabled: true</nw-code-block></li>
  <li><strong>Loki:</strong> Activated with <nw-code-block inline="true" language="yaml">auth_enabled: true</nw-code-block></li>
</ul>
<p>With these flags enabled, any request arriving at the storage gateways <em>must</em> include the <nw-code-block inline="true" language="text">X-Scope-OrgID</nw-code-block> header, or it will be rejected.</p>

<h2>🚀 Getting Started</h2>

<h3>Prerequisites</h3>
<ul>
  <li>Docker Desktop running on macOS/Linux/Windows</li>
  <li>Terminal CLI</li>
</ul>

<h3>1. Build the Applications</h3>
<p>Compile the instrumented application containers:</p>
<pre>docker compose build team-frontend team-backend</pre>

<h3>2. Pull Pre-Built Containers</h3>
<p>Pull the remaining pipeline, storage, and visualization images:</p>
<pre>docker compose pull --ignore-buildable</pre>

<h3>3. Run the Stack</h3>
<p>Launch the platform in detached mode:</p>
<pre>docker compose up -d</pre>

<h3>4. Access the Stack Services</h3>
<ul>
  <li><strong>Grafana:</strong> <a href="http://localhost:3000" target="_blank">http://localhost:3000</a> (Visualize isolated dashboards)</li>
  <li><strong>Grafana Alloy UI:</strong> <a href="http://localhost:12345" target="_blank">http://localhost:12345</a> (Inspect processing pipeline components)</li>
</ul>

<h2>🧹 Clean Up</h2>
<p>To stop the containers and free up ports without deleting your collected telemetry volumes, run:</p>
<pre>docker compose down</pre>
<p>To completely remove the stack along with all stored metrics, logs, and traces, run:</p>
<pre>docker compose down -v</pre>

<hr />
<p><em>Built with 💙 as part of the Multi-Tenant Observability with Alloy challenge on <a href="https://nextwork.ai" target="_blank">nextwork.ai</a>.</em></p>
