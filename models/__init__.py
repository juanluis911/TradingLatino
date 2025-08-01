# models/__init__.py
"""
Modelos de datos para Jaime Merino Trading Bot
Metodología Trading Latino - Análisis Técnico Avanzado
"""

# Modelos originales (mantener compatibilidad)
from .trading_analysis import TradingAnalysis, MarketData, TechnicalIndicators, create_analysis

# Modelos mejorados para metodología Jaime Merino
from .enhanced_trading_model import (
    MerinoTechnicalIndicators,
    MerinoMarketContext,
    MerinoSignal,
    MerinoRiskManagement,
    MerinoTradingLevels,
    MerinoTradingAnalysis,
    create_merino_analysis
)

__all__ = [
    # Modelos originales
    'TradingAnalysis',
    'MarketData',
    'TechnicalIndicators',
    'create_analysis',
    
    # Modelos Merino
    'MerinoTechnicalIndicators',
    'MerinoMarketContext',
    'MerinoSignal',
    'MerinoRiskManagement',
    'MerinoTradingLevels',
    'MerinoTradingAnalysis',
    'create_merino_analysis'
]

__version__ = '2.0.0'
__methodology__ = 'JAIME_MERINO'
__description__ = 'Modelos de datos para análisis técnico según metodología Jaime Merino'

# services/__init__.py
"""
Servicios de análisis para Jaime Merino Trading Bot
Metodología Trading Latino - Análisis Técnico Avanzado
"""

# Servicios originales (mantener compatibilidad)
from .binance_service import BinanceService, binance_service
from .analysis_service import AnalysisService, analysis_service
from .indicators import TechnicalIndicatorsCalculator, SignalGenerator, indicators_calculator, signal_generator

# Servicios mejorados para metodología Jaime Merino
from .enhanced_indicators import (
    JaimeMerinoIndicators,
    JaimeMerinoSignalGenerator,
    jaime_merino_indicators,
    jaime_merino_signal_generator
)
from .enhanced_analysis_service import EnhancedAnalysisService, enhanced_analysis_service

__all__ = [
    # Servicios originales
    'BinanceService',
    'binance_service',
    'AnalysisService',
    'analysis_service',
    'TechnicalIndicatorsCalculator',
    'SignalGenerator',
    'indicators_calculator',
    'signal_generator',
    
    # Servicios Merino
    'JaimeMerinoIndicators',
    'JaimeMerinoSignalGenerator',
    'jaime_merino_indicators',
    'jaime_merino_signal_generator',
    'EnhancedAnalysisService',
    'enhanced_analysis_service'
]

__version__ = '2.0.0'
__methodology__ = 'JAIME_MERINO'
__description__ = 'Servicios de análisis técnico según metodología Jaime Merino'

# websocket/__init__.py
"""
Módulo WebSocket para Jaime Merino Trading Bot
Comunicación en tiempo real para metodología Trading Latino
"""

# Handlers originales (mantener compatibilidad)
from .socket_handlers import SocketHandlers

# Handlers mejorados para metodología Jaime Merino
from .enhanced_socket_handlers import EnhancedSocketHandlers

__all__ = [
    'SocketHandlers',           # Original
    'EnhancedSocketHandlers'    # Mejorado para Merino
]

__version__ = '2.0.0'
__methodology__ = 'JAIME_MERINO'
__description__ = 'Comunicación WebSocket en tiempo real para metodología Jaime Merino'

# utils/__init__.py
"""
Utilidades para Jaime Merino Trading Bot
Metodología Trading Latino - Análisis Técnico Avanzado
"""

# Utilidades existentes
from .logger import setup_logger, app_logger, analysis_logger, websocket_logger, binance_logger
from .json_utils import make_json_serializable, safe_json_dumps, debug_json_serialization, clean_analysis_dict
from .validators import validate_symbol, validate_timeframe, validate_price

__all__ = [
    # Logging
    'setup_logger',
    'app_logger',
    'analysis_logger',
    'websocket_logger',
    'binance_logger',
    
    # JSON utilities
    'make_json_serializable',
    'safe_json_dumps',
    'debug_json_serialization',
    'clean_analysis_dict',
    
    # Validators
    'validate_symbol',
    'validate_timeframe',
    'validate_price'
]

__version__ = '2.0.0'
__methodology__ = 'JAIME_MERINO'
__description__ = 'Utilidades para análisis técnico según metodología Jaime Merino'

# tests/__init__.py
"""
Tests para Jaime Merino Trading Bot
Metodología Trading Latino - Análisis Técnico Avanzado
"""

__version__ = '2.0.0'
__methodology__ = 'JAIME_MERINO'
__description__ = 'Suite de tests para validar metodología Jaime Merino'

# Configuración de tests
import os
import sys

# Agregar el directorio raíz al path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Configuración de logging para tests
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler()]
)

# Importar módulos de test principales
try:
    from .test_analysis import *
    from .test_websocket import *
    from .test_enhanced_indicators import *
    from .test_backtesting import *
except ImportError:
    # Los archivos de test específicos se crearán según necesidad
    pass

__all__ = [
    'test_analysis',
    'test_websocket', 
    'test_enhanced_indicators',
    'test_backtesting'
]