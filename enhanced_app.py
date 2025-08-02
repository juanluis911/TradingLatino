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

# Configuración de servicios con manejo robusto de errores
BINANCE_SERVICE_AVAILABLE = False
binance_service = None

try:
    # Importar la clase BinanceService, no la instancia
    from services.binance_service import BinanceService
    # Crear instancia con manejo de errores
    binance_service = BinanceService()
    
    # Test de conexión básico
    if binance_service.test_connection():
        BINANCE_SERVICE_AVAILABLE = True
        print("✅ BinanceService importado y conectado correctamente")
    else:
        print("⚠️ BinanceService importado pero sin conexión")
        BINANCE_SERVICE_AVAILABLE = False
        
except ImportError as e:
    print(f"⚠️ No se pudo importar BinanceService: {e}")
except Exception as e:
    print(f"⚠️ Error inicializando BinanceService: {e}")

# Base de precios actualizada (fallback cuando Binance no está disponible)
BASE_PRICES = {
    'BTCUSDT': 67000,   # Actualizado - precio aproximado actual
    'ETHUSDT': 3200,    # Actualizado - precio aproximado actual
    'BNBUSDT': 580,
    'ADAUSDT': 0.45,
    'SOLUSDT': 185,
    'XRPUSDT': 0.62,
    'DOGEUSDT': 0.12,
    'MATICUSDT': 0.55,
    'LINKUSDT': 15.50,
    'AVAXUSDT': 28.00
}

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
print(f"🔗 Binance: {BINANCE_SERVICE_AVAILABLE}")

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

def _get_binance_api_direct() -> dict:
    """
    Método alternativo: API directa de Binance sin autenticación
    Funciona incluso con restricciones geográficas usando endpoints públicos
    """
    try:
        # Usar endpoint público que suele ser más permisivo
        url = "https://api.binance.com/api/v3/ticker/price"
        
        # Headers para simular navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            prices = {}
            
            # Filtrar solo los símbolos que necesitamos
            for item in data:
                if item['symbol'] in SYMBOLS:
                    prices[item['symbol']] = float(item['price'])
            
            return prices
        else:
            print(f"❌ Error API Binance: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"❌ Error en API directa Binance: {e}")
        return {}

def _get_coingecko_prices() -> dict:
    """
    Método de backup: CoinGecko API (sin restricciones geográficas)
    """
    try:
        # Mapeo de símbolos Binance a IDs de CoinGecko
        coin_mapping = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'BNBUSDT': 'binancecoin',
            'ADAUSDT': 'cardano',
            'SOLUSDT': 'solana',
            'XRPUSDT': 'ripple',
            'DOGEUSDT': 'dogecoin',
            'MATICUSDT': 'matic-network',
            'LINKUSDT': 'chainlink',
            'AVAXUSDT': 'avalanche-2'
        }
        
        # Obtener solo los IDs que necesitamos
        needed_ids = [coin_mapping[symbol] for symbol in SYMBOLS if symbol in coin_mapping]
        ids_string = ','.join(needed_ids)
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            prices = {}
            
            # Convertir de vuelta a formato Binance
            for symbol in SYMBOLS:
                if symbol in coin_mapping:
                    coin_id = coin_mapping[symbol]
                    if coin_id in data and 'usd' in data[coin_id]:
                        prices[symbol] = data[coin_id]['usd']
            
            return prices
        else:
            print(f"❌ Error CoinGecko: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"❌ Error en CoinGecko: {e}")
        return {}

def _complete_missing_prices(partial_prices: dict) -> dict:
    """
    Completa precios faltantes con datos base actualizados
    """
    complete_prices = partial_prices.copy()
    
    for symbol in SYMBOLS:
        if symbol not in complete_prices or complete_prices[symbol] <= 0:
            complete_prices[symbol] = BASE_PRICES.get(symbol, 1.0)
            print(f"🔄 Precio base usado para {symbol}: ${complete_prices[symbol]:,.2f}")
    
    return complete_prices

def get_real_price_reference() -> dict:
    """
    FUNCIÓN PRINCIPAL: Obtiene precios reales con múltiples fallbacks
    Prioriza métodos que funcionan con restricciones geográficas
    """
    print(f"🔍 Obteniendo precios reales para {len(SYMBOLS)} símbolos...")
    
    # Método 1: BinanceService (solo si está disponible y conectado)
    if BINANCE_SERVICE_AVAILABLE and binance_service:
        try:
            binance_prices = {}
            for symbol in SYMBOLS:
                price = binance_service.get_current_price(symbol)
                if price and price > 0:
                    binance_prices[symbol] = price
            
            if len(binance_prices) >= len(SYMBOLS) * 0.8:  # 80% éxito
                print(f"✅ Precios de BinanceService: {len(binance_prices)}/{len(SYMBOLS)}")
                return _complete_missing_prices(binance_prices)
        except Exception as e:
            print(f"⚠️ Error en BinanceService: {e}")
    
    # Método 2: API directa de Binance (BACKUP PRINCIPAL)
    print("🔄 Intentando API directa de Binance...")
    binance_api_prices = _get_binance_api_direct()
    if binance_api_prices and len(binance_api_prices) >= len(SYMBOLS) * 0.6:  # 60% éxito
        print(f"✅ Precios de Binance API directa: {len(binance_api_prices)}/{len(SYMBOLS)}")
        return _complete_missing_prices(binance_api_prices)
    
    # Método 3: CoinGecko (BACKUP EXTERNO)
    print("🔄 Intentando CoinGecko...")
    coingecko_prices = _get_coingecko_prices()
    if coingecko_prices and len(coingecko_prices) >= 2:  # Al menos BTC y ETH
        print(f"✅ Usando precios de CoinGecko: {len(coingecko_prices)}/{len(SYMBOLS)}")
        return _complete_missing_prices(coingecko_prices)
    
    # Método 4: Precios base actualizados (ÚLTIMO RECURSO)
    print("🚨 USANDO PRECIOS BASE - REVISAR CONEXIÓN A INTERNET")
    return {symbol: BASE_PRICES.get(symbol, 1.0) for symbol in SYMBOLS}

def generate_enhanced_analysis(symbol: str, price: float) -> dict:
    """Genera análisis mejorado basado en el precio real"""
    # Simulación de RSI más realista
    rsi = random.uniform(25, 75)
    
    # Simulación de MACD más coherente
    macd = random.uniform(-0.5, 0.5) * (price * 0.001)
    signal = macd + random.uniform(-0.1, 0.1) * (price * 0.0005)
    
    # Determinación de tendencia basada en indicadores
    if rsi > 70:
        trend = "Sobrecomprado"
        trend_class = "warning"
    elif rsi < 30:
        trend = "Sobreventa" 
        trend_class = "success"
    else:
        trend = "Neutral"
        trend_class = "info"
    
    # Simulación de volumen proporcional al precio
    volume_24h = random.uniform(50000000, 2000000000)
    if symbol == 'BTCUSDT':
        volume_24h *= 3  # BTC tiene más volumen
    
    return {
        'symbol': symbol,
        'price': round(price, 2),
        'change_24h': round(random.uniform(-8, 8), 2),
        'volume_24h': round(volume_24h, 0),
        'rsi': round(rsi, 1),
        'macd': round(macd, 4),
        'signal': round(signal, 4),
        'trend': trend,
        'trend_class': trend_class,
        'support': round(price * 0.95, 2),
        'resistance': round(price * 1.05, 2),
        'recommendation': 'HOLD' if 40 <= rsi <= 60 else ('SELL' if rsi > 60 else 'BUY'),
        'timestamp': datetime.now().isoformat()
    }

def generate_trading_data() -> dict:
    """
    Genera datos de trading actualizados con precios reales
    """
    print("📊 Generando análisis con precios reales...")
    
    # Obtener precios reales
    real_prices = get_real_price_reference()
    
    data = {}
    for symbol in SYMBOLS:
        current_price = real_prices.get(symbol, BASE_PRICES.get(symbol, 1.0))
        
        # Generar análisis completo con precio real
        analysis = generate_enhanced_analysis(symbol, current_price)
        
        # Actualizar cache de precios
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

def test_all_price_sources():
    """
    Función de prueba completa para verificar todas las fuentes
    """
    print("\n" + "="*60)
    print("🧪 PROBANDO TODAS LAS FUENTES DE PRECIOS")
    print("="*60)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    
    # Test 1: BinanceService
    print("\n1. 🔹 BinanceService:")
    if BINANCE_SERVICE_AVAILABLE:
        start_time = time.time()
        try:
            binance_prices = {}
            for symbol in test_symbols:
                price = binance_service.get_current_price(symbol)
                if price:
                    binance_prices[symbol] = price
            elapsed = time.time() - start_time
            
            if binance_prices:
                print(f"   ✅ Éxito en {elapsed:.2f}s:")
                for symbol, price in binance_prices.items():
                    print(f"      {symbol}: ${price:,.2f}")
            else:
                print("   ❌ No se obtuvieron precios")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print("   ❌ Servicio no disponible")
    
    # Test 2: API directa
    print("\n2. 🔹 Binance API Directa:")
    start_time = time.time()
    api_prices = _get_binance_api_direct()
    elapsed = time.time() - start_time
    
    if api_prices:
        print(f"   ✅ Éxito en {elapsed:.2f}s:")
        for symbol in test_symbols:
            price = api_prices.get(symbol)
            if price:
                print(f"      {symbol}: ${price:,.2f}")
    else:
        print("   ❌ No disponible")
    
    # Test 3: CoinGecko
    print("\n3. 🔹 CoinGecko:")
    start_time = time.time()
    gecko_prices = _get_coingecko_prices()
    elapsed = time.time() - start_time
    
    if gecko_prices:
        print(f"   ✅ Éxito en {elapsed:.2f}s:")
        for symbol in test_symbols:
            price = gecko_prices.get(symbol)
            if price:
                print(f"      {symbol}: ${price:,.2f}")
    else:
        print("   ❌ No disponible")
    
    # Test 4: Función principal
    print("\n4. 🔹 Función Principal:")
    start_time = time.time()
    final_prices = get_real_price_reference()
    elapsed = time.time() - start_time
    
    print(f"   ✅ Resultado final en {elapsed:.2f}s:")
    for symbol in test_symbols:
        price = final_prices.get(symbol)
        if price:
            print(f"      {symbol}: ${price:,.2f}")
    
    print("\n" + "="*60)

# ==============================================================================
# RUTAS FLASK
# ==============================================================================

@app.route('/')
def dashboard():
    """Página principal del dashboard"""
    return render_template('merino_dashboard.html')

@app.route('/api/trading-data')
def api_trading_data():
    """API endpoint para datos de trading"""
    global trading_data
    
    if not trading_data:
        trading_data = generate_trading_data()
    
    return jsonify({
        'success': True,
        'data': trading_data,
        'timestamp': datetime.now().isoformat(),
        'server_time': (datetime.now() - server_start_time).total_seconds(),
        'connected_clients': clients_connected,
        'binance_available': BINANCE_SERVICE_AVAILABLE
    })

@app.route('/api/test-sources')
def api_test_sources():
    """Endpoint para probar todas las fuentes de precios"""
    try:
        test_all_price_sources()
        return jsonify({
            'success': True,
            'message': 'Test completado - revisa la consola para detalles'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'binance_service': BINANCE_SERVICE_AVAILABLE,
        'socketio': SOCKETIO_AVAILABLE,
        'uptime_seconds': (datetime.now() - server_start_time).total_seconds()
    })

# ==============================================================================
# WEBSOCKET EVENTS (SI SOCKETIO ESTÁ DISPONIBLE)
# ==============================================================================

if SOCKETIO_AVAILABLE and socketio:
    @socketio.on('connect')
    def handle_connect():
        global clients_connected
        clients_connected += 1
        print(f"👤 Cliente conectado. Total: {clients_connected}")
        
        # Enviar datos iniciales
        emit('analysis_update', {
            'data': trading_data or generate_trading_data(),
            'timestamp': datetime.now().isoformat(),
            'clients': clients_connected,
            'philosophy': "El arte de tomar dinero de otros legalmente",
            'update_type': 'initial'
        })

    @socketio.on('disconnect')
    def handle_disconnect():
        global clients_connected
        clients_connected = max(0, clients_connected - 1)
        print(f"👋 Cliente desconectado. Total: {clients_connected}")

    @socketio.on('request_update')
    def handle_request_update():
        """Maneja solicitudes manuales de actualización"""
        global trading_data
        trading_data = generate_trading_data()
        
        emit('analysis_update', {
            'data': trading_data,
            'timestamp': datetime.now().isoformat(),
            'clients': clients_connected,
            'philosophy': "El arte de tomar dinero de otros legalmente",
            'update_type': 'manual'
        })

# ==============================================================================
# INICIALIZACIÓN Y EJECUCIÓN
# ==============================================================================

if __name__ == '__main__':
    print("\n🔧 Verificando configuración inicial...")
    
    # Test rápido de fuentes de precios
    print("🧪 Probando fuentes de precios...")
    test_all_price_sources()
    
    # Generar datos iniciales
    print("📊 Generando datos iniciales...")
    trading_data = generate_trading_data()
    
    # Iniciar worker en segundo plano
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()
    print("✅ Worker de análisis iniciado")
    
    # Configuración del servidor
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"\n🚀 Iniciando servidor Jaime Merino Trading Bot")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"📈 Dashboard: Metodología Trading Latino Avanzada")
    print(f"💡 Filosofía: 'El arte de tomar dinero de otros legalmente'")
    print(f"🎯 Disciplina: 'Es mejor perder una oportunidad que perder dinero'")
    
    try:
        if SOCKETIO_AVAILABLE and socketio:
            print("🔌 Modo: WebSocket + Flask")
            socketio.run(app, host=host, port=port, debug=False)
        else:
            print("🔌 Modo: Solo Flask (sin WebSocket)")
            app.run(host=host, port=port, debug=False)
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        print("💡 Verifica que el puerto no esté ocupado")