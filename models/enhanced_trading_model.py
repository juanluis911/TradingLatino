"""
Modelos de datos mejorados para análisis según metodología Jaime Merino
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, List, Any
import json

@dataclass
class MerinoTechnicalIndicators:
    """
    Indicadores técnicos específicos de la metodología Jaime Merino
    """
    # EMAs principales
    ema_11_4h: float
    ema_55_4h: float
    ema_11_1h: float
    ema_55_1h: float
    ema_11_daily: float
    ema_55_daily: float
    
    # ADX modificado (punto 23 como 0)
    adx: float
    adx_modified: float
    adx_strength: str  # DEBIL, MODERADA, FUERTE, MUY_FUERTE
    adx_slope: float
    adx_trending: bool
    adx_strengthening: bool
    
    # Squeeze Momentum (LazyBear)
    squeeze_momentum: float
    squeeze_on: bool  # True = consolidación, False = movimiento
    squeeze_just_released: bool
    
    # Volume Profile
    vpoc: float  # Volume Point of Control
    vpoc_distance_pct: float
    high_volume_levels: List[Dict]
    
    # Indicadores adicionales
    rsi_4h: float
    macd_4h: Optional[float] = None
    bollinger_squeeze: bool = False

@dataclass
class MerinoMarketContext:
    """
    Contexto de mercado multi-temporal
    """
    # Tendencia macro (diario/semanal)
    macro_trend: str  # BULL_MARKET, BEAR_MARKET, SIDEWAYS
    weekly_bias: str  # BULLISH, BEARISH, NEUTRAL
    daily_bias: str
    
    # Niveles críticos
    resistance_20d: float
    support_20d: float
    resistance_weekly: Optional[float] = None
    support_weekly: Optional[float] = None
    
    # Volatilidad y momentum
    volatility_20d: float
    volume_avg_20d: float
    price_vs_resistance_pct: float
    price_vs_support_pct: float

@dataclass
class MerinoSignal:
    """
    Señal de trading según metodología Jaime Merino
    """
    signal: str  # LONG, SHORT, WAIT, WAIT_SQUEEZE, NO_SIGNAL
    signal_strength: int  # 0-100
    bias_4h: str  # BULLISH, BEARISH, NEUTRAL
    confluence_score: int  # 0-4
    
    # Razones específicas
    reasons: List[str]
    invalidation_conditions: List[str]
    
    # Timing
    optimal_timeframe: str  # 4h, 1h, daily
    entry_timing: str  # IMMEDIATE, ON_CONFIRMATION, WAIT_BETTER_SETUP

@dataclass
class MerinoRiskManagement:
    """
    Gestión de riesgo según filosofía 40-30-20-10 de Merino
    """
    # Asignación de capital
    btc_long_term_pct: float = 40.0
    weekly_charts_pct: float = 30.0
    daily_trading_pct: float = 20.0
    futures_pct: float = 10.0
    
    # Riesgo por operación
    position_size_pct: float  # % del capital total
    max_risk_per_trade_pct: float = 1.0
    risk_reward_ratio: float = 2.5
    
    # Límites de pérdida
    max_daily_loss_pct: float = 6.0
    max_weekly_loss_pct: float = 8.0
    max_monthly_loss_pct: float = 10.0
    
    # Apalancamiento
    max_leverage: float = 3.0
    recommended_leverage: float = 1.0

@dataclass
class MerinoTradingLevels:
    """
    Niveles de trading específicos
    """
    entry_price: float
    entry_range_low: float
    entry_range_high: float
    
    # Objetivos
    target_1: float
    target_1_pct: float = 2.0
    target_2: float
    target_2_pct: float = 5.0
    
    # Stop loss
    stop_loss: float
    stop_loss_pct: float = 2.0
    technical_stop: float  # Basado en EMA 11
    
    # Invalidación
    invalidation_level: float
    invalidation_reason: str

@dataclass
class MerinoTradingAnalysis:
    """
    Análisis completo según metodología Jaime Merino
    """
    # Información básica
    symbol: str
    timestamp: datetime
    current_price: float
    methodology: str = "JAIME_MERINO"
    
    # Componentes del análisis
    indicators: MerinoTechnicalIndicators
    market_context: MerinoMarketContext
    signal: MerinoSignal
    risk_management: MerinoRiskManagement
    trading_levels: Optional[MerinoTradingLevels] = None
    
    # Textos generados
    analysis_text: str
    recommendation: str
    
    # Metadatos
    confidence_level: str  # LOW, MEDIUM, HIGH
    suggested_review_hours: int = 4
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        result = asdict(self)
        # Convertir datetime a string
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    def to_json(self) -> str:
        """Convierte a JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumen ejecutivo"""
        return {
            'symbol': self.symbol,
            'signal': self.signal.signal,
            'strength': self.signal.signal_strength,
            'bias': self.signal.bias_4h,
            'confluences': self.signal.confluence_score,
            'confidence': self.confidence_level,
            'position_size': self.risk_management.position_size_pct,
            'risk_reward': self.risk_management.risk_reward_ratio,
            'entry': self.trading_levels.entry_price if self.trading_levels else self.current_price,
            'stop': self.trading_levels.stop_loss if self.trading_levels else None,
            'target_1': self.trading_levels.target_1 if self.trading_levels else None
        }

def create_merino_analysis(
    symbol: str,
    current_price: float,
    df_4h, df_1h, df_daily,
    merino_signal_data: Dict
) -> MerinoTradingAnalysis:
    """
    Factory function para crear análisis completo de Merino
    
    Args:
        symbol: Símbolo del activo
        current_price: Precio actual
        df_4h, df_1h, df_daily: DataFrames de diferentes timeframes
        merino_signal_data: Datos de señal generados por MerinoSignalGenerator
        
    Returns:
        MerinoTradingAnalysis completo
    """
    try:
        # Extraer datos de la señal
        signal_info = merino_signal_data['signal']
        timeframe_4h = merino_signal_data['timeframe_4h']
        volume_data = merino_signal_data['volume_profile']
        market_context_data = merino_signal_data.get('market_context', {})
        
        # Crear indicadores
        indicators = MerinoTechnicalIndicators(
            ema_11_4h=timeframe_4h.get('ema_11', 0),
            ema_55_4h=timeframe_4h.get('ema_55', 0),
            ema_11_1h=df_1h['close'].ewm(span=11).mean().iloc[-1] if len(df_1h) > 11 else 0,
            ema_55_1h=df_1h['close'].ewm(span=55).mean().iloc[-1] if len(df_1h) > 55 else 0,
            ema_11_daily=market_context_data.get('ema_11_daily', 0),
            ema_55_daily=market_context_data.get('ema_55_daily', 0),
            adx=timeframe_4h.get('adx', {}).get('adx', 0),
            adx_modified=timeframe_4h.get('adx', {}).get('adx_modified', -23),
            adx_strength=timeframe_4h.get('adx', {}).get('strength', 'DEBIL'),
            adx_slope=timeframe_4h.get('adx', {}).get('slope', 0),
            adx_trending=timeframe_4h.get('adx', {}).get('trending', False),
            adx_strengthening=timeframe_4h.get('adx', {}).get('strengthening', False),
            squeeze_momentum=timeframe_4h.get('momentum', 0),
            squeeze_on=timeframe_4h.get('squeeze', False),
            squeeze_just_released=False,  # Se podría calcular comparando con período anterior
            vpoc=volume_data.get('vpoc', current_price),
            vpoc_distance_pct=volume_data.get('vpoc_distance_pct', 0),
            high_volume_levels=volume_data.get('high_volume_levels', []),
            rsi_4h=50.0  # Se podría calcular si se necesita
        )
        
        # Crear contexto de mercado
        market_context = MerinoMarketContext(
            macro_trend=market_context_data.get('macro_trend', 'UNKNOWN'),
            weekly_bias='NEUTRAL',  # Se podría calcular
            daily_bias=merino_signal_data['bias'],
            resistance_20d=market_context_data.get('resistance_20d', current_price * 1.05),
            support_20d=market_context_data.get('support_20d', current_price * 0.95),
            volatility_20d=market_context_data.get('volatility_pct', 0),
            volume_avg_20d=0,  # Se podría calcular
            price_vs_resistance_pct=market_context_data.get('price_vs_resistance', 0),
            price_vs_support_pct=market_context_data.get('price_vs_support', 0)
        )
        
        # Crear señal
        signal = MerinoSignal(
            signal=signal_info,
            signal_strength=merino_signal_data['signal_strength'],
            bias_4h=merino_signal_data['bias'],
            confluence_score=merino_signal_data['confluence_score'],
            reasons=[],  # Se podría llenar con las razones específicas
            invalidation_conditions=[],
            optimal_timeframe='4h',
            entry_timing='IMMEDIATE' if merino_signal_data['signal_strength'] > 70 else 'ON_CONFIRMATION'
        )
        
        # Crear gestión de riesgo
        risk_mgmt = MerinoRiskManagement(
            position_size_pct=2.0 if signal_info in ['LONG', 'SHORT'] else 0.0
        )
        
        # Crear niveles de trading si hay señal
        trading_levels = None
        if signal_info in ['LONG', 'SHORT'] and 'trading_levels' in merino_signal_data:
            levels_data = merino_signal_data['trading_levels']
            trading_levels = MerinoTradingLevels(
                entry_price=levels_data.get('entry', current_price),
                entry_range_low=current_price * 0.999,
                entry_range_high=current_price * 1.001,
                target_1=levels_data.get('targets', [current_price])[0] if levels_data.get('targets') else current_price,
                target_2=levels_data.get('targets', [current_price, current_price])[1] if len(levels_data.get('targets', [])) > 1 else current_price,
                stop_loss=levels_data.get('stop_loss', current_price),
                technical_stop=indicators.ema_11_4h * (0.995 if signal_info == 'LONG' else 1.005),
                invalidation_level=indicators.ema_11_4h,
                invalidation_reason=f"Cierre {'bajo' if signal_info == 'LONG' else 'sobre'} EMA 11 en 4H"
            )
        
        # Determinar nivel de confianza
        if signal.confluence_score >= 3 and signal.signal_strength >= 70:
            confidence = 'HIGH'
        elif signal.confluence_score >= 2 and signal.signal_strength >= 50:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        # Crear análisis completo
        analysis = MerinoTradingAnalysis(
            symbol=symbol,
            timestamp=datetime.now(),
            current_price=current_price,
            indicators=indicators,
            market_context=market_context,
            signal=signal,
            risk_management=risk_mgmt,
            trading_levels=trading_levels,
            analysis_text=merino_signal_data.get('analysis_text', ''),
            recommendation=merino_signal_data.get('recommendation', ''),
            confidence_level=confidence
        )
        
        return analysis
        
    except Exception as e:
        # En caso de error, crear análisis básico
        return MerinoTradingAnalysis(
            symbol=symbol,
            timestamp=datetime.now(),
            current_price=current_price,
            indicators=MerinoTechnicalIndicators(
                ema_11_4h=0, ema_55_4h=0, ema_11_1h=0, ema_55_1h=0,
                ema_11_daily=0, ema_55_daily=0, adx=0, adx_modified=-23,
                adx_strength='DEBIL', adx_slope=0, adx_trending=False,
                adx_strengthening=False, squeeze_momentum=0, squeeze_on=True,
                squeeze_just_released=False, vpoc=current_price,
                vpoc_distance_pct=0, high_volume_levels=[], rsi_4h=50
            ),
            market_context=MerinoMarketContext(
                macro_trend='UNKNOWN', weekly_bias='NEUTRAL', daily_bias='NEUTRAL',
                resistance_20d=current_price*1.05, support_20d=current_price*0.95,
                volatility_20d=0, volume_avg_20d=0, price_vs_resistance_pct=0,
                price_vs_support_pct=0
            ),
            signal=MerinoSignal(
                signal='NO_SIGNAL', signal_strength=0, bias_4h='NEUTRAL',
                confluence_score=0, reasons=[], invalidation_conditions=[],
                optimal_timeframe='4h', entry_timing='WAIT_BETTER_SETUP'
            ),
            risk_management=MerinoRiskManagement(position_size_pct=0.0),
            analysis_text=f'Error generando análisis para {symbol}: {str(e)}',
            recommendation='ERROR - Revisar logs del sistema',
            confidence_level='LOW'
        )