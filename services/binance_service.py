"""
Servicio refactorizado para conectar con Binance API - Optimizado para datos reales
"""
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from binance.client import Client
from binance.exceptions import BinanceAPIException
from models.trading_analysis import MarketData
from utils.logger import binance_logger

logger = binance_logger

class BinanceService:
    """
    Servicio mejorado para interactuar con la API de Binance
    Optimizado para obtener datos reales y manejar errores robustamente
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        """
        Inicializa el servicio de Binance
        
        Args:
            api_key: API key de Binance (opcional para datos públicos)
            secret_key: Secret key de Binance (opcional para datos públicos)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.client = None
        self.base_url = "https://api.binance.com"
        self.session = self._create_session()
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms entre requests para evitar rate limits
        
        # Cache de precios para evitar requests excesivos
        self._price_cache = {}
        self._cache_timeout = 30  # 30 segundos
        
        # Inicializar cliente si hay credenciales
        if api_key and secret_key:
            try:
                self.client = Client(api_key, secret_key)
                # Test inicial
                self.client.get_account()
                logger.info("✅ Cliente Binance inicializado con credenciales")
            except Exception as e:
                logger.error(f"❌ Error inicializando cliente Binance: {e}")
                self.client = None
        else:
            logger.info("📊 Usando API pública de Binance (sin credenciales)")
        
        # Verificar conexión inicial
        if self.test_connection():
            logger.info("🌐 Conexión con Binance establecida exitosamente")
        else:
            logger.warning("⚠️ Problemas de conexión con Binance")
    
    def _create_session(self) -> requests.Session:
        """Crea una sesión HTTP optimizada"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'JaimeMerino-TradingBot/1.0',
            'Content-Type': 'application/json'
        })
        # Configurar timeouts y reintentos
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('https://', adapter)
        return session
    
    def _rate_limit_check(self):
        """Evita exceder los límites de rate de Binance"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        self._last_request_time = time.time()
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Verifica si el cache es válido para un símbolo"""
        if symbol not in self._price_cache:
            return False
        
        cache_time = self._price_cache[symbol].get('timestamp', 0)
        return (time.time() - cache_time) < self._cache_timeout
    
    def _update_cache(self, symbol: str, price: float):
        """Actualiza el cache de precios"""
        self._price_cache[symbol] = {
            'price': price,
            'timestamp': time.time()
        }
    
    def get_current_price(self, symbol: str, use_cache: bool = True) -> Optional[float]:
        """
        Obtiene el precio actual de un símbolo - MÉTODO PRINCIPAL
        
        Args:
            symbol: Símbolo del activo (ej: 'BTCUSDT')
            use_cache: Si usar cache para evitar requests excesivos
            
        Returns:
            Precio actual como float o None si hay error
        """
        # Verificar cache primero
        if use_cache and self._is_cache_valid(symbol):
            cached_price = self._price_cache[symbol]['price']
            logger.debug(f"💾 Precio de cache para {symbol}: ${cached_price:,.4f}")
            return cached_price
        
        self._rate_limit_check()
        
        # Intentar múltiples métodos en orden de preferencia
        methods = [
            self._get_price_simple,
            self._get_price_24hr,
            self._get_price_from_klines
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                price = method(symbol)
                if price and price > 0:
                    logger.debug(f"✅ Precio {symbol}: ${price:,.4f} (método {i})")
                    self._update_cache(symbol, price)
                    return price
            except Exception as e:
                logger.warning(f"⚠️ Método {i} falló para {symbol}: {e}")
                continue
        
        logger.error(f"❌ Todos los métodos fallaron para obtener precio de {symbol}")
        return None
    
    def _get_price_simple(self, symbol: str) -> Optional[float]:
        """Método 1: Endpoint simple de precio"""
        if self.client:
            # Con credenciales
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        else:
            # API pública
            url = f"{self.base_url}/api/v3/ticker/price"
            response = self.session.get(url, params={'symbol': symbol}, timeout=10)
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
    
    def _get_price_24hr(self, symbol: str) -> Optional[float]:
        """Método 2: Ticker 24hr (más información)"""
        if self.client:
            ticker = self.client.get_ticker(symbol=symbol)
            return float(ticker['lastPrice'])
        else:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            response = self.session.get(url, params={'symbol': symbol}, timeout=10)
            response.raise_for_status()
            data = response.json()
            return float(data['lastPrice'])
    
    def _get_price_from_klines(self, symbol: str) -> Optional[float]:
        """Método 3: Último precio de klines"""
        df = self.get_klines(symbol, interval='1m', limit=1)
        if df is not None and len(df) > 0:
            return float(df.iloc[-1]['close'])
        return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Obtiene precios múltiples de manera eficiente
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            Diccionario {symbol: price}
        """
        logger.info(f"📊 Obteniendo precios para {len(symbols)} símbolos...")
        
        # Intentar obtener todos los precios de una vez
        try:
            prices = self._get_all_prices_bulk(symbols)
            if prices and len(prices) >= len(symbols) * 0.7:  # 70% éxito mínimo
                logger.info(f"✅ Precios bulk obtenidos: {len(prices)}/{len(symbols)}")
                return prices
        except Exception as e:
            logger.warning(f"⚠️ Método bulk falló: {e}")
        
        # Fallback: obtener precios individuales
        logger.info("🔄 Obteniendo precios individuales...")
        prices = {}
        for symbol in symbols:
            try:
                price = self.get_current_price(symbol)
                if price:
                    prices[symbol] = price
                else:
                    logger.warning(f"⚠️ No se pudo obtener precio de {symbol}")
            except Exception as e:
                logger.error(f"❌ Error obteniendo precio de {symbol}: {e}")
        
        logger.info(f"📈 Precios obtenidos: {len(prices)}/{len(symbols)}")
        return prices
    
    def _get_all_prices_bulk(self, symbols: List[str]) -> Dict[str, float]:
        """Obtiene todos los precios de una vez usando el endpoint bulk"""
        self._rate_limit_check()
        
        url = f"{self.base_url}/api/v3/ticker/price"
        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        
        all_tickers = response.json()
        
        # Filtrar solo los símbolos que necesitamos
        prices = {}
        for ticker in all_tickers:
            symbol = ticker['symbol']
            if symbol in symbols:
                price = float(ticker['price'])
                if price > 0:
                    prices[symbol] = price
                    self._update_cache(symbol, price)
        
        return prices
    
    def get_market_data(self, symbol: str) -> Optional['MarketData']:
        """
        Obtiene datos completos de mercado para un símbolo
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Objeto MarketData o None si hay error
        """
        self._rate_limit_check()
        
        try:
            if self.client:
                # Usar cliente con credenciales
                ticker = self.client.get_ticker(symbol=symbol)
                data = {
                    'symbol': symbol,
                    'price': float(ticker['lastPrice']),
                    'high': float(ticker['highPrice']),
                    'low': float(ticker['lowPrice']),
                    'volume': float(ticker['volume']),
                    'change': float(ticker['priceChange']),
                    'change_percent': float(ticker['priceChangePercent'])
                }
            else:
                # Usar API pública
                url = f"{self.base_url}/api/v3/ticker/24hr"
                params = {'symbol': symbol}
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                ticker = response.json()
                
                data = {
                    'symbol': symbol,
                    'price': float(ticker['lastPrice']),
                    'high': float(ticker['highPrice']),
                    'low': float(ticker['lowPrice']),
                    'volume': float(ticker['volume']),
                    'change': float(ticker['priceChange']),
                    'change_percent': float(ticker['priceChangePercent'])
                }
            
            # Crear objeto MarketData
            from models.trading_analysis import MarketData
            market_data = MarketData(
                symbol=data['symbol'],
                close_price=data['price'],
                high_price=data['high'],
                low_price=data['low'],
                volume=data['volume'],
                price_change=data['change'],
                price_change_percent=data['change_percent'],
                timestamp=datetime.now()
            )
            
            # Actualizar cache
            self._update_cache(symbol, data['price'])
            
            logger.debug(f"✅ Market data obtenida para {symbol}: ${data['price']:,.4f}")
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo market data para {symbol}: {e}")
            return None
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Obtiene datos de velas (klines) para análisis técnico - MEJORADO
        
        Args:
            symbol: Símbolo del trading pair
            interval: Intervalo de tiempo ('1m', '5m', '1h', '4h', '1d')
            limit: Número de velas (máximo 1000)
            
        Returns:
            DataFrame con datos OHLCV o None si hay error
        """
        # Validar parámetros
        if limit > 1000:
            limit = 1000
            logger.warning(f"⚠️ Límite reducido a 1000 para {symbol}")
        
        valid_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        if interval not in valid_intervals:
            logger.error(f"❌ Intervalo inválido: {interval}")
            return None
        
        self._rate_limit_check()
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.client:
                    # Usar cliente con credenciales
                    klines = self.client.get_klines(
                        symbol=symbol,
                        interval=interval,
                        limit=limit
                    )
                else:
                    # Usar API pública
                    url = f"{self.base_url}/api/v3/klines"
                    params = {
                        'symbol': symbol,
                        'interval': interval,
                        'limit': limit
                    }
                    
                    response = self.session.get(url, params=params, timeout=20)
                    response.raise_for_status()
                    klines = response.json()
                
                if not klines or len(klines) == 0:
                    logger.error(f"❌ API retornó datos vacíos para {symbol}")
                    return None
                
                # Convertir a DataFrame con validación robusta
                df = pd.DataFrame(klines, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                ])
                
                # Convertir tipos de datos con manejo de errores
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
                    
                    for col in numeric_columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Verificar datos válidos
                    if df[numeric_columns].isnull().any().any():
                        null_counts = df[numeric_columns].isnull().sum()
                        logger.warning(f"⚠️ Datos nulos en {symbol}: {null_counts.to_dict()}")
                        # Eliminar filas con datos nulos
                        df = df.dropna(subset=numeric_columns)
                    
                    if len(df) == 0:
                        logger.error(f"❌ No hay datos válidos para {symbol}")
                        return None
                    
                    # Validar que los precios son lógicos
                    for col in ['open', 'high', 'low', 'close']:
                        if (df[col] <= 0).any():
                            logger.error(f"❌ Precios inválidos en columna {col} para {symbol}")
                            return None
                    
                    # Verificar que high >= low, etc.
                    if not (df['high'] >= df['low']).all():
                        logger.error(f"❌ Datos inconsistentes (high < low) para {symbol}")
                        return None
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando datos de {symbol}: {e}")
                    return None
                
                # Mantener solo columnas necesarias y establecer índice
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()
                df.set_index('timestamp', inplace=True)
                
                # Verificar cantidad mínima de datos
                min_required = min(20, limit // 2)
                if len(df) < min_required:
                    logger.warning(f"⚠️ Pocos datos para {symbol}: {len(df)}/{limit} velas")
                    if attempt < max_retries - 1:
                        continue
                
                logger.info(f"✅ Klines obtenidas para {symbol} ({interval}): {len(df)} velas")
                return df
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Error de conexión para {symbol} (intento {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
                continue
                
            except Exception as e:
                logger.error(f"❌ Error obteniendo klines {symbol} ({interval}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                break
        
        logger.error(f"❌ Falló obtener klines para {symbol} después de {max_retries} intentos")
        return None
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Binance API - MEJORADO
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            # Test 1: Ping básico
            url = f"{self.base_url}/api/v3/ping"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            # Test 2: Tiempo del servidor
            url_time = f"{self.base_url}/api/v3/time"
            time_response = self.session.get(url_time, timeout=5)
            time_response.raise_for_status()
            
            # Test 3: Si hay cliente, probar credenciales
            if self.client:
                try:
                    account_info = self.client.get_account()
                    logger.info("✅ Conexión Binance exitosa (con credenciales)")
                    return True
                except Exception as e:
                    logger.warning(f"⚠️ Credenciales inválidas, usando API pública: {e}")
                    self.client = None  # Disable client si las credenciales fallan
            
            logger.info("✅ Conexión Binance exitosa (API pública)")
            return True
            
        except requests.exceptions.Timeout:
            logger.error("❌ Error de conexión Binance: Timeout")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Error de conexión Binance: No se puede conectar")
            return False
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Error HTTP Binance: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error de conexión Binance: {e}")
            return False
    
    def get_server_status(self) -> Dict:
        """
        Obtiene estado completo del servidor Binance y capacidades
        
        Returns:
            Diccionario con información detallada del estado
        """
        status = {
            'connected': False,
            'server_time': None,
            'local_time': datetime.now(),
            'api_type': 'none',
            'rate_limits': {},
            'symbols_tested': {},
            'cache_size': len(self._price_cache),
            'errors': []
        }
        
        try:
            # Test conexión básica
            if self.test_connection():
                status['connected'] = True
                
                # Obtener tiempo del servidor y calcular latencia
                try:
                    start_time = time.time()
                    url = f"{self.base_url}/api/v3/time"
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    latency = (time.time() - start_time) * 1000  # ms
                    
                    time_data = response.json()
                    status['server_time'] = datetime.fromtimestamp(time_data['serverTime'] / 1000)
                    status['latency_ms'] = round(latency, 2)
                    
                    # Verificar sincronización de tiempo
                    time_diff = abs((status['server_time'] - status['local_time']).total_seconds())
                    status['time_sync_ok'] = time_diff < 60  # Menos de 1 minuto de diferencia
                    
                except Exception as e:
                    status['errors'].append(f"Error obteniendo tiempo servidor: {e}")
                
                # Determinar tipo de API
                if self.client:
                    try:
                        account_info = self.client.get_account()
                        status['api_type'] = 'authenticated'
                        status['account_type'] = account_info.get('accountType', 'unknown')
                    except:
                        status['api_type'] = 'public_only'
                        status['client_error'] = True
                else:
                    status['api_type'] = 'public_only'
                
                # Test símbolos principales con detalles
                test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
                for symbol in test_symbols:
                    try:
                        start_time = time.time()
                        price = self.get_current_price(symbol, use_cache=False)
                        response_time = (time.time() - start_time) * 1000
                        
                        status['symbols_tested'][symbol] = {
                            'accessible': price is not None,
                            'price': price,
                            'response_time_ms': round(response_time, 2)
                        }
                    except Exception as e:
                        status['symbols_tested'][symbol] = {
                            'accessible': False,
                            'error': str(e)
                        }
                
                # Información de rate limits (si está disponible)
                try:
                    # Esta información generalmente viene en los headers de respuesta
                    status['rate_limits'] = {
                        'requests_per_minute': '1200 (estimated)',
                        'weight_per_minute': '6000 (estimated)'
                    }
                except Exception as e:
                    status['errors'].append(f"Error obteniendo rate limits: {e}")
            
            else:
                status['errors'].append('No se pudo establecer conexión básica')
        
        except Exception as e:
            status['errors'].append(f'Error general: {e}')
        
        return status
    
    def clear_cache(self):
        """Limpia el cache de precios"""
        self._price_cache.clear()
        logger.info("🧹 Cache de precios limpiado")
    
    def get_cache_info(self) -> Dict:
        """Retorna información del cache"""
        current_time = time.time()
        valid_entries = 0
        
        for symbol, data in self._price_cache.items():
            if (current_time - data['timestamp']) < self._cache_timeout:
                valid_entries += 1
        
        return {
            'total_entries': len(self._price_cache),
            'valid_entries': valid_entries,
            'cache_timeout': self._cache_timeout,
            'symbols': list(self._price_cache.keys())
        }

# INSTANCIA GLOBAL - Configurada desde enhanced_config
try:
    from enhanced_config import MerinoConfig
    binance_service = BinanceService(
        api_key=MerinoConfig.BINANCE_API_KEY,
        secret_key=MerinoConfig.BINANCE_SECRET_KEY
    )
    logger.info("🚀 BinanceService global inicializado")
except ImportError:
    # Fallback si no hay config
    binance_service = BinanceService()
    logger.warning("⚠️ BinanceService inicializado sin configuración")