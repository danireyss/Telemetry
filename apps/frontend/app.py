import time
import logging
import random
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
import os

# Create an OpenTelemetry resource identifying this service and its tenant
resource = Resource.create(
    {
        "service.name": os.environ.get("OTEL_SERVICE_NAME", "frontend-api"),
        "service.namespace": os.environ.get(
            "OTEL_RESOURCE_ATTRIBUTES", "service.namespace=team-frontend"
        ).split("=")[-1],
    }
)

# OTLP endpoint where Alloy listens for telemetry
endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

# Set up trace provider with OTLP gRPC exporter
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
)
trace.set_tracer_provider(trace_provider)

# Set up metric provider with periodic export every 5 seconds
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=endpoint, insecure=True), export_interval_millis=5000
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Set up log provider with OTLP gRPC exporter
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint, insecure=True))
)
set_logger_provider(logger_provider)
handler = LoggingHandler(logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

# Create instruments for tracking HTTP requests
tracer = trace.get_tracer("frontend-api")
meter = metrics.get_meter("frontend-api")
request_counter = meter.create_counter(
    "http_requests_total", description="Total HTTP requests"
)
request_duration = meter.create_histogram(
    "http_request_duration_seconds", description="HTTP request duration"
)

logger = logging.getLogger("frontend-api")

# Simulate HTTP traffic in an infinite loop
while True:
    with tracer.start_as_current_span("handle_request") as span:
        method = random.choice(["GET", "POST", "PUT"])
        path = random.choice(["/api/users", "/api/products", "/api/orders"])
        duration = random.uniform(0.01, 0.5)
        status = random.choice([200, 200, 200, 201, 400, 500])

        span.set_attribute("http.method", method)
        span.set_attribute("http.url", path)
        span.set_attribute("http.status_code", status)

        request_counter.add(1, {"method": method, "path": path, "status": str(status)})
        request_duration.record(duration, {"method": method, "path": path})

        logger.info(f"{method} {path} - {status} ({duration:.3f}s)")
        if status == 500:
            logger.error(f"Internal server error on {method} {path}")

        time.sleep(random.uniform(1, 3))
