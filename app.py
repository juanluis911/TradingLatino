"""
Aplicación principal de Trading Analysis - Metodología Jaime Merino
"""
import os
import threading
import time
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from config import config, Config
from utils.logger import setup_logger, app_logger
from websocket.socket_handlers import SocketHandlers
from services.analysis_service import analysis_service
from services.binance_service import binance_service

# Configurar logging
logger = app_logger

def create_app(config_name=None):
    """
    Factory function para crear la aplicación Flask
    
    Args:
        config_name: Nombre de la configuración a usar
        
    Returns:
        Tupla (app, socketio)
    """
    # Determinar configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Crear aplicación Flask
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))
    
    # Inicializar SocketIO
    socketio = SocketIO(
        app,
        cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'],
        async_mode=app.config['SOCKETIO_ASYNC_MODE'],
        logger=False,  # Usar nuestro logger personalizado
        engineio_logger=False
    )
    
    # Configurar handlers de Socket.IO
    socket_handlers = SocketHandlers(socketio)
    socket_handlers.register_handlers()
    
    # Registrar rutas
    register_routes(app)
    
    # Configurar servicios de fondo
    setup_background_services(socketio, socket_handlers)
    
    logger.info("🚀 Aplicación Flask creada exitosamente")
    return app, socketio, socket_handlers

