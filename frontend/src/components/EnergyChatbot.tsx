import React, { useState, useRef, useEffect } from 'react';
import { Send, Zap, MessageSquare, Loader2, X, ChevronUp, ChevronDown } from 'lucide-react';

interface ChatMessage {
  role: 'user' | 'bot';
  content: string;
  parameters?: any;
  type?: string;
}

interface EnergyChatbotProps {
  context?: Record<string, any>; // device_id, fecha, etc.
  onParametersExtracted?: (params: any, type: string) => void;
}

const FAQS = [
  'Busca medidores con desviaciones mayores al 50% en el año base 2024 entre enero y octubre de 2025',
  '¿Cuál es la máxima potencia del medidor 1234567 en el mes de septiembre 2024?',
  'Calcula la energía total del medidor 1234567 en la última semana de octubre',
  '¿Cuánta energía consumió el medidor 1234567 en agosto 2024?',
  'Encuentra outliers en medidores con desviaciones del 30% usando año base 2023',
  'Demanda de energía del medidor 1234567 en julio 2024',
  'compara la curva de carga del día 20 de octubre de 2025, con la curva de carga promedio para el año 2024, del medidor 36075003',
  'compara el comportamiento de la demanda para el día 20 de octubre de 2025, con el comportamiento promedio de la demanda para el año 2024, del medidor 36075003',
];

const EnergyChatbot: React.FC<EnergyChatbotProps> = ({ context, onParametersExtracted }) => {
  console.log('🔍 [CHATBOT] Component props:', { context, onParametersExtracted: !!onParametersExtracted });
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Cargar estado de visibilidad desde localStorage al iniciar
  useEffect(() => {
    const savedVisibility = localStorage.getItem('chatbotVisible');
    if (savedVisibility !== null) {
      setIsVisible(JSON.parse(savedVisibility));
    }
  }, []);

  // Guardar estado de visibilidad en localStorage cuando cambie
  useEffect(() => {
    localStorage.setItem('chatbotVisible', JSON.stringify(isVisible));
  }, [isVisible]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (msg: string) => {
    if (!msg.trim()) return;
    setMessages((prev) => [...prev, { role: 'user', content: msg }]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, context }),
      });
      const data = await res.json();
      console.log('🔍 [CHATBOT] Full response from backend:', data);

      // Handle the new response structure with parameters
      const botMessage: ChatMessage = {
        role: 'bot',
        content: data.response,
        parameters: data.parameters,
        type: data.type
      };

      setMessages((prev) => [...prev, botMessage]);

      // If parameters are available and callback is provided, call it
      if (data.parameters && onParametersExtracted) {
        console.log('🔍 [CHATBOT] Extracted parameters from chatbot:', data.parameters);
        console.log('🔍 [CHATBOT] Type:', data.type);
        console.log('🔍 [CHATBOT] Calling onParametersExtracted callback...');

        // Ensure we have the required parameters for load curve comparison
        if (data.type === 'load_curve_comparison') {
          const requiredParams = ['device_id', 'target_date', 'base_year'];
          const missingParams = requiredParams.filter(param => !data.parameters[param]);

          if (missingParams.length > 0) {
            console.warn('⚠️ [CHATBOT] Missing required parameters:', missingParams);
            console.warn('⚠️ [CHATBOT] Available parameters:', data.parameters);
          } else {
            console.log('✅ [CHATBOT] All required parameters present');
          }
        }

        // Call the callback with the parameters
        try {
          onParametersExtracted(data.parameters, data.type);
          console.log('✅ [CHATBOT] Callback executed successfully');
        } catch (error) {
          console.error('❌ [CHATBOT] Error executing callback:', error);
        }
      } else {
        console.log('🔍 [CHATBOT] No parameters found or callback not provided:', {
          hasParameters: !!data.parameters,
          hasCallback: !!onParametersExtracted,
          parameters: data.parameters,
          type: data.type
        });
      }
    } catch (e) {
      setMessages((prev) => [...prev, { role: 'bot', content: 'Error al contactar con el asistente.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
    if (!isVisible) {
      setIsOpen(false); // Al mostrar, asegurar que el chat esté cerrado inicialmente
    }
  };

  if (!isVisible) {
    return (
      <button
        onClick={toggleVisibility}
        className="fixed bottom-6 right-6 bg-slate-600 text-white p-3 rounded-full shadow-lg hover:bg-slate-700 transition-all duration-200 z-50"
        aria-label="Mostrar asistente IA energético"
      >
        <ChevronUp className="w-5 h-5" />
      </button>
    );
  }

  return (
    <>
      {/* Contenedor del botón flotante y controles */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end space-y-2">
        {/* Botón para ocultar/mostrar */}
        <button
          onClick={toggleVisibility}
          className="bg-slate-500 text-white p-2 rounded-full shadow-lg hover:bg-slate-600 transition-all duration-200"
          aria-label="Ocultar asistente"
        >
          <ChevronDown className="w-4 h-4" />
        </button>

        {/* Botón principal del chat */}
        {!isOpen && (
          <button
            onClick={toggleChat}
            className="bg-indigo-600 text-white p-4 rounded-full shadow-lg hover:bg-indigo-700 transition-all duration-200"
            aria-label="Abrir asistente IA energético"
          >
            <Zap className="w-6 h-6" />
          </button>
        )}

        {/* Modal del chat */}
        {isOpen && (
          <div className="w-96 h-[600px] bg-white rounded-xl border border-slate-200 shadow-xl flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b bg-slate-50">
              <div className="flex items-center gap-2">
                <Zap className="text-indigo-600 w-5 h-5" />
                <span className="font-bold text-slate-800">Asistente IA Energético</span>
              </div>
              <button
                onClick={toggleChat}
                className="text-slate-500 hover:text-slate-700 transition-colors"
                aria-label="Cerrar chat"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Mensajes */}
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
                    {m.parameters && m.type === 'load_curve_comparison' && (
                      <div className="mt-2 text-xs text-green-600">
                        ✅ Parámetros detectados automáticamente
                      </div>
                    )}
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

            {/* Input */}
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
        )}
      </div>
    </>
  );
};

export default EnergyChatbot;
