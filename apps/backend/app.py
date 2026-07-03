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
        "service.name": os.environ.get("OTEL_SERVICE_NAME", "batch-processor"),
        "service.namespace": os.environ.get(
            "OTEL_RESOURCE_ATTRIBUTES", "service.namespace=team-backend"
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

# Create instruments for tracking batch jobs
tracer = trace.get_tracer("batch-processor")
meter = metrics.get_meter("batch-processor")
jobs_processed = meter.create_counter(
    "batch_jobs_processed_total", description="Total batch jobs processed"
)
job_duration = meter.create_histogram(
    "batch_job_duration_seconds", description="Batch job processing duration"
)

logger = logging.getLogger("batch-processor")

# Simulate batch processing in an infinite loop
while True:
    with tracer.start_as_current_span("process_batch") as span:
        batch_size = random.randint(10, 100)
        job_type = random.choice(["data-sync", "report-gen", "cleanup", "notification"])
        duration = random.uniform(0.5, 5.0)
        success = random.random() > 0.1

        span.set_attribute("batch.size", batch_size)
        span.set_attribute("batch.job_type", job_type)
        span.set_attribute("batch.success", success)

        jobs_processed.add(1, {"job_type": job_type, "success": str(success)})
        job_duration.record(duration, {"job_type": job_type})

        logger.info(
            f"Processed batch: type={job_type}, size={batch_size}, duration={duration:.2f}s"
        )
        if not success:
            logger.error(f"Batch job failed: type={job_type}, size={batch_size}")

        time.sleep(random.uniform(2, 5))