def register_routes(app):
    """
    Registra las rutas de la aplicación
    
    Args:
        app: Instancia de Flask
    """
    
    @app.route('/')
    def index():
        """Página principal con el dashboard de trading"""
        try:
            return render_template('index.html')
        except Exception as e:
            logger.error(f"❌ Error sirviendo página principal: {e}")
            return f"Error cargando página: {str(e)}", 500
    
    @app.route('/health')
    def health_check():
        """Endpoint de salud para monitoreo"""
        try:
            # Verificar conexión a Binance
            binance_status = binance_service.test_connection()
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'binance': 'connected' if binance_status else 'disconnected',
                    'analysis': 'active',
                    'websocket': 'active'
                },
                'config': {
                    'symbols': Config.TRADING_SYMBOLS,
                    'update_interval': Config.UPDATE_INTERVAL
                }
            })
        except Exception as e:
            logger.error(f"❌ Error en health check: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/api/symbols')
    def get_symbols():
        """API endpoint para obtener símbolos soportados"""
        return jsonify({
            'symbols': Config.TRADING_SYMBOLS,
            'count': len(Config.TRADING_SYMBOLS),
            'update_interval': Config.UPDATE_INTERVAL
        })
    
    @app.route('/api/analysis/<symbol>')
    def get_analysis(symbol):
        """
        API endpoint para obtener análisis de un símbolo específico
        
        Args:
            symbol: Símbolo a analizar
        """
        try:
            symbol = symbol.upper()
            
            if symbol not in Config.TRADING_SYMBOLS:
                return jsonify({
                    'error': f'Símbolo {symbol} no soportado',
                    'supported_symbols': Config.TRADING_SYMBOLS
                }), 400
            
            # Realizar análisis
            analysis = analysis_service.analyze_symbol(symbol)
            
            if analysis:
                return jsonify({
                    'success': True,
                    'symbol': symbol,
                    'data': analysis.to_dict(),
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'symbol': symbol,
                    'error': 'No se pudo completar el análisis',
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        except Exception as e:
            logger.error(f"❌ Error en API análisis para {symbol}: {e}")
            return jsonify({
                'success': False,
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Maneja errores 404"""
        return jsonify({
            'error': 'Endpoint no encontrado',
            'available_endpoints': [
                '/',
                '/health',
                '/api/symbols',
                '/api/analysis/<symbol>'
            ]
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores internos"""
        logger.error(f"❌ Error interno del servidor: {error}")
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Consulte los logs para más detalles'
        }), 500

def setup_background_services(socketio, socket_handlers):
    """
    Configura los servicios de fondo para actualizaciones automáticas
    
    Args:
        socketio: Instancia de SocketIO
        socket_handlers: Manejadores de Socket.IO
    """
    
    def auto_update_analysis():
        """
        Servicio de fondo para actualizar análisis automáticamente
        """
        logger.info("🔄 Servicio de actualización automática iniciado")
        
        while True:
            try:
                # Esperar el intervalo configurado
                time.sleep(Config.UPDATE_INTERVAL)
                
                # Solo actualizar si hay clientes conectados
                if socket_handlers.get_connected_clients_count() > 0:
                    logger.info(f"🔄 Iniciando actualización automática para {len(Config.TRADING_SYMBOLS)} símbolos")
                    
                    for symbol in Config.TRADING_SYMBOLS:
                        try:
                            # Análisis automático
                            analysis = analysis_service.analyze_symbol(symbol)
                            
                            if analysis:
                                analysis_dict = analysis.to_dict()
                                socket_handlers.broadcast_analysis_update(symbol, analysis_dict)
                                
                                # Pequeña pausa entre símbolos
                                time.sleep(2)
                            else:
                                logger.warning(f"⚠️ Análisis automático falló para {symbol}")
                                
                        except Exception as e:
                            logger.error(f"❌ Error en actualización automática de {symbol}: {e}")
                            continue
                    
                    logger.info("✅ Actualización automática completada")
                else:
                    logger.debug("📭 No hay clientes conectados, saltando actualización automática")
                    
            except Exception as e:
                logger.error(f"❌ Error en servicio de actualización automática: {e}")
                time.sleep(60)  # Esperar un minuto antes de reintentar
    
    def cleanup_service():
        """
        Servicio de limpieza periódica
        """
        logger.info("🧹 Servicio de limpieza iniciado")
        
        while True:
            try:
                # Limpiar cada 1 hora
                time.sleep(3600)
                
                # Limpiar cache de análisis si es muy grande
                if len(socket_handlers.analysis_cache) > 50:
                    socket_handlers.clear_analysis_cache()
                    logger.info("🗑️ Cache de análisis limpiado por tamaño")
                
                # Log de estadísticas
                logger.info(f"📊 Estadísticas: {socket_handlers.get_connected_clients_count()} clientes, "
                          f"{len(socket_handlers.analysis_cache)} análisis en cache")
                
            except Exception as e:
                logger.error(f"❌ Error en servicio de limpieza: {e}")
    
    # Iniciar servicios de fondo
    update_thread = threading.Thread(target=auto_update_analysis)
    update_thread.daemon = True
    update_thread.start()
    
    cleanup_thread = threading.Thread(target=cleanup_service)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    logger.info("✅ Servicios de fondo iniciados")

def main():
    """Función principal para ejecutar la aplicación"""
    try:
        logger.info("🚀 Iniciando aplicación de Trading Analysis")
        logger.info("📈 Metodología Jaime Merino - Análisis Técnico Avanzado")
        logger.info("=" * 60)
        
        # Mostrar configuración
        logger.info(f"🔧 Configuración:")
        logger.info(f"   • Símbolos: {Config.TRADING_SYMBOLS}")
        logger.info(f"   • Intervalo actualización: {Config.UPDATE_INTERVAL} segundos")
        logger.info(f"   • Puerto: {Config.PORT}")
        logger.info(f"   • Host: {Config.HOST}")
        logger.info(f"   • Debug: {Config.DEBUG}")
        
        # Verificar conexión a Binance
        logger.info("🔍 Verificando conexión a Binance...")
        if binance_service.test_connection():
            logger.info("✅ Conexión a Binance exitosa")
        else:
            logger.warning("⚠️ Conexión a Binance falló - usando modo demo")
        
        # Crear aplicación
        app, socketio, socket_handlers = create_app()
        
        # Análisis inicial
        logger.info("📊 Realizando análisis inicial...")
        initial_thread = threading.Thread(
            target=perform_initial_analysis,
            args=(socket_handlers,)
        )
        initial_thread.daemon = True
        initial_thread.start()
        
        # Información de inicio
        logger.info("=" * 60)
        logger.info(f"🌐 Servidor disponible en: http://{Config.HOST}:{Config.PORT}")
        logger.info(f"📱 Dashboard: http://localhost:{Config.PORT}")
        logger.info(f"❤️ Health check: http://localhost:{Config.PORT}/health")
        logger.info(f"📊 API: http://localhost:{Config.PORT}/api/symbols")
        logger.info("=" * 60)
        logger.info("🎯 ¡Servidor de análisis técnico iniciado!")
        logger.info("💡 Presiona Ctrl+C para detener")
        
        # Iniciar servidor
        socketio.run(
            app,
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ Deteniendo servidor por solicitud del usuario...")
    except Exception as e:
        logger.error(f"❌ Error crítico al iniciar aplicación: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("👋 Aplicación de Trading Analysis finalizada")

def perform_initial_analysis(socket_handlers):
    """
    Realiza análisis inicial para todos los símbolos
    
    Args:
        socket_handlers: Manejadores de Socket.IO
    """
    try:
        logger.info("🔄 Iniciando análisis inicial de todos los símbolos...")
        
        # Esperar un poco para que el servidor se establezca
        time.sleep(5)
        
        completed = 0
        for symbol in Config.TRADING_SYMBOLS:
            try:
                analysis = analysis_service.analyze_symbol(symbol)
                
                if analysis:
                    analysis_dict = analysis.to_dict()
                    socket_handlers.analysis_cache[symbol] = analysis_dict
                    completed += 1
                    logger.info(f"✅ Análisis inicial completado: {symbol} ({completed}/{len(Config.TRADING_SYMBOLS)})")
                else:
                    logger.warning(f"⚠️ Análisis inicial falló: {symbol}")
                
                # Pausa entre análisis
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error en análisis inicial de {symbol}: {e}")
                continue
        
        logger.info(f"🏁 Análisis inicial completado: {completed}/{len(Config.TRADING_SYMBOLS)} símbolos")
        
    except Exception as e:
        logger.error(f"❌ Error en análisis inicial: {e}")

if __name__ == '__main__':
    main()