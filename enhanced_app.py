"""
🚀 Jaime Merino Trading Bot - Enhanced Version for Render
📈 Metodología Trading Latino Avanzada
"""

import os
import sys
import threading
import time
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la aplicación para Render
class RenderConfig:
    """Configuración optimizada para Render"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'jaime-merino-enhanced-2024')
    DEBUG = False
    
    # Configuración específica para Render
    PORT = int(os.environ.get('PORT', 5000))
    HOST = '0.0.0.0'
    
    # Configuración de CORS para Render
    CORS_ORIGINS = ["*"]  # En producción, especifica tu dominio
    
    # Símbolos de trading
    TRADING_SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
        'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT'
    ]
    
    # Intervalos de actualización (optimizados para Render Free Plan)
    UPDATE_INTERVALS = {
        '4h': 1800,    # 30 minutos
        '1h': 900,     # 15 minutos
        '1d': 3600,    # 1 hora
        'realtime': 300  # 5 minutos
    }

# Crear aplicación Flask
app = Flask(__name__)
app.config.from_object(RenderConfig)

# Configurar CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# Configurar SocketIO para Render
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

# Variables globales para datos
trading_data = {}
analysis_active = False

def mock_market_data():
    """
    Genera datos de mercado simulados para demostración
    (Reemplazar con datos reales de Binance cuando se configuren las APIs)
    """
    import random
    import time
    
    symbols = app.config['TRADING_SYMBOLS']
    base_prices = {
        'BTCUSDT': 45000,
        'ETHUSDT': 3000,
        'BNBUSDT': 300,
        'ADAUSDT': 0.50,
        'XRPUSDT': 0.60,
        'SOLUSDT': 100,
        'DOTUSDT': 7,
        'DOGEUSDT': 0.08,
        'AVAXUSDT': 40,
        'MATICUSDT': 1.0
    }
    
    data = {}
    for symbol in symbols:
        base_price = base_prices.get(symbol, 100)
        current_price = base_price * (1 + random.uniform(-0.05, 0.05))
        
        data[symbol] = {
            'symbol': symbol,
            'price': round(current_price, 6),
            'change_24h': round(random.uniform(-10, 10), 2),
            'volume': random.randint(1000000, 100000000),
            'timestamp': int(time.time()),
            
            # Indicadores técnicos simulados
            'indicators': {
                'rsi': round(random.uniform(20, 80), 2),
                'macd': round(random.uniform(-1, 1), 4),
                'ema_20': round(current_price * 0.98, 6),
                'ema_50': round(current_price * 0.95, 6),
                'bollinger_upper': round(current_price * 1.02, 6),
                'bollinger_lower': round(current_price * 0.98, 6),
                'adx': round(random.uniform(20, 60), 2)
            },
            
            # Señales de trading (metodología Jaime Merino)
            'signals': {
                'trend': random.choice(['ALCISTA', 'BAJISTA', 'LATERAL']),
                'strength': random.choice(['FUERTE', 'MODERADA', 'DÉBIL']),
                'recommendation': random.choice(['COMPRA', 'VENTA', 'ESPERAR']),
                'confidence': round(random.uniform(60, 95), 1),
                'entry_point': round(current_price * random.uniform(0.98, 1.02), 6),
                'stop_loss': round(current_price * random.uniform(0.93, 0.97), 6),
                'take_profit': round(current_price * random.uniform(1.03, 1.08), 6)
            }
        }
    
    return data

def analysis_thread():
    """Hilo principal de análisis"""
    global analysis_active, trading_data
    
    logger.info("🚀 Iniciando análisis de mercado - Metodología Jaime Merino")
    
    while analysis_active:
        try:
            # Generar datos actualizados
            trading_data = mock_market_data()
            
            # Emitir datos a todos los clientes conectados
            socketio.emit('market_update', {
                'data': trading_data,
                'timestamp': datetime.now().isoformat(),
                'philosophy': "El arte de tomar dinero de otros legalmente"
            })
            
            logger.info(f"📊 Datos actualizados para {len(trading_data)} símbolos")
            
            # Esperar antes de la siguiente actualización
            time.sleep(app.config['UPDATE_INTERVALS']['realtime'])
            
        except Exception as e:
            logger.error(f"❌ Error en análisis: {e}")
            time.sleep(30)  # Esperar más tiempo en caso de error

# Rutas de la aplicación

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check para Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'app': 'Jaime Merino Enhanced Trading Bot',
        'version': '2.0.0',
        'methodology': 'Trading Latino Avanzado'
    })

@app.route('/api/status')
def api_status():
    """Estado de la API"""
    return jsonify({
        'analysis_active': analysis_active,
        'symbols_count': len(trading_data),
        'last_update': datetime.now().isoformat(),
        'philosophy': "Es mejor perder una oportunidad que perder dinero"
    })

@app.route('/api/data')
def get_market_data():
    """Obtener datos de mercado actuales"""
    return jsonify({
        'success': True,
        'data': trading_data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/symbol/<symbol>')
def get_symbol_data(symbol):
    """Obtener datos de un símbolo específico"""
    if symbol.upper() in trading_data:
        return jsonify({
            'success': True,
            'data': trading_data[symbol.upper()],
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': f'Símbolo {symbol} no encontrado'
        }), 404

# Eventos de SocketIO

@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    logger.info(f"🔗 Cliente conectado: {request.sid}")
    
    # Enviar datos actuales al cliente recién conectado
    emit('market_update', {
        'data': trading_data,
        'timestamp': datetime.now().isoformat(),
        'message': 'Conectado al Bot Jaime Merino - Trading Latino'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    logger.info(f"❌ Cliente desconectado: {request.sid}")

@socketio.on('request_update')
def handle_request_update():
    """Cliente solicita actualización manual"""
    logger.info(f"🔄 Actualización solicitada por: {request.sid}")
    
    # Generar nuevos datos
    global trading_data
    trading_data = mock_market_data()
    
    emit('market_update', {
        'data': trading_data,
        'timestamp': datetime.now().isoformat(),
        'message': 'Datos actualizados manualmente'
    })

@socketio.on('subscribe_symbol')
def handle_subscribe_symbol(data):
    """Suscribirse a un símbolo específico"""
    symbol = data.get('symbol', '').upper()
    logger.info(f"📊 Suscripción a {symbol} por: {request.sid}")
    
    if symbol in trading_data:
        emit('symbol_update', {
            'symbol': symbol,
            'data': trading_data[symbol],
            'timestamp': datetime.now().isoformat()
        })

def start_background_services():
    """Iniciar servicios en segundo plano"""
    global analysis_active
    
    if not analysis_active:
        analysis_active = True
        
        # Iniciar hilo de análisis
        analysis_thread_obj = threading.Thread(target=analysis_thread, daemon=True)
        analysis_thread_obj.start()
        
        logger.info("✅ Servicios de fondo iniciados")

def create_basic_template():
    """Crear template básico si no existe"""
    template_dir = 'templates'
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, 'index.html')
    
    if not os.path.exists(template_path):
        html_content = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Jaime Merino Trading Bot</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
        .header { text-align: center; margin-bottom: 30px; }
        .philosophy { background: #2a2a2a; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .symbols-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .symbol-card { background: #2a2a2a; border-radius: 8px; padding: 20px; border-left: 4px solid #00ff88; }
        .price { font-size: 24px; font-weight: bold; color: #00ff88; }
        .change { font-size: 18px; margin: 10px 0; }
        .positive { color: #00ff88; }
        .negative { color: #ff4444; }
        .indicators { margin-top: 15px; }
        .indicator { display: flex; justify-content: space-between; margin: 5px 0; }
        .signals { background: #3a3a3a; padding: 10px; border-radius: 5px; margin-top: 10px; }
        .status { position: fixed; top: 20px; right: 20px; background: #00ff88; color: #000; padding: 10px; border-radius: 5px; }
        .loading { text-align: center; margin: 50px 0; }
    </style>
</head>
<body>
    <div class="status" id="status">🔴 Desconectado</div>
    
    <div class="header">
        <h1>🚀 Jaime Merino Trading Bot</h1>
        <h2>📈 Metodología Trading Latino Avanzada</h2>
    </div>
    
    <div class="philosophy">
        <h3>💡 Filosofía de Trading</h3>
        <p><strong>"El arte de tomar dinero de otros legalmente"</strong></p>
        <p><strong>"Es mejor perder una oportunidad que perder dinero"</strong></p>
        <p><strong>"Solo operamos con alta probabilidad de éxito"</strong></p>
    </div>
    
    <div class="loading" id="loading">🔄 Conectando al servidor...</div>
    
    <div id="symbols-container" class="symbols-grid" style="display: none;"></div>

    <script>
        const socket = io();
        const statusEl = document.getElementById('status');
        const loadingEl = document.getElementById('loading');
        const containerEl = document.getElementById('symbols-container');

        socket.on('connect', function() {
            statusEl.textContent = '🟢 Conectado';
            statusEl.style.background = '#00ff88';
            loadingEl.style.display = 'none';
            containerEl.style.display = 'grid';
        });

        socket.on('disconnect', function() {
            statusEl.textContent = '🔴 Desconectado';
            statusEl.style.background = '#ff4444';
        });

        socket.on('market_update', function(response) {
            updateMarketData(response.data);
        });

        function updateMarketData(data) {
            containerEl.innerHTML = '';
            
            Object.values(data).forEach(symbol => {
                const card = createSymbolCard(symbol);
                containerEl.appendChild(card);
            });
        }

        function createSymbolCard(symbol) {
            const card = document.createElement('div');
            card.className = 'symbol-card';
            
            const changeClass = symbol.change_24h >= 0 ? 'positive' : 'negative';
            const changeSign = symbol.change_24h >= 0 ? '+' : '';
            
            card.innerHTML = `
                <h3>${symbol.symbol}</h3>
                <div class="price">$${symbol.price}</div>
                <div class="change ${changeClass}">${changeSign}${symbol.change_24h}%</div>
                
                <div class="indicators">
                    <div class="indicator">
                        <span>RSI:</span>
                        <span>${symbol.indicators.rsi}</span>
                    </div>
                    <div class="indicator">
                        <span>MACD:</span>
                        <span>${symbol.indicators.macd}</span>
                    </div>
                    <div class="indicator">
                        <span>ADX:</span>
                        <span>${symbol.indicators.adx}</span>
                    </div>
                </div>
                
                <div class="signals">
                    <div><strong>Tendencia:</strong> ${symbol.signals.trend}</div>
                    <div><strong>Recomendación:</strong> ${symbol.signals.recommendation}</div>
                    <div><strong>Confianza:</strong> ${symbol.signals.confidence}%</div>
                </div>
            `;
            
            return card;
        }

        // Solicitar actualización cada 30 segundos
        setInterval(() => {
            socket.emit('request_update');
        }, 30000);
    </script>
</body>
</html>'''
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info("✅ Template básico creado")

if __name__ == '__main__':
    logger.info("🚀 Iniciando Jaime Merino Enhanced Trading Bot")
    logger.info("📈 Metodología: Trading Latino Avanzado")
    
    # Crear template si no existe
    create_basic_template()
    
    # Inicializar datos
    trading_data = mock_market_data()
    
    # Iniciar servicios de fondo
    start_background_services()
    
    logger.info(f"🌍 Servidor iniciando en {app.config['HOST']}:{app.config['PORT']}")
    
    # Ejecutar aplicación (configuración específica para Render)
    socketio.run(
        app,
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'],
        allow_unsafe_werkzeug=True  # Necesario para Render
    )