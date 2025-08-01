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
        """Obtiene el precio actual de un símbolo"""
        # Implementación del método
        pass
    
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
        
        Args:
            symbol: Símbolo del activo
            interval: Intervalo de tiempo ('1m', '5m', '1h', '4h', '1d', etc.)
            limit: Número de velas a obtener (máximo 1000)
            
        Returns:
            DataFrame con columnas: timestamp, open, high, low, close, volume
        """
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
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                klines = response.json()
            
            if not klines:
                logger.error(f"❌ No se obtuvieron datos para {symbol}")
                return None
            
            # Convertir a DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convertir tipos de datos
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
            # Mantener solo las columnas necesarias
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            # Establecer timestamp como índice
            df.set_index('timestamp', inplace=True)
            
            logger.debug(f"✅ Klines obtenidas para {symbol} ({interval}): {len(df)} velas")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo klines {symbol} ({interval}): {e}")
            return None
    

# IMPORTANTE: Esta instancia debe ir AL FINAL del archivo, después de la clase
from enhanced_config import MerinoConfig

binance_service = BinanceService(
    api_key=MerinoConfig.BINANCE_API_KEY,
    secret_key=MerinoConfig.BINANCE_SECRET_KEY
)