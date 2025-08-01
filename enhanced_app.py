"""
Aplicación principal mejorada - Bot de Trading Jaime Merino
Implementa la metodología completa de Trading Latino
"""
import os
import threading
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from enhanced_config import merino_config, MerinoConfig, merino_methodology
from utils.logger import setup_logger, app_logger
from websocket.enhanced_socket_handlers import EnhancedSocketHandlers
from services.enhanced_analysis_service import enhanced_analysis_service
from services.binance_service import binance_service

# Configurar logging mejorado
logger = app_logger

def create_merino_app(config_name=None):
    """
    Factory function para crear la aplicación Jaime Merino Bot
    
    Args:
        config_name: Nombre de la configuración a usar
        
    Returns:
        Tupla (app, socketio, socket_handlers)
    """
    # Determinar configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Crear aplicación Flask
    app = Flask(__name__)
    config_class = merino_config.get(config_name, merino_config['default'])
    app.config.from_object(config_class)
    
    # Configurar logging específico
    setup_merino_logging(config_class.LOG_LEVEL)
    
    # Inicializar SocketIO
    socketio = SocketIO(
        app,
        cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'],
        async_mode=app.config['SOCKETIO_ASYNC_MODE'],
        logger=False,
        engineio_logger=False
    )
    
    # Configurar handlers mejorados de Socket.IO
    socket_handlers = EnhancedSocketHandlers(socketio, config_class)
    socket_handlers.register_handlers()
    
    # Registrar rutas mejoradas
    register_merino_routes(app, config_class)
    
    # Configurar servicios de fondo mejorados
    setup_merino_background_services(socketio, socket_handlers, config_class)
    
    logger.info("🚀 Jaime Merino Trading Bot creado exitosamente")
    logger.info(f"📈 Metodología: {merino_methodology.PHILOSOPHY['main_principle']}")
    
    return app, socketio, socket_handlers

def setup_merino_logging(log_level: str):
    """
    Configura logging específico para la metodología Merino
    
    Args:
        log_level: Nivel de logging
    """
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Configurar loggers específicos
    loggers = {
        'merino_app': MerinoConfig.LOG_FILES['app'],
        'merino_analysis': MerinoConfig.LOG_FILES['analysis'],
        'merino_signals': MerinoConfig.LOG_FILES['signals'],
        'merino_trades': MerinoConfig.LOG_FILES['trades'],
        'merino_websocket': MerinoConfig.LOG_FILES['websocket'],
        'merino_binance': MerinoConfig.LOG_FILES['binance']
    }
    
    for logger_name, log_file in loggers.items():
        setup_logger(logger_name, log_file, log_level)

def register_merino_routes(app, config):
    """
    Registra las rutas mejoradas de la aplicación
    
    Args:
        app: Instancia de Flask
        config: Configuración de la app
    """
    
    @app.route('/')
    def index():
        """Dashboard principal del Jaime Merino Bot"""
        try:
            return render_template('merino_dashboard.html', 
                                 config=config,
                                 methodology=merino_methodology)
        except Exception as e:
            logger.error(f"❌ Error sirviendo dashboard: {e}")
            return f"Error cargando dashboard: {str(e)}", 500
    
    @app.route('/health')
    def health_check():
        """Endpoint de salud mejorado"""
        try:
            # Verificar conexión a Binance
            binance_status = binance_service.test_connection()
            
            # Verificar servicios internos
            analysis_status = enhanced_analysis_service is not None
            
            health_data = {
                'status': 'healthy' if binance_status and analysis_status else 'degraded',
                'timestamp': datetime.now().isoformat(),
                'methodology': 'JAIME_MERINO',
                'version': '2.0.0',
                'services': {
                    'binance': 'connected' if binance_status else 'disconnected',
                    'analysis_service': 'active' if analysis_status else 'inactive',
                    'websocket': 'active',
                    'enhanced_indicators': 'active'
                },
                'configuration': {
                    'symbols': config.TRADING_SYMBOLS,
                    'timeframes': config.TIMEFRAMES,
                    'update_intervals': config.UPDATE_INTERVALS,
                    'risk_management': config.RISK_MANAGEMENT,
                    'signals_config': config.SIGNALS
                },
                'philosophy': merino_methodology.PHILOSOPHY['main_principle']
            }
            
            return jsonify(health_data)
            
        except Exception as e:
            logger.error(f"❌ Error en health check: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'methodology': 'JAIME_MERINO'
            }), 500
    
    @app.route('/api/merino/symbols')
    def get_merino_symbols():
        """API endpoint para obtener símbolos según Merino"""
        return jsonify({
            'symbols': config.TRADING_SYMBOLS,
            'count': len(config.TRADING_SYMBOLS),
            'timeframes': config.TIMEFRAMES,
            'methodology': 'JAIME_MERINO',
            'focus': 'Bitcoin y principales altcoins según Trading Latino'
        })
    
    @app.route('/api/merino/analysis/<symbol>')
    def get_merino_analysis(symbol):
        """
        API endpoint para obtener análisis según metodología Merino
        
        Args:
            symbol: Símbolo a analizar
        """
        try:
            symbol = symbol.upper()
            
            if symbol not in config.TRADING_SYMBOLS:
                return jsonify({
                    'success': False,
                    'error': f'Símbolo {symbol} no está en la metodología Merino',
                    'supported_symbols': config.TRADING_SYMBOLS,
                    'methodology': 'JAIME_MERINO'
                }), 400
            
            # Realizar análisis completo según Merino
            analysis = enhanced_analysis_service.analyze_symbol_merino(symbol)
            
            if analysis:
                return jsonify({
                    'success': True,
                    'methodology': 'JAIME_MERINO',
                    'symbol': symbol,
                    'data': analysis,
                    'timestamp': datetime.now().isoformat(),
                    'philosophy': merino_methodology.PHILOSOPHY['discipline']
                })
            else:
                return jsonify({
                    'success': False,
                    'methodology': 'JAIME_MERINO',
                    'symbol': symbol,
                    'error': 'No se pudo completar el análisis según metodología Merino',
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        except Exception as e:
            logger.error(f"❌ Error en API análisis Merino para {symbol}: {e}")
            return jsonify({
                'success': False,
                'methodology': 'JAIME_MERINO',
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/api/merino/philosophy')
    def get_merino_philosophy():
        """Endpoint para obtener la filosofía de Jaime Merino"""
        return jsonify({
            'methodology': 'JAIME_MERINO',
            'philosophy': merino_methodology.PHILOSOPHY,
            'market_states': merino_methodology.MARKET_STATES,
            'confluences': merino_methodology.CONFLUENCES,
            'invalidation_rules': merino_methodology.INVALIDATION_RULES,
            'trading_hours': merino_methodology.OPTIMAL_TRADING_HOURS
        })
    
    @app.route('/api/merino/risk-management')
    def get_risk_management():
        """Endpoint para obtener reglas de gestión de riesgo"""
        return jsonify({
            'methodology': 'JAIME_MERINO',
            'capital_allocation': '40-30-20-10',
            'rules': config.RISK_MANAGEMENT,
            'philosophy': {
                'max_risk': merino_methodology.PHILOSOPHY['risk_motto'],
                'discipline': merino_methodology.PHILOSOPHY['discipline']
            }
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Maneja errores 404"""
        return jsonify({
            'error': 'Endpoint no encontrado',
            'methodology': 'JAIME_MERINO',
            'available_endpoints': [
                '/',
                '/health',
                '/api/merino/symbols',
                '/api/merino/analysis/<symbol>',
                '/api/merino/philosophy',
                '/api/merino/risk-management'
            ]
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores internos"""
        logger.error(f"❌ Error interno del servidor: {error}")
        return jsonify({
            'error': 'Error interno del servidor',
            'methodology': 'JAIME_MERINO',
            'message': 'Consulte los logs para más detalles',
            'philosophy': merino_methodology.PHILOSOPHY['discipline']
        }), 500

def setup_merino_background_services(socketio, socket_handlers, config):
    """
    Configura los servicios de fondo mejorados para la metodología Merino
    
    Args:
        socketio: Instancia de SocketIO
        socket_handlers: Manejadores de Socket.IO
        config: Configuración de la aplicación
    """
    
    def merino_auto_analysis():
        """
        Servicio de análisis automático según metodología Merino
        """
        logger.info("🔄 Servicio de análisis automático Merino iniciado")
        logger.info(f"📈 Filosofía: {merino_methodology.PHILOSOPHY['main_principle']}")
        
        while True:
            try:
                # Usar intervalo del timeframe principal (4H)
                interval = config.UPDATE_INTERVALS['4h']
                time.sleep(interval)
                
                # Solo analizar si hay clientes conectados
                if socket_handlers.get_connected_clients_count() > 0:
                    logger.info(f"🔄 Iniciando análisis automático Merino para {len(config.TRADING_SYMBOLS)} símbolos")
                    
                    for symbol in config.TRADING_SYMBOLS:
                        try:
                            # Análisis completo según Merino
                            analysis = enhanced_analysis_service.analyze_symbol_merino(symbol)
                            
                            if analysis:
                                # Broadcast del análisis
                                socket_handlers.broadcast_merino_analysis(symbol, analysis)
                                
                                # Log específico para señales fuertes
                                signal_strength = analysis.get('signal', {}).get('signal_strength', 0)
                                if signal_strength >= config.SIGNALS['min_strength_for_trade']:
                                    logger.info(f"🎯 SEÑAL MERINO: {symbol} - {analysis.get('signal', {}).get('signal', 'UNKNOWN')} ({signal_strength}%)")
                                
                                # Pausa entre análisis para no sobrecargar
                                time.sleep(5)
                            else:
                                logger.warning(f"⚠️ Análisis Merino falló para {symbol}")
                                
                        except Exception as e:
                            logger.error(f"❌ Error en análisis automático de {symbol}: {e}")
                            continue
                    
                    logger.info("✅ Ciclo de análisis automático Merino completado")
                else:
                    logger.debug("📭 No hay clientes conectados, saltando análisis automático")
                    
            except Exception as e:
                logger.error(f"❌ Error en servicio de análisis automático Merino: {e}")
                time.sleep(300)  # Esperar 5 minutos antes de reintentar
    
    def merino_market_monitor():
        """
        Monitor de mercado según criterios de Merino
        """
        logger.info("👁️ Monitor de mercado Merino iniciado")
        
        while True:
            try:
                time.sleep(config.UPDATE_INTERVALS['realtime'])
                
                # Monitorear Bitcoin (símbolo principal)
                btc_price = binance_service.get_current_price('BTCUSDT')
                
                if btc_price:
                    # Broadcast de precio en tiempo real
                    socketio.emit('btc_price_update', {
                        'price': btc_price,
                        'timestamp': time.time(),
                        'methodology': 'JAIME_MERINO'
                    })
                
                # Cada 10 minutos, verificar estado general del mercado
                if int(time.time()) % 600 == 0:
                    market_sentiment = analyze_market_sentiment(config.TRADING_SYMBOLS[:5])
                    socketio.emit('market_sentiment', {
                        'sentiment': market_sentiment,
                        'timestamp': time.time(),
                        'methodology': 'JAIME_MERINO'
                    })
                
            except Exception as e:
                logger.error(f"❌ Error en monitor de mercado: {e}")
                time.sleep(60)
    
    def merino_risk_monitor():
        """
        Monitor de riesgo según reglas de Merino
        """
        logger.info("🛡️ Monitor de riesgo Merino iniciado")
        
        while True:
            try:
                time.sleep(1800)  # Cada 30 minutos
                
                # Monitorear exposición total
                risk_status = {
                    'timestamp': time.time(),
                    'methodology': 'JAIME_MERINO',
                    'philosophy': merino_methodology.PHILOSOPHY['risk_motto'],
                    'limits': config.RISK_MANAGEMENT,
                    'status': 'MONITORING'
                }
                
                socketio.emit('risk_status', risk_status)
                
            except Exception as e:
                logger.error(f"❌ Error en monitor de riesgo: {e}")
                time.sleep(300)
    
    # Iniciar servicios de fondo
    analysis_thread = threading.Thread(target=merino_auto_analysis)
    analysis_thread.daemon = True
    analysis_thread.start()
    
    monitor_thread = threading.Thread(target=merino_market_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    risk_thread = threading.Thread(target=merino_risk_monitor)
    risk_thread.daemon = True
    risk_thread.start()
    
    logger.info("✅ Servicios de fondo Merino iniciados")

def analyze_market_sentiment(symbols):
    """
    Analiza el sentimiento general del mercado
    
    Args:
        symbols: Lista de símbolos a analizar
        
    Returns:
        Sentimiento del mercado
    """
    try:
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        for symbol in symbols:
            try:
                # Análisis rápido de EMAs para determinar sesgo
                df = binance_service.get_klines(symbol, '4h', 20)
                if df is not None and len(df) >= 11:
                    ema_11 = df['close'].ewm(span=11).mean().iloc[-1]
                    ema_55 = df['close'].ewm(span=55).mean().iloc[-1] if len(df) >= 55 else ema_11
                    
                    if ema_11 > ema_55 * 1.005:  # 0.5% threshold
                        bullish_count += 1
                    elif ema_11 < ema_55 * 0.995:
                        bearish_count += 1
                    else:
                        neutral_count += 1
                        
            except Exception:
                neutral_count += 1
                continue
        
        total = bullish_count + bearish_count + neutral_count
        if total == 0:
            return 'UNKNOWN'
        
        bullish_pct = (bullish_count / total) * 100
        bearish_pct = (bearish_count / total) * 100
        
        if bullish_pct >= 60:
            return 'BULLISH'
        elif bearish_pct >= 60:
            return 'BEARISH'
        else:
            return 'MIXED'
            
    except Exception as e:
        logger.error(f"❌ Error analizando sentimiento: {e}")
        return 'UNKNOWN'

def perform_initial_merino_analysis(socket_handlers, config):
    """
    Realiza análisis inicial según metodología Merino
    
    Args:
        socket_handlers: Manejadores de Socket.IO
        config: Configuración de la aplicación
    """
    try:
        logger.info("🔄 Iniciando análisis inicial Merino...")
        logger.info(f"📈 {merino_methodology.PHILOSOPHY['discipline']}")
        
        # Esperar estabilización del servidor
        time.sleep(10)
        
        completed = 0
        high_probability_signals = 0
        
        for symbol in config.TRADING_SYMBOLS:
            try:
                analysis = enhanced_analysis_service.analyze_symbol_merino(symbol)
                
                if analysis:
                    socket_handlers.cache_merino_analysis(symbol, analysis)
                    completed += 1
                    
                    # Contar señales de alta probabilidad
                    signal_strength = analysis.get('signal', {}).get('signal_strength', 0)
                    if signal_strength >= config.SIGNALS['min_strength_for_trade']:
                        high_probability_signals += 1
                        logger.info(f"🎯 Alta probabilidad detectada: {symbol} ({signal_strength}%)")
                    
                    logger.info(f"✅ Análisis inicial Merino: {symbol} ({completed}/{len(config.TRADING_SYMBOLS)})")
                else:
                    logger.warning(f"⚠️ Análisis inicial falló: {symbol}")
                
                # Pausa entre análisis
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Error en análisis inicial de {symbol}: {e}")
                continue
        
        logger.info(f"🏁 Análisis inicial Merino completado:")
        logger.info(f"   • Total analizado: {completed}/{len(config.TRADING_SYMBOLS)}")
        logger.info(f"   • Señales alta probabilidad: {high_probability_signals}")
        logger.info(f"   • Filosofía: {merino_methodology.PHILOSOPHY['main_principle']}")
        
    except Exception as e:
        logger.error(f"❌ Error en análisis inicial Merino: {e}")

def main():
    """Función principal para ejecutar el Jaime Merino Trading Bot"""
    try:
        print("=" * 80)
        print("🚀 JAIME MERINO TRADING BOT")
        print("📈 Metodología Trading Latino - Análisis Técnico Avanzado")
        print("=" * 80)
        
        # Banner con filosofía de Merino
        print(f"💡 Filosofía: {merino_methodology.PHILOSOPHY['main_principle']}")
        print(f"🎯 Principio: {merino_methodology.PHILOSOPHY['discipline']}")
        print(f"⚠️ Riesgo: {merino_methodology.PHILOSOPHY['risk_motto']}")
        print("=" * 80)
        
        # Mostrar configuración
        config_name = os.environ.get('FLASK_ENV', 'development')
        config_class = merino_config.get(config_name, merino_config['default'])
        
        logger.info(f"🔧 Configuración Merino:")
        logger.info(f"   • Ambiente: {config_name}")
        logger.info(f"   • Símbolos: {config_class.TRADING_SYMBOLS}")
        logger.info(f"   • Timeframe principal: {config_class.TIMEFRAMES['primary']}")
        logger.info(f"   • Intervalo actualización: {config_class.UPDATE_INTERVALS}")
        logger.info(f"   • Gestión riesgo: {config_class.RISK_MANAGEMENT['btc_long_term_pct']}-{config_class.RISK_MANAGEMENT['weekly_charts_pct']}-{config_class.RISK_MANAGEMENT['daily_trading_pct']}-{config_class.RISK_MANAGEMENT['futures_pct']}")
        logger.info(f"   • Puerto: {config_class.PORT}")
        logger.info(f"   • Host: {config_class.HOST}")
        logger.info(f"   • Debug: {config_class.DEBUG}")
        
        # Verificar conexión a Binance
        logger.info("🔍 Verificando conexión a Binance...")
        if binance_service.test_connection():
            logger.info("✅ Conexión a Binance exitosa")
        else:
            logger.warning("⚠️ Conexión a Binance falló - usando modo demo")
        
        # Crear aplicación
        app, socketio, socket_handlers = create_merino_app(config_name)
        
        # Análisis inicial en hilo separado
        logger.info("📊 Iniciando análisis inicial Merino...")
        initial_thread = threading.Thread(
            target=perform_initial_merino_analysis,
            args=(socket_handlers, config_class)
        )
        initial_thread.daemon = True
        initial_thread.start()
        
        # Información de inicio
        print("=" * 80)
        print(f"🌐 Servidor Merino disponible en: http://{config_class.HOST}:{config_class.PORT}")
        print(f"📱 Dashboard: http://localhost:{config_class.PORT}")
        print(f"❤️ Health check: http://localhost:{config_class.PORT}/health")
        print(f"📊 API Símbolos: http://localhost:{config_class.PORT}/api/merino/symbols")
        print(f"🧠 Filosofía: http://localhost:{config_class.PORT}/api/merino/philosophy")
        print(f"🛡️ Gestión Riesgo: http://localhost:{config_class.PORT}/api/merino/risk-management")
        print("=" * 80)
        print("🎯 ¡Jaime Merino Trading Bot iniciado!")
        print("💡 Presiona Ctrl+C para detener")
        print("📚 Metodología: EMAs + ADX + Squeeze Momentum + Volume Profile")
        print("=" * 80)
        
        # Iniciar servidor
        socketio.run(
            app,
            host=config_class.HOST,
            port=config_class.PORT,
            debug=config_class.DEBUG,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ Deteniendo Jaime Merino Bot por solicitud del usuario...")
        print("\n" + "=" * 80)
        print("👋 Gracias por usar Jaime Merino Trading Bot")
        print("📈 Recuerda: 'Es mejor perder una oportunidad que perder dinero'")
        print("=" * 80)
    except Exception as e:
        logger.error(f"❌ Error crítico al iniciar Jaime Merino Bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("👋 Jaime Merino Trading Bot finalizado")

if __name__ == '__main__':
    main()