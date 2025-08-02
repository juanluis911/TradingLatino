"""
🚀 Jaime Merino Trading Bot - Enhanced Version MINIMAL
📈 Metodología Trading Latino Avanzada
Versión optimizada para evitar errores de dependencias
"""

import os
import sys
import threading
import time
import json
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

# Importaciones opcionales para evitar errores
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("⚠️ flask-cors no disponible - CORS básico usado")

try:
    import ujson as json_lib
    print("✅ ujson disponible")
except ImportError:
    import json as json_lib
    print("✅ json nativo usado")

try:
    import numpy as np
    import pandas as pd
    ADVANCED_ANALYSIS = True
    print("✅ numpy y pandas disponibles")
except ImportError:
    ADVANCED_ANALYSIS = False
    print("⚠️ Análisis básico usado (numpy/pandas no disponibles)")

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MerinoConfig:
    """Configuración optimizada para máxima compatibilidad"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'jaime-merino-enhanced-2024-secure')
    DEBUG = False
    
    # Configuración para Render
    PORT = int(os.environ.get('PORT', 5000))
    HOST = '0.0.0.0'
    
    # Símbolos principales
    TRADING_SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT'
    ]
    
    # Intervalos conservadores
    UPDATE_INTERVAL = 300  # 5 minutos

# Crear aplicación Flask
app = Flask(__name__)
app.config.from_object(MerinoConfig)

# Configurar CORS si está disponible
if CORS_AVAILABLE:
    CORS(app, origins="*")
else:
    # CORS básico manual
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

# Configurar SocketIO con configuración muy básica
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',  # Más compatible que eventlet
    logger=False,
    engineio_logger=False
)

# Variables globales
trading_data = {}
analysis_active = False
connected_clients = 0

def generate_mock_data():
    """Genera datos simulados básicos"""
    import random
    import time
    
    symbols = app.config['TRADING_SYMBOLS']
    base_prices = {
        'BTCUSDT': 45000,
        'ETHUSDT': 3000,
        'BNBUSDT': 300,
        'ADAUSDT': 0.50,
        'XRPUSDT': 0.60
    }
    
    data = {}
    
    for symbol in symbols:
        base_price = base_prices.get(symbol, 100)
        
        # Variación realista del precio
        price_change = random.uniform(-0.03, 0.03)  # ±3%
        current_price = base_price * (1 + price_change)
        
        # Indicadores técnicos básicos
        rsi = random.uniform(30, 70)
        trend = "ALCISTA" if price_change > 0.01 else "BAJISTA" if price_change < -0.01 else "LATERAL"
        
        # Recomendación basada en RSI y tendencia
        if rsi < 30 and trend != "BAJISTA":
            recommendation = "COMPRA"
            confidence = random.uniform(75, 90)
        elif rsi > 70 and trend != "ALCISTA":
            recommendation = "VENTA"
            confidence = random.uniform(75, 90)
        else:
            recommendation = "ESPERAR"
            confidence = random.uniform(60, 75)
        
        data[symbol] = {
            'symbol': symbol,
            'price': round(current_price, 6),
            'change_24h': round(price_change * 100, 2),
            'volume': random.randint(1000000, 50000000),
            'timestamp': int(time.time()),
            
            'indicators': {
                'rsi': round(rsi, 2),
                'trend': trend,
                'strength': random.choice(['FUERTE', 'MODERADA', 'DÉBIL'])
            },
            
            'signals': {
                'recommendation': recommendation,
                'confidence': round(confidence, 1),
                'entry_point': round(current_price * random.uniform(0.99, 1.01), 6),
                'philosophy': "Es mejor perder una oportunidad que perder dinero"
            }
        }
    
    return data

def analysis_worker():
    """Hilo de trabajo para análisis"""
    global analysis_active, trading_data, connected_clients
    
    logger.info("🚀 Iniciando análisis Jaime Merino")
    
    while analysis_active:
        try:
            if connected_clients > 0:
                # Solo generar datos si hay clientes conectados
                trading_data = generate_mock_data()
                
                # Emitir a todos los clientes
                socketio.emit('market_update', {
                    'data': trading_data,
                    'timestamp': datetime.now().isoformat(),
                    'philosophy': "El arte de tomar dinero de otros legalmente",
                    'connected_clients': connected_clients
                })
                
                logger.info(f"📊 Datos enviados a {connected_clients} clientes")
            
            # Pausa entre actualizaciones
            time.sleep(app.config['UPDATE_INTERVAL'])
            
        except Exception as e:
            logger.error(f"❌ Error en análisis: {e}")
            time.sleep(60)  # Pausa más larga en caso de error

# Rutas principales

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
        'version': '2.0.1',
        'methodology': 'Trading Latino Avanzado',
        'connected_clients': connected_clients,
        'advanced_analysis': ADVANCED_ANALYSIS,
        'cors_enabled': CORS_AVAILABLE
    })

@app.route('/api/data')
def get_data():
    """API para obtener datos actuales"""
    return jsonify({
        'success': True,
        'data': trading_data,
        'timestamp': datetime.now().isoformat(),
        'philosophy': "Solo operamos con alta probabilidad de éxito"
    })

@app.route('/api/symbol/<symbol>')
def get_symbol(symbol):
    """Datos de símbolo específico"""
    symbol = symbol.upper()
    if symbol in trading_data:
        return jsonify({
            'success': True,
            'data': trading_data[symbol],
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': f'Símbolo {symbol} no encontrado'
        }), 404

# Eventos SocketIO

@socketio.on('connect')
def on_connect():
    """Cliente conectado"""
    global connected_clients
    connected_clients += 1
    
    logger.info(f"🔗 Cliente conectado: {request.sid} (Total: {connected_clients})")
    
    # Enviar datos inmediatos
    if trading_data:
        emit('market_update', {
            'data': trading_data,
            'timestamp': datetime.now().isoformat(),
            'message': 'Bienvenido al Bot Jaime Merino',
            'philosophy': "Operamos contra el 90% que pierde dinero"
        })

@socketio.on('disconnect')
def on_disconnect():
    """Cliente desconectado"""
    global connected_clients
    connected_clients = max(0, connected_clients - 1)
    
    logger.info(f"❌ Cliente desconectado: {request.sid} (Total: {connected_clients})")

@socketio.on('manual_update')
def on_manual_update():
    """Actualización manual solicitada"""
    logger.info(f"🔄 Actualización manual por: {request.sid}")
    
    # Generar datos frescos
    global trading_data
    trading_data = generate_mock_data()
    
    emit('market_update', {
        'data': trading_data,
        'timestamp': datetime.now().isoformat(),
        'message': 'Datos actualizados manualmente'
    })

def create_minimal_template():
    """Crear template HTML mínimo"""
    template_dir = 'templates'
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, 'index.html')
    
    if not os.path.exists(template_path):
        html_content = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Jaime Merino Trading Bot Enhanced</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0, 255, 136, 0.1);
            border-bottom: 2px solid #00ff88;
        }
        .philosophy {
            background: rgba(255, 255, 255, 0.05);
            margin: 20px;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #00ff88;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            background: rgba(0, 0, 0, 0.3);
            font-size: 14px;
        }
        .symbols-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .symbol-card {
            background: linear-gradient(145deg, #2a2a2a, #1e1e1e);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #333;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease;
        }
        .symbol-card:hover {
            transform: translateY(-5px);
            border-color: #00ff88;
        }
        .symbol-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .symbol-name {
            font-size: 18px;
            font-weight: bold;
            color: #00ff88;
        }
        .price {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .change {
            font-size: 16px;
            font-weight: bold;
        }
        .positive { color: #00ff88; }
        .negative { color: #ff4444; }
        .neutral { color: #ffaa00; }
        .indicators {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #333;
        }
        .indicator-row {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 14px;
        }
        .signals {
            background: rgba(0, 255, 136, 0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .recommendation {
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            padding: 8px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .compra { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
        .venta { background: rgba(255, 68, 68, 0.2); color: #ff4444; }
        .esperar { background: rgba(255, 170, 0, 0.2); color: #ffaa00; }
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 18px;
        }
        .spinner {
            border: 3px solid #333;
            border-top: 3px solid #00ff88;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .update-btn {
            background: #00ff88;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s ease;
        }
        .update-btn:hover {
            background: #00cc6a;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Jaime Merino Trading Bot</h1>
        <h2>📈 Metodología Trading Latino Avanzada</h2>
        <p>Versión Enhanced - Optimizada para Render</p>
    </div>
    
    <div class="status-bar">
        <div id="connection-status">🔴 Conectando...</div>
        <div id="last-update">Última actualización: --</div>
        <button class="update-btn" onclick="requestUpdate()">🔄 Actualizar</button>
    </div>
    
    <div class="philosophy">
        <h3>💡 Filosofía de Trading Jaime Merino</h3>
        <p><strong>"El arte de tomar dinero de otros legalmente"</strong></p>
        <p><strong>"Es mejor perder una oportunidad que perder dinero"</strong></p>
        <p><strong>"Solo operamos con alta probabilidad de éxito"</strong></p>
        <p><strong>"Operamos contra el 90% que pierde dinero"</strong></p>
    </div>
    
    <div class="loading" id="loading">
        <div class="spinner"></div>
        <p>Conectando al servidor de análisis...</p>
    </div>
    
    <div id="symbols-container" class="symbols-grid" style="display: none;"></div>

    <script>
        const socket = io();
        let lastUpdateTime = null;

        // Elementos DOM
        const statusEl = document.getElementById('connection-status');
        const updateEl = document.getElementById('last-update');
        const loadingEl = document.getElementById('loading');
        const containerEl = document.getElementById('symbols-container');

        // Eventos de conexión
        socket.on('connect', function() {
            statusEl.innerHTML = '🟢 Conectado';
            statusEl.style.color = '#00ff88';
            console.log('✅ Conectado al servidor');
        });

        socket.on('disconnect', function() {
            statusEl.innerHTML = '🔴 Desconectado';
            statusEl.style.color = '#ff4444';
            console.log('❌ Desconectado del servidor');
        });

        // Recibir datos de mercado
        socket.on('market_update', function(response) {
            console.log('📊 Datos recibidos:', response);
            updateMarketData(response.data);
            lastUpdateTime = new Date(response.timestamp);
            updateEl.innerHTML = `Última actualización: ${lastUpdateTime.toLocaleTimeString()}`;
            
            loadingEl.style.display = 'none';
            containerEl.style.display = 'grid';
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
            
            const changeClass = symbol.change_24h > 0 ? 'positive' : 
                               symbol.change_24h < 0 ? 'negative' : 'neutral';
            const changeSign = symbol.change_24h > 0 ? '+' : '';
            
            const recClass = symbol.signals.recommendation.toLowerCase();
            
            card.innerHTML = `
                <div class="symbol-header">
                    <div class="symbol-name">${symbol.symbol}</div>
                    <div style="font-size: 12px; color: #888;">
                        ${new Date(symbol.timestamp * 1000).toLocaleTimeString()}
                    </div>
                </div>
                
                <div class="price">$${symbol.price.toLocaleString()}</div>
                <div class="change ${changeClass}">
                    ${changeSign}${symbol.change_24h}% (24h)
                </div>
                
                <div class="indicators">
                    <div class="indicator-row">
                        <span>RSI:</span>
                        <span>${symbol.indicators.rsi}</span>
                    </div>
                    <div class="indicator-row">
                        <span>Tendencia:</span>
                        <span>${symbol.indicators.trend}</span>
                    </div>
                    <div class="indicator-row">
                        <span>Fuerza:</span>
                        <span>${symbol.indicators.strength}</span>
                    </div>
                </div>
                
                <div class="signals">
                    <div class="recommendation ${recClass}">
                        ${symbol.signals.recommendation}
                    </div>
                    <div style="text-align: center; margin: 10px 0;">
                        <strong>Confianza: ${symbol.signals.confidence}%</strong>
                    </div>
                    <div style="font-size: 12px; text-align: center; color: #888;">
                        Entrada: $${symbol.signals.entry_point.toLocaleString()}
                    </div>
                </div>
            `;
            
            return card;
        }

        function requestUpdate() {
            socket.emit('manual_update');
            console.log('🔄 Actualización manual solicitada');
        }

        // Auto-refresh cada 5 minutos
        setInterval(requestUpdate, 300000);
    </script>
</body>
</html>'''
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info("✅ Template HTML creado")

def start_services():
    """Iniciar servicios de fondo"""
    global analysis_active
    
    if not analysis_active:
        analysis_active = True
        
        # Generar datos iniciales
        global trading_data
        trading_data = generate_mock_data()
        
        # Iniciar hilo de análisis
        worker_thread = threading.Thread(target=analysis_worker, daemon=True)
        worker_thread.start()
        
        logger.info("✅ Servicios iniciados")

if __name__ == '__main__':
    logger.info("🚀 Iniciando Jaime Merino Enhanced Trading Bot")
    logger.info(f"🐍 Python: {sys.version}")
    logger.info(f"📊 Análisis avanzado: {ADVANCED_ANALYSIS}")
    logger.info(f"🌐 CORS: {CORS_AVAILABLE}")
    
    # Crear template
    create_minimal_template()
    
    # Iniciar servicios
    start_services()
    
    logger.info(f"🌍 Servidor iniciando en {app.config['HOST']}:{app.config['PORT']}")
    
    # Ejecutar aplicación
    socketio.run(
        app,
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'],
        allow_unsafe_werkzeug=True
    )