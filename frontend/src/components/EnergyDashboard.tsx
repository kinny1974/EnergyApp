import React, { useState, useEffect } from 'react';
import EnergyChatbot from './EnergyChatbot';
import {
  Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ComposedChart, Area, Bar, BarChart, Cell
} from 'recharts';
import {
  Activity, AlertTriangle, Zap, CheckCircle,
  BrainCircuit, Database, TrendingUp, TrendingDown,
  Download, Clock, Sun, Moon, Sunrise, Sunset
} from 'lucide-react';
import {
  getAvailableYears, analyzeEnergy, AnalysisResult,
  getAvailableDevices, DeviceInfo
} from '../services/api';

// Props para el componente StatusBadge
interface StatusBadgeProps {
  status: 'NORMAL' | 'ALERTA' | 'CRITICO' | 'DESCONOCIDO';
}

// Interfaz para métricas calculadas
interface DashboardMetrics {
  maxDeviation: number;
  avgDeviation: number;
  peakHour: string;
  peakValue: number;
  totalEnergyActual: number;
  totalEnergyExpected: number;
  deviationPercentage: number;
}

const EnergyDashboard: React.FC = () => {
  // --- Estado Local Tipado ---
  const [deviceId, setDeviceId] = useState<string>('');
  const [selectedBaseYear, setSelectedBaseYear] = useState<string | number>('');
  const [targetDate, setTargetDate] = useState<string>('');
  const [years, setYears] = useState<number[]>([]);
  const [devices, setDevices] = useState<DeviceInfo[]>([]);

  // Estado de UI
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>('');
  const [msg, setMsg] = useState<string>('');
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);

  // Cargar dispositivos al montar el componente
  useEffect(() => {
    const loadDevices = async () => {
      try {
        const data = await getAvailableDevices();
        setDevices(data.devices);
        if (data.devices.length > 0) {
          setDeviceId(data.devices[0].deviceid);
        }
      } catch (err) {
        console.warn("No se pudieron cargar los dispositivos:", err);
      }
    };
    loadDevices();
  }, []);

  // Refrescar años cuando cambia el medidor
  useEffect(() => {
    if (deviceId) {
      refreshYears();
    } else {
      setYears([]);
      setSelectedBaseYear('');
    }
  }, [deviceId]);

  // Calcular métricas cuando cambia el resultado
  useEffect(() => {
    if (result && result.chart_data) {
      calculateMetrics(result.chart_data);
    }
  }, [result]);

  // --- Funciones de cálculo ---
  const calculateMetrics = (chartData: any[]) => {
    if (!chartData || chartData.length === 0) return;

    const deviations = chartData.map(d => Math.abs(((d.value - d.mean) / d.mean) * 100));
    const maxDeviation = Math.max(...deviations);
    const avgDeviation = deviations.reduce((a, b) => a + b, 0) / deviations.length;

    const peakPoint = chartData.reduce((max, p) => p.value > max.value ? p : max, chartData[0]);

    const totalActual = chartData.reduce((sum, d) => sum + d.value, 0);
    const totalExpected = chartData.reduce((sum, d) => sum + d.mean, 0);
    const deviationPercentage = ((totalActual - totalExpected) / totalExpected) * 100;

    setMetrics({
      maxDeviation,
      avgDeviation,
      peakHour: peakPoint.time_str,
      peakValue: peakPoint.value,
      totalEnergyActual: totalActual,
      totalEnergyExpected: totalExpected,
      deviationPercentage
    });
  };

  const getPeriodData = () => {
    if (!result || !result.chart_data) return [];

    const periods = [
      { name: 'Madrugada', icon: Moon, start: 0, end: 6, color: '#818cf8' },
      { name: 'Mañana', icon: Sunrise, start: 6, end: 12, color: '#fbbf24' },
      { name: 'Tarde', icon: Sun, start: 12, end: 18, color: '#f59e0b' },
      { name: 'Noche', icon: Sunset, start: 18, end: 24, color: '#6366f1' }
    ];

    return periods.map(period => {
      const periodData = result.chart_data.filter((d: any) => {
        const hour = parseInt(d.time_str.split(':')[0]);
        return hour >= period.start && hour < period.end;
      });

      const avgActual = periodData.reduce((sum: number, d: any) => sum + d.value, 0) / periodData.length;
      const avgExpected = periodData.reduce((sum: number, d: any) => sum + d.mean, 0) / periodData.length;
      const deviation = ((avgActual - avgExpected) / avgExpected) * 100;

      return {
        ...period,
        avgActual,
        avgExpected,
        deviation
      };
    });
  };

  const getDistributionData = () => {
    if (!result || !result.chart_data) return [];

    const bins = [
      { range: '0-10', min: 0, max: 10 },
      { range: '10-20', min: 10, max: 20 },
      { range: '20-30', min: 20, max: 30 },
      { range: '30-40', min: 30, max: 40 },
      { range: '40-50', min: 40, max: 50 },
      { range: '50+', min: 50, max: Infinity }
    ];

    return bins.map(bin => {
      const count = result.chart_data.filter((d: any) =>
        d.value >= bin.min && d.value < bin.max
      ).length;

      return {
        range: bin.range,
        count,
        percentage: (count / result.chart_data.length) * 100
      };
    });
  };

  const getHourlyComparisonTable = () => {
    if (!result || !result.chart_data) return [];

    return result.chart_data
      .map((d: any) => ({
        time: d.time_str,
        actual: d.value,
        expected: d.mean,
        deviation: ((d.value - d.mean) / d.mean) * 100,
        diff: d.value - d.mean
      }))
      .sort((a: any, b: any) => Math.abs(b.deviation) - Math.abs(a.deviation))
      .slice(0, 10);
  };

  // --- Manejadores de Eventos ---
  const refreshYears = async () => {
    if (!deviceId) return;
    try {
      const data = await getAvailableYears(deviceId);
      setYears(data.years);
      if (data.years.length > 0 && !selectedBaseYear) {
        setSelectedBaseYear(data.years[0]);
      }
    } catch (err) {
      console.warn("No se pudieron cargar años:", err);
    }
  };

  const handleAnalyze = async () => {
    if (!targetDate) return setError("Selecciona una fecha objetivo");
    if (!selectedBaseYear) return setError("Por favor selecciona un año base.");

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await analyzeEnergy(deviceId, selectedBaseYear, targetDate);
      setResult(data);
      setMsg('✅ Análisis completado exitosamente.');
    } catch (err: any) {
      setError(err.message || "Error en el análisis");
    } finally {
      setLoading(false);
    }
  };

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

  // Función de exportación
  const exportToCSV = () => {
    if (!result || !result.chart_data) return;

    const csvContent = [
      ['Hora', 'Demanda Real (kW)', 'Demanda Esperada (kW)', 'Desviación (%)'].join(','),
      ...result.chart_data.map((d: any) => [
        d.time_str,
        d.value.toFixed(2),
        d.mean.toFixed(2),
        (((d.value - d.mean) / d.mean) * 100).toFixed(2)
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `analisis_${deviceId}_${targetDate}.csv`;
    link.click();
  };

  // --- Sub-componentes UI ---
  const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
    const styles: Record<string, string> = {
      'NORMAL': 'bg-green-100 text-green-800 border-green-200',
      'ALERTA': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'CRITICO': 'bg-red-100 text-red-800 border-red-200',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-bold border ${styles[status] || 'bg-gray-100 text-gray-600'}`}>
        {status || 'DESCONOCIDO'}
      </span>
    );
  };

  const MetricCard: React.FC<{ icon: any, label: string, value: string | number, trend?: 'up' | 'down' | 'neutral', color?: string }> =
    ({ icon: Icon, label, value, trend, color = 'indigo' }) => (
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <div className={`p-2 rounded-lg bg-${color}-100`}>
            <Icon className={`w-5 h-5 text-${color}-600`} />
          </div>
          {trend && (
            <div className={`p-1 rounded ${trend === 'up' ? 'bg-red-100' : trend === 'down' ? 'bg-green-100' : 'bg-gray-100'}`}>
              {trend === 'up' ? <TrendingUp className="w-4 h-4 text-red-600" /> :
                trend === 'down' ? <TrendingDown className="w-4 h-4 text-green-600" /> :
                  <Activity className="w-4 h-4 text-gray-600" />}
            </div>
          )}
        </div>
        <p className="text-xs text-slate-500 font-medium uppercase">{label}</p>
        <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
      </div>
    );

  return (
    <div className="max-w-7xl mx-auto space-y-6 p-4">

      {/* Header */}
      <header className="flex items-center justify-between bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg">
            <Database className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Análisis Inteligente de la Demanda</h1>
            <p className="text-slate-500 text-sm">Monitorización Inteligente & Detección de Anomalías</p>
          </div>
        </div>
        {result && (
          <button
            onClick={exportToCSV}
            className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">Exportar CSV</span>
          </button>
        )}
      </header>

      <div className="grid md:grid-cols-12 gap-6">

        {/* Sidebar de Configuración */}
        <div className="md:col-span-4 space-y-6">

          {/* Card: Medidor */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
            <h2 className="font-semibold flex items-center gap-2 mb-4 text-slate-700">
              <Zap className="w-4 h-4" /> Configuración Medidor
            </h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-500 uppercase block mb-1">Seleccionar Medidor</label>
                <select
                  className="w-full p-2 border border-slate-300 rounded-md text-sm"
                  value={deviceId}
                  onChange={(e) => setDeviceId(e.target.value)}
                >
                  <option value="">Seleccione un medidor</option>
                  {devices.map(device => (
                    <option key={device.deviceid} value={device.deviceid}>
                      {device.deviceid} - {device.description}
                    </option>
                  ))}
                </select>
              </div>

              {deviceId && (
                <div className="bg-slate-50 p-3 rounded-md border border-slate-200">
                  <h4 className="text-xs font-bold text-slate-600 uppercase mb-2">Información del Medidor</h4>
                  {(() => {
                    const selectedDevice = devices.find(d => d.deviceid === deviceId);
                    return selectedDevice ? (
                      <div className="text-xs text-slate-700 space-y-1">
                        <div><span className="font-medium">Tipo:</span> {selectedDevice.devicetype || 'N/A'}</div>
                        <div><span className="font-medium">Cliente:</span> {selectedDevice.customerid || 'N/A'}</div>
                        <div><span className="font-medium">Grupo:</span> {selectedDevice.usergroup || 'N/A'}</div>
                        <div><span className="font-medium">Descripción:</span> {selectedDevice.description || 'N/A'}</div>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500">Cargando información...</p>
                    );
                  })()}
                </div>
              )}
            </div>
          </div>

          {/* Card: IA */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
            <h2 className="font-semibold flex items-center gap-2 mb-4 text-slate-700">
              <BrainCircuit className="w-4 h-4" /> Análisis Inteligente
            </h2>
            <div className="space-y-4">

              {years.length > 0 ? (
                <div>
                  <label className="text-xs font-bold text-slate-500 uppercase block mb-1">Año Base (Baseline)</label>
                  <select
                    className="w-full p-2 border border-slate-300 rounded-md text-sm"
                    value={selectedBaseYear}
                    onChange={(e) => setSelectedBaseYear(e.target.value)}
                  >
                    {years.map(y => <option key={y} value={y}>{y}</option>)}
                  </select>
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">
                  Selecciona un medidor para ver años disponibles.
                </p>
              )}

              <div>
                <label className="text-xs font-bold text-slate-500 uppercase block mb-1">Fecha a Analizar</label>
                <input
                  type="date"
                  className="w-full p-2 border border-slate-300 rounded-md text-sm"
                  value={targetDate}
                  onChange={(e) => setTargetDate(e.target.value)}
                />
              </div>

              <button
                onClick={handleAnalyze}
                disabled={loading}
                className="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors flex justify-center items-center gap-2"
              >
                {loading ? 'Procesando...' : <><BrainCircuit className="w-4 h-4" /> Analizar</>}
              </button>

              {error && (
                <div className="p-3 bg-red-50 border border-red-100 text-red-600 text-xs rounded-md">
                  {error}
                </div>
              )}

              {msg && (
                <div className="p-3 bg-green-50 border border-green-100 text-green-600 text-xs rounded-md">
                  {msg}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Panel Principal de Resultados */}
        <div className="md:col-span-8 space-y-6">
          {!result ? (
            <div className="h-full min-h-[400px] bg-white rounded-xl border border-slate-200 flex flex-col items-center justify-center text-slate-400">
              <Activity className="w-16 h-16 mb-4 opacity-20" />
              <p>Esperando análisis...</p>
            </div>
          ) : (
            <>
              {/* KPIs Cards */}
              {metrics && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <MetricCard
                    icon={TrendingUp}
                    label="Desv. Máxima"
                    value={`${metrics.maxDeviation.toFixed(1)}%`}
                    trend={metrics.maxDeviation > 20 ? 'up' : 'neutral'}
                    color="red"
                  />
                  <MetricCard
                    icon={Activity}
                    label="Desv. Promedio"
                    value={`${metrics.avgDeviation.toFixed(1)}%`}
                    color="orange"
                  />
                  <MetricCard
                    icon={Zap}
                    label="Pico de Demanda"
                    value={`${metrics.peakValue.toFixed(1)} kW`}
                    color="indigo"
                  />
                  <MetricCard
                    icon={Clock}
                    label="Hora Pico"
                    value={metrics.peakHour}
                    color="blue"
                  />
                </div>
              )}

              {/* Gráfica Principal */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h3 className="font-bold text-lg text-slate-800">Curva de Carga: {result.day_name}</h3>
                    <p className="text-xs text-slate-400">Comparativa Real vs Esperado (Base: {selectedBaseYear})</p>
                  </div>
                  <div className="flex gap-4 text-xs">
                    <div className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-500/20 border border-blue-500 rounded"></div> Real</div>
                    <div className="flex items-center gap-1"><div className="w-3 h-1 bg-slate-400 border-t border-slate-400 border-dashed"></div> Esperado</div>
                  </div>
                </div>
                <div className="h-[320px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={result.chart_data}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="time_str" tick={{ fontSize: 10, fill: '#94a3b8' }} interval={8} />
                      <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} />
                      <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                      <Line type="monotone" dataKey="mean" stroke="#94a3b8" strokeWidth={2} strokeDasharray="5 5" dot={false} name="Esperado" />
                      <Area type="monotone" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.1} strokeWidth={2} dot={false} name="Real" />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Indicadores por Período del Día */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <h3 className="font-bold text-lg text-slate-800 mb-4">Análisis por Período del Día</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {getPeriodData().map((period, idx) => {
                    const Icon = period.icon;
                    const isNegative = period.deviation < 0;
                    return (
                      <div key={idx} className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                        <div className="flex items-center gap-2 mb-2">
                          <Icon className="w-5 h-5" style={{ color: period.color }} />
                          <span className="font-semibold text-sm">{period.name}</span>
                        </div>
                        <div className="text-xs text-slate-600 space-y-1">
                          <div>Real: <span className="font-bold">{period.avgActual.toFixed(1)} kW</span></div>
                          <div>Esperado: {period.avgExpected.toFixed(1)} kW</div>
                          <div className={`font-bold ${isNegative ? 'text-green-600' : 'text-red-600'}`}>
                            {isNegative ? '↓' : '↑'} {Math.abs(period.deviation).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Tabla de Comparación Horaria */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <h3 className="font-bold text-lg text-slate-800 mb-4">Top 10 Horas con Mayor Desviación</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200">
                      <tr>
                        <th className="text-left p-2 font-semibold text-slate-600">Hora</th>
                        <th className="text-right p-2 font-semibold text-slate-600">Real (kW)</th>
                        <th className="text-right p-2 font-semibold text-slate-600">Esperado (kW)</th>
                        <th className="text-right p-2 font-semibold text-slate-600">Diferencia</th>
                        <th className="text-right p-2 font-semibold text-slate-600">Desviación</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getHourlyComparisonTable().map((row: any, idx: number) => (
                        <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="p-2 font-mono">{row.time}</td>
                          <td className="p-2 text-right font-semibold">{row.actual.toFixed(2)}</td>
                          <td className="p-2 text-right text-slate-600">{row.expected.toFixed(2)}</td>
                          <td className={`p-2 text-right font-semibold ${row.diff > 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {row.diff > 0 ? '+' : ''}{row.diff.toFixed(2)}
                          </td>
                          <td className={`p-2 text-right font-bold ${Math.abs(row.deviation) > 20 ? 'text-red-600' : 'text-slate-600'}`}>
                            {row.deviation > 0 ? '+' : ''}{row.deviation.toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Histograma de Distribución */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <h3 className="font-bold text-lg text-slate-800 mb-4">Distribución de Demanda (kW)</h3>
                <div className="h-[250px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getDistributionData()}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="range" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                      <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} label={{ value: 'Frecuencia', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                      <Tooltip
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        formatter={(value: any, name: string) => {
                          if (name === 'count') return [value, 'Lecturas'];
                          if (name === 'percentage') return [`${value.toFixed(1)}%`, 'Porcentaje'];
                          return [value, name];
                        }}
                      />
                      <Bar dataKey="count" name="count">
                        {getDistributionData().map((_entry, index) => (
                          <Cell key={`cell-${index}`} fill={`hsl(${220}, ${70 - index * 10}%, ${50 + index * 5}%)`} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Panel IA */}
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="bg-slate-900 p-4 flex justify-between items-center">
                  <div className="flex items-center gap-2 text-white font-medium">
                    <BrainCircuit className="w-5 h-5 text-indigo-400" />
                    Diagnóstico Observer
                  </div>
                  <StatusBadge status={result.analysis.estado_general} />
                </div>
                <div className="p-6 space-y-5">
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Resumen Ejecutivo</h4>
                    <p className="text-slate-700 leading-relaxed text-sm">{result.analysis.resumen}</p>
                  </div>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                      <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Hábitos Detectados</h4>
                      <p className="text-sm text-slate-600">{result.analysis.habitos}</p>
                    </div>
                    <div className="bg-red-50 p-4 rounded-lg border border-red-100">
                      <h4 className="text-xs font-bold text-red-700 uppercase mb-2 flex items-center gap-2">
                        <AlertTriangle className="w-3 h-3" /> Anomalías
                      </h4>
                      {result.analysis.anomalias && result.analysis.anomalias.length > 0 ? (
                        <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
                          {result.analysis.anomalias.map((a: any, i: number) => {
                            // Safely handle anomaly objects - they might be strings or objects
                            if (typeof a === 'string') {
                              return <li key={i}>{a}</li>;
                            } else if (a && typeof a === 'object') {
                              // Ensure we're rendering strings, not objects
                              // Handle both formato {periodo, descripcion} and nested objects
                              let displayText = '';
                              
                              if (a.periodo) {
                                displayText += `${a.periodo}: `;
                              }
                              
                              if (a.descripcion) {
                                // Si descripcion es un objeto, convertirlo a string
                                if (typeof a.descripcion === 'object') {
                                  displayText += JSON.stringify(a.descripcion);
                                } else {
                                  displayText += String(a.descripcion);
                                }
                              } else if (a.cambio || a.descripcion) {
                                // Formato alternativo con cambio y descripcion
                                displayText += `${a.cambio || ''} - ${a.descripcion || ''}`;
                              } else {
                                // Si no tiene estructura conocida, convertir todo el objeto
                                displayText = JSON.stringify(a);
                              }
                              
                              return <li key={i}>{displayText || 'Anomalía detectada'}</li>;
                            } else {
                              return <li key={i}>Anomalía no válida</li>;
                            }
                          })}
                        </ul>
                      ) : (
                        <p className="text-sm text-green-600 flex items-center gap-1"><CheckCircle className="w-3 h-3" /> Ninguna crítica.</p>
                      )}
                    </div>
                  </div>
                  <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-100 flex gap-3">
                    <div className="shrink-0 mt-1"><Zap className="w-4 h-4 text-indigo-600" /></div>
                    <div>
                      <h4 className="text-xs font-bold text-indigo-800 uppercase mb-1">Recomendación Operativa</h4>
                      <p className="text-sm text-indigo-900 font-medium italic">"{result.analysis.recomendacion}"</p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Chatbot flotante - CON AUTOMATIZACIÓN */}
      <EnergyChatbot
        context={{ device_id: deviceId, fecha: targetDate, base_year: selectedBaseYear }}
        onParametersExtracted={handleParametersExtracted}
      />
    </div>
  );
};

export default EnergyDashboard;