"""
System Monitor for Expeta 2.0

This module monitors the system status and reports metrics.
"""

import time
import threading
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

class SystemMonitor:
    """Monitors system status and reports metrics"""
    
    def __init__(self, event_bus=None):
        """Initialize system monitor
        
        Args:
            event_bus: Optional event bus for publishing system events
        """
        self.event_bus = event_bus
        self.components = {}
        self.metrics = {}
        self.alerts = {}
        self.monitoring_thread = None
        self.monitoring_interval = 60  # seconds
        self.is_monitoring = False
        self.logger = logging.getLogger(__name__)
    
    def register_component(self, component_id: str, component_info: Dict[str, Any]) -> None:
        """Register a component for monitoring
        
        Args:
            component_id: Component ID
            component_info: Component information
        """
        self.components[component_id] = {
            "id": component_id,
            "info": component_info,
            "status": "unknown",
            "last_check": None,
            "health_check": component_info.get("health_check"),
            "metrics": {}
        }
    
    def update_component_status(self, component_id: str, status: str, metrics: Dict[str, Any] = None) -> bool:
        """Update component status
        
        Args:
            component_id: Component ID
            status: New status
            metrics: Optional component metrics
            
        Returns:
            True if component was updated, False otherwise
        """
        if component_id not in self.components:
            return False
        
        self.components[component_id]["status"] = status
        self.components[component_id]["last_check"] = datetime.now().isoformat()
        
        if metrics:
            self.components[component_id]["metrics"].update(metrics)
        
        if self.event_bus:
            self.event_bus.publish("system.component.status_update", {
                "component_id": component_id,
                "status": status,
                "metrics": metrics
            })
        
        return True
    
    def get_component_status(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get component status
        
        Args:
            component_id: Component ID
            
        Returns:
            Component status or None if not found
        """
        return self.components.get(component_id)
    
    def get_all_component_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get all component statuses
        
        Returns:
            Dictionary of component statuses
        """
        return self.components
    
    def register_metric(self, metric_id: str, metric_info: Dict[str, Any]) -> None:
        """Register a metric for monitoring
        
        Args:
            metric_id: Metric ID
            metric_info: Metric information
        """
        self.metrics[metric_id] = {
            "id": metric_id,
            "info": metric_info,
            "collector": metric_info.get("collector"),
            "last_value": None,
            "last_collection": None,
            "history": []
        }
    
    def update_metric(self, metric_id: str, value: Any) -> bool:
        """Update metric value
        
        Args:
            metric_id: Metric ID
            value: New metric value
            
        Returns:
            True if metric was updated, False otherwise
        """
        if metric_id not in self.metrics:
            return False
        
        timestamp = datetime.now().isoformat()
        
        self.metrics[metric_id]["last_value"] = value
        self.metrics[metric_id]["last_collection"] = timestamp
        self.metrics[metric_id]["history"].append({
            "timestamp": timestamp,
            "value": value
        })
        
        max_history = self.metrics[metric_id]["info"].get("max_history", 100)
        if len(self.metrics[metric_id]["history"]) > max_history:
            self.metrics[metric_id]["history"] = self.metrics[metric_id]["history"][-max_history:]
        
        if self.event_bus:
            self.event_bus.publish("system.metric.update", {
                "metric_id": metric_id,
                "value": value,
                "timestamp": timestamp
            })
        
        return True
    
    def get_metric(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """Get metric
        
        Args:
            metric_id: Metric ID
            
        Returns:
            Metric data or None if not found
        """
        return self.metrics.get(metric_id)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all metrics
        
        Returns:
            Dictionary of metrics
        """
        return self.metrics
    
    def register_alert(self, alert_id: str, alert_info: Dict[str, Any]) -> None:
        """Register an alert
        
        Args:
            alert_id: Alert ID
            alert_info: Alert information
        """
        self.alerts[alert_id] = {
            "id": alert_id,
            "info": alert_info,
            "condition": alert_info.get("condition"),
            "action": alert_info.get("action"),
            "status": "inactive",
            "last_triggered": None,
            "trigger_count": 0
        }
    
    def trigger_alert(self, alert_id: str, data: Dict[str, Any] = None) -> bool:
        """Trigger an alert
        
        Args:
            alert_id: Alert ID
            data: Optional alert data
            
        Returns:
            True if alert was triggered, False otherwise
        """
        if alert_id not in self.alerts:
            return False
        
        timestamp = datetime.now().isoformat()
        
        self.alerts[alert_id]["status"] = "active"
        self.alerts[alert_id]["last_triggered"] = timestamp
        self.alerts[alert_id]["trigger_count"] += 1
        
        if self.event_bus:
            self.event_bus.publish("system.alert.triggered", {
                "alert_id": alert_id,
                "timestamp": timestamp,
                "data": data
            })
        
        action = self.alerts[alert_id]["action"]
        if action and callable(action):
            try:
                action(alert_id, data)
            except Exception as e:
                self.logger.error(f"Error executing alert action for {alert_id}: {str(e)}")
        
        return True
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if alert was resolved, False otherwise
        """
        if alert_id not in self.alerts:
            return False
        
        self.alerts[alert_id]["status"] = "inactive"
        
        if self.event_bus:
            self.event_bus.publish("system.alert.resolved", {
                "alert_id": alert_id,
                "timestamp": datetime.now().isoformat()
            })
        
        return True
    
    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get alert
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert data or None if not found
        """
        return self.alerts.get(alert_id)
    
    def get_all_alerts(self) -> Dict[str, Dict[str, Any]]:
        """Get all alerts
        
        Returns:
            Dictionary of alerts
        """
        return self.alerts
    
    def get_active_alerts(self) -> Dict[str, Dict[str, Any]]:
        """Get active alerts
        
        Returns:
            Dictionary of active alerts
        """
        return {alert_id: alert for alert_id, alert in self.alerts.items() if alert["status"] == "active"}
    
    def start_monitoring(self, interval: int = None) -> None:
        """Start monitoring thread
        
        Args:
            interval: Optional monitoring interval in seconds
        """
        if self.is_monitoring:
            return
        
        if interval:
            self.monitoring_interval = interval
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        if self.event_bus:
            self.event_bus.publish("system.monitoring.started", {
                "timestamp": datetime.now().isoformat(),
                "interval": self.monitoring_interval
            })
    
    def stop_monitoring(self) -> None:
        """Stop monitoring thread"""
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            self.monitoring_thread = None
        
        if self.event_bus:
            self.event_bus.publish("system.monitoring.stopped", {
                "timestamp": datetime.now().isoformat()
            })
    
    def _monitoring_loop(self) -> None:
        """Monitoring loop"""
        while self.is_monitoring:
            try:
                self._collect_system_metrics()
                self._check_component_health()
                self._check_alert_conditions()
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
            
            time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self) -> None:
        """Collect system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        self.update_metric("system.cpu.percent", cpu_percent)
        
        memory = psutil.virtual_memory()
        self.update_metric("system.memory.percent", memory.percent)
        self.update_metric("system.memory.available", memory.available)
        
        disk = psutil.disk_usage("/")
        self.update_metric("system.disk.percent", disk.percent)
        self.update_metric("system.disk.free", disk.free)
        
        for metric_id, metric in self.metrics.items():
            if metric_id.startswith("system."):
                continue
            
            collector = metric.get("collector")
            if collector and callable(collector):
                try:
                    value = collector()
                    self.update_metric(metric_id, value)
                except Exception as e:
                    self.logger.error(f"Error collecting metric {metric_id}: {str(e)}")
    
    def _check_component_health(self) -> None:
        """Check component health"""
        for component_id, component in self.components.items():
            health_check = component.get("health_check")
            if health_check and callable(health_check):
                try:
                    status, metrics = health_check()
                    self.update_component_status(component_id, status, metrics)
                except Exception as e:
                    self.logger.error(f"Error checking health for component {component_id}: {str(e)}")
                    self.update_component_status(component_id, "error", {"error": str(e)})
    
    def _check_alert_conditions(self) -> None:
        """Check alert conditions"""
        for alert_id, alert in self.alerts.items():
            condition = alert.get("condition")
            if condition and callable(condition):
                try:
                    should_trigger, data = condition()
                    if should_trigger:
                        self.trigger_alert(alert_id, data)
                    elif alert["status"] == "active":
                        self.resolve_alert(alert_id)
                except Exception as e:
                    self.logger.error(f"Error checking condition for alert {alert_id}: {str(e)}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status
        
        Returns:
            System status
        """
        component_statuses = {component_id: component["status"] for component_id, component in self.components.items()}
        active_alerts = self.get_active_alerts()
        
        cpu_metric = self.get_metric("system.cpu.percent")
        memory_metric = self.get_metric("system.memory.percent")
        disk_metric = self.get_metric("system.disk.percent")
        
        cpu_percent = cpu_metric["last_value"] if cpu_metric else None
        memory_percent = memory_metric["last_value"] if memory_metric else None
        disk_percent = disk_metric["last_value"] if disk_metric else None
        
        if "error" in component_statuses.values():
            overall_status = "error"
        elif "warning" in component_statuses.values():
            overall_status = "warning"
        elif active_alerts:
            overall_status = "warning"
        elif all(status == "healthy" for status in component_statuses.values()):
            overall_status = "healthy"
        else:
            overall_status = "unknown"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": component_statuses,
            "active_alerts": len(active_alerts),
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            }
        }
