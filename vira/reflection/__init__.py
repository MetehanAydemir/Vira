"""
VIRA Self-Reflection System
---------------------------
Kullanıcı desenleri analiz ederek içgörüler üretir ve 
proaktif aksiyonlar almayı sağlayan otonom yansıtma sistemi.
"""

from .data_gatherer import ReflectionDataGatherer
from .pattern_analyzers import TemporalPatternAnalyzer, BehavioralPatternAnalyzer
from .insight_generator import InsightGenerator
from .goal_generator import EmergentGoalGenerator
from .action_executor import ActionExecutor
from .reflection_nodes import reflection_trigger_node, autonomous_reflection_node
from .reflection_monitor import ReflectionMonitor

__all__ = [
    'ReflectionDataGatherer',
    'TemporalPatternAnalyzer',
    'BehavioralPatternAnalyzer',
    'InsightGenerator',
    'EmergentGoalGenerator',
    'ActionExecutor',
    'reflection_trigger_node',
    'autonomous_reflection_node',
    'ReflectionMonitor'
]