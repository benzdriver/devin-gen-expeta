"""
Unit tests for System Monitor
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestrator.system_monitor import SystemMonitor

class TestSystemMonitor(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.event_bus = MagicMock()
        self.system_monitor = SystemMonitor(event_bus=self.event_bus)
    
    def test_register_component(self):
        """Test registering a component for monitoring"""
        component_info = {
            "name": "Test Component",
            "description": "A test component",
            "health_check": lambda: ("healthy", {"metric": "value"})
        }
        
        self.system_monitor.register_component("test-component", component_info)
        
        self.assertIn("test-component", self.system_monitor.components)
        
        component = self.system_monitor.get_component_status("test-component")
        self.assertEqual(component["id"], "test-component")
        self.assertEqual(component["info"], component_info)
        self.assertEqual(component["status"], "unknown")
    
    def test_update_component_status(self):
        """Test updating component status"""
        self.system_monitor.register_component("test-component", {"name": "Test Component"})
        
        metrics = {"cpu": 10, "memory": 20}
        result = self.system_monitor.update_component_status("test-component", "healthy", metrics)
        
        self.assertTrue(result)
        
        component = self.system_monitor.get_component_status("test-component")
        self.assertEqual(component["status"], "healthy")
        self.assertEqual(component["metrics"]["cpu"], 10)
        self.assertEqual(component["metrics"]["memory"], 20)
        
        self.event_bus.publish.assert_called_once_with("system.component.status_update", {
            "component_id": "test-component",
            "status": "healthy",
            "metrics": metrics
        })
        
        result = self.system_monitor.update_component_status("non-existent", "healthy")
        self.assertFalse(result)
    
    def test_get_component_status(self):
        """Test getting component status"""
        self.system_monitor.register_component("test-component", {"name": "Test Component"})
        
        self.system_monitor.update_component_status("test-component", "healthy")
        
        component = self.system_monitor.get_component_status("test-component")
        
        self.assertEqual(component["id"], "test-component")
        self.assertEqual(component["status"], "healthy")
        
        non_existent_component = self.system_monitor.get_component_status("non-existent")
        self.assertIsNone(non_existent_component)
    
    def test_get_all_component_statuses(self):
        """Test getting all component statuses"""
        self.system_monitor.register_component("component1", {"name": "Component 1"})
        self.system_monitor.register_component("component2", {"name": "Component 2"})
        
        self.system_monitor.update_component_status("component1", "healthy")
        self.system_monitor.update_component_status("component2", "warning")
        
        components = self.system_monitor.get_all_component_statuses()
        
        self.assertEqual(len(components), 2)
        self.assertEqual(components["component1"]["status"], "healthy")
        self.assertEqual(components["component2"]["status"], "warning")
    
    def test_register_metric(self):
        """Test registering a metric for monitoring"""
        metric_info = {
            "name": "Test Metric",
            "description": "A test metric",
            "collector": lambda: 42
        }
        
        self.system_monitor.register_metric("test-metric", metric_info)
        
        self.assertIn("test-metric", self.system_monitor.metrics)
        
        metric = self.system_monitor.get_metric("test-metric")
        self.assertEqual(metric["id"], "test-metric")
        self.assertEqual(metric["info"], metric_info)
        self.assertIsNone(metric["last_value"])
    
    def test_update_metric(self):
        """Test updating metric value"""
        self.system_monitor.register_metric("test-metric", {"name": "Test Metric"})
        
        result = self.system_monitor.update_metric("test-metric", 42)
        
        self.assertTrue(result)
        
        metric = self.system_monitor.get_metric("test-metric")
        self.assertEqual(metric["last_value"], 42)
        self.assertEqual(len(metric["history"]), 1)
        self.assertEqual(metric["history"][0]["value"], 42)
        
        self.event_bus.publish.assert_called_once()
        self.assertEqual(self.event_bus.publish.call_args[0][0], "system.metric.update")
        self.assertEqual(self.event_bus.publish.call_args[0][1]["metric_id"], "test-metric")
        self.assertEqual(self.event_bus.publish.call_args[0][1]["value"], 42)
        
        result = self.system_monitor.update_metric("non-existent", 42)
        self.assertFalse(result)
    
    def test_get_metric(self):
        """Test getting metric"""
        self.system_monitor.register_metric("test-metric", {"name": "Test Metric"})
        
        self.system_monitor.update_metric("test-metric", 42)
        
        metric = self.system_monitor.get_metric("test-metric")
        
        self.assertEqual(metric["id"], "test-metric")
        self.assertEqual(metric["last_value"], 42)
        
        non_existent_metric = self.system_monitor.get_metric("non-existent")
        self.assertIsNone(non_existent_metric)
    
    def test_get_all_metrics(self):
        """Test getting all metrics"""
        self.system_monitor.register_metric("metric1", {"name": "Metric 1"})
        self.system_monitor.register_metric("metric2", {"name": "Metric 2"})
        
        self.system_monitor.update_metric("metric1", 10)
        self.system_monitor.update_metric("metric2", 20)
        
        metrics = self.system_monitor.get_all_metrics()
        
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics["metric1"]["last_value"], 10)
        self.assertEqual(metrics["metric2"]["last_value"], 20)
    
    def test_register_alert(self):
        """Test registering an alert"""
        alert_info = {
            "name": "Test Alert",
            "description": "A test alert",
            "condition": lambda: (True, {"reason": "test"})
        }
        
        self.system_monitor.register_alert("test-alert", alert_info)
        
        self.assertIn("test-alert", self.system_monitor.alerts)
        
        alert = self.system_monitor.get_alert("test-alert")
        self.assertEqual(alert["id"], "test-alert")
        self.assertEqual(alert["info"], alert_info)
        self.assertEqual(alert["status"], "inactive")
    
    def test_trigger_alert(self):
        """Test triggering an alert"""
        self.system_monitor.register_alert("test-alert", {"name": "Test Alert"})
        
        data = {"reason": "test"}
        result = self.system_monitor.trigger_alert("test-alert", data)
        
        self.assertTrue(result)
        
        alert = self.system_monitor.get_alert("test-alert")
        self.assertEqual(alert["status"], "active")
        self.assertEqual(alert["trigger_count"], 1)
        
        self.event_bus.publish.assert_called_once()
        self.assertEqual(self.event_bus.publish.call_args[0][0], "system.alert.triggered")
        self.assertEqual(self.event_bus.publish.call_args[0][1]["alert_id"], "test-alert")
        self.assertEqual(self.event_bus.publish.call_args[0][1]["data"], data)
        
        result = self.system_monitor.trigger_alert("non-existent")
        self.assertFalse(result)
    
    def test_resolve_alert(self):
        """Test resolving an alert"""
        self.system_monitor.register_alert("test-alert", {"name": "Test Alert"})
        
        self.system_monitor.trigger_alert("test-alert")
        
        self.event_bus.reset_mock()
        
        result = self.system_monitor.resolve_alert("test-alert")
        
        self.assertTrue(result)
        
        alert = self.system_monitor.get_alert("test-alert")
        self.assertEqual(alert["status"], "inactive")
        
        self.event_bus.publish.assert_called_once()
        self.assertEqual(self.event_bus.publish.call_args[0][0], "system.alert.resolved")
        self.assertEqual(self.event_bus.publish.call_args[0][1]["alert_id"], "test-alert")
        
        result = self.system_monitor.resolve_alert("non-existent")
        self.assertFalse(result)
    
    def test_get_active_alerts(self):
        """Test getting active alerts"""
        self.system_monitor.register_alert("alert1", {"name": "Alert 1"})
        self.system_monitor.register_alert("alert2", {"name": "Alert 2"})
        self.system_monitor.register_alert("alert3", {"name": "Alert 3"})
        
        self.system_monitor.trigger_alert("alert1")
        self.system_monitor.trigger_alert("alert3")
        
        active_alerts = self.system_monitor.get_active_alerts()
        
        self.assertEqual(len(active_alerts), 2)
        self.assertIn("alert1", active_alerts)
        self.assertIn("alert3", active_alerts)
        self.assertNotIn("alert2", active_alerts)
    
    @patch('orchestrator.system_monitor.threading.Thread')
    def test_start_monitoring(self, mock_thread):
        """Test starting monitoring thread"""
        self.system_monitor.start_monitoring(interval=30)
        
        self.assertTrue(self.system_monitor.is_monitoring)
        self.assertEqual(self.system_monitor.monitoring_interval, 30)
        
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
        
        self.event_bus.publish.assert_called_once()
        self.assertEqual(self.event_bus.publish.call_args[0][0], "system.monitoring.started")
    
    @patch('orchestrator.system_monitor.threading.Thread')
    def test_stop_monitoring(self, mock_thread):
        """Test stopping monitoring thread"""
        self.system_monitor.start_monitoring()
        
        self.event_bus.reset_mock()
        
        self.system_monitor.stop_monitoring()
        
        self.assertFalse(self.system_monitor.is_monitoring)
        
        self.system_monitor.monitoring_thread.join.assert_called_once()
        
        self.event_bus.publish.assert_called_once()
        self.assertEqual(self.event_bus.publish.call_args[0][0], "system.monitoring.stopped")
    
    @patch('orchestrator.system_monitor.psutil.cpu_percent')
    @patch('orchestrator.system_monitor.psutil.virtual_memory')
    @patch('orchestrator.system_monitor.psutil.disk_usage')
    def test_collect_system_metrics(self, mock_disk_usage, mock_virtual_memory, mock_cpu_percent):
        """Test collecting system metrics"""
        mock_cpu_percent.return_value = 50
        
        mock_memory = MagicMock()
        mock_memory.percent = 60
        mock_memory.available = 1024
        mock_virtual_memory.return_value = mock_memory
        
        mock_disk = MagicMock()
        mock_disk.percent = 70
        mock_disk.free = 2048
        mock_disk_usage.return_value = mock_disk
        
        self.system_monitor.register_metric("system.cpu.percent", {"name": "CPU Percent"})
        self.system_monitor.register_metric("system.memory.percent", {"name": "Memory Percent"})
        self.system_monitor.register_metric("system.memory.available", {"name": "Memory Available"})
        self.system_monitor.register_metric("system.disk.percent", {"name": "Disk Percent"})
        self.system_monitor.register_metric("system.disk.free", {"name": "Disk Free"})
        
        self.system_monitor._collect_system_metrics()
        
        self.assertEqual(self.system_monitor.get_metric("system.cpu.percent")["last_value"], 50)
        self.assertEqual(self.system_monitor.get_metric("system.memory.percent")["last_value"], 60)
        self.assertEqual(self.system_monitor.get_metric("system.memory.available")["last_value"], 1024)
        self.assertEqual(self.system_monitor.get_metric("system.disk.percent")["last_value"], 70)
        self.assertEqual(self.system_monitor.get_metric("system.disk.free")["last_value"], 2048)
    
    def test_check_component_health(self):
        """Test checking component health"""
        health_check = MagicMock(return_value=("healthy", {"metric": "value"}))
        self.system_monitor.register_component("test-component", {
            "name": "Test Component",
            "health_check": health_check
        })
        
        self.system_monitor._check_component_health()
        
        health_check.assert_called_once()
        
        component = self.system_monitor.get_component_status("test-component")
        self.assertEqual(component["status"], "healthy")
        self.assertEqual(component["metrics"]["metric"], "value")
    
    def test_check_alert_conditions(self):
        """Test checking alert conditions"""
        condition = MagicMock(return_value=(True, {"reason": "test"}))
        self.system_monitor.register_alert("test-alert", {
            "name": "Test Alert",
            "condition": condition
        })
        
        self.system_monitor._check_alert_conditions()
        
        condition.assert_called_once()
        
        alert = self.system_monitor.get_alert("test-alert")
        self.assertEqual(alert["status"], "active")
    
    def test_get_system_status(self):
        """Test getting overall system status"""
        self.system_monitor.register_component("component1", {"name": "Component 1"})
        self.system_monitor.register_component("component2", {"name": "Component 2"})
        self.system_monitor.register_component("component3", {"name": "Component 3"})
        
        self.system_monitor.update_component_status("component1", "healthy")
        self.system_monitor.update_component_status("component2", "warning")
        self.system_monitor.update_component_status("component3", "healthy")
        
        self.system_monitor.register_metric("system.cpu.percent", {"name": "CPU Percent"})
        self.system_monitor.register_metric("system.memory.percent", {"name": "Memory Percent"})
        self.system_monitor.register_metric("system.disk.percent", {"name": "Disk Percent"})
        
        self.system_monitor.update_metric("system.cpu.percent", 50)
        self.system_monitor.update_metric("system.memory.percent", 60)
        self.system_monitor.update_metric("system.disk.percent", 70)
        
        status = self.system_monitor.get_system_status()
        
        self.assertEqual(status["status"], "warning")
        self.assertEqual(status["components"]["component1"], "healthy")
        self.assertEqual(status["components"]["component2"], "warning")
        self.assertEqual(status["components"]["component3"], "healthy")
        self.assertEqual(status["metrics"]["cpu_percent"], 50)
        self.assertEqual(status["metrics"]["memory_percent"], 60)
        self.assertEqual(status["metrics"]["disk_percent"], 70)

if __name__ == "__main__":
    unittest.main()
