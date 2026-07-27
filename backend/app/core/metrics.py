"""
Prometheus Metrics & Observability Collector for TalentScout Enterprise.
Provides thread-safe Prometheus plaintext metrics rendering for HTTP requests, latency histograms,
evaluation throughput, cache hit ratios, stage-by-stage execution timings, and API error counts.
Tailored for Google Cloud Run container observability and Vercel cross-origin request tracing.
"""
import time
import threading
from typing import Dict, List, Tuple

class MetricsCollector:
    def __init__(self):
        self._lock = threading.Lock()
        self._requests_total: Dict[Tuple[str, str, int], int] = {}
        self._request_duration_sum: float = 0.0
        self._request_duration_count: int = 0
        self._evaluations_total: Dict[str, int] = {}
        self._cache_hits_total: Dict[str, int] = {}
        self._errors_total: Dict[Tuple[str, int], int] = {}
        self._stage_duration_sum: Dict[str, float] = {}
        self._stage_duration_count: Dict[str, int] = {}
        self._start_time = time.time()

    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        with self._lock:
            key = (method, endpoint, status_code)
            self._requests_total[key] = self._requests_total.get(key, 0) + 1
            self._request_duration_sum += duration
            self._request_duration_count += 1
            if status_code >= 400:
                err_key = ("HTTP_ERROR", status_code)
                self._errors_total[err_key] = self._errors_total.get(err_key, 0) + 1

    def record_evaluation(self, tier: str = "Standard"):
        with self._lock:
            self._evaluations_total[tier] = self._evaluations_total.get(tier, 0) + 1

    def record_cache_hit(self, stage: str = "parsing"):
        with self._lock:
            self._cache_hits_total[stage] = self._cache_hits_total.get(stage, 0) + 1

    def record_stage_duration(self, stage: str, duration_ms: float):
        """Records stage-by-stage pipeline execution timing breakdown in milliseconds."""
        with self._lock:
            self._stage_duration_sum[stage] = self._stage_duration_sum.get(stage, 0.0) + (duration_ms / 1000.0)
            self._stage_duration_count[stage] = self._stage_duration_count.get(stage, 0) + 1

    def generate_prometheus_text(self) -> str:
        with self._lock:
            lines = [
                "# HELP talentscout_uptime_seconds Total runtime in seconds.",
                "# TYPE talentscout_uptime_seconds gauge",
                f"talentscout_uptime_seconds {time.time() - self._start_time:.2f}",
                "",
                "# HELP talentscout_http_requests_total Total count of HTTP requests processed.",
                "# TYPE talentscout_http_requests_total counter",
            ]

            for (method, endpoint, status), count in self._requests_total.items():
                lines.append(f'talentscout_http_requests_total{{method="{method}",endpoint="{endpoint}",status="{status}"}} {count}')

            lines.extend([
                "",
                "# HELP talentscout_http_request_duration_seconds_sum Total HTTP request latency sum.",
                "# TYPE talentscout_http_request_duration_seconds_sum counter",
                f"talentscout_http_request_duration_seconds_sum {self._request_duration_sum:.4f}",
                "# HELP talentscout_http_request_duration_seconds_count Total HTTP request count.",
                "# TYPE talentscout_http_request_duration_seconds_count counter",
                f"talentscout_http_request_duration_seconds_count {self._request_duration_count}",
                "",
                "# HELP talentscout_evaluations_total Total candidate evaluations completed.",
                "# TYPE talentscout_evaluations_total counter",
            ])

            for tier, count in self._evaluations_total.items():
                lines.append(f'talentscout_evaluations_total{{tier="{tier}"}} {count}')

            lines.extend([
                "",
                "# HELP talentscout_stage_duration_seconds_sum Pipeline stage duration sum in seconds.",
                "# TYPE talentscout_stage_duration_seconds_sum counter",
            ])

            for stage, sum_val in self._stage_duration_sum.items():
                count_val = self._stage_duration_count.get(stage, 0)
                lines.append(f'talentscout_stage_duration_seconds_sum{{stage="{stage}"}} {sum_val:.4f}')
                lines.append(f'talentscout_stage_duration_seconds_count{{stage="{stage}"}} {count_val}')

            lines.extend([
                "",
                "# HELP talentscout_cache_hits_total Total AI Gateway cache hits.",
                "# TYPE talentscout_cache_hits_total counter",
            ])

            for stage, count in self._cache_hits_total.items():
                lines.append(f'talentscout_cache_hits_total{{stage="{stage}"}} {count}')

            lines.extend([
                "",
                "# HELP talentscout_errors_total Total API error count.",
                "# TYPE talentscout_errors_total counter",
            ])

            for (err_type, status), count in self._errors_total.items():
                lines.append(f'talentscout_errors_total{{type="{err_type}",status="{status}"}} {count}')

            lines.append("")
            return "\n".join(lines)

metrics_collector = MetricsCollector()
