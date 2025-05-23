# Plugin de Panel para Grafana: Interpretación con LLM Local

Este proyecto es un punto de partida para construir un plugin de panel para Grafana que permite interpretar visualizaciones usando un modelo multimodales de lenguajes local como LLama 3.2 Vision o GPT-4o Vision.

Este repositorio es un fork del desarrollado por Tom Glenn en este [enlace](https://github.com/tomglenn/tomglenn-openaianalyser-panel).

---

## ¿Qué es un plugin en Grafana?

Los plugins son paneles que permiten agregar nuevos tipos de visualizaciones o interacciones en un dashboard de Grafana. En este caso, el objetivo es permitir que un modelo de lenguaje interprete los gráficos y genere descripciones automáticas útiles para el usuario.

Algunos ejemplos de uso:
- Interpretar una tendencia en un gráfico.
- Detectar anomalías o picos.
- Sugerir causas probables de un comportamiento observado.
- Explicar métricas a personas no técnicas.

---

## Requisitos previos

Antes de comenzar, asegurate de tener **Node.js** instalado. Recomendamos usar `nvm` para instalar la versión correcta de forma sencilla:

###

Instalar Node.js con `nvm`

```bash
# Descargar e instalar nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# (Opcional) Cargar nvm sin reiniciar la terminal:
. "$HOME/.nvm/nvm.sh"

# Instalar Node.js versión 22:
nvm install 22
```

### Verificar que esté instalado correctamente:

```bash
node -v       # "v22.14.0"
nvm current   # "v22.14.0"
npm -v        # "10.9.2"
```

## Si quieres desarrollarlo puedes:

### 1. Instalar dependencias
```bash
npm install
```
## 2. Ejecutar el plugin en modo desarrollo
```bash
npm run dev
```

## 3. Para empaquetar el plugin para producción
```bash
npm run build
```

## Distribuir tu plugin

Para distribuir un plugin (públicamente o en privado), debe estar firmado. Esto asegura que Grafana pueda verificar su autenticidad.

    ❗ No es necesario firmar durante el desarrollo local. El entorno Docker de desarrollo ya permite ejecutarlo sin firma.
