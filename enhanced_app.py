"""
🚀 Jaime Merino Trading Bot - Usando template merino_dashboard.html
📈 Conectado con el dashboard profesional existente
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
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.binance_service import BinanceService

# Inicializar servicio real de Binance
binance_service = BinanceService()

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

# Configuración específica para template merino_dashboard.html
SYMBOLS = ['BTCUSDT', 'ETHUSDT']  # Simplificado para coincidir con el template
BASE_PRICES = {
    'BTCUSDT': 43500,
    'ETHUSDT': 2920
}

def get_real_price_reference():
    """Obtiene precios de múltiples fuentes"""
    
    # Método 1: Binance directo (preferido)
    try:
        binance_prices = {}
        for symbol in SYMBOLS:
            price = binance_service.get_current_price(symbol)
            if price:
                binance_prices[symbol] = price
        
        if binance_prices:
            print(f"✅ Precios de Binance obtenidos: {len(binance_prices)} símbolos")
            return binance_prices
    except Exception as e:
        print(f"⚠️ Error Binance: {e}")
    
    # Método 2: CoinGecko (backup)
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin&vs_currencies=usd',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            gecko_prices = {
                'BTCUSDT': data.get('bitcoin', {}).get('usd'),
                'ETHUSDT': data.get('ethereum', {}).get('usd'),
                'BNBUSDT': data.get('binancecoin', {}).get('usd')
            }
            
            # Filtrar None values
            gecko_prices = {k: v for k, v in gecko_prices.items() if v is not None}
            
            if gecko_prices:
                print(f"✅ Precios de CoinGecko: {len(gecko_prices)} símbolos")
                return gecko_prices
                
    except Exception as e:
        print(f"⚠️ Error CoinGecko: {e}")
    
    # Método 3: Precios base actualizados (último recurso)
    print("⚠️ Usando precios base actualizados")
    return BASE_PRICES

def generate_enhanced_analysis(symbol, current_price):
    """Genera análisis completo para el template merino_dashboard.html"""
    
    # Indicadores técnicos simulados
    rsi = random.uniform(25, 75)
    ema_11 = current_price * random.uniform(0.98, 1.02)
    ema_55 = current_price * random.uniform(0.95, 1.05)
    adx = random.uniform(20, 60)
    macd = (current_price - BASE_PRICES[symbol]) * random.uniform(0.001, 0.003)
    
    # Bollinger Bands
    bb_upper = current_price * 1.02
    bb_lower = current_price * 0.98
    bb_middle = current_price
    
    # Lógica de señales según metodología Merino
    signal_strength = 0
    signal = "WAIT"
    
    # Análisis de tendencia
    if ema_11 > ema_55:
        signal_strength += 25
        trend = "ALCISTA"
    else:
        trend = "BAJISTA"
        signal_strength += 15
    
    # RSI
    if rsi < 30:
        signal_strength += 20
        if trend == "ALCISTA":
            signal = "LONG"
    elif rsi > 70:
        signal_strength += 20
        if trend == "BAJISTA":
            signal = "SHORT"
    
    # ADX (fuerza de tendencia)
    if adx > 25:
        signal_strength += 15
    
    # MACD
    if macd > 0 and signal == "LONG":
        signal_strength += 20
    elif macd < 0 and signal == "SHORT":
        signal_strength += 20
    
    # Determinar señal final
    if signal_strength >= 70:
        confidence = "HIGH"
    elif signal_strength >= 50:
        confidence = "MEDIUM" 
    else:
        confidence = "LOW"
        signal = "WAIT"
    
    # Cálculos para futuros (metodología Merino)
    entry_optimal = current_price
    if signal == "LONG":
        entry_range_low = current_price * 0.99
        entry_range_high = current_price * 1.01
        target_1 = current_price * 1.02
        target_2 = current_price * 1.04
        target_3 = current_price * 1.06
        stop_loss = current_price * 0.97
        invalidation = current_price * 0.95
    elif signal == "SHORT":
        entry_range_low = current_price * 0.99
        entry_range_high = current_price * 1.01
        target_1 = current_price * 0.98
        target_2 = current_price * 0.96
        target_3 = current_price * 0.94
        stop_loss = current_price * 1.03
        invalidation = current_price * 1.05
    else:
        entry_range_low = current_price * 0.995
        entry_range_high = current_price * 1.005
        target_1 = current_price * 1.01
        target_2 = current_price * 1.02
        target_3 = current_price * 1.03
        stop_loss = current_price * 0.99
        invalidation = current_price * 0.97
    
    return {
        'current_price': current_price,
        'signal': {
            'signal': signal,
            'signal_strength': signal_strength,
            'confluence_score': random.randint(1, 4),
            'confidence': confidence
        },
        'indicators': {
            'rsi': {
                'value': round(rsi, 1),
                'status': 'OVERSOLD' if rsi < 30 else 'OVERBOUGHT' if rsi > 70 else 'NEUTRAL'
            },
            'ema': {
                'ema_11': round(ema_11, 2),
                'ema_55': round(ema_55, 2),
                'trend': trend
            },
            'adx': {
                'value': round(adx, 1),
                'strength': 'STRONG' if adx > 25 else 'WEAK'
            },
            'macd': {
                'value': round(macd, 6),
                'signal': 'BULLISH' if macd > 0 else 'BEARISH'
            },
            'bollinger': {
                'upper': round(bb_upper, 2),
                'middle': round(bb_middle, 2),
                'lower': round(bb_lower, 2)
            }
        },
        'futures_setup': {
            'entry': {
                'optimal': round(entry_optimal, 2),
                'range_low': round(entry_range_low, 2),
                'range_high': round(entry_range_high, 2)
            },
            'targets': {
                'target_1': round(target_1, 2),
                'target_2': round(target_2, 2),
                'target_3': round(target_3, 2)
            },
            'risk_management': {
                'stop_loss': round(stop_loss, 2),
                'invalidation': round(invalidation, 2),
                'risk_reward': round(abs(target_1 - entry_optimal) / abs(stop_loss - entry_optimal), 2)
            }
        },
        'last_update': datetime.now().strftime('%H:%M:%S'),
        'timestamp': int(time.time())
    }

def generate_trading_data():
    """Genera datos compatibles con merino_dashboard.html"""
    global last_prices
    
    # Obtener precios reales como referencia
    real_prices = get_real_price_reference()
    
    data = {}
    
    for symbol in SYMBOLS:
        base_price = real_prices.get(symbol, BASE_PRICES[symbol])
        
        # Variación suave si tenemos precio anterior
        if symbol in last_prices:
            change_factor = random.uniform(-0.005, 0.005)  # ±0.5%
            current_price = last_prices[symbol] * (1 + change_factor)
        else:
            change_factor = random.uniform(-0.02, 0.02)  # ±2%
            current_price = base_price * (1 + change_factor)
        
        # Generar análisis completo
        analysis = generate_enhanced_analysis(symbol, current_price)
        
        # Almacenar precio para próxima iteración
        last_prices[symbol] = current_price
        
        data[symbol] = analysis
    
    return data

def background_worker():
    """Hilo de trabajo optimizado"""
    global trading_data, clients_connected
    
    print("🔄 Iniciando worker de análisis para dashboard Merino...")
    
    while True:
        try:
            # Generar nuevos datos
            trading_data = generate_trading_data()
            
            # Emitir datos si hay SocketIO y clientes
            if SOCKETIO_AVAILABLE and socketio and clients_connected > 0:
                socketio.emit('analysis_update', {
                    'data': trading_data,
                    'timestamp': datetime.now().isoformat(),
                    'clients': clients_connected,
                    'philosophy': "El arte de tomar dinero de otros legalmente",
                    'update_type': 'background'
                })
                print(f"📊 Análisis enviado a {clients_connected} clientes")
            
            # Pausa de 2 minutos
            time.sleep(120)
            
        except Exception as e:
            print(f"❌ Error en worker: {e}")
            time.sleep(180)

def get_real_prices():
    """Obtiene precios reales de Binance"""
    real_prices = {}
    
    for symbol in SYMBOLS:
        try:
            # Método 1: Precio directo
            price = binance_service.get_current_price(symbol)
            if price:
                real_prices[symbol] = price
                continue
                
            # Método 2: Market data completo
            market_data = binance_service.get_market_data(symbol)
            if market_data:
                real_prices[symbol] = market_data.close_price
                continue
                
            # Método 3: Solo como último recurso usar fallback
            real_prices[symbol] = BASE_PRICES.get(symbol, 0)
            print(f"⚠️ Usando precio fallback para {symbol}")
            
        except Exception as e:
            print(f"❌ Error obteniendo precio real {symbol}: {e}")
            real_prices[symbol] = BASE_PRICES.get(symbol, 0)
    
    return real_prices

def generate_trading_data():
    """Genera datos usando precios REALES"""
    global last_prices
    
    # ✅ Obtener precios reales
    real_prices = get_real_prices()
    
    data = {}
    for symbol in SYMBOLS:
        current_price = real_prices[symbol]
        
        # ✅ Usar precio real, no simulado
        analysis = generate_enhanced_analysis(symbol, current_price)
        last_prices[symbol] = current_price
        data[symbol] = analysis
    
    return data
# Rutas principales

@app.route('/')
def home():
    """Página principal usando merino_dashboard.html"""
    global trading_data
    
    try:
        # Generar datos iniciales si no existen
        if not trading_data:
            trading_data = generate_trading_data()
        
        # Preparar datos para el template
        template_data = {
            'symbols_data': trading_data,
            'server_time': datetime.now().strftime('%H:%M:%S'),
            'socketio_enabled': SOCKETIO_AVAILABLE,
            'philosophy': {
                'main_principle': "El arte de tomar dinero de otros legalmente",
                'risk_principle': "Es mejor perder una oportunidad que perder dinero",
                'probability_principle': "Solo operamos con alta probabilidad de éxito",
                'market_principle': "Operamos contra el 90% que pierde dinero"
            },
            'stats': {
                'active_signals': len([s for s in trading_data.values() if s['signal']['signal'] != 'WAIT']),
                'high_prob_signals': len([s for s in trading_data.values() if s['signal']['signal_strength'] >= 70]),
                'symbols_analyzed': f"{len(trading_data)}/{len(SYMBOLS)}"
            }
        }
        
        return render_template('merino_dashboard.html', **template_data)
        
    except Exception as e:
        print(f"❌ Error cargando template merino_dashboard.html: {e}")
        # Fallback a template simple
        return f"""
        <h1>🚀 Jaime Merino Trading Bot</h1>
        <p>Error cargando dashboard: {str(e)}</p>
        <p>📊 <a href="/api/data">Ver datos JSON</a></p>
        <p>💡 <a href="/health">Health Check</a></p>
        <p><strong>Template esperado:</strong> templates/merino_dashboard.html</p>
        """

@app.route('/health')
def health():
    """Health check mejorado"""
    uptime = datetime.now() - server_start_time
    
    return jsonify({
        'status': 'healthy',
        'app': 'Jaime Merino Trading Bot',
        'version': '2.2.0',
        'template': 'merino_dashboard.html',
        'uptime_seconds': int(uptime.total_seconds()),
        'socketio_enabled': SOCKETIO_AVAILABLE,
        'clients_connected': clients_connected,
        'symbols_tracked': len(SYMBOLS),
        'last_data_update': trading_data.get('BTCUSDT', {}).get('last_update', 'never'),
        'real_prices_enabled': True,
        'timestamp': datetime.now().isoformat(),
        'philosophy': "Es mejor perder una oportunidad que perder dinero"
    })

@app.route('/api/data')
def api_data():
    """API de datos compatible con dashboard"""
    global trading_data
    
    if not trading_data:
        trading_data = generate_trading_data()
    
    return jsonify({
        'success': True,
        'data': trading_data,
        'timestamp': datetime.now().isoformat(),
        'template': 'merino_dashboard.html',
        'data_source': 'enhanced_analysis_service',
        'philosophy': "Solo operamos con alta probabilidad de éxito"
    })

@app.route('/api/analysis/<symbol>')
def api_analysis(symbol):
    """API para análisis específico de símbolo"""
    symbol = symbol.upper()
    if symbol in trading_data:
        return jsonify({
            'success': True,
            'symbol': symbol,
            'analysis': trading_data[symbol],
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': f'Símbolo {symbol} no encontrado',
            'available_symbols': list(trading_data.keys())
        }), 404

# Rutas adicionales para compatibilidad con el dashboard

@app.route('/api/symbols')
def api_symbols():
    """Lista de símbolos soportados"""
    return jsonify({
        'success': True,
        'symbols': SYMBOLS,
        'count': len(SYMBOLS),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/philosophy')
def api_philosophy():
    """Filosofía Merino para el dashboard"""
    return jsonify({
        'success': True,
        'philosophy': {
            'main_principle': "El arte de tomar dinero de otros legalmente",
            'risk_principle': "Es mejor perder una oportunidad que perder dinero",
            'probability_principle': "Solo operamos con alta probabilidad de éxito",
            'market_principle': "Operamos contra el 90% que pierde dinero",
            'discipline': "Disciplina > Análisis técnico perfecto"
        },
        'methodology': {
            'timeframes': ['4H', '1H', '1D'],
            'key_indicators': ['EMA11/55', 'RSI', 'ADX', 'MACD', 'Bollinger Bands'],
            'risk_management': 'Metodología 40-30-20-10'
        },
        'timestamp': datetime.now().isoformat()
    })

# Eventos SocketIO compatibles con el dashboard
if SOCKETIO_AVAILABLE:
    @socketio.on('connect')
    def on_connect():
        global clients_connected
        clients_connected += 1
        print(f"🔗 Cliente conectado al dashboard Merino. Total: {clients_connected}")
        
        # Enviar datos iniciales compatibles con el dashboard
        emit('analysis_update', {
            'data': trading_data,
            'timestamp': datetime.now().isoformat(),
            'message': 'Conectado al Dashboard Jaime Merino',
            'philosophy': "Operamos contra el 90% que pierde dinero",
            'update_type': 'initial'
        })
    
    @socketio.on('disconnect')
    def on_disconnect():
        global clients_connected
        clients_connected = max(0, clients_connected - 1)
        print(f"❌ Cliente desconectado del dashboard. Total: {clients_connected}")
    
    @socketio.on('request_analysis')
    def on_request_analysis(data):
        """Evento específico del dashboard para solicitar análisis"""
        symbol = data.get('symbol', '').upper()
        print(f"📊 Análisis solicitado para {symbol}")
        
        if symbol in SYMBOLS:
            global trading_data
            trading_data = generate_trading_data()
            
            emit('analysis_update', {
                'data': trading_data,
                'timestamp': datetime.now().isoformat(),
                'message': f'Análisis actualizado para {symbol}',
                'update_type': 'manual'
            })
        else:
            emit('analysis_error', {
                'error': f'Símbolo {symbol} no soportado',
                'available_symbols': SYMBOLS
            })
    
    @socketio.on('request_all_symbols')
    def on_request_all_symbols():
        """Evento para solicitar análisis de todos los símbolos"""
        print("📊 Análisis completo solicitado")
        
        global trading_data
        trading_data = generate_trading_data()
        
        emit('analysis_update', {
            'data': trading_data,
            'timestamp': datetime.now().isoformat(),
            'message': 'Análisis completo actualizado',
            'update_type': 'complete'
        })

def check_template_exists():
    """Verificar que el template merino_dashboard.html existe"""
    template_path = 'templates/merino_dashboard.html'
    if os.path.exists(template_path):
        print("✅ Template merino_dashboard.html encontrado")
        return True
    else:
        print("⚠️ Template merino_dashboard.html NO encontrado")
        print(f"   Esperado en: {os.path.abspath(template_path)}")
        return False

if __name__ == '__main__':
    print("🚀 Configurando Jaime Merino Trading Bot...")
    print("📋 Usando template: merino_dashboard.html")
    
    # Verificar template
    template_exists = check_template_exists()
    
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
    print(f"📋 Template: {'✅ Encontrado' if template_exists else '❌ Faltante'}")
    print(f"📊 Símbolos: {', '.join(SYMBOLS)}")
    
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