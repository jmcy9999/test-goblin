"""
Analyzers package for iOS Test Optimizer.

This package contains specialized analyzers for different aspects of iOS test suites:
- test_inventory_analyzer: Test file and method inventory
- accessibility_analyzer: Accessibility identifier extraction and mapping
- test_plan_analyzer: Test plan configuration analysis
- screen_graph_analyzer: Screen navigation graph analysis (optional)
"""

from .accessibility_analyzer import AccessibilityAnalyzer, analyze_accessibility_ids
from .screen_graph_analyzer import ScreenGraphAnalyzer, analyze_screen_graph
from .test_inventory_analyzer import TestInventoryAnalyzer
from .test_plan_analyzer import TestPlanAnalyzer

__all__ = [
    "AccessibilityAnalyzer",
    "analyze_accessibility_ids",
    "ScreenGraphAnalyzer",
    "analyze_screen_graph",
    "TestInventoryAnalyzer",
    "TestPlanAnalyzer",
]
