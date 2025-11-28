# Trabajo Final: Análisis Inteligente de la Demanda Energética

**1. Presentación del Grupo**

Este proyecto ha sido desarrollado de manera individual, abarcando el ciclo completo de ingeniería de software: desde el diseño de la arquitectura y la base de datos, hasta la implementación del backend, frontend y la integración de servicios de Inteligencia Artificial.
●   **Rol:** Desarrollador Full Stack & Arquitecto de Soluciones.

**2. Presentación del Proyecto**

**Nombre de la Aplicación:** Análisis Inteligente de la Demanda ⚡🤖

Este proyecto consiste en una aplicación web diseñada para la gestión y el análisis avanzado del consumo energético. El sistema actúa como un auditor virtual inteligente, permitiendo a los gestores energéticos transformar datos brutos en decisiones estratégicas.

La aplicación permite cargar históricos de consumo (curvas de carga), establecer un año base para definir el comportamiento "normal", y utilizar la Inteligencia Artificial de Google (Gemini) para comparar un día objetivo contra esa línea base. El objetivo es detectar automáticamente anomalías, cambios en los patrones de consumo y oportunidades de ahorro que de otro modo serían invisibles.

**3. Problemática Principal**

A pesar de la proliferación de medidores inteligentes, la gestión energética eficiente se ve obstaculizada por tres barreras críticas:

1.  **Dificultad para Definir la "Normalidad":** El consumo energético es dinámico y varía por hora, día de la semana y estación del año. Sin una línea base contextual, es casi imposible saber si un pico de consumo es una anomalía costosa o parte de la operación normal.
2.  **Brecha de Interpretación entre Datos y Causa Raíz:** Las plataformas tradicionales (como los sistemas SCADA) muestran gráficos, pero no explican el "porqué" de una anomalía. Esta tarea de análisis de causa raíz requiere una inversión significativa de tiempo y conocimiento experto.
3.  **Ineficacia de las Alertas por Umbral:** Las alertas tradicionales que se basan en umbrales fijos (ej. "alertar si el consumo supera los 200 kW") son incapaces de detectar problemas sutiles pero costosos, como el desperdicio acumulativo por cambios en los hábitos operativos (ej. encender la climatización una hora antes de lo necesario cada día).

**4. Propuesta de Solución**

La solución es una plataforma de **Auditoría Energética Asistida por IA** que automatiza el análisis cognitivo, abordando directamente los problemas mencionados.

●   **Comparativa Contextual Automatizada:** El servicio de backend (`energy_service.py`) procesa los datos históricos de un año base seleccionado por el usuario. Utilizando la librería **Pandas**, construye una curva de consumo "esperado" para un día específico, tomando en cuenta el día de la semana y la estacionalidad. Esta línea base se compara, punto por punto, con los datos reales del día objetivo.
●   **Diagnóstico con IA Generativa:** Las desviaciones significativas entre la curva real y la esperada se envían al servicio `chat_service.py`. Este servicio formatea un prompt técnico y consulta al modelo **Google Gemini**, que analiza las discrepancias y genera un diagnóstico en lenguaje natural, identificando anomalías y emitiendo recomendaciones operativas.

**5. Alcance de la Solución**

El alcance actual del proyecto (MVP) abarca las siguientes funcionalidades:

●   **Gestión de Datos:** Carga masiva de históricos de consumo en formato CSV a través de un endpoint de API REST, con almacenamiento persistente en una base de datos PostgreSQL.
●   **Visualización Interactiva:** Un dashboard en React que presenta gráficas (usando **Recharts**) superponiendo la curva de consumo real (área azul) contra la línea base histórica esperada (línea punteada).
●   **Análisis Explicativo por IA:** Generación de un reporte diagnóstico que incluye: un **estado** (Normal, Alerta, Crítico), un **resumen ejecutivo**, una lista de **anomalías** detectadas y una **recomendación** operativa.
●   **Arquitectura Escalable:** Se implementa una arquitectura N-Tier y patrones de diseño como el **Patrón Observer** (`observers.py`), que permite desacoplar funcionalidades secundarias (como el logging o futuras notificaciones) del servicio de análisis principal, facilitando la expansión del sistema.

**Limitaciones Actuales:** El sistema opera con carga de datos bajo demanda (modo "offline"). No incluye, en esta fase, ingesta de datos en tiempo real (streaming) desde medidores IoT.

**6. Presentación de las Herramientas**

Para construir esta solución se seleccionó un stack tecnológico moderno y eficiente:

●   **Frontend (Capa de Presentación):**
    ○   **Framework:** React con TypeScript para un desarrollo robusto y tipado.
    ○   **Build Tool:** Vite para un entorno de desarrollo ultra-rápido.
    ○   **UI y Estilos:** TailwindCSS para un diseño basado en utilidades y Lucide-React para la iconografía.
    ○   **Visualización:** Recharts, librería especializada para la renderización de las curvas de carga.

●   **Backend (Capa de Lógica de Negocio):**
    ○   **Framework:** FastAPI sobre Python 3.10+ para crear una API REST asíncrona y de alto rendimiento.
    ○   **Procesamiento de Datos:** Pandas para la manipulación de series temporales y el cálculo de las líneas base.
    ○   **ORM y Base de Datos:** SQLAlchemy como ORM para interactuar con la base de datos relacional PostgreSQL.

●   **Inteligencia Artificial:**
    ○   **Modelo:** Google Gemini (a través de la librería `google-generativeai`) para el razonamiento y la generación de los diagnósticos operativos.

**7. Presentación de la Solución (Funcionamiento)**

El flujo de trabajo de la aplicación se ha diseñado para ser intuitivo, dividiéndose en tres pasos claros para el usuario dentro del dashboard:

1.  **Configuración y Carga de Datos:** El usuario introduce un identificador para el medidor a analizar (Device ID). Si es necesario, utiliza el componente de "Carga Masiva" para subir un archivo CSV con los datos históricos de consumo, que son procesados y almacenados por el backend.
2.  **Definición del Análisis:** El usuario selecciona el **Año Base** (el año histórico que servirá como referencia para el comportamiento "normal") y la **Fecha Objetivo** (el día específico que desea analizar). Además, debe proporcionar su API Key de Google Gemini para la sesión actual.
3.  **Ejecución e Interpretación:** Al hacer clic en "Analizar", el frontend solicita al backend que realice la comparativa. En segundos, la interfaz se actualiza mostrando la gráfica comparativa y el diagnóstico completo generado por la IA, permitiendo al gestor interpretar los resultados y tomar acciones informadas.
