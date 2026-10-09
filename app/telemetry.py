import logging
import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

LOG_FORMAT = (
    "%(asctime)s %(levelname)s [%(name)s] "
    "[trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] - %(message)s"
)


def setup_telemetry(app: FastAPI, db_engine) -> None:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return  # sin endpoint (tests, ejecución local) no se activa el tracing

    provider = TracerProvider(
        resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "notifications-api")})
    )
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True)))
    trace.set_tracer_provider(provider)

    LoggingInstrumentor().instrument(set_logging_format=True, logging_format=LOG_FORMAT)
    logging.getLogger().setLevel(logging.INFO)
    FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics")
    SQLAlchemyInstrumentor().instrument(engine=db_engine.sync_engine)
