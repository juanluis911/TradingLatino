"""
Servicio para conectar con Binance API
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
    Servicio para interactuar con la API de Binance
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
        
        # Inicializar cliente si hay credenciales
        if api_key and secret_key:
            try:
                self.client = Client(api_key, secret_key)
                logger.info("✅ Cliente Binance inicializado con credenciales")
            except Exception as e:
                logger.error(f"❌ Error inicializando cliente Binance: {e}")
        else:
            logger.info("📊 Usando API pública de Binance (sin credenciales)")
    
    # ... aquí van todos los métodos de la clase ...
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obtiene precio real de Binance"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if self.client:
                    # Con credenciales
                    ticker = self.client.get_symbol_ticker(symbol=symbol)
                    return float(ticker['price'])
                else:
                    # API pública
                    url = f"{self.base_url}/api/v3/ticker/price"
                    response = requests.get(url, params={'symbol': symbol}, timeout=10)
                    response.raise_for_status()
                    return float(response.json()['price'])
                    
            except Exception as e:
                print(f"❌ Intento {attempt+1} falló para {symbol}: {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(1)
        
        return None
    
    # services/binance_service.py

    def get_market_data(self, symbol: str) -> Optional['MarketData']:
        """
        Obtiene datos completos de mercado para un símbolo
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Objeto MarketData o None si hay error
        """
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
                response = requests.get(url, params=params, timeout=10)
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
            
            logger.debug(f"✅ Market data obtenida para {symbol}: ${data['price']:,.4f}")
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo market data para {symbol}: {e}")
            return None
        # ... otros métodos ...
        def test_connection(self) -> bool:
            """
            Prueba la conexión con Binance API
            
            Returns:
                True si la conexión es exitosa
            """
            try:
                if self.client:
                    # Test con credenciales
                    account_info = self.client.get_account()
                    logger.info("✅ Conexión Binance exitosa (con credenciales)")
                    return True
                else:
                    # Test API pública
                    url = f"{self.base_url}/api/v3/ping"
                    response = requests.get(url, timeout=5)
                    response.raise_for_status()
                    logger.info("✅ Conexión Binance exitosa (API pública)")
                    return True
                    
            except Exception as e:
                logger.error(f"❌ Error de conexión Binance: {e}")
                return False

        def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
            """
            Obtiene datos de velas (klines) para análisis técnico
            """
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
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
                        
                        headers = {
                            'User-Agent': 'python-binance-client'
                        }
                        
                        response = requests.get(url, params=params, headers=headers, timeout=15)
                        response.raise_for_status()
                        klines = response.json()
                    
                    if not klines or len(klines) == 0:
                        logger.error(f"❌ API retornó datos vacíos para {symbol}")
                        return None
                    
                    # Convertir a DataFrame
                    df = pd.DataFrame(klines, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_asset_volume', 'number_of_trades',
                        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                    ])
                    
                    # Convertir tipos de datos con manejo de errores
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
                    
                    for col in numeric_columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Verificar si hay datos válidos
                    if df[numeric_columns].isnull().all().any():
                        logger.error(f"❌ Datos inválidos en {symbol}")
                        return None
                    
                    # Mantener solo columnas necesarias
                    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                    
                    # Verificar cantidad mínima de datos
                    if len(df) < 20:  # Reducir el mínimo para debugging
                        logger.warning(f"⚠️ Pocos datos para {symbol}: {len(df)} velas")
                        return None
                    
                    # Establecer timestamp como índice
                    df.set_index('timestamp', inplace=True)
                    
                    logger.info(f"✅ Klines obtenidas para {symbol} ({interval}): {len(df)} velas")
                    return df
                    
                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    logger.warning(f"⚠️ Error de conexión para {symbol} (intento {retry_count}/{max_retries}): {e}")
                    if retry_count >= max_retries:
                        logger.error(f"❌ Falló obtener datos para {symbol} después de {max_retries} intentos")
                        return None
                    
                except Exception as e:
                    logger.error(f"❌ Error obteniendo klines {symbol} ({interval}): {e}")
                    return None
            
            return None
        def test_symbol_data(self, symbol: str) -> Dict:
            """
            Método de debugging para verificar disponibilidad de datos
            """
            result = {
                'symbol': symbol,
                'connection_ok': False,
                'symbol_info': None,
                'klines_1h': 0,
                'klines_4h': 0,
                'current_price': None,
                'errors': []
            }
            
            try:
                # 1. Test conexión básica
                if self.test_connection():
                    result['connection_ok'] = True
                
                # 2. Verificar información del símbolo
                try:
                    url = f"{self.base_url}/api/v3/exchangeInfo"
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    exchange_info = response.json()
                    
                    symbol_info = None
                    for s in exchange_info['symbols']:
                        if s['symbol'] == symbol:
                            symbol_info = s
                            break
                    
                    if symbol_info:
                        result['symbol_info'] = {
                            'status': symbol_info['status'],
                            'base_asset': symbol_info['baseAsset'],
                            'quote_asset': symbol_info['quoteAsset']
                        }
                    else:
                        result['errors'].append(f"Símbolo {symbol} no encontrado")
                        
                except Exception as e:
                    result['errors'].append(f"Error verificando símbolo: {e}")
                
                # 3. Test obtención de datos 1h
                try:
                    df_1h = self.get_klines(symbol, '1h', 50)
                    if df_1h is not None:
                        result['klines_1h'] = len(df_1h)
                except Exception as e:
                    result['errors'].append(f"Error klines 1h: {e}")
                
                # 4. Test obtención de datos 4h
                try:
                    df_4h = self.get_klines(symbol, '4h', 50)
                    if df_4h is not None:
                        result['klines_4h'] = len(df_4h)
                except Exception as e:
                    result['errors'].append(f"Error klines 4h: {e}")
                
                # 5. Test precio actual
                try:
                    price = self.get_current_price(symbol)
                    result['current_price'] = price
                except Exception as e:
                    result['errors'].append(f"Error precio actual: {e}")
            
            except Exception as e:
                result['errors'].append(f"Error general: {e}")
            
            return result
        # services/binance_service.py

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Obtiene el precio actual de un símbolo
        
        Args:
            symbol: Símbolo del activo (ej: 'BTCUSDT')
            
        Returns:
            Precio actual como float o None si hay error
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if self.client:
                    # Usar cliente con credenciales
                    ticker = self.client.get_symbol_ticker(symbol=symbol)
                    price = float(ticker['price'])
                    logger.debug(f"✅ Precio actual {symbol}: ${price:,.4f} (con credenciales)")
                    return price
                else:
                    # Usar API pública
                    url = f"{self.base_url}/api/v3/ticker/price"
                    params = {'symbol': symbol}
                    
                    headers = {
                        'User-Agent': 'python-binance-client'
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'price' not in data:
                        logger.error(f"❌ Respuesta de precio inválida para {symbol}: {data}")
                        return None
                    
                    price = float(data['price'])
                    logger.debug(f"✅ Precio actual {symbol}: ${price:,.4f} (API pública)")
                    return price
                    
            except requests.exceptions.RequestException as e:
                retry_count += 1
                logger.warning(f"⚠️ Error de conexión obteniendo precio {symbol} (intento {retry_count}/{max_retries}): {e}")
                if retry_count >= max_retries:
                    logger.error(f"❌ Falló obtener precio para {symbol} después de {max_retries} intentos")
                    return None
                time.sleep(1)  # Pausa antes de reintentar
                
            except (ValueError, KeyError) as e:
                logger.error(f"❌ Error procesando precio de {symbol}: {e}")
                return None
                
            except Exception as e:
                logger.error(f"❌ Error inesperado obteniendo precio de {symbol}: {e}")
                return None
        
        return None

    # services/binance_service.py

    def get_current_price_advanced(self, symbol: str) -> Optional[float]:
        """
        Obtiene precio actual usando múltiples endpoints como backup
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Precio actual o None si falla
        """
        # Método 1: Ticker price (más simple)
        price = self.get_current_price(symbol)
        if price is not None:
            return price
        
        # Método 2: 24hr ticker stats
        try:
            if self.client:
                ticker = self.client.get_ticker(symbol=symbol)
                price = float(ticker['lastPrice'])
                logger.info(f"✅ Precio {symbol} vía ticker stats: ${price:,.4f}")
                return price
            else:
                url = f"{self.base_url}/api/v3/ticker/24hr"
                params = {'symbol': symbol}
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                price = float(data['lastPrice'])
                logger.info(f"✅ Precio {symbol} vía 24hr ticker: ${price:,.4f}")
                return price
                
        except Exception as e:
            logger.warning(f"⚠️ Método backup falló para {symbol}: {e}")
        
        # Método 3: Usar último precio de klines
        try:
            df = self.get_klines(symbol, interval='1m', limit=1)
            if df is not None and len(df) > 0:
                price = float(df.iloc[-1]['close'])
                logger.info(f"✅ Precio {symbol} vía klines: ${price:,.4f}")
                return price
        except Exception as e:
            logger.warning(f"⚠️ Método klines falló para {symbol}: {e}")
        
        logger.error(f"❌ Todos los métodos fallaron para obtener precio de {symbol}")
        return None
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Obtiene datos de velas (klines) para análisis técnico
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
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
                    
                    headers = {
                        'User-Agent': 'python-binance-client'
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=15)
                    response.raise_for_status()
                    klines = response.json()
                
                if not klines or len(klines) == 0:
                    logger.error(f"❌ API retornó datos vacíos para {symbol}")
                    return None
                
                # Convertir a DataFrame
                df = pd.DataFrame(klines, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                ])
                
                # Convertir tipos de datos con manejo de errores
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                numeric_columns = ['open', 'high', 'low', 'close', 'volume']
                
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Verificar si hay datos válidos
                if df[numeric_columns].isnull().all().any():
                    logger.error(f"❌ Datos inválidos en {symbol}")
                    return None
                
                # Mantener solo columnas necesarias
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                
                # Verificar cantidad mínima de datos
                if len(df) < 20:  # Reducir el mínimo para debugging
                    logger.warning(f"⚠️ Pocos datos para {symbol}: {len(df)} velas")
                    return None
                
                # Establecer timestamp como índice
                df.set_index('timestamp', inplace=True)
                
                logger.info(f"✅ Klines obtenidas para {symbol} ({interval}): {len(df)} velas")
                return df
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                logger.warning(f"⚠️ Error de conexión para {symbol} (intento {retry_count}/{max_retries}): {e}")
                if retry_count >= max_retries:
                    logger.error(f"❌ Falló obtener datos para {symbol} después de {max_retries} intentos")
                    return None
                
            except Exception as e:
                logger.error(f"❌ Error obteniendo klines {symbol} ({interval}): {e}")
                return None
        
        return None

    # services/binance_service.py

    def test_connection(self) -> bool:
        """
        Prueba la conexión con Binance API
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            if self.client:
                # Test con credenciales - verificar info de cuenta
                try:
                    account_info = self.client.get_account()
                    logger.info("✅ Conexión Binance exitosa (con credenciales)")
                    return True
                except Exception as e:
                    logger.warning(f"⚠️ Error con credenciales, probando API pública: {e}")
                    # Si falla con credenciales, intentar API pública como backup
            
            # Test API pública
            url = f"{self.base_url}/api/v3/ping"
            headers = {
                'User-Agent': 'python-binance-client'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Test adicional: verificar que podemos obtener info del servidor
            url_time = f"{self.base_url}/api/v3/time"
            time_response = requests.get(url_time, headers=headers, timeout=10)
            time_response.raise_for_status()
            
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

    def test_symbol_access(self, symbol: str) -> bool:
        """
        Prueba el acceso a un símbolo específico
        
        Args:
            symbol: Símbolo a probar (ej: 'BTCUSDT')
            
        Returns:
            True si el símbolo es accesible
        """
        try:
            # Probar obtener precio del símbolo
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {'symbol': symbol}
            headers = {
                'User-Agent': 'python-binance-client'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'price' in data:
                logger.debug(f"✅ Símbolo {symbol} accesible - Precio: ${float(data['price']):,.4f}")
                return True
            else:
                logger.warning(f"⚠️ Respuesta inválida para símbolo {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error probando símbolo {symbol}: {e}")
            return False

    def get_server_status(self) -> Dict:
        """
        Obtiene estado completo del servidor Binance
        
        Returns:
            Diccionario con información del estado
        """
        status = {
            'connected': False,
            'server_time': None,
            'api_type': None,
            'symbols_accessible': [],
            'errors': []
        }
        
        try:
            # Test conexión básica
            if self.test_connection():
                status['connected'] = True
                
                # Obtener tiempo del servidor
                try:
                    url = f"{self.base_url}/api/v3/time"
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    time_data = response.json()
                    status['server_time'] = datetime.fromtimestamp(time_data['serverTime'] / 1000)
                except Exception as e:
                    status['errors'].append(f"Error obteniendo tiempo servidor: {e}")
                
                # Determinar tipo de API
                if self.client:
                    try:
                        self.client.get_account()
                        status['api_type'] = 'authenticated'
                    except:
                        status['api_type'] = 'public_only'
                else:
                    status['api_type'] = 'public_only'
                
                # Test símbolos principales
                test_symbols = ['BTCUSDT', 'ETHUSDT']
                for symbol in test_symbols:
                    if self.test_symbol_access(symbol):
                        status['symbols_accessible'].append(symbol)
            
            else:
                status['errors'].append('No se pudo establecer conexión básica')
        
        except Exception as e:
            status['errors'].append(f'Error general: {e}')
        
        return status

# IMPORTANTE: Esta instancia debe ir AL FINAL del archivo, después de la clase
from enhanced_config import MerinoConfig

binance_service = BinanceService(
    api_key=MerinoConfig.BINANCE_API_KEY,
    secret_key=MerinoConfig.BINANCE_SECRET_KEY
)