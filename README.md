# **Análisis Inteligente de la Demanda ⚡🤖**

Una aplicación web para la gestión y análisis inteligente de consumo energético. Utiliza inteligencia artificial (Google Gemini) para comparar curvas de carga reales contra comportamientos históricos, detectando anomalías y cambios de hábitos automáticamente.

## **📋 Tabla de Contenidos**

1. [Características Principales](https://www.google.com/search?q=%23-caracter%C3%ADsticas-principales)  
2. [Requisitos Previos](https://www.google.com/search?q=%23-requisitos-previos)  
3. [Instalación y Configuración](https://www.google.com/search?q=%23-instalaci%C3%B3n-y-configuraci%C3%B3n)  
   * [Base de Datos](https://www.google.com/search?q=%231-base-de-datos-postgresql)  
   * [Backend (Python)](https://www.google.com/search?q=%232-backend-fastapi)  
   * [Frontend (React \+ Vite)](https://www.google.com/search?q=%233-frontend-react)  
4. [Ejecución](https://www.google.com/search?q=%23-ejecuci%C3%B3n)  
5. [Manual de Usuario](https://www.google.com/search?q=%23-manual-de-usuario)

## **🚀 Características Principales**

* **Arquitectura N-Tier:** Separación lógica en Capas de Presentación, Negocio y Datos.  
* **Patrón Observer:** Sistema de notificaciones interno para auditoría y alertas críticas.  
* **Análisis con IA:** Integración con **Gemini 2.0 Flash** para diagnósticos operativos.  
* **Visualización Interactiva:** Gráficas comparativas (Real vs. Esperado) usando Recharts.  
* **Gestión de Datos:** Carga masiva de históricos vía CSV y almacenamiento en PostgreSQL.

## **🛠 Requisitos Previos**

Antes de comenzar, asegúrate de tener instalado:

* **Python 3.10+**  
* **Node.js v18+** (Recomendado v20 o superior)  
* **PostgreSQL** (Corriendo y accesible)  
* **API Key de Google Gemini** (Obtenla en Google AI Studio)

## **⚙️ Instalación y Configuración**

### **1\. Base de Datos (PostgreSQL)**

Asegúrate de que tu servidor PostgreSQL esté corriendo. La aplicación espera la siguiente configuración por defecto (ajustable en el backend):

* **Host:** localhost  
* **Puerto:** 54321  
* **Base de Datos:** sgcnmdb  
* **Usuario:** administrador  
* **Contraseña:** marcela2005

La tabla m\_lecturas se creará automáticamente al iniciar el backend si no existe.

### **2\. Backend (FastAPI)**

Navega a la carpeta backend:

cd EnergyApp/backend

1. **Crear entorno virtual (opcional pero recomendado):**  
   python \-m venv venv  
   \# Windows  
   venv\\Scripts\\activate  
   \# Mac/Linux  
   source venv/bin/activate

2. **Instalar dependencias:**  
   pip install \-r requirements.txt

3. Configurar variables de entorno:  
   Crea un archivo .env en la carpeta backend (si no existe) con el siguiente contenido:  
   DATABASE\_URL=postgresql+psycopg2://administrador:marcela2005@localhost:54321/sgcnmdb

### **3\. Frontend (React)**

Navega a la carpeta frontend:

cd EnergyApp/frontend

1. **Instalar dependencias:**  
   npm install

## **▶️ Ejecución**

Para usar la aplicación, necesitas correr el backend y el frontend simultáneamente en dos terminales distintas.

**Terminal 1: Backend**

cd EnergyApp/backend  
\# Ejecuta el servidor desde el módulo app  
python \-m app.main

*Verás el mensaje: Uvicorn running on http://0.0.0.0:8000*

**Terminal 2: Frontend**

cd EnergyApp/frontend  
npm run dev

*Verás el mensaje: Local: http://localhost:3000/*

## **📖 Manual de Usuario**

Abre tu navegador en **http://localhost:3000** para ver el panel de control.

### **Paso 1: Configurar Medidor y Cargar Datos**

1. En el panel izquierdo, ingresa el **Device ID** (ej. MED-001).  
2. Si es la primera vez o quieres agregar datos, ve a la sección **"Carga Masiva (CSV)"**.  
3. Sube un archivo .csv con el siguiente formato (encabezados en minúscula):

| timestamp | value | kvarhd (opcional) |
| :---- | :---- | :---- |
| 2023-01-01 00:15:00 | 120.5 | 10.2 |
| 2023-01-01 00:30:00 | 125.0 | 11.0 |

4.   
   *Nota: El sistema necesita al menos un año de datos histórico para crear una "Línea Base" fiable.*

### **Paso 2: Configurar Análisis**

1. Haz clic en el botón de **Lupa** 🔍 junto al Device ID para cargar los años disponibles.  
2. **Año Base (Baseline):** Selecciona un año histórico (ej. 2023). El sistema usará este año para "aprender" el comportamiento normal.  
3. **Gemini API Key:** Pega tu clave de Google AI Studio. (No se guarda, solo se usa para la sesión).  
4. **Fecha Objetivo:** Selecciona el día específico que quieres analizar y comparar (ej. un día de 2024 o 2025).

### **Paso 3: Interpretar Resultados**

Haz clic en **"Analizar"**. El sistema procesará los datos y mostrará:

* **Gráfica Principal:**  
  * **Línea Punteada (Gris):** Es el consumo *esperado* según el comportamiento histórico de ese día de la semana (Línea Base).  
  * **Área Azul:** Es el consumo *real* del día seleccionado.  
* **Diagnóstico Observer (IA):**  
  * **Estado:** NORMAL, ALERTA o CRITICO.  
  * **Resumen:** Explicación en lenguaje natural de lo que sucedió.  
  * **Anomalías:** Lista puntual de eventos extraños (ej. "Pico inusual a las 03:00 AM").  
  * **Recomendación:** Sugerencia operativa para el gestor energético.

## **🆘 Solución de Problemas Comunes**

* **Error "Could not resolve...":** Asegúrate de estar ejecutando el frontend desde la carpeta correcta donde está vite.config.ts.  
* **Error de conexión DB:** Verifica que las credenciales en backend/.env sean correctas y que el puerto 54321 esté abierto.  
* **Gráfica vacía:** Verifica que hayas subido datos para la "Fecha Objetivo" seleccionada y que existan datos históricos para el "Año Base".