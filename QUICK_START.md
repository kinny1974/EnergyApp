# 🎯 Guía Rápida - Nuevas Funcionalidades del Dashboard

## 🚀 Cómo Usar las Nuevas Funcionalidades

### 1. **Ver las Mejoras en Acción**
El servidor de desarrollo está corriendo en: **http://localhost:3001/**

---

## 📊 Nuevas Visualizaciones Disponibles

### **KPI Cards** (4 Tarjetas Métricas)
Al ejecutar un análisis, verás 4 tarjetas en la parte superior:

1. **Desviación Máxima** 📈
   - Muestra el mayor % de desviación del día
   - Indicador rojo si > 20%

2. **Desviación Promedio** 📊
   - Promedio de todas las desviaciones
   - Color naranja

3. **Pico de Demanda** ⚡
   - Valor máximo en kW
   - Color índigo

4. **Hora Pico** 🕐
   - Hora exacta del consumo máximo
   - Color azul

---

### **Análisis por Período del Día** 🌅
Divide el día en 4 períodos con iconos visuales:

- 🌙 **Madrugada** (00:00 - 06:00)
- 🌅 **Mañana** (06:00 - 12:00)
- ☀️ **Tarde** (12:00 - 18:00)
- 🌆 **Noche** (18:00 - 24:00)

Para cada período verás:
- Demanda Real promedio
- Demanda Esperada promedio
- % de Desviación con indicador ↑/↓

---

### **Tabla Top 10** 📋
Muestra las 10 horas con mayor desviación:

| Columna | Descripción |
|---------|-------------|
| **Hora** | Timestamp |
| **Real (kW)** | Demanda medida |
| **Esperado (kW)** | Demanda baseline |
| **Diferencia** | Absoluta en kW |
| **Desviación** | Porcentaje |

- ✅ Colores: Rojo (exceso) / Verde (ahorro)
- ✅ Resalta desviaciones > 20%

---

### **Histograma de Distribución** 📊
Gráfico de barras mostrando frecuencias de demanda:

Rangos:
- 0-10 kW
- 10-20 kW
- 20-30 kW
- 30-40 kW
- 40-50 kW
- 50+ kW

Cada barra muestra:
- Cantidad de lecturas
- Porcentaje del total
- Color graduado único

---

### **Exportación a CSV** 💾
Botón "Exportar CSV" en el header (solo visible con resultados):

**Contenido del CSV:**
- Hora
- Demanda Real (kW)
- Demanda Esperada (kW)
- Desviación (%)

**Nombre del archivo:**
`analisis_{medidor}_{fecha}.csv`

---

## 🤖 Integración con Chatbot

### **Funcionamiento Automático**
Ahora puedes hacer preguntas como:

```
"compara la curva de carga del día 20 de octubre de 2025, 
con la curva de carga promedio para el año 2024, 
del medidor 36075003"
```

El chatbot automáticamente:
1. ✅ Detecta los parámetros (medidor, fecha, año base)
2. ✅ Actualiza los campos del formulario
3. ✅ Ejecuta el análisis
4. ✅ Muestra TODAS las visualizaciones nuevas

---

## 🎨 Mejoras Visuales

### **Antes**
- Gráfico simple
- Análisis de IA básico
- Sin métricas destacadas

### **Ahora** ✨
- ✅ 4 KPI Cards
- ✅ Gráfico mejorado
- ✅ 4 Indicadores de período
- ✅ Tabla comparativa
- ✅ Histograma de distribución
- ✅ Análisis de IA
- ✅ Botón de exportación

---

## ❌ Funcionalidades Removidas

Las siguientes opciones ya NO están disponibles:

- ❌ Radio buttons "Base de Datos" vs "Archivo CSV"
- ❌ Upload de archivo CSV base
- ❌ Carga masiva de datos CSV

### ¿Por qué?
- Simplificación de la interfaz
- Menos errores potenciales
- **Todos los datos ahora vienen de la base de datos**

---

## 🔍 Cómo Probar

### Opción 1: Uso Manual
1. Abre http://localhost:3001/
2. Selecciona un medidor
3. Selecciona un año base
4. Selecciona una fecha
5. Click en "Analizar"
6. ¡Disfruta las nuevas visualizaciones!

### Opción 2: Uso con Chatbot
1. Abre http://localhost:3001/
2. Click en el botón del chatbot (⚡)
3. Escribe o selecciona una pregunta sugerida:
   - "compara la curva de carga del día 20 de octubre de 2025..."
4. El análisis se ejecuta automáticamente

---

## 📱 Responsive Design

Todas las nuevas visualizaciones son responsive:

### Mobile (< 768px)
- KPI Cards: 2 columnas
- Períodos: 2 columnas
- Tabla: Scroll horizontal
- Histograma: Ajustado

### Desktop (≥ 768px)
- KPI Cards: 4 columnas
- Períodos: 4 columnas
- Tabla: Vista completa
- Sidebar: 4 cols / Main: 8 cols

---

## 🎯 Casos de Uso

### 1. Identificar Horas Críticas
➡️ Usa la **Tabla Top 10** para ver exactamente cuándo hubo las mayores desviaciones

### 2. Comparar Períodos del Día
➡️ Usa los **Indicadores de Período** para ver si el problema es en la mañana, tarde, etc.

### 3. Analizar Distribución de Consumo
➡️ Usa el **Histograma** para entender el comportamiento general del medidor

### 4. Monitorear KPIs
➡️ Usa las **KPI Cards** para tener una vista rápida de métricas clave

### 5. Exportar Datos
➡️ Usa el **botón CSV** para generar reportes o análisis externos

---

## 🐛 Troubleshooting

### "No veo las nuevas visualizaciones"
- ✅ Asegúrate de ejecutar un análisis primero
- ✅ Verifica que haya datos en la BD para ese medidor/fecha
- ✅ Refresca la página (Ctrl+R)

### "El chatbot no funciona"
- ✅ Verifica que el backend esté corriendo (port 8000)
- ✅ Revisa la consola del navegador (F12)

### "Error al exportar CSV"
- ✅ Verifica que haya resultados del análisis
- ✅ Comprueba permisos de descarga del navegador

---

## 📞 Soporte

Si encuentras algún problema:
1. Revisa `IMPLEMENTATION_SUMMARY.md` para detalles técnicos
2. Revisa la consola del navegador (F12)
3. Verifica logs del backend

---

## ✅ Checklist de Pruebas

Prueba cada funcionalidad:

- [ ] KPI Cards se muestran correctamente
- [ ] Indicadores de período calculan bien
- [ ] Tabla Top 10 ordena por desviación
- [ ] Histograma muestra distribución
- [ ] Botón CSV descarga archivo
- [ ] Chatbot detecta parámetros
- [ ] Análisis automático funciona
- [ ] Responsive en mobile
- [ ] Sin errores en consola

---

**¡Disfruta el nuevo dashboard! 🎉**
