"""
🚀 Jaime Merino Trading Bot - SIN PARPADEO + DATOS REALES
📈 Actualización suave y precios más realistas
"""

import os
import sys
import json
import time
import random
import threading
import requests
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Importar SocketIO con manejo de errores
try:
    from flask_socketio import SocketIO, emit
    SOCKETIO_AVAILABLE = True
    print("✅ SocketIO disponible")
except ImportError:
    SOCKETIO_AVAILABLE = False
    print("⚠️ SocketIO no disponible - modo básico")

print("🚀 Iniciando Jaime Merino Trading Bot")
print(f"🐍 Python: {sys.version}")
print(f"📡 SocketIO: {SOCKETIO_AVAILABLE}")

# Configuración de Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'jaime-merino-2024')

# Configurar SocketIO si está disponible
if SOCKETIO_AVAILABLE:
    socketio = SocketIO(app, cors_allowed_origins="*")
else:
    socketio = None

# Variables globales
trading_data = {}
clients_connected = 0
server_start_time = datetime.now()
last_prices = {}

# Datos base más realistas
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']

# Precios base más actuales
BASE_PRICES = {
    'BTCUSDT': 43500,  # Más cercano al precio real actual
    'ETHUSDT': 2920,
    'BNBUSDT': 285,
    'ADAUSDT': 0.48,
    'XRPUSDT': 0.58
}

def get_real_price_reference():
    """Intenta obtener precios reales de APIs públicas"""
    try:
        # API pública de CoinGecko (sin necesidad de API key)
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,cardano,ripple&vs_currencies=usd',
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'BTCUSDT': data.get('bitcoin', {}).get('usd', BASE_PRICES['BTCUSDT']),
                'ETHUSDT': data.get('ethereum', {}).get('usd', BASE_PRICES['ETHUSDT']),
                'BNBUSDT': data.get('binancecoin', {}).get('usd', BASE_PRICES['BNBUSDT']),
                'ADAUSDT': data.get('cardano', {}).get('usd', BASE_PRICES['ADAUSDT']),
                'XRPUSDT': data.get('ripple', {}).get('usd', BASE_PRICES['XRPUSDT'])
            }
    except Exception as e:
        print(f"⚠️ No se pudo obtener precios reales: {e}")
    
    return BASE_PRICES

def generate_trading_data():
    """Genera datos de trading más realistas"""
    global last_prices
    
    # Intentar obtener precios reales
    real_prices = get_real_price_reference()
    
    data = {}
    
    for symbol in SYMBOLS:
        # Usar precio real como base
        base_price = real_prices.get(symbol, BASE_PRICES[symbol])
        
        # Si tenemos precio anterior, hacer variación más suave
        if symbol in last_prices:
            # Variación muy pequeña para simular movimiento real
            change_factor = random.uniform(-0.005, 0.005)  # ±0.5%
            current_price = last_prices[symbol] * (1 + change_factor)
        else:
            # Primera vez, usar precio base con pequeña variación
            change_factor = random.uniform(-0.02, 0.02)  # ±2%
            current_price = base_price * (1 + change_factor)
        
        # Calcular cambio en 24h más realista
        change_24h = ((current_price - base_price) / base_price) * 100
        
        # RSI más estable
        previous_rsi = last_prices.get(f"{symbol}_rsi", random.uniform(35, 65))
        rsi = previous_rsi + random.uniform(-3, 3)  # Cambio gradual
        rsi = max(15, min(85, rsi))  # Límites realistas
        
        # MACD calculado como proporción del precio
        macd = (current_price - base_price) * random.uniform(0.001, 0.003)
        
        # Determinar señal con lógica más sofisticada
        if rsi < 25 and macd > 0 and change_24h < -2:
            signal = "COMPRA FUERTE"
            confidence = random.uniform(85, 95)
            color = "success"
        elif rsi > 75 and macd < 0 and change_24h > 2:
            signal = "VENTA FUERTE" 
            confidence = random.uniform(85, 95)
            color = "danger"
        elif rsi < 35 and change_24h < 0:
            signal = "COMPRA"
            confidence = random.uniform(70, 85)
            color = "success"
        elif rsi > 65 and change_24h > 0:
            signal = "VENTA"
            confidence = random.uniform(70, 85)
            color = "warning"
        else:
            signal = "ESPERAR"
            confidence = random.uniform(55, 75)
            color = "secondary"
        
        # Almacenar precios para próxima iteración
        last_prices[symbol] = current_price
        last_prices[f"{symbol}_rsi"] = rsi
        
        data[symbol] = {
            'symbol': symbol,
            'price': round(current_price, 8),
            'change_24h': round(change_24h, 2),
            'volume': random.randint(50000000, 200000000),  # Volúmenes más realistas
            'rsi': round(rsi, 1),
            'macd': round(macd, 6),
            'signal': signal,
            'confidence': round(confidence, 1),
            'color': color,
            'timestamp': int(time.time()),
            'last_update': datetime.now().strftime('%H:%M:%S'),
            'trend': 'ALCISTA' if change_24h > 0 else 'BAJISTA' if change_24h < -1 else 'LATERAL'
        }
    
    return data

def background_worker():
    """Hilo de trabajo con intervalos más largos"""
    global trading_data, clients_connected
    
    print("🔄 Iniciando worker de análisis con intervalos optimizados...")
    
    while True:
        try:
            # Generar nuevos datos
            trading_data = generate_trading_data()
            
            # Emitir datos si hay SocketIO y clientes
            if SOCKETIO_AVAILABLE and socketio and clients_connected > 0:
                socketio.emit('data_update', {
                    'data': trading_data,
                    'timestamp': datetime.now().isoformat(),
                    'clients': clients_connected,
                    'philosophy': "El arte de tomar dinero de otros legalmente",
                    'update_type': 'background'
                })
                print(f"📊 Datos enviados a {clients_connected} clientes")
            
            # Pausa MÁS LARGA para evitar parpadeo
            time.sleep(120)  # 2 minutos en lugar de 30 segundos
            
        except Exception as e:
            print(f"❌ Error en worker: {e}")
            time.sleep(180)  # 3 minutos en caso de error

# Rutas principales

@app.route('/')
def home():
    """Página principal"""
    global trading_data
    
    try:
        # Generar datos iniciales si no existen
        if not trading_data:
            trading_data = generate_trading_data()
        
        return render_template('index.html', 
                             symbols_data=trading_data,
                             server_time=datetime.now().strftime('%H:%M:%S'),
                             socketio_enabled=SOCKETIO_AVAILABLE)
    except Exception as e:
        print(f"❌ Error en ruta /: {e}")
        return f"""
        <h1>🚀 Jaime Merino Trading Bot</h1>
        <p>Error cargando template: {str(e)}</p>
        <p>📊 <a href="/api/data">Ver datos JSON</a></p>
        <p>💡 <a href="/health">Health Check</a></p>
        """

@app.route('/health')
def health():
    """Health check mejorado"""
    uptime = datetime.now() - server_start_time
    
    return jsonify({
        'status': 'healthy',
        'app': 'Jaime Merino Trading Bot',
        'version': '2.1.0',
        'uptime_seconds': int(uptime.total_seconds()),
        'socketio_enabled': SOCKETIO_AVAILABLE,
        'clients_connected': clients_connected,
        'symbols_tracked': len(SYMBOLS),
        'last_data_update': trading_data.get('BTCUSDT', {}).get('last_update', 'never'),
        'real_prices_enabled': True,
        'smooth_updates': True,
        'timestamp': datetime.now().isoformat(),
        'philosophy': "Es mejor perder una oportunidad que perder dinero"
    })

@app.route('/api/data')
def api_data():
    """API de datos mejorada"""
    global trading_data
    
    if not trading_data:
        trading_data = generate_trading_data()
    
    return jsonify({
        'success': True,
        'data': trading_data,
        'timestamp': datetime.now().isoformat(),
        'data_source': 'hybrid_real_simulated',
        'update_interval': '120_seconds',
        'philosophy': "Solo operamos con alta probabilidad de éxito"
    })

@app.route('/api/symbol/<symbol>')
def api_symbol(symbol):
    """API para símbolo específico"""
    symbol = symbol.upper()
    if symbol in trading_data:
        return jsonify({
            'success': True,
            'symbol': symbol,
            'data': trading_data[symbol],
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': f'Símbolo {symbol} no encontrado',
            'available_symbols': list(trading_data.keys())
        }), 404

# Eventos SocketIO optimizados
if SOCKETIO_AVAILABLE:
    @socketio.on('connect')
    def on_connect():
        global clients_connected
        clients_connected += 1
        print(f"🔗 Cliente conectado. Total: {clients_connected}")
        
        # Enviar datos inmediatos
        emit('data_update', {
            'data': trading_data,
            'timestamp': datetime.now().isoformat(),
            'message': 'Conectado al Jaime Merino Bot',
            'philosophy': "Operamos contra el 90% que pierde dinero",
            'update_type': 'initial'
        })
    
    @socketio.on('disconnect')
    def on_disconnect():
        global clients_connected
        clients_connected = max(0, clients_connected - 1)
        print(f"❌ Cliente desconectado. Total: {clients_connected}")
    
    @socketio.on('refresh_data')
    def on_refresh():
        global trading_data
        trading_data = generate_trading_data()
        emit('data_update', {
            'data': trading_data,
            'timestamp': datetime.now().isoformat(),
            'message': 'Datos actualizados manualmente',
            'update_type': 'manual'
        })

