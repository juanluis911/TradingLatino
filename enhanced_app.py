"""
🚀 Jaime Merino Trading Bot - VERSIÓN QUE FUNCIONA GARANTIZADA
📈 Simplificada para solucionar página en blanco
"""

import os
import sys
import json
import time
import random
import threading
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

# Datos base
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']
BASE_PRICES = {
    'BTCUSDT': 45000,
    'ETHUSDT': 3000, 
    'BNBUSDT': 300,
    'ADAUSDT': 0.50,
    'XRPUSDT': 0.60
}

def generate_trading_data():
    """Genera datos de trading realistas"""
    data = {}
    
    for symbol in SYMBOLS:
        base_price = BASE_PRICES[symbol]
        
        # Variación realista de precio
        change_pct = random.uniform(-0.08, 0.08)  # ±8%
        current_price = base_price * (1 + change_pct)
        
        # RSI entre 20-80
        rsi = random.uniform(20, 80)
        
        # MACD simulado
        macd = random.uniform(-0.02, 0.02) * base_price
        
        # Determinar señal basada en indicadores
        if rsi < 30 and macd > 0:
            signal = "COMPRA FUERTE"
            confidence = random.uniform(80, 95)
            color = "success"
        elif rsi > 70 and macd < 0:
            signal = "VENTA FUERTE" 
            confidence = random.uniform(80, 95)
            color = "danger"
        elif rsi < 40:
            signal = "COMPRA"
            confidence = random.uniform(65, 80)
            color = "success"
        elif rsi > 60:
            signal = "VENTA"
            confidence = random.uniform(65, 80)
            color = "warning"
        else:
            signal = "ESPERAR"
            confidence = random.uniform(50, 70)
            color = "secondary"
        
        data[symbol] = {
            'symbol': symbol,
            'price': round(current_price, 8),
            'change_24h': round(change_pct * 100, 2),
            'volume': random.randint(1000000, 100000000),
            'rsi': round(rsi, 1),
            'macd': round(macd, 6),
            'signal': signal,
            'confidence': round(confidence, 1),
            'color': color,
            'timestamp': int(time.time()),
            'last_update': datetime.now().strftime('%H:%M:%S')
        }
    
    return data

def background_worker():
    """Hilo de trabajo en segundo plano"""
    global trading_data, clients_connected
    
    print("🔄 Iniciando worker de análisis...")
    
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
                    'philosophy': "El arte de tomar dinero de otros legalmente"
                })
                print(f"📊 Datos enviados a {clients_connected} clientes")
            
            # Pausa entre actualizaciones
            time.sleep(30)  # 30 segundos
            
        except Exception as e:
            print(f"❌ Error en worker: {e}")
            time.sleep(60)

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
    """Health check"""
    uptime = datetime.now() - server_start_time
    
    return jsonify({
        'status': 'healthy',
        'app': 'Jaime Merino Trading Bot',
        'version': '2.0.0',
        'uptime_seconds': int(uptime.total_seconds()),
        'socketio_enabled': SOCKETIO_AVAILABLE,
        'clients_connected': clients_connected,
        'symbols_tracked': len(SYMBOLS),
        'last_data_update': trading_data.get('BTCUSDT', {}).get('last_update', 'never'),
        'timestamp': datetime.now().isoformat(),
        'philosophy': "Es mejor perder una oportunidad que perder dinero"
    })

@app.route('/api/data')
def api_data():
    """API de datos"""
    global trading_data
    
    if not trading_data:
        trading_data = generate_trading_data()
    
    return jsonify({
        'success': True,
        'data': trading_data,
        'timestamp': datetime.now().isoformat(),
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

# Eventos SocketIO (si está disponible)
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
            'philosophy': "Operamos contra el 90% que pierde dinero"
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
            'message': 'Datos actualizados manualmente'
        })

def create_simple_template():
    """Crear template HTML simple pero funcional"""
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
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
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
        }
        
        .change {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
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
        }
        
        .signal-section {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            margin-top: 1.5rem;
        }
        
        .signal {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            border-radius: 8px;
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
        <p>🎯 Versión Enhanced - Live en Render</p>
    </div>
    
    <div class="status-bar">
        <div class="status-item">
            <span class="status-dot"></span>
            <span id="connection-status">
                {% if socketio_enabled %}🟢 WebSocket Activo{% else %}📡 Modo HTTP{% endif %}
            </span>
        </div>
        <div class="status-item">
            <span>🕒 {{ server_time }}</span>
        </div>
        <div class="status-item">
            <span>📊 {{ symbols_data|length }} Símbolos</span>
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
        <div class="symbol-card">
            <div class="symbol-header">
                <div class="symbol-name">{{ data.symbol }}</div>
                <div class="last-update">{{ data.last_update }}</div>
            </div>
            
            <div class="price-section">
                <div class="price">${{ "%.8f"|format(data.price) }}</div>
                <div class="change {% if data.change_24h >= 0 %}positive{% else %}negative{% endif %}">
                    {{ "%.2f"|format(data.change_24h) }}% (24h)
                </div>
            </div>
            
            <div class="indicators">
                <div class="indicator">
                    <div class="indicator-label">RSI</div>
                    <div class="indicator-value">{{ data.rsi }}</div>
                </div>
                <div class="indicator">
                    <div class="indicator-label">MACD</div>
                    <div class="indicator-value">{{ "%.6f"|format(data.macd) }}</div>
                </div>
            </div>
            
            <div class="signal-section">
                <div class="signal {{ data.color }}">
                    {{ data.signal }}
                </div>
                <div class="confidence">
                    🎯 Confianza: {{ data.confidence }}%
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
        
        socket.on('connect', function() {
            console.log('✅ Conectado al servidor');
            document.getElementById('connection-status').innerHTML = '🟢 WebSocket Conectado';
        });
        
        socket.on('disconnect', function() {
            console.log('❌ Desconectado del servidor');
            document.getElementById('connection-status').innerHTML = '🔴 WebSocket Desconectado';
        });
        
        socket.on('data_update', function(response) {
            console.log('📊 Datos actualizados:', response);
            updateSymbolsData(response.data);
        });
        
        function updateSymbolsData(data) {
            // Aquí podrías actualizar dinámicamente las tarjetas
            // Por simplicidad, recargamos la página
            location.reload();
        }
        
        function refreshData() {
            socket.emit('refresh_data');
        }
    </script>
    {% else %}
    <script>
        function refreshData() {
            location.reload();
        }
        
        // Auto-refresh cada 2 minutos en modo HTTP
        setInterval(function() {
            location.reload();
        }, 120000);
    </script>
    {% endif %}
</body>
</html>"""
    
    with open(os.path.join(template_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Template HTML simple creado")

if __name__ == '__main__':
    print("🚀 Configurando Jaime Merino Trading Bot...")
    
    # Crear template simple
    create_simple_template()
    
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