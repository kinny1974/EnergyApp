// Definición de Tipos para las Respuestas del Backend

export interface UploadResponse {
  status: string;
  records: number;
}

export interface YearsResponse {
  years: number[];
}

export interface ChartDataPoint {
  time_str: string;
  value: number;      // Valor real
  mean: number;       // Valor esperado (baseline)
  std?: number;       // Desviación estándar (opcional)
}

export interface AIAnalysis {
  resumen: string;
  habitos: string;
  anomalias: {periodo: string, descripcion: string}[];
  recomendacion: string;
  estado_general: 'NORMAL' | 'ALERTA' | 'CRITICO' | 'DESCONOCIDO';
}

export interface MedidorInfo {
  description: string;
  devicetype: string;
  customerid: string;
  usergroup: string;
}

export interface AnalysisResult {
  device_id: string;
  medidor_info: MedidorInfo;
  day_name: string;
  chart_data: ChartDataPoint[];
  analysis: AIAnalysis;
}

export interface DeviceInfo {
  deviceid: string;
  description: string;
  devicetype: string;
  customerid: string;
  usergroup: string;
}

export interface DevicesResponse {
  devices: DeviceInfo[];
}

// Payload para la petición de análisis
interface AnalyzePayload {
  device_id: string;
  base_year: number;
  target_date: string;
}

// URL base de tu backend FastAPI
const BASE_URL = "http://localhost:8000";

/**
 * Sube un archivo CSV asociado a un Device ID para carga masiva en la DB.
 */
export const uploadReadings = async (deviceId: string, file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/upload/${deviceId}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Error al subir archivo");
  }
  return response.json();
};

/**
 * Obtiene los años disponibles para análisis desde la base de datos.
 */
export const getAvailableYears = async (deviceId: string): Promise<YearsResponse> => {
  const response = await fetch(`${BASE_URL}/years/${deviceId}`);
  
  if (!response.ok) {
    throw new Error("Error al obtener años disponibles");
  }
  return response.json();
};

/**
 * Obtiene los años disponibles para análisis desde un archivo CSV.
 */
export const getYearsFromCsv = async (file: File): Promise<YearsResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/years-from-csv`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Error al procesar el archivo CSV");
  }
  return response.json();
};

/**
 * Obtiene la lista de medidores disponibles
 */
export const getAvailableDevices = async (): Promise<DevicesResponse> => {
  const response = await fetch(`${BASE_URL}/devices`);
  
  if (!response.ok) {
    throw new Error("Error al obtener dispositivos disponibles");
  }
  return response.json();
};

/**
 * Obtiene información de un medidor específico
 */
export const getDeviceInfo = async (deviceId: string): Promise<DeviceInfo> => {
  const response = await fetch(`${BASE_URL}/devices/${deviceId}`);
  
  if (!response.ok) {
    throw new Error("Error al obtener información del dispositivo");
  }
  return response.json();
};

/**
 * Ejecuta el análisis de IA usando la base de datos como fuente base.
 */
export const analyzeEnergy = async (
  deviceId: string, 
  baseYear: string | number, 
  targetDate: string
): Promise<AnalysisResult> => {
  
  const payload: AnalyzePayload = {
    device_id: deviceId,
    base_year: typeof baseYear === 'string' ? parseInt(baseYear) : baseYear,
    target_date: targetDate
  };

  const response = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Error en el análisis");
  }
  return response.json();
};

/**
 * Ejecuta el análisis de IA usando un archivo CSV como fuente base.
 */
export const analyzeEnergyWithFile = async (
  deviceId: string,
  baseYear: string | number,
  targetDate: string,
  baseFile: File
): Promise<AnalysisResult> => {
  const formData = new FormData();
  formData.append('device_id', deviceId);
  formData.append('base_year', typeof baseYear === 'string' ? baseYear : baseYear.toString());
  formData.append('target_date', targetDate);
  formData.append('base_file', baseFile);

  const response = await fetch(`${BASE_URL}/analyze-with-file`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Error en el análisis con archivo");
  }
  return response.json();
};