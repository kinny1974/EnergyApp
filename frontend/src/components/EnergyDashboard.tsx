import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, AreaChart, Area, ComposedChart
} from 'recharts';
import {
  Upload, Activity, AlertTriangle, Zap, CheckCircle,
  BrainCircuit, Database, Search, File as FileIcon
} from 'lucide-react';
import { 
  uploadReadings, getAvailableYears, analyzeEnergy, AnalysisResult, 
  getAvailableDevices, DeviceInfo, getYearsFromCsv, analyzeEnergyWithFile 
} from '../services/api';

// Props para el componente StatusBadge
interface StatusBadgeProps {
  status: 'NORMAL' | 'ALERTA' | 'CRITICO' | 'DESCONOCIDO';
}

const EnergyDashboard: React.FC = () => {
  // --- Estado Local Tipado ---
  const [deviceId, setDeviceId] = useState<string>('');
  const [selectedBaseYear, setSelectedBaseYear] = useState<string | number>('');
  const [targetDate, setTargetDate] = useState<string>('');
  const [years, setYears] = useState<number[]>([]);
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [baseDataMode, setBaseDataMode] = useState<'database' | 'file'>('database');
  const [baseFile, setBaseFile] = useState<File | null>(null);
  
  // Estado de UI
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>('');
  const [msg, setMsg] = useState<string>('');

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

  // Refrescar años cuando cambia el modo de datos o el medidor
  useEffect(() => {
    if (baseDataMode === 'database' && deviceId) {
      refreshYears();
    } else {
      setYears([]);
      setSelectedBaseYear('');
    }
  }, [baseDataMode, deviceId]);

  // Obtener años desde el archivo CSV cuando se selecciona uno
  useEffect(() => {
    const getYearsFromFile = async () => {
      if (baseDataMode === 'file' && baseFile) {
        setLoading(true);
        setError('');
        try {
          const data = await getYearsFromCsv(baseFile);
          setYears(data.years);
          if (data.years.length > 0) {
            setSelectedBaseYear(data.years[0]);
          }
        } catch (err: any) {
          setError(err.message || "Error al procesar el archivo CSV");
          setYears([]);
          setSelectedBaseYear('');
        } finally {
          setLoading(false);
        }
      }
    };
    getYearsFromFile();
  }, [baseFile, baseDataMode]);


  // --- Manejadores de Eventos ---

  const handleMassiveFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !deviceId) {
      setError("Por favor, selecciona un medidor antes de subir un archivo.");
      return;
    }
    
    const file = e.target.files[0];
    setLoading(true);
    setError('');
    setMsg('');

    try {
      const data = await uploadReadings(deviceId, file);
      setMsg(`✅ Carga masiva exitosa: ${data.records} registros procesados.`);
      await refreshYears(); // Refrescar años de la DB
    } catch (err: any) {
      setError(err.message || "Error desconocido al subir");
    } finally {
      setLoading(false);
    }
  };

  const handleBaseFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setBaseFile(e.target.files[0]);
    } else {
      setBaseFile(null);
    }
  };

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

  return (
    <div className="max-w-6xl mx-auto space-y-6 p-4">
      
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
        <div className="text-right hidden sm:block">
            <p className="text-xs text-slate-400 font-mono">TS • React 18 • Vite</p>
        </div>
      </header>

      <div className="grid md:grid-cols-12 gap-6">
        
        {/* Sidebar de Configuración */}
        <div className="md:col-span-4 space-y-6">
          
          {/* Card 1: Medidor */}
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
              
              <div className="border-t border-slate-100 pt-4">
                 <label className="text-xs font-bold text-slate-500 uppercase block mb-2">Carga Masiva (CSV)</label>
                 <label className="flex flex-col items-center justify-center w-full h-24 border-2 border-slate-300 border-dashed rounded-lg cursor-pointer bg-slate-50 hover:bg-slate-100">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <Upload className="w-6 h-6 text-slate-400 mb-1"/>
                        <p className="text-xs text-slate-500">Click para subir historial a la DB</p>
                    </div>
                    <input type="file" className="hidden" accept=".csv" onChange={handleMassiveFileUpload} />
                </label>
                {msg && <p className="text-xs text-green-600 mt-2 font-medium">{msg}</p>}
              </div>
            </div>
          </div>

          {/* Card 2: IA */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
            <h2 className="font-semibold flex items-center gap-2 mb-4 text-slate-700">
              <BrainCircuit className="w-4 h-4" /> Análisis Inteligente
            </h2>
            <div className="space-y-4">


              <div>
                <label className="text-xs font-bold text-slate-500 uppercase block mb-1">Fuente de Datos Base</label>
                <div className="flex gap-4 py-1">
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input
                      type="radio"
                      name="baseDataMode"
                      value="database"
                      checked={baseDataMode === 'database'}
                      onChange={() => setBaseDataMode('database')}
                      className="h-4 w-4 text-indigo-600 border-slate-300 focus:ring-indigo-500"
                    />
                    Base de Datos
                  </label>
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input
                      type="radio"
                      name="baseDataMode"
                      value="file"
                      checked={baseDataMode === 'file'}
                      onChange={() => setBaseDataMode('file')}
                      className="h-4 w-4 text-indigo-600 border-slate-300 focus:ring-indigo-500"
                    />
                    Archivo CSV
                  </label>
                </div>
              </div>

              {baseDataMode === 'file' && (
                <div className="bg-slate-50 p-3 rounded-md border border-slate-200">
                  <label className="text-xs font-bold text-slate-500 uppercase block mb-2">Archivo CSV Base</label>
                  <input
                    type="file"
                    className="w-full text-sm file:mr-4 file:py-1 file:px-2 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                    accept=".csv"
                    onChange={handleBaseFileChange}
                  />
                </div>
              )}

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
                  {baseDataMode === 'database' 
                    ? "Selecciona un medidor para ver años." 
                    : "Selecciona un archivo CSV para ver los años disponibles."}
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
                {loading ? 'Procesando...' : <><BrainCircuit className="w-4 h-4"/> Analizar</>}
              </button>
              
              {error && (
                <div className="p-3 bg-red-50 border border-red-100 text-red-600 text-xs rounded-md">
                    {error}
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
                    {/* Gráfica */}
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
                                    <XAxis dataKey="time_str" tick={{fontSize: 10, fill:'#94a3b8'}} interval={8} />
                                    <YAxis tick={{fontSize: 10, fill:'#94a3b8'}} />
                                    <Tooltip contentStyle={{borderRadius:'8px', border:'none', boxShadow:'0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                                    <Line type="monotone" dataKey="mean" stroke="#94a3b8" strokeWidth={2} strokeDasharray="5 5" dot={false} name="Esperado" />
                                    <Area type="monotone" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.1} strokeWidth={2} dot={false} name="Real" />
                                </ComposedChart>
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
                                        <AlertTriangle className="w-3 h-3"/> Anomalías
                                    </h4>
                                    {result.analysis.anomalias && result.analysis.anomalias.length > 0 ? (
                                        <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
                                            {result.analysis.anomalias.map((a: any, i) => <li key={i}>{a.periodo}: {a.descripcion}</li>)}
                                        </ul>
                                    ) : (
                                        <p className="text-sm text-green-600 flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Ninguna crítica.</p>
                                    )}
                                </div>
                            </div>

                            <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-100 flex gap-3">
                                <div className="shrink-0 mt-1"><Zap className="w-4 h-4 text-indigo-600"/></div>
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
    </div>
  );
};

export default EnergyDashboard;