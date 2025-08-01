"""
Servicio de análisis mejorado implementando la metodología completa de Jaime Merino
"""
from datetime import datetime
from typing import Optional, Dict
from services.binance_service import binance_service
from services.enhanced_indicators import jaime_merino_signal_generator
from models.trading_analysis import TradingAnalysis, create_analysis
from utils.logger import analysis_logger
from config import Config

logger = analysis_logger

class EnhancedAnalysisService:
    """
    Servicio de análisis mejorado siguiendo la metodología exacta de Jaime Merino
    """
    
    def __init__(self):
        """Inicializa el servicio de análisis mejorado"""
        self.binance = binance_service
        self.merino_generator = jaime_merino_signal_generator
        logger.info("🚀 Servicio de análisis mejorado inicializado - Metodología Jaime Merino")
    
    def analyze_symbol_merino(self, symbol: str) -> Optional[Dict]:
        """
        Realiza análisis completo siguiendo la metodología de Jaime Merino
        
        Args:
            symbol: Símbolo a analizar (ej: 'BTCUSDT')
            
        Returns:
            Análisis completo según metodología Merino
        """
        try:
            logger.info(f"📊 Iniciando análisis Merino para {symbol}")
            
            # 1. Obtener datos multi-temporales
            df_4h = self.binance.get_klines(symbol, interval='4h', limit=100)
            df_1h = self.binance.get_klines(symbol, interval='1h', limit=50)
            df_daily = self.binance.get_klines(symbol, interval='1d', limit=30)
            
            if any(df is None or len(df) < 55 for df in [df_4h, df_1h]):
                logger.error(f"❌ Insuficientes datos históricos para {symbol}")
                return None
            
            # 2. Obtener precio actual
            current_price = self.binance.get_current_price(symbol)
            if not current_price:
                logger.error(f"❌ No se pudo obtener precio actual de {symbol}")
                return None
            
            # 3. Generar señal completa de Merino
            merino_signal = self.merino_generator.generate_merino_signal(
                df_4h, df_1h, current_price
            )
            
            # 4. Análisis de contexto de mercado
            market_context = self._analyze_market_context(df_daily, current_price)
            
            # 5. Gestión de capital según filosofía 40-30-20-10
            capital_allocation = self._calculate_capital_allocation(
                merino_signal['signal'], merino_signal['signal_strength']
            )
            
            # 6. Generar análisis textual detallado
            analysis_text = self._generate_merino_analysis_text(
                symbol, current_price, merino_signal, market_context
            )
            
            # 7. Generar recomendación específica
            recommendation = self._generate_merino_recommendation(
                symbol, current_price, merino_signal, capital_allocation
            )
            
            # 8. Compilar resultado final
            analysis_result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'current_price': current_price,
                'methodology': 'JAIME_MERINO',
                'signal': merino_signal,
                'market_context': market_context,
                'capital_allocation': capital_allocation,
                'analysis_text': analysis_text,
                'recommendation': recommendation,
                'risk_management': self._get_risk_management_rules(),
                'confluence_analysis': self._analyze_confluence(merino_signal)
            }
            
            logger.info(f"✅ Análisis Merino completado para {symbol}: {merino_signal['signal']} ({merino_signal['signal_strength']}%)")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Error en análisis Merino de {symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _analyze_market_context(self, df_daily: pd.DataFrame, current_price: float) -> Dict:
        """
        Analiza el contexto general del mercado en timeframe diario
        """
        try:
            # EMAs en diario para contexto macro
            ema_11_daily = df_daily['close'].ewm(span=11).mean().iloc[-1]
            ema_55_daily = df_daily['close'].ewm(span=55).mean().iloc[-1]
            
            # Determinar tendencia macro
            if ema_11_daily > ema_55_daily:
                macro_trend = "BULL_MARKET"
            elif ema_11_daily < ema_55_daily:
                macro_trend = "BEAR_MARKET"
            else:
                macro_trend = "SIDEWAYS"
            
            # Calcular volatilidad reciente
            returns = df_daily['close'].pct_change().dropna()
            volatility = returns.std() * 100
            
            # Niveles de soporte/resistencia diarios
            high_20d = df_daily['high'].tail(20).max()
            low_20d = df_daily['low'].tail(20).min()
            
            return {
                'macro_trend': macro_trend,
                'ema_11_daily': ema_11_daily,
                'ema_55_daily': ema_55_daily,
                'volatility_pct': volatility,
                'resistance_20d': high_20d,
                'support_20d': low_20d,
                'price_vs_resistance': ((current_price - high_20d) / high_20d) * 100,
                'price_vs_support': ((current_price - low_20d) / low_20d) * 100
            }
            
        except Exception as e:
            logger.error(f"❌ Error analizando contexto de mercado: {e}")
            return {'macro_trend': 'UNKNOWN', 'volatility_pct': 0}
    
    def _calculate_capital_allocation(self, signal: str, strength: int) -> Dict:
        """
        Calcula asignación de capital según filosofía 40-30-20-10 de Merino
        """
        base_allocation = {
            'btc_long_term': 40,  # 40% Bitcoin largo plazo
            'weekly_charts': 30,  # 30% gráficos semanales
            'daily_trading': 20,  # 20% trading diario
            'futures': 10         # 10% futuros
        }
        
        # Ajustar según fuerza de señal
        if signal in ['LONG', 'SHORT'] and strength >= 70:
            # Señal muy fuerte: aumentar asignación a trading diario
            trading_allocation = {
                'position_size': 3.0,  # 3% del capital total
                'max_risk_per_trade': 1.0,  # 1% máximo riesgo
                'recommended_timeframe': 'daily_trading'
            }
        elif signal in ['LONG', 'SHORT'] and strength >= 50:
            # Señal moderada
            trading_allocation = {
                'position_size': 2.0,  # 2% del capital total
                'max_risk_per_trade': 1.0,
                'recommended_timeframe': 'daily_trading'
            }
        else:
            # Sin señal clara: preservar capital
            trading_allocation = {
                'position_size': 0.0,
                'max_risk_per_trade': 0.0,
                'recommended_timeframe': 'wait'
            }
        
        return {
            'base_allocation': base_allocation,
            'current_trade': trading_allocation,
            'philosophy': '40-30-20-10 (BTC_LT-Weekly-Daily-Futures)'
        }
    
    def _generate_merino_analysis_text(self, symbol: str, price: float, 
                                     signal: Dict, context: Dict) -> str:
        """
        Genera análisis textual detallado al estilo de Jaime Merino
        """
        try:
            timeframe_4h = signal['timeframe_4h']
            volume_data = signal['volume_profile']
            adx_data = timeframe_4h.get('adx', {})
            
            analysis = f"""📊 ANÁLISIS TÉCNICO JAIME MERINO - {symbol}
{'='*60}

💰 PRECIO ACTUAL: ${price:,.4f}
🎯 SEÑAL: {signal['signal']} | FUERZA: {signal['signal_strength']}/100
📈 SESGO 4H: {signal['bias']} | CONFLUENCIAS: {signal['confluence_score']}/4

🔍 ANÁLISIS MULTI-TEMPORAL:
{'─'*40}
📊 Contexto Diario:
   • Tendencia Macro: {context['macro_trend']}
   • EMA 11 Diario: ${context.get('ema_11_daily', 0):,.4f}
   • EMA 55 Diario: ${context.get('ema_55_daily', 0):,.4f}
   • Volatilidad: {context.get('volatility_pct', 0):.2f}%

⏰ Timeframe 4H (Principal):
   • EMA 11: ${timeframe_4h.get('ema_11', 0):,.4f}
   • EMA 55: ${timeframe_4h.get('ema_55', 0):,.4f}
   • Relación EMAs: {"ALCISTA" if timeframe_4h.get('ema_11', 0) > timeframe_4h.get('ema_55', 0) else "BAJISTA"}
   • Precio vs EMA11: {((price - timeframe_4h.get('ema_11', price)) / timeframe_4h.get('ema_11', price)) * 100:+.2f}%

📊 INDICADORES CLAVE:
{'─'*40}
🎯 ADX (Fuerza de Tendencia):
   • Valor: {adx_data.get('adx', 0):.1f} | Modificado: {adx_data.get('adx_modified', -23):.1f}
   • Clasificación: {adx_data.get('strength', 'DESCONOCIDA')}
   • Pendiente: {"FORTALECIENDO" if adx_data.get('strengthening', False) else "DEBILITANDO"}
   • Trending: {"SÍ" if adx_data.get('trending', False) else "NO"}

⚡ Squeeze Momentum:
   • Estado: {"SQUEEZE ON (Consolidación)" if timeframe_4h.get('squeeze', False) else "SQUEEZE OFF (Movimiento)"}
   • Momentum: {timeframe_4h.get('momentum', 0):+.4f}
   • Dirección: {"ALCISTA" if timeframe_4h.get('momentum', 0) > 0 else "BAJISTA" if timeframe_4h.get('momentum', 0) < 0 else "NEUTRAL"}

📊 VOLUME PROFILE (VPVR):
   • VPoC: ${volume_data.get('vpoc', 0):,.4f}
   • Distancia del VPoC: {volume_data.get('vpoc_distance_pct', 0):+.2f}%
   • Niveles de Alto Volumen: {len(volume_data.get('high_volume_levels', []))} identificados

💡 METODOLOGÍA JAIME MERINO:
{'─'*40}
✅ Criterios Cumplidos:
   • EMAs alineadas para sesgo: {"✓" if signal['bias'] != 'NEUTRAL' else "✗"}
   • ADX confirma tendencia: {"✓" if adx_data.get('trending', False) else "✗"}
   • Momentum direccional: {"✓" if abs(timeframe_4h.get('momentum', 0)) > 0.001 else "✗"}
   • Sin squeeze (consolidación): {"✓" if not timeframe_4h.get('squeeze', True) else "✗"}

🎯 FILOSOFÍA CONTRARIA:
   • Operando contra el 90% que pierde
   • Disciplina > Análisis técnico perfecto
   • "Solo operamos con alta probabilidad"

📈 NIVELES CRÍTICOS:
{'─'*40}
🛡️ Soporte 20D: ${context.get('support_20d', 0):,.4f} ({context.get('price_vs_support', 0):+.2f}%)
🚫 Resistencia 20D: ${context.get('resistance_20d', 0):,.4f} ({context.get('price_vs_resistance', 0):+.2f}%)
📊 VPoC: ${volume_data.get('vpoc', 0):,.4f} (Nivel de mayor volumen)

⚠️ EVALUACIÓN DE RIESGO:
{'─'*40}
🎲 Riesgo General: {self._assess_risk_level(signal['signal_strength'], adx_data.get('adx', 0))}
📊 Volatilidad: {context.get('volatility_pct', 0):.2f}% ({"ALTA" if context.get('volatility_pct', 0) > 4 else "MODERADA" if context.get('volatility_pct', 0) > 2 else "BAJA"})
🔍 Manipulación: {"POSIBLE" if signal['signal_strength'] < 40 else "BAJA"}

⏰ Análisis generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
📚 Metodología: Jaime Merino - Trading Latino Avanzado"""

            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error generando análisis textual: {e}")
            return f"Error generando análisis detallado para {symbol}"
    
    def _generate_merino_recommendation(self, symbol: str, price: float, 
                                      signal: Dict, capital: Dict) -> str:
        """
        Genera recomendación específica al estilo de Jaime Merino
        """
        try:
            signal_type = signal['signal']
            strength = signal['signal_strength']
            levels = signal['trading_levels']
            
            if signal_type == 'LONG' and strength >= 50:
                recommendation = f"""🟢 RECOMENDACIÓN JAIME MERINO: POSICIÓN LARGA
{'='*55}

✅ SETUP ALCISTA CONFIRMADO:
   • Sesgo 4H: {signal['bias']}
   • Confluencias técnicas: {signal['confluence_score']}/4
   • Fuerza de señal: {strength}% ({"EXCELENTE" if strength > 70 else "BUENA"})

💰 GESTIÓN DE CAPITAL (Filosofía 40-30-20-10):
   • Asignación recomendada: {capital['current_trade']['position_size']:.1f}% del capital total
   • Riesgo máximo: {capital['current_trade']['max_risk_per_trade']:.1f}% por operación
   • Timeframe: Trading diario (20% de la cartera)

🎯 PLAN DE TRADING:
   • Entrada: ${levels.get('entry', price):,.4f}
   • Target 1: ${levels.get('targets', [price*1.02])[0]:,.4f} (+2%) - CERRAR 50%
   • Target 2: ${levels.get('targets', [price*1.02, price*1.05])[1] if len(levels.get('targets', [])) > 1 else price*1.05:,.4f} (+5%) - CERRAR RESTO
   • Stop Loss: ${levels.get('stop_loss', price*0.98):,.4f} (-2%)

🛡️ REGLAS DE MERINO:
   • Sin apalancamiento > 1:3
   • Stop si cierra bajo EMA 11
   • Máximo 6% pérdida diaria
   • Máximo 8% pérdida semanal

⚡ EJECUCIÓN:
   1. Verificar volumen en breakout
   2. Entrada gradual en 2-3 tramos
   3. Mover stop a breakeven en +1%
   4. Seguir plan sin emociones

💡 METODOLOGÍA: "Tomar dinero de otros legalmente"
⚠️ INVALIDACIÓN: Cierre bajo EMA 11 en 4H"""

            elif signal_type == 'SHORT' and strength >= 50:
                recommendation = f"""🔴 RECOMENDACIÓN JAIME MERINO: POSICIÓN CORTA
{'='*55}

✅ SETUP BAJISTA CONFIRMADO:
   • Sesgo 4H: {signal['bias']}
   • Confluencias técnicas: {signal['confluence_score']}/4
   • Fuerza de señal: {strength}% ({"EXCELENTE" if strength > 70 else "BUENA"})

💰 GESTIÓN DE CAPITAL (Filosofía 40-30-20-10):
   • Asignación recomendada: {capital['current_trade']['position_size']:.1f}% del capital total
   • Riesgo máximo: {capital['current_trade']['max_risk_per_trade']:.1f}% por operación
   • Timeframe: Trading diario (20% de la cartera)

🎯 PLAN DE TRADING:
   • Entrada: ${levels.get('entry', price):,.4f}
   • Target 1: ${levels.get('targets', [price*0.98])[0]:,.4f} (-2%) - CERRAR 50%
   • Target 2: ${levels.get('targets', [price*0.98, price*0.95])[1] if len(levels.get('targets', [])) > 1 else price*0.95:,.4f} (-5%) - CERRAR RESTO
   • Stop Loss: ${levels.get('stop_loss', price*1.02):,.4f} (+2%)

🛡️ REGLAS DE MERINO:
   • Sin apalancamiento > 1:3
   • Stop si cierra sobre EMA 11
   • Máximo 6% pérdida diaria
   • Máximo 8% pérdida semanal

⚡ EJECUCIÓN:
   1. Confirmar presión vendedora
   2. Entrada gradual en 2-3 tramos
   3. Mover stop a breakeven en +1%
   4. Mantener disciplina total

💡 METODOLOGÍA: "Operar contra el 90% que pierde"
⚠️ INVALIDACIÓN: Cierre sobre EMA 11 en 4H"""

            elif signal_type == 'WAIT_SQUEEZE':
                recommendation = f"""🟡 RECOMENDACIÓN JAIME MERINO: ESPERAR - SQUEEZE DETECTADO
{'='*60}

⏳ SITUACIÓN: CONSOLIDACIÓN (SQUEEZE ON)
   • El mercado está en compresión
   • Esperando expansión de volatilidad
   • Bollinger Bands dentro de Keltner Channels

📊 ESTADO ACTUAL:
   • Precio: ${price:,.4f}
   • Momentum actual: {signal['timeframe_4h'].get('momentum', 0):+.4f}
   • ADX: {signal['timeframe_4h'].get('adx', {}).get('adx', 0):.1f}

🎯 PLAN DE ACCIÓN:
   • ESPERAR ruptura del squeeze
   • Preparar alertas en niveles clave
   • NO forzar operaciones
   • Preservar capital es prioridad

🔔 ALERTAS SUGERIDAS:
   • Ruptura alcista: > ${price * 1.015:,.4f}
   • Ruptura bajista: < ${price * 0.985:,.4f}
   • Activación ADX: > 25

💡 FILOSOFÍA MERINO:
   "Es mejor perder una oportunidad que perder dinero"
   
⏰ REVISIÓN: Cada 2-4 horas hasta expansión"""

            else:
                recommendation = f"""⚪ RECOMENDACIÓN JAIME MERINO: SIN OPERACIÓN
{'='*50}

🚫 RAZÓN: Condiciones técnicas insuficientes
   • Fuerza de señal: {strength}% (Mínimo: 50%)
   • Confluencias: {signal['confluence_score']}/4 (Mínimo: 3/4)

📊 ESTADO ACTUAL:
   • Señal: {signal_type}
   • Sesgo: {signal['bias']}
   • ADX: {signal['timeframe_4h'].get('adx', {}).get('adx', 0):.1f}

💰 ACCIÓN RECOMENDADA:
   • PRESERVAR CAPITAL (40% en BTC largo plazo)
   • ESPERAR mejor configuración
   • MANTENER disciplina

📚 RECORDATORIO MERINO:
   "Solo operamos con alta probabilidad de éxito"
   "El dinero no se hace forzando operaciones"

🔍 PRÓXIMA REVISIÓN: 4 horas
⚠️ NO OPERAR hasta confluencia ≥ 3/4"""

            return recommendation
            
        except Exception as e:
            logger.error(f"❌ Error generando recomendación: {e}")
            return f"Error generando recomendación para {symbol}"
    
    def _assess_risk_level(self, strength: int, adx: float) -> str:
        """Evalúa el nivel de riesgo"""
        if strength > 70 and adx > 35:
            return "BAJO (Setup sólido)"
        elif strength > 50 and adx > 25:
            return "MEDIO (Aceptable)"
        else:
            return "ALTO (No recomendado)"
    
    def _get_risk_management_rules(self) -> Dict:
        """Retorna las reglas de gestión de riesgo de Merino"""
        return {
            'max_risk_per_trade': 1.0,  # 1% máximo por operación
            'max_daily_loss': 6.0,      # 6% máximo diario
            'max_weekly_loss': 8.0,     # 8% máximo semanal  
            'max_monthly_loss': 10.0,   # 10% máximo mensual
            'leverage_limit': 3.0,      # Máximo 1:3
            'capital_allocation': '40-30-20-10',
            'position_sizing': 'Division en 20 partes iguales',
            'stop_strategy': 'Donde retail NO pone stops'
        }
    
    def _analyze_confluence(self, signal: Dict) -> Dict:
        """Analiza la confluencia técnica detallada"""
        confluences = []
        
        # EMAs
        if signal['bias'] != 'NEUTRAL':
            confluences.append({
                'factor': 'EMAs alineadas',
                'status': True,
                'description': f"EMA 11 {'>' if signal['bias'] == 'BULLISH' else '<'} EMA 55"
            })
        
        # ADX
        adx_data = signal['timeframe_4h'].get('adx', {})
        if adx_data.get('trending', False):
            confluences.append({
                'factor': 'ADX trending',
                'status': True,
                'description': f"ADX {adx_data.get('adx', 0):.1f} > 25"
            })
        
        # Momentum
        momentum = signal['timeframe_4h'].get('momentum', 0)
        if abs(momentum) > 0.001:
            confluences.append({
                'factor': 'Momentum direccional', 
                'status': True,
                'description': f"Momentum {momentum:+.4f}"
            })
        
        # Volume Profile
        vpoc_distance = signal['volume_profile'].get('vpoc_distance_pct', 100)
        if abs(vpoc_distance) < 3:
            confluences.append({
                'factor': 'Cerca del VPoC',
                'status': True, 
                'description': f"Distancia VPoC: {vpoc_distance:+.2f}%"
            })
        
        return {
            'total_confluences': len(confluences),
            'details': confluences,
            'strength': 'ALTA' if len(confluences) >= 3 else 'MEDIA' if len(confluences) >= 2 else 'BAJA'
        }

# Instancia global del servicio mejorado
enhanced_analysis_service = EnhancedAnalysisService()