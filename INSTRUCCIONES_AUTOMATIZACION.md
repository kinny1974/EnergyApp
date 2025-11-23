# 🔧 Instrucciones para Activar la Automatización del Chatbot

## Problema Identificado
El archivo `EnergyDashboard.tsx` **NO TIENE** la función `handleParametersExtracted` que permite que el chatbot active automáticamente el análisis.

## Solución: Agregar la Función

### Paso 1: Ubicar dónde agregar el código

Abre `C:\EnergyApp\frontend\src\components\EnergyDashboard.tsx` y busca la función `handleAnalyze`.

Deberías ver algo así (alrededor de la línea 135-155):

```typescript
  const handleAnalyze = async () => {
    if (!targetDate) return setError("Selecciona una fecha objetivo");
    if (baseDataMode === 'file' && !baseFile) return setError("Por favor selecciona un archivo CSV base.");
    if (!selectedBaseYear) return setError("Por favor selecciona un año base.");

    setLoading(true);
    setError('');
    setResult(null);

    try {
      let data;
      if (baseDataMode === 'file' && baseFile) {
        data = await analyzeEnergyWithFile(deviceId, selectedBaseYear, targetDate, baseFile);
      } else {
        data = await analyzeEnergy(deviceId, selectedBaseYear, targetDate);
      }
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Error en el análisis");
    } finally {
      setLoading(false);
    }
  };
```

### Paso 2: Agregar INMEDIATAMENTE DESPUÉS la nueva función

Justo después del cierre de `handleAnalyze` (después del `};`), agrega este código:

```typescript
  // 🤖 Callback para automatización desde chatbot
  const handleParametersExtracted = (params: any, type: string) => {
    console.log('🔄 [DASHBOARD] Parameters extracted from chatbot:', { params, type });
    
    // Verificar que sea una consulta de comparación de curva de carga
    if (type === 'load_curve_comparison' && params) {
      console.log('✅ [DASHBOARD] Load curve comparison detected');
      
      // Validar que todos los parámetros requeridos estén presentes
      const requiredParams = ['device_id', 'target_date', 'base_year'];
      const missingParams = requiredParams.filter(param => !params[param]);
      
      if (missingParams.length > 0) {
        console.error('❌ [DASHBOARD] Missing required parameters:', missingParams);
        setError(`Faltan parámetros: ${missingParams.join(', ')}`);
        setMsg('');
        return;
      }
      
      // Actualizar los estados del formulario con los parámetros del chatbot
      console.log('📝 [DASHBOARD] Updating form states...');
      if (params.device_id) {
        setDeviceId(params.device_id);
        console.log('   ✓ Device ID:', params.device_id);
      }
      if (params.base_year) {
        setSelectedBaseYear(params.base_year);
        console.log('   ✓ Base Year:', params.base_year);
      }
      if (params.target_date) {
        setTargetDate(params.target_date);
        console.log('   ✓ Target Date:', params.target_date);
      }
      
      // Mostrar mensaje de inicio
      setMsg('🤖 Parámetros detectados desde chatbot. Iniciando análisis automático...');
      setError('');
      
      // Iniciar el análisis automáticamente
      console.log('🚀 [DASHBOARD] Starting automatic analysis...');
      setLoading(true);
      setResult(null);
      
      // Pequeño delay para que la UI se actualice con los nuevos valores
      setTimeout(() => {
        analyzeEnergy(params.device_id, params.base_year, params.target_date)
          .then(data => {
            console.log('✅ [DASHBOARD] Analysis completed successfully from chatbot');
            setResult(data);
            setMsg('✅ Análisis completado automáticamente desde el chatbot.');
            setError('');
          })
          .catch(err => {
            console.error('❌ [DASHBOARD] Analysis error:', err);
            setError(err.message || "Error en el análisis automático");
            setMsg('');
          })
          .finally(() => {
            setLoading(false);
            console.log('🏁 [DASHBOARD] Analysis process finished');
          });
      }, 300);
      
    } else {
      console.log('ℹ️ [DASHBOARD] Non-load-curve type received:', type);
    }
  };
```

### Paso 3: Conectar con EnergyChatbot

Busca al final del archivo donde se renderiza el chatbot. Deberías ver algo como:

```typescript
      {/* Chatbot flotante */}
      <EnergyChatbot />
```

**REEMPLÁZALO** con:

```typescript
      {/* Chatbot flotante */}
      <EnergyChatbot 
        context={{ device_id: deviceId, fecha: targetDate, base_year: selectedBaseYear }}
        onParametersExtracted={handleParametersExtracted}
      />
```

## Verificación

### 1. Compilar
```bash
cd frontend
npm run build
```

Debe compilar sin errores.

###2. Probar

1. Inicia el servidor: `npm run dev`
2. Abre http://localhost:3001/
3. Abre la consola del navegador (F12)
4. Abre el chatbot
5. Escribe:
   ```
   compara la curva de carga del día 20 de octubre de 2025,
   con la curva promedio del año 2024,
   del medidor 36075003
   ```

6. **Deberías ver en la consola**:
   ```
   🔄 [DASHBOARD] Parameters extracted from chatbot: {...}
   ✅ [DASHBOARD] Load curve comparison detected
   📝 [DASHBOARD] Updating form states...
      ✓ Device ID: 36075003
      ✓ Base Year: 2024
      ✓ Target Date: 2025-10-20
   🚀 [DASHBOARD] Starting automatic analysis...
   ```

7. **Y en la interfaz**:
   - Los campos se llenan automáticamente
   - Se muestra "Procesando..."
   - El análisis se ejecuta
   - Se muestran los resultados

## Ubicación Exacta en el Archivo

```
Línea ~135: función handleAnalyze
Línea ~155: fin de handleAnalyze (};)
Línea ~156: AGREGAR AQUÍ handleParametersExtracted
Línea ~215: AGREGAR AQUÍ la función completa

...

Línea ~434: Buscar <EnergyChatbot />
Línea ~434: REEMPLAZAR con la versión que incluye las props
```

## Si algo sale mal

1. **Error de compilación**: Verifica que hayas cerrado correctamente todas las llaves `{}`
2. **No se ejecuta**: Verifica la consola del navegador para ver los logs
3. **Falta la función**: Asegúrate de agregarla DESPUÉS de handleAnalyze pero ANTES del return

## Alternativa Rápida

Si prefieres, puedo crear un nuevo archivo completo con todos los cambios ya aplicados y sobrescribirlo. ¿Prefieres eso o intentarlo manualmente con estas instrucciones?
