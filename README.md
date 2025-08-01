# 🚀 Trading Analysis App
## Metodología Jaime Merino - Análisis Técnico Avanzado

### 📋 Descripción
Aplicación web de análisis técnico en tiempo real para trading de criptomonedas, implementando la metodología de Jaime Merino con indicadores técnicos avanzados.

### ✨ Características
- 📊 Análisis técnico en tiempo real
- 🎯 Señales de trading automatizadas  
- 📈 Indicadores: EMA, ADX, RSI, MACD, Bollinger Bands
- 🔄 Actualizaciones automáticas vía WebSocket
- 📱 Interfaz responsive y moderna
- 🛡️ Gestión de riesgo integrada

### 🔧 Instalación

#### Opción 1: Instalación automática
```bash
python setup.py
```

#### Opción 2: Instalación manual
```bash
# 1. Clonar o descargar el proyecto
git clone <tu-repositorio>

# 2. Instalar dependencias  
pip install -r requirements.txt

# 3. Configurar variables de entorno (opcional)
cp .env.example .env
# Editar .env con tus credenciales de Binance

# 4. Ejecutar aplicación
python app.py
```

### 🚀 Uso

#### Iniciar servidor
```bash
# Windows
run.bat

# Linux/Mac
./run.sh

# O directamente
python app.py
```

#### Acceder a la aplicación
- **Dashboard**: http://localhost:5000
- **Health Check**: http://localhost:5000/health  
- **API**: http://localhost:5000/api/symbols

### 📊 API Endpoints

- `GET /` - Dashboard principal
- `GET /health` - Estado del servidor
- `GET /api/symbols` - Símbolos soportados
- `GET /api/analysis/<symbol>` - Análisis de símbolo específico

### 🔌 WebSocket Events

#### Cliente → Servidor
- `request_analysis` - Solicitar análisis de símbolo
- `request_all_symbols` - Análisis de todos los símbolos
- `ping` - Ping de conexión

#### Servidor → Cliente  
- `analysis_update` - Actualización de análisis
- `analysis_error` - Error en análisis
- `status` - Estado del servidor
- `pong` - Respuesta a ping

### 📁 Estructura del Proyecto
```
trading_project/
├── app.py                     # Aplicación principal
├── config.py                  # Configuración
├── requirements.txt           # Dependencias
├── models/                    # Modelos de datos
│   └── trading_analysis.py    
├── services/                  # Servicios de negocio
│   ├── binance_service.py     
│   ├── analysis_service.py    
│   └── indicators.py          
├── utils/                     # Utilidades
│   ├── logger.py              
│   └── json_utils.py          
├── websocket/                 # WebSocket handlers
│   └── socket_handlers.py     
├── templates/                 # Templates HTML
│   └── index.html             
└── logs/                      # Archivos de log
```

### 🔑 Variables de entorno (.env)
```env
# Servidor
DEBUG=True
HOST=0.0.0.0  
PORT=5000

# Binance API (opcional)
BINANCE_API_KEY=tu_api_key
BINANCE_SECRET_KEY=tu_secret_key

# Configuración
UPDATE_INTERVAL=60
LOG_LEVEL=INFO
```

### 📈 Símbolos Soportados
- BTCUSDT, ETHUSDT, ADAUSDT, BNBUSDT
- SOLUSDT, XRPUSDT, DOTUSDT, LINKUSDT

### 🛠️ Desarrollo

#### Ejecutar en modo desarrollo
```bash
export FLASK_ENV=development
python app.py
```

#### Ejecutar tests (cuando estén disponibles)
```bash
python -m pytest tests/
```

### 📊 Metodología de Análisis

#### Indicadores Utilizados
- **EMA 11/55**: Medias móviles exponenciales para tendencia
- **ADX**: Fuerza de la tendencia  
- **RSI**: Momentum y sobrecompra/sobreventa
- **MACD**: Convergencia/divergencia de medias
- **Bollinger Bands**: Volatilidad y niveles

#### Señales de Trading
- **LONG**: EMA11 > EMA55 + confirmaciones técnicas
- **SHORT**: EMA11 < EMA55 + confirmaciones técnicas  
- **WAIT**: Condiciones indecisas
- **NO_SIGNAL**: Sin configuración clara

### ⚠️ Disclaimer
Esta aplicación es solo para fines educativos y de análisis. No constituye asesoría financiera. El trading conlleva riesgos significativos.

### 📞 Soporte
Para soporte técnico, consulta los logs en la carpeta `logs/` o revisa el health check del servidor.

### 📄 Licencia
Proyecto educativo - Metodología Jaime Merino
