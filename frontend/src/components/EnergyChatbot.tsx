
import React, { useState, useRef, useEffect } from 'react';
import { Send, Zap, MessageSquare, Loader2 } from 'lucide-react';
import { analyzeOutliers, OutlierResult } from '../services/api';

interface ChatMessage {
  role: 'user' | 'bot';
  content: string;
}

interface EnergyChatbotProps {
  context?: Record<string, any>; // device_id, fecha, etc.
}

const FAQS = [
  '¿Por qué hubo un pico de consumo a las 3 AM?',
  '¿Cómo puedo mejorar el factor de carga?',
  '¿Qué significa el estado CRITICO en mi curva?',
  'Explica el concepto de demanda máxima.',
  '¿Qué hábitos de consumo detecta el sistema?',
  '¿Cómo puedo reducir anomalías en mi consumo?',
];

const EnergyChatbot: React.FC<EnergyChatbotProps> = ({ context }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (msg: string) => {
    if (!msg.trim()) return;
    setMessages((prev) => [...prev, { role: 'user', content: msg }]);
    setInput('');
    setLoading(true);
    // Detectar si la pregunta es de outliers (simple: busca palabras clave)
    const outlierRegex = /desviaciones? mayores? al? (\d+)%?.*año (\d{4}).*entre (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre) y (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre) de (\d{4})/i;
    const meses = {
      'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04', 'mayo': '05', 'junio': '06',
      'julio': '07', 'agosto': '08', 'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    };
    const match = msg.match(outlierRegex);
    if (match) {
      // Extraer parámetros
      const threshold = parseFloat(match[1]);
      const base_year = parseInt(match[2]);
      const mes_inicio = meses[match[3].toLowerCase()];
      const mes_fin = meses[match[4].toLowerCase()];
      const year_fin = parseInt(match[5]);
      // Construir fechas
      const start_date = `${year_fin}-${mes_inicio}-01`;
      const end_date = `${year_fin}-${mes_fin}-31`;
      try {
        const outlierRes = await analyzeOutliers({ base_year, start_date, end_date, threshold });
        if (outlierRes.outliers.length === 0) {
          setMessages((prev) => [...prev, { role: 'bot', content: 'No se encontraron medidores con desviaciones mayores al umbral en el periodo indicado.' }]);
        } else {
          setMessages((prev) => [...prev, { role: 'bot', content: resumenOutliers(outlierRes.outliers) }]);
        }
      } catch (e) {
        setMessages((prev) => [...prev, { role: 'bot', content: 'Error al buscar desviaciones: ' + (e as Error).message }]);
      } finally {
        setLoading(false);
      }
      return;
    }
    // Si no es pregunta de outliers, usa el backend normal
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, context }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: 'bot', content: data.response }]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: 'bot', content: 'Error al contactar con el asistente.' }]);
    } finally {
      setLoading(false);
    }
  };

  // Función para resumir los resultados de outliers
  function resumenOutliers(outliers: OutlierResult[]): string {
    let resumen = `Se encontraron ${outliers.length} casos de desviaciones mayores al umbral.\n`;
    for (const o of outliers.slice(0, 5)) {
      resumen += `\nMedidor: ${o.device_id} (${o.medidor_info.description})\nFecha: ${o.fecha}\nDesviación máxima: ${o.max_deviation.toFixed(2)}%\n`;
    }
    if (outliers.length > 5) resumen += `\n...y ${outliers.length - 5} más.`;
    return resumen;
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="flex flex-col h-full max-h-[600px] bg-white rounded-xl border border-slate-200 shadow-sm">
      <div className="flex items-center gap-2 p-4 border-b bg-slate-50">
        <Zap className="text-indigo-600 w-5 h-5" />
        <span className="font-bold text-slate-800">Asistente IA Energético</span>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-xs text-slate-400 mb-2">
            <MessageSquare className="inline w-4 h-4 mr-1" />
            Haz una pregunta sobre tu consumo, análisis eléctrico o selecciona una sugerencia:
            <div className="flex flex-wrap gap-2 mt-2">
              {FAQS.map((faq, i) => (
                <button
                  key={i}
                  className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-xs border border-indigo-100 hover:bg-indigo-100"
                  onClick={() => sendMessage(faq)}
                  disabled={loading}
                >
                  {faq}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] px-4 py-2 rounded-lg text-sm ${m.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-800'}`}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="px-4 py-2 rounded-lg bg-slate-100 text-slate-500 flex items-center gap-2 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" /> Pensando...
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t bg-slate-50">
        <input
          type="text"
          className="flex-1 p-2 border border-slate-300 rounded-md text-sm"
          placeholder="Escribe tu pregunta..."
          value={input}
          onChange={e => setInput(e.target.value)}
          disabled={loading}
        />
        <button
          type="submit"
          className="bg-indigo-600 text-white px-4 py-2 rounded-md font-medium hover:bg-indigo-700 disabled:bg-slate-300"
          disabled={loading || !input.trim()}
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};

export default EnergyChatbot;