def create_smooth_template():
    """Template con actualización suave (sin parpadeo)"""
    template_dir = 'templates'
    os.makedirs(template_dir, exist_ok=True)
    
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Jaime Merino Trading Bot</title>
    {% if socketio_enabled %}
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.js"></script>
    {% endif %}
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
            line-height: 1.6;
        }
        
        .header {
            text-align: center;
            padding: 2rem;
            background: rgba(0, 255, 136, 0.1);
            border-bottom: 2px solid #00ff88;
            margin-bottom: 2rem;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            font-size: 1.2rem;
            color: #00ff88;
            margin-bottom: 1rem;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ff88;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .philosophy {
            background: rgba(255, 215, 0, 0.1);
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 12px;
            padding: 2rem;
            margin: 2rem;
            text-align: center;
        }
        
        .philosophy h3 {
            color: #ffd700;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .philosophy p {
            font-size: 1.1rem;
            margin: 0.5rem 0;
            font-style: italic;
            color: #ffd700;
        }
        
        .controls {
            text-align: center;
            margin: 2rem;
        }
        
        .btn {
            background: #00ff88;
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            margin: 0 10px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            background: #00cc6a;
            transform: translateY(-2px);
        }
        
        .symbols-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .symbol-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
            /* TRANSICIÓN SUAVE PARA EVITAR PARPADEO */
            transition: all 0.5s ease;
        }
        
        .symbol-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #00ff88, #00ccff);
        }
        
        .symbol-card:hover {
            transform: translateY(-5px);
            border-color: #00ff88;
            box-shadow: 0 10px 25px rgba(0, 255, 136, 0.2);
        }
        
        .symbol-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .symbol-name {
            font-size: 1.3rem;
            font-weight: bold;
            color: #00ff88;
        }
        
        .last-update {
            font-size: 0.8rem;
            color: #888;
        }
        
        .price-section {
            margin: 1.5rem 0;
        }
        
        .price {
            font-size: 2rem;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            color: #fff;
            margin-bottom: 0.5rem;
            /* TRANSICIÓN SUAVE PARA CAMBIOS DE PRECIO */
            transition: color 0.3s ease;
        }
        
        .change {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            /* TRANSICIÓN SUAVE */
            transition: color 0.3s ease;
        }
        
        .positive { color: #00ff88; }
        .negative { color: #ff4757; }
        .neutral { color: #ffa502; }
        
        .indicators {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .indicator {
            text-align: center;
            padding: 0.8rem;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            /* TRANSICIÓN SUAVE */
            transition: background 0.3s ease;
        }
        
        .indicator-label {
            font-size: 0.8rem;
            color: #888;
            margin-bottom: 0.3rem;
        }
        
        .indicator-value {
            font-size: 1.1rem;
            font-weight: bold;
            color: #00ccff;
            /* TRANSICIÓN SUAVE */
            transition: color 0.3s ease;
        }
        
        .signal-section {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            margin-top: 1.5rem;
            /* TRANSICIÓN SUAVE */
            transition: all 0.3s ease;
        }
        
        .signal {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            border-radius: 8px;
            /* TRANSICIÓN SUAVE */
            transition: all 0.3s ease;
        }
        
        .signal.success { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
        .signal.danger { background: rgba(255, 71, 87, 0.2); color: #ff4757; }
        .signal.warning { background: rgba(255, 165, 2, 0.2); color: #ffa502; }
        .signal.secondary { background: rgba(128, 128, 128, 0.2); color: #888; }
        
        .confidence {
            font-size: 1rem;
            color: #00ccff;
            margin-top: 0.5rem;
        }
        
        .loading {
            text-align: center;
            padding: 3rem;
            font-size: 1.2rem;
        }
        
        .spinner {
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-top: 3px solid #00ff88;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* INDICADOR DE ACTUALIZACIÓN */
        .updating {
            opacity: 0.7;
            transform: scale(0.98);
        }
        
        .price-up {
            color: #00ff88 !important;
            animation: priceFlash 0.5s ease;
        }
        
        .price-down {
            color: #ff4757 !important;
            animation: priceFlash 0.5s ease;
        }
        
        @keyframes priceFlash {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 2rem; }
            .symbols-grid { 
                grid-template-columns: 1fr;
                padding: 1rem;
            }
            .status-bar {
                flex-direction: column;
                gap: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Jaime Merino Trading Bot</h1>
        <p>📈 Metodología Trading Latino Avanzada</p>
        <p>🎯 Versión Enhanced - Actualización Suave</p>
    </div>
    
    <div class="status-bar">
        <div class="status-item">
            <span class="status-dot"></span>
            <span id="connection-status">
                {% if socketio_enabled %}🟢 WebSocket Activo{% else %}📡 Modo HTTP{% endif %}
            </span>
        </div>
        <div class="status-item">
            <span>🕒 <span id="current-time">{{ server_time }}</span></span>
        </div>
        <div class="status-item">
            <span>📊 {{ symbols_data|length }} Símbolos</span>
        </div>
        <div class="status-item">
            <span id="last-update">💫 Actualizado</span>
        </div>
    </div>
    
    <div class="philosophy">
        <h3>💡 Filosofía Jaime Merino</h3>
        <p><strong>"El arte de tomar dinero de otros legalmente"</strong></p>
        <p><strong>"Es mejor perder una oportunidad que perder dinero"</strong></p>
        <p><strong>"Solo operamos con alta probabilidad de éxito"</strong></p>
        <p><strong>"Operamos contra el 90% que pierde dinero"</strong></p>
    </div>
    
    <div class="controls">
        <button class="btn" onclick="refreshData()">🔄 Actualizar Datos</button>
        <button class="btn" onclick="window.open('/api/data', '_blank')">📊 Ver JSON</button>
        <button class="btn" onclick="window.open('/health', '_blank')">💚 Health Check</button>
    </div>
    
    {% if symbols_data %}
    <div class="symbols-grid" id="symbols-container">
        {% for symbol, data in symbols_data.items() %}
        <div class="symbol-card" id="card-{{ data.symbol }}">
            <div class="symbol-header">
                <div class="symbol-name">{{ data.symbol }}</div>
                <div class="last-update">{{ data.last_update }}</div>
            </div>
            
            <div class="price-section">
                <div class="price" id="price-{{ data.symbol }}">${{ "%.8f"|format(data.price) }}</div>
                <div class="change {% if data.change_24h >= 0 %}positive{% else %}negative{% endif %}" id="change-{{ data.symbol }}">
                    {{ "%.2f"|format(data.change_24h) }}% (24h)
                </div>
            </div>
            
            <div class="indicators">
                <div class="indicator">
                    <div class="indicator-label">RSI</div>
                    <div class="indicator-value" id="rsi-{{ data.symbol }}">{{ data.rsi }}</div>
                </div>
                <div class="indicator">
                    <div class="indicator-label">MACD</div>
                    <div class="indicator-value" id="macd-{{ data.symbol }}">{{ "%.6f"|format(data.macd) }}</div>
                </div>
            </div>
            
            <div class="signal-section">
                <div class="signal {{ data.color }}" id="signal-{{ data.symbol }}">
                    {{ data.signal }}
                </div>
                <div class="confidence">
                    🎯 Confianza: <span id="confidence-{{ data.symbol }}">{{ data.confidence }}%</span>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="loading">
        <div class="spinner"></div>
        <p>Cargando datos de mercado...</p>
    </div>
    {% endif %}

    {% if socketio_enabled %}
    <script>
        const socket = io();
        let lastPrices = {};
        
        socket.on('connect', function() {
            console.log('✅ Conectado al servidor');
            document.getElementById('connection-status').innerHTML = '🟢 WebSocket Conectado';
        });
        
        socket.on('disconnect', function() {
            console.log('❌ Desconectado del servidor');
            document.getElementById('connection-status').innerHTML = '🔴 WebSocket Desconectado';
        });
        
        socket.on('data_update', function(response) {
            console.log('📊 Datos actualizados:', response.update_type);
            updateSymbolsDataSmooth(response.data);
            
            // Actualizar indicador
            document.getElementById('last-update').innerHTML = '✨ Actualizado ' + new Date().toLocaleTimeString();
        });
        
        function updateSymbolsDataSmooth(data) {
            // ACTUALIZACIÓN SUAVE SIN RECARGAR LA PÁGINA
            Object.values(data).forEach(symbolData => {
                const symbol = symbolData.symbol;
                const oldPrice = lastPrices[symbol];
                const newPrice = symbolData.price;
                
                // Actualizar precio con animación
                const priceEl = document.getElementById(`price-${symbol}`);
                if (priceEl) {
                    // Añadir clase de actualización
                    const cardEl = document.getElementById(`card-${symbol}`);
                    cardEl.classList.add('updating');
                    
                    setTimeout(() => {
                        priceEl.textContent = `$${newPrice.toFixed(8)}`;
                        
                        // Animación de color según cambio de precio
                        if (oldPrice && newPrice > oldPrice) {
                            priceEl.classList.add('price-up');
                        } else if (oldPrice && newPrice < oldPrice) {
                            priceEl.classList.add('price-down');
                        }
                        
                        // Limpiar clases después de la animación
                        setTimeout(() => {
                            priceEl.classList.remove('price-up', 'price-down');
                            cardEl.classList.remove('updating');
                        }, 500);
                        
                    }, 100);
                    
                    lastPrices[symbol] = newPrice;
                }
                
                // Actualizar cambio 24h
                const changeEl = document.getElementById(`change-${symbol}`);
                if (changeEl) {
                    changeEl.textContent = `${symbolData.change_24h.toFixed(2)}% (24h)`;
                    changeEl.className = `change ${symbolData.change_24h >= 0 ? 'positive' : 'negative'}`;
                }
                
                // Actualizar RSI
                const rsiEl = document.getElementById(`rsi-${symbol}`);
                if (rsiEl) {
                    rsiEl.textContent = symbolData.rsi;
                }
                
                // Actualizar MACD
                const macdEl = document.getElementById(`macd-${symbol}`);
                if (macdEl) {
                    macdEl.textContent = symbolData.macd.toFixed(6);
                }
                
                // Actualizar señal
                const signalEl = document.getElementById(`signal-${symbol}`);
                if (signalEl) {
                    signalEl.textContent = symbolData.signal;
                    signalEl.className = `signal ${symbolData.color}`;
                }
                
                // Actualizar confianza
                const confidenceEl = document.getElementById(`confidence-${symbol}`);
                if (confidenceEl) {
                    confidenceEl.textContent = `${symbolData.confidence}%`;
                }
            });
            
            // Actualizar hora
            document.getElementById('current-time').textContent = new Date().toLocaleTimeString();
        }
        
        function refreshData() {
            socket.emit('refresh_data');
            document.getElementById('last-update').innerHTML = '🔄 Actualizando...';
        }
        
        // Inicializar precios para comparación
        window.addEventListener('load', function() {
            {% for symbol, data in symbols_data.items() %}
            lastPrices['{{ data.symbol }}'] = {{ data.price }};
            {% endfor %}
        });
        
    </script>
    {% else %}
    <script>
        function refreshData() {
            // En modo HTTP, actualizar suavemente sin recargar
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateSymbolsDataSmooth(data.data);
                    }
                })
                .catch(error => {
                    console.error('Error actualizando datos:', error);
                    // Solo recargar si hay error
                    location.reload();
                });
        }
        
        function updateSymbolsDataSmooth(data) {
            // Misma función de actualización suave para modo HTTP
            Object.values(data).forEach(symbolData => {
                const symbol = symbolData.symbol;
                
                // Actualizar elementos sin recargar página
                const priceEl = document.getElementById(`price-${symbol}`);
                if (priceEl) {
                    priceEl.textContent = `${symbolData.price.toFixed(8)}`;
                }
                
                const changeEl = document.getElementById(`change-${symbol}`);
                if (changeEl) {
                    changeEl.textContent = `${symbolData.change_24h.toFixed(2)}% (24h)`;
                    changeEl.className = `change ${symbolData.change_24h >= 0 ? 'positive' : 'negative'}`;
                }
                
                const rsiEl = document.getElementById(`rsi-${symbol}`);
                if (rsiEl) rsiEl.textContent = symbolData.rsi;
                
                const macdEl = document.getElementById(`macd-${symbol}`);
                if (macdEl) macdEl.textContent = symbolData.macd.toFixed(6);
                
                const signalEl = document.getElementById(`signal-${symbol}`);
                if (signalEl) {
                    signalEl.textContent = symbolData.signal;
                    signalEl.className = `signal ${symbolData.color}`;
                }
                
                const confidenceEl = document.getElementById(`confidence-${symbol}`);
                if (confidenceEl) confidenceEl.textContent = `${symbolData.confidence}%`;
            });
            
            document.getElementById('current-time').textContent = new Date().toLocaleTimeString();
            document.getElementById('last-update').innerHTML = '✨ Actualizado ' + new Date().toLocaleTimeString();
        }
        
        // Auto-refresh cada 3 minutos en modo HTTP (menos frecuente)
        setInterval(refreshData, 180000);
    </script>
    {% endif %}
    
    <script>
        // Actualizar reloj cada segundo
        setInterval(function() {
            document.getElementById('current-time').textContent = new Date().toLocaleTimeString();
        }, 1000);
    </script>
</body>
</html>"""
    
    with open(os.path.join(template_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Template HTML con actualización suave creado")

if __name__ == '__main__':
    print("🚀 Configurando Jaime Merino Trading Bot...")
    
    # Crear template optimizado
    create_smooth_template()
    
    # Generar datos iniciales
    trading_data = generate_trading_data()
    
    # Iniciar worker en segundo plano
    worker = threading.Thread(target=background_worker, daemon=True)
    worker.start()
    
    # Configuración para Render
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"🌍 Iniciando servidor en {host}:{port}")
    print("💡 Filosofía: El arte de tomar dinero de otros legalmente")
    print(f"📡 SocketIO: {'Habilitado' if SOCKETIO_AVAILABLE else 'Deshabilitado'}")
    print("🔄 Actualización suave activada - Sin parpadeo")
    print("📊 Precios semi-reales desde CoinGecko API")
    
    # Ejecutar aplicación
    if SOCKETIO_AVAILABLE and socketio:
        socketio.run(
            app,
            host=host,
            port=port,
            debug=False,
            allow_unsafe_werkzeug=True
        )
    else:
        app.run(
            host=host,
            port=port,
            debug=False
        )