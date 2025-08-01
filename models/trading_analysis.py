"""
Servicio para conectar con Binance API
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from binance.client import Client
from binance.exceptions import BinanceAPIException
from models.trading_analysis import MarketData
from utils.logger import binance_logger
from config import Config

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
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Obtiene el precio actual de un símbolo
        
        Args:
            symbol: Símbolo del activo (ej: 'BTCUSDT')
            
        Returns:
            Precio actual o None si hay error
        """
        try:
            if self.client:
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
            else:
                # Usar API pública
                url = f"{self.base_url}/api/v3/ticker/price"
                params = {'symbol': symbol}
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                price = float(data['price'])
            
            logger.debug(f"💰 Precio actual {symbol}: ${price:,.4f}")
            return price
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de conexión obteniendo precio {symbol}: {e}")
            return None
        except BinanceAPIException as e:
            logger.error(f"❌ Error API Binance obteniendo precio {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado obteniendo precio {symbol}: {e}")
            return None
    
    def get_24hr_stats(self, symbol: str) -> Optional[Dict]:
        """
        Obtiene estadísticas de 24 horas para un símbolo
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Diccionario con estadísticas o None si hay error
        """
        try:
            if self.client:
                stats = self.client.get_ticker(symbol=symbol)
            else:
                url = f"{self.base_url}/api/v3/ticker/24hr"
                params = {'symbol': symbol}
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                stats = response.json()
            
            result = {
                'symbol': stats['symbol'],
                'price_change': float(stats['priceChange']),
                'price_change_percent': float(stats['priceChangePercent']),
                'open_price': float(stats['openPrice']),
                'high_price': float(stats['highPrice']),
                'low_price': float(stats['lowPrice']),
                'current_price': float(stats['lastPrice']),
                'volume': float(stats['volume']),
                'count': int(stats['count'])
            }
            
            logger.debug(f"📈 Stats 24h {symbol}: {result['price_change_percent']:+.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats 24h {symbol}: {e}")
            return None
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Obtiene datos de velas (klines) para análisis técnico
        
        Args:
            symbol: Símbolo del activo
            interval: Intervalo de tiempo ('1m', '5m', '1h', '1d', etc.)
            limit: Número de velas a obtener (máximo 1000)
            
        Returns:
            DataFrame con datos OHLCV o None si hay error
        """
        try:
            if self.client:
                klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            else:
                url = f"{self.base_url}/api/v3/klines"
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'limit': limit
                }
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                klines = response.json()
            
            # Convertir a DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convertir tipos y timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Limpiar datos
            df = df.dropna()
            df = df.reset_index(drop=True)
            
            logger.debug(f"📊 Obtenidas {len(df)} velas para {symbol} ({interval})")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo klines {symbol}: {e}")
            return None
    
    def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """
        Obtiene datos de mercado actuales para un símbolo
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            MarketData o None si hay error
        """
        try:
            # Obtener estadísticas 24h
            stats = self.get_24hr_stats(symbol)
            if not stats:
                return None
            
            market_data = MarketData(
                symbol=symbol,
                open_price=stats['open_price'],
                high_price=stats['high_price'],
                low_price=stats['low_price'],
                close_price=stats['current_price'],
                volume=stats['volume'],
                timestamp=datetime.now()
            )
            
            logger.debug(f"✅ Datos de mercado obtenidos para {symbol}")
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de mercado {symbol}: {e}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Obtiene precios actuales para múltiples símbolos
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            Diccionario {símbolo: precio}
        """
        prices = {}
        
        try:
            if self.client:
                # Usar API con credenciales
                tickers = self.client.get_all_tickers()
                ticker_dict = {ticker['symbol']: float(ticker['price']) for ticker in tickers}
                
                for symbol in symbols:
                    if symbol in ticker_dict:
                        prices[symbol] = ticker_dict[symbol]
                    else:
                        logger.warning(f"⚠️ Símbolo no encontrado: {symbol}")
            else:
                # Usar API pública - obtener todos los precios
                url = f"{self.base_url}/api/v3/ticker/price"
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                all_tickers = response.json()
                
                ticker_dict = {ticker['symbol']: float(ticker['price']) for ticker in all_tickers}
                
                for symbol in symbols:
                    if symbol in ticker_dict:
                        prices[symbol] = ticker_dict[symbol]
                    else:
                        logger.warning(f"⚠️ Símbolo no encontrado: {symbol}")
            
            logger.info(f"📊 Precios obtenidos para {len(prices)}/{len(symbols)} símbolos")
            return prices
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo múltiples precios: {e}")
            # Fallback: obtener precios uno por uno
            for symbol in symbols:
                price = self.get_current_price(symbol)
                if price:
                    prices[symbol] = price
            
            return prices
    
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
    
    def get_server_time(self) -> Optional[datetime]:
        """
        Obtiene la hora del servidor de Binance
        
        Returns:
            Datetime del servidor o None si hay error
        """
        try:
            if self.client:
                server_time = self.client.get_server_time()
                timestamp = server_time['serverTime']
            else:
                url = f"{self.base_url}/api/v3/time"
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                timestamp = data['serverTime']
            
            server_datetime = datetime.fromtimestamp(timestamp / 1000)
            logger.debug(f"🕐 Hora servidor Binance: {server_datetime}")
            return server_datetime
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo hora servidor: {e}")
            return None

# Instancia global del servicio
binance_service = BinanceService(
    api_key=Config.BINANCE_API_KEY,
    secret_key=Config.BINANCE_SECRET_KEY
)