# -----------------------------------------------------------------------------
# Predbat Home Battery System - Prometheus Metrics
# Copyright Trefor Southwell 2024 - All Rights Reserved
# This application maybe used for personal use only and not for commercial use
# -----------------------------------------------------------------------------

from prometheus_client import Counter, Gauge, Histogram, Info
import time
from datetime import datetime


class PredBatMetrics:
    def __init__(self, base):
        self.base = base
        self.log = base.log
        
        # Application health metrics
        self.up = Gauge('predbat_up', 'Application is running', ['version'])
        self.errors_total = Counter('predbat_errors_total', 'Total number of errors', ['type'])
        self.last_update_timestamp = Gauge('predbat_last_update_timestamp', 'Timestamp of last update')
        self.plan_valid = Gauge('predbat_plan_valid', 'Whether the current plan is valid')
        self.plan_age_minutes = Gauge('predbat_plan_age_minutes', 'Age of current plan in minutes')
        
        # External API metrics
        self.api_requests_total = Counter('predbat_api_requests_total', 'Total API requests', ['service'])
        self.api_failures_total = Counter('predbat_api_failures_total', 'Total API failures', ['service'])
        self.api_response_time = Histogram('predbat_api_response_time_seconds', 'API response time', ['service'])
        self.api_last_success_timestamp = Gauge('predbat_api_last_success_timestamp', 'Last successful API call timestamp', ['service'])
        
        # Battery and energy management
        self.battery_soc_percent = Gauge('predbat_battery_soc_percent', 'Battery state of charge percentage')
        self.charge_rate_kw = Gauge('predbat_charge_rate_kw', 'Current charge rate in kW')
        self.discharge_rate_kw = Gauge('predbat_discharge_rate_kw', 'Current discharge rate in kW')
        self.inverter_register_writes_total = Counter('predbat_inverter_register_writes_total', 'Total inverter register writes')
        self.plan_execution_failures_total = Counter('predbat_plan_execution_failures_total', 'Total plan execution failures')
        
        # Prediction and forecasting
        self.forecast_accuracy_percent = Gauge('predbat_forecast_accuracy_percent', 'Forecast accuracy percentage', ['type'])
        self.prediction_calculation_duration = Histogram('predbat_prediction_calculation_duration_seconds', 'Time taken to calculate predictions')
        self.prediction_confidence_score = Gauge('predbat_prediction_confidence_score', 'Prediction confidence score', ['type'])
        
        # Web interface metrics
        self.web_requests_total = Counter('predbat_web_requests_total', 'Total web requests', ['endpoint'])
        self.web_response_time = Histogram('predbat_web_response_time_seconds', 'Web response time', ['endpoint'])
        
        # Energy metrics
        self.load_today_kwh = Gauge('predbat_load_today_kwh', 'Load energy today in kWh')
        self.import_today_kwh = Gauge('predbat_import_today_kwh', 'Import energy today in kWh')
        self.export_today_kwh = Gauge('predbat_export_today_kwh', 'Export energy today in kWh')
        self.pv_today_kwh = Gauge('predbat_pv_today_kwh', 'PV energy today in kWh')
        
        # Cost metrics
        self.cost_today = Gauge('predbat_cost_today', 'Cost today in currency units')
        self.savings_total = Gauge('predbat_savings_total', 'Total savings from Predbat')
        
        # Initialize API service tracking
        self.api_services = ['octopus', 'solcast', 'gecloud', 'home_assistant']
        for service in self.api_services:
            self.api_last_success_timestamp.labels(service=service).set_to_current_time()
        
        self.log("Metrics collection initialized")

    def update_app_health(self, version, has_errors, plan_valid, plan_age_minutes):
        """Update application health metrics"""
        self.up.labels(version=version).set(1)
        self.last_update_timestamp.set_to_current_time()
        self.plan_valid.set(1 if plan_valid else 0)
        self.plan_age_minutes.set(plan_age_minutes)
        
        if has_errors:
            self.errors_total.labels(type='general').inc()

    def record_api_request(self, service, success=True, response_time=None):
        """Record API request metrics"""
        self.api_requests_total.labels(service=service).inc()
        
        if success:
            self.api_last_success_timestamp.labels(service=service).set_to_current_time()
        else:
            self.api_failures_total.labels(service=service).inc()
            
        if response_time is not None:
            self.api_response_time.labels(service=service).observe(response_time)

    def record_error(self, error_type):
        """Record an error occurrence"""
        self.errors_total.labels(type=error_type).inc()

    def update_battery_metrics(self, soc_percent=None, charge_rate_kw=None, discharge_rate_kw=None):
        """Update battery-related metrics"""
        if soc_percent is not None:
            self.battery_soc_percent.set(soc_percent)
        if charge_rate_kw is not None:
            self.charge_rate_kw.set(charge_rate_kw)
        if discharge_rate_kw is not None:
            self.discharge_rate_kw.set(discharge_rate_kw)

    def record_inverter_write(self):
        """Record an inverter register write"""
        self.inverter_register_writes_total.inc()

    def record_plan_execution_failure(self):
        """Record a plan execution failure"""
        self.plan_execution_failures_total.inc()

    def update_energy_metrics(self, load_kwh=None, import_kwh=None, export_kwh=None, pv_kwh=None):
        """Update energy metrics"""
        if load_kwh is not None:
            self.load_today_kwh.set(load_kwh)
        if import_kwh is not None:
            self.import_today_kwh.set(import_kwh)
        if export_kwh is not None:
            self.export_today_kwh.set(export_kwh)
        if pv_kwh is not None:
            self.pv_today_kwh.set(pv_kwh)

    def update_cost_metrics(self, cost_today=None, savings_total=None):
        """Update cost and savings metrics"""
        if cost_today is not None:
            self.cost_today.set(cost_today)
        if savings_total is not None:
            self.savings_total.set(savings_total)

    def update_forecast_accuracy(self, forecast_type, accuracy_percent):
        """Update forecast accuracy metrics"""
        self.forecast_accuracy_percent.labels(type=forecast_type).set(accuracy_percent)

    def record_prediction_calculation_time(self, duration_seconds):
        """Record time taken for prediction calculation"""
        self.prediction_calculation_duration.observe(duration_seconds)

    def update_prediction_confidence(self, prediction_type, confidence_score):
        """Update prediction confidence score"""
        self.prediction_confidence_score.labels(type=prediction_type).set(confidence_score)

    def record_web_request(self, endpoint, response_time=None):
        """Record web request metrics"""
        self.web_requests_total.labels(endpoint=endpoint).inc()
        
        if response_time is not None:
            self.web_response_time.labels(endpoint=endpoint).observe(response_time)

    def collect_current_metrics(self):
        """Collect current state from base application and update metrics"""
        try:
            # Get version from base
            from predbat import THIS_VERSION
            version = THIS_VERSION
            
            # Update app health
            plan_age_minutes = 0
            if hasattr(self.base, 'plan_last_updated') and self.base.plan_last_updated:
                plan_age = self.base.now_utc - self.base.plan_last_updated
                plan_age_minutes = plan_age.total_seconds() / 60.0
            
            self.update_app_health(
                version=version,
                has_errors=getattr(self.base, 'had_errors', False),
                plan_valid=getattr(self.base, 'plan_valid', False),
                plan_age_minutes=plan_age_minutes
            )
            
            # Update battery metrics if available
            if hasattr(self.base, 'soc_kw') and self.base.soc_kw:
                soc_percent = (self.base.soc_kw / self.base.soc_max) * 100 if self.base.soc_max > 0 else 0
                self.update_battery_metrics(soc_percent=soc_percent)
            
            # Update energy metrics if available
            if hasattr(self.base, 'load_minutes_today'):
                load_kwh = sum(self.base.load_minutes_today) / 60.0 if self.base.load_minutes_today else 0
                self.update_energy_metrics(load_kwh=load_kwh)
            
            # Update cost metrics if available
            if hasattr(self.base, 'cost_today_sofar'):
                self.update_cost_metrics(cost_today=self.base.cost_today_sofar)
                
        except Exception as e:
            self.log(f"Error collecting metrics: {e}")
            self.record_error('metrics_collection')