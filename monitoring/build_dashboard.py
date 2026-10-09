"""Genera monitoring/grafana/dashboards/notifications-api.json (dashboard provisionado)."""
import json
from pathlib import Path

PROM = {"type": "prometheus", "uid": "prometheus"}
LOKI = {"type": "loki", "uid": "loki"}
TEMPO = {"type": "tempo", "uid": "tempo"}
SEL = 'handler!="/metrics"'
panels, pid = [], 0


def add(kind, title, x, y, w, h, targets, ds=PROM, unit=None, options=None, extra=None):
    global pid
    pid += 1
    p = {
        "id": pid, "type": kind, "title": title, "datasource": ds,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [dict(t, datasource=ds, refId=chr(65 + i)) for i, t in enumerate(targets)],
        "fieldConfig": {"defaults": {"unit": unit} if unit else {}, "overrides": []},
        "options": options or {},
    }
    if extra:
        p.update(extra)
    panels.append(p)


def row(title, y):
    global pid
    pid += 1
    panels.append({"id": pid, "type": "row", "title": title, "collapsed": False,
                   "gridPos": {"x": 0, "y": y, "w": 24, "h": 1}, "panels": []})


def q(expr, legend=""):
    return {"expr": expr, "legendFormat": legend}


# --- Resumen ---
row("Resumen", 0)
stat = {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "value"}
add("stat", "Requests/s", 0, 1, 6, 4, [q(f'sum(rate(http_requests_total{{{SEL}}}[1m]))')], unit="reqps", options=stat)
add("stat", "Errores 5xx (%)", 6, 1, 6, 4,
    [q(f'100 * sum(rate(http_requests_total{{{SEL},status="5xx"}}[5m])) / sum(rate(http_requests_total{{{SEL}}}[5m]))')],
    unit="percent", options=stat,
    extra={"fieldConfig": {"defaults": {"unit": "percent", "thresholds": {"mode": "absolute", "steps": [
        {"color": "green", "value": None}, {"color": "orange", "value": 1}, {"color": "red", "value": 5}]},
        "color": {"mode": "thresholds"}}, "overrides": []}})
add("stat", "Latencia p95", 12, 1, 6, 4,
    [q(f'histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{{{SEL}}}[5m])))')],
    unit="s", options=stat)
add("stat", "Requests totales", 18, 1, 6, 4, [q(f'sum(http_requests_total{{{SEL}}})')], unit="short", options=stat)

# --- Tráfico ---
row("Tráfico y errores", 5)
ts = {"legend": {"displayMode": "table", "placement": "bottom", "calcs": ["mean", "max"]}}
add("timeseries", "Requests/s por endpoint", 0, 6, 12, 8,
    [q(f'sum by (method, handler) (rate(http_requests_total{{{SEL}}}[1m]))', "{{method}} {{handler}}")], unit="reqps", options=ts)
add("timeseries", "Requests/s por código de estado", 12, 6, 12, 8,
    [q(f'sum by (status) (rate(http_requests_total{{{SEL}}}[1m]))', "{{status}}")], unit="reqps", options=ts)

# --- Latencia ---
row("Latencia", 14)
hist = 'http_request_duration_seconds_bucket'
add("timeseries", "Latencia p50 / p95 / p99", 0, 15, 12, 8, [
    q(f'histogram_quantile(0.50, sum by (le) (rate({hist}{{{SEL}}}[5m])))', "p50"),
    q(f'histogram_quantile(0.95, sum by (le) (rate({hist}{{{SEL}}}[5m])))', "p95"),
    q(f'histogram_quantile(0.99, sum by (le) (rate({hist}{{{SEL}}}[5m])))', "p99")], unit="s", options=ts)
add("timeseries", "Latencia p95 por endpoint", 12, 15, 12, 8,
    [q(f'histogram_quantile(0.95, sum by (le, handler) (rate({hist}{{{SEL}}}[5m])))', "{{handler}}")], unit="s", options=ts)

# --- Recursos ---
row("Recursos del proceso", 23)
add("timeseries", "CPU (cores)", 0, 24, 8, 7, [q('rate(process_cpu_seconds_total[1m])', "cpu")], unit="short")
add("timeseries", "Memoria residente", 8, 24, 8, 7, [q('process_resident_memory_bytes', "rss")], unit="bytes")
add("timeseries", "Archivos abiertos", 16, 24, 8, 7, [q('process_open_fds', "fds")], unit="short")

# --- Logs ---
row("Logs (Loki)", 31)
add("timeseries", "Volumen de logs por nivel", 0, 32, 24, 5,
    [{"expr": 'sum by (level) (count_over_time({container="backend_app"} | regexp `(?P<level>INFO|WARNING|ERROR|CRITICAL)` [1m]))',
      "legendFormat": "{{level}}"}], ds=LOKI, unit="short", options=ts)
add("logs", "Logs del backend", 0, 37, 24, 10,
    [{"expr": '{container="backend_app"} |~ "(?i)$search"'}], ds=LOKI,
    options={"showTime": True, "wrapLogMessage": True, "enableLogDetails": True, "sortOrder": "Descending"})
add("logs", "Solo errores (backend)", 0, 47, 24, 8,
    [{"expr": '{container="backend_app"} |~ "ERROR|CRITICAL|Traceback"'}], ds=LOKI,
    options={"showTime": True, "wrapLogMessage": True, "enableLogDetails": True})

# --- Trazas ---
row("Trazas (Tempo)", 55)
add("table", "Trazas recientes", 0, 56, 24, 10,
    [{"queryType": "traceqlSearch", "limit": 20, "tableType": "traces",
      "filters": [{"id": "service-name", "tag": "service.name", "operator": "=", "scope": "resource",
                   "value": ["notifications-api"], "valueType": "string"}]}], ds=TEMPO)
add("table", "Trazas lentas (> 500ms)", 0, 66, 24, 8,
    [{"queryType": "traceql", "query": '{ resource.service.name = "notifications-api" && duration > 500ms }',
      "limit": 20, "tableType": "traces"}], ds=TEMPO)

dashboard = {
    "uid": "notifications-api", "title": "Notifications API - Observabilidad",
    "tags": ["fastapi", "observability"], "timezone": "browser", "schemaVersion": 39,
    "version": 1, "refresh": "10s", "time": {"from": "now-30m", "to": "now"},
    "templating": {"list": [{"name": "search", "label": "Buscar en logs", "type": "textbox",
                             "query": "", "current": {"value": "", "text": ""}}]},
    "panels": panels,
}
out = Path(__file__).parent / "grafana" / "dashboards" / "notifications-api.json"
out.write_text(json.dumps(dashboard, indent=2, ensure_ascii=False))
print(out)
