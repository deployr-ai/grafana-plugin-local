# Plugin de Panel para Grafana: Interpretación con LLM Local

> **Una IA que te ayuda a ver más allá de los gráficos**

Este proyecto integra **modelos de lenguaje multimodales locales** (como Llama 3.2 Vision, GPT-4o Vision o Moondream) con Grafana para interpretar visualizaciones automáticamente y convertir información visual en explicaciones claras y útiles.

**¿El resultado?** Un dashboard que no solo muestra datos, sino que también los explica, detecta anomalías y sugiere posibles causas o acciones.

Este repositorio es un fork del desarrollado por Tom Glenn en este [enlace](https://github.com/tomglenn/tomglenn-openaianalyser-panel).

---

## 🎯 ¿Por qué usar una LLM local en Grafana?

Los plugins son paneles que permiten agregar nuevos tipos de visualizaciones o interacciones en un dashboard de Grafana. En este caso, el objetivo es permitir que un modelo de lenguaje interprete los gráficos y genere descripciones automáticas útiles para el usuario.

Imaginá que tenés un dashboard con múltiples métricas y detectás una anomalía en un gráfico. Una LLM puede:


- **Interpretar tendencias** en tiempo real
- **Detectar anomalías** o picos automáticamente  
- **Sugerir causas probables** de comportamientos observados
- **Explicar métricas** a personas no técnicas
- **Comparar períodos históricos** similares
- **Mantener la privacidad** de tus datos (todo local, sin APIs externas)

---

## 🔄 ¿Cómo funciona?

El proceso ensambla dos mundos: **visualización** y **IA Generativa**:

1. **Captura de datos del gráfico**: Se extraen los datos relevantes del panel de Grafana
2. **Procesamiento por LLM**: La información se envía a un modelo de lenguaje local (via Ollama)
3. **Generación de insights**: La LLM devuelve análisis/resúmenes en lenguaje natural
4. **Visualización integrada**: Los resultados se presentan junto al gráfico original

---

## 📋 Requisitos previos

### Node.js
Necesitás **Node.js** para el desarrollo del plugin. Recomendamos usar `nvm`:

```bash
# Descargar e instalar nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# (Opcional) Cargar nvm sin reiniciar la terminal:
. "$HOME/.nvm/nvm.sh"

# Instalar Node.js versión 22:
nvm install 22
```

### Verificar instalación:
```bash
node -v       # "v22.14.0"
nvm current   # "v22.14.0"
npm -v        # "10.9.2"
```

### Ollama (para LLM local)
```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelo (ejemplo con Moondream - 1.8B parámetros)
ollama pull moondream

# O usar un modelo más potente como Llama 3.2 Vision
ollama pull llama3.2-vision
```

---

## 🚀 Configuración paso a paso

### 1. Clonar y levantar el entorno

```bash
git clone [tu-repo]
cd grafana-plugin-local

# Levantar Grafana + TimescaleDB
docker-compose up -d
```

Grafana estará disponible en: http://localhost:3000

### 2. Poblar la base de datos con datos financieros

Tenés dos opciones para obtener datos del S&P 500:

**Opción A: API de Yahoo Finance (puede tener rate limiting)**
```bash
poetry run python upload/download.py
```

**Opción B: Ingestión local desde CSV (recomendado)**
```bash
poetry run python data_ingestion/local_ingest.py
```

### 3. Instalar el plugin

```bash
# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

Si hay problemas de permisos:
```bash
sudo chown -R $USER:$USER .
```

### 4. Reiniciar containers
```bash
docker-compose restart
```

---

## 📊 Uso del plugin

Una vez instalado, verás el panel "Chart Analyzer" en la esquina superior derecha de tus dashboards.

### Tipos de análisis disponibles:

- **🔍 Análisis de tendencias**: Detecta patrones crecientes o decrecientes
- **⚠️ Detección de anomalías**: Identifica picos o valores atípicos  
- **📈 Comparativa histórica**: Contrasta períodos similares
- **💡 Explicación para no técnicos**: Traduce métricas a lenguaje simple

### Configuración del plugin:

1. Hace clic en los **tres puntos** del panel
2. Selecciona **"Edit"**
3. Configura:
   - **URL de la LLM**: Por defecto `http://localhost:11434` (Ollama)
   - **Modelo**: `moondream`, `llama3.2-vision`, etc.
   - **Prompts personalizados**: Editá los prompts según tus necesidades

---

## 🛠️ Desarrollo

### Estructura del proyecto:
```
src/
├── components/          # Componentes React del panel
├── img/                # Recursos gráficos  
├── module.ts           # Configuración del plugin
├── plugin.json         # Metadatos del plugin
└── types.ts            # Definiciones de tipos

data_ingestion/         # Scripts para poblar datos
├── download.py         # Descarga desde Yahoo Finance
└── local_ingest.py     # Ingesta desde CSV local

provisioning/           # Configuración de Grafana
├── dashboards/         # Dashboards predefinidos
└── datasources/        # Configuración de TimescaleDB
```

### Comandos útiles:

```bash
# Desarrollo con hot-reload
npm run dev

# Build para producción
npm run build

# Linting
npm run lint

# Tests
npm run test
```

---

## 🔒 Ventajas de la implementación local

- **Privacidad**: Tus datos nunca salen de tu infraestructura
- **Velocidad**: Sin latencia de APIs externas
- **Control total**: Elegís el modelo y configuración que mejor se adapte
- **Sin costos por API**: Una vez configurado, no hay límites de uso
- **Personalización**: Prompts y comportamiento completamente customizables

---

## 📦 Distribución

Para distribuir el plugin (públicamente o en privado), debe estar firmado:

```bash
# Firmar plugin (solo para distribución)
npm run sign
```

> ❗ **Nota**: No es necesario firmar durante el desarrollo local. El entorno Docker permite ejecutarlo sin firma.

---

## 🤝 Casos de uso

### Monitoreo de infraestructura
- Detectar picos de CPU/memoria automáticamente
- Explicar correlaciones entre métricas
- Sugerir optimizaciones basadas en patrones

### Análisis financiero  
- Interpretar movimientos de acciones
- Detectar anomalías en trading
- Comparar performance histórica

### Business Intelligence
- Explicar KPIs a stakeholders no técnicos
- Identificar tendencias en ventas
- Alertas inteligentes sobre métricas críticas

---

## 🔧 Troubleshooting

### Plugin no aparece en Grafana
```bash
# Verificar que el build fue exitoso
npm run build

# Reiniciar containers
docker-compose restart
```

### Ollama no responde
```bash
# Verificar que Ollama está corriendo
ollama list

# Reiniciar servicio
ollama serve
```

### Problemas de permisos
```bash
sudo chown -R $USER:$USER .
```

---

## 🚀 Próximos pasos

- Experimentá con diferentes modelos de LLM según tu hardware
- Personalizá los prompts para casos de uso específicos
- Integrá con tus propias fuentes de datos
- Expandí los tipos de análisis disponibles

**¿Necesitás ayuda implementando esto en tu organización?** No dudes en contactarnos.

---

*Hacemos IA aplicada con sentido para crear soluciones con criterio.*
