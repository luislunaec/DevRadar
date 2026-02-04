import { useState, useEffect, useRef } from 'react';
import { Diamond, Send, Sparkles, Bot, User } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { enviarMensajeChat, type ChatRespuesta } from '@/services/api';
// 1. IMPORTANTE: Importamos el maquillador de texto
import ReactMarkdown from 'react-markdown';

const suggestedQueries = [
  '¿Cuáles son los salarios más comunes en Ecuador?',
  '¿Qué tecnologías son más demandadas?',
  'Diferencias entre trabajo remoto y presencial',
  'Tendencias de seniority en el mercado',
];

// 2. IMPORTANTE: Actualizamos la "forma" del mensaje para incluir las fuentes
interface Mensaje {
  role: 'user' | 'assistant';
  content: string;
  ofertas_encontradas?: number;
  fuentes?: { titulo: string; empresa: string; url: string }[];
}

export default function AIReportsPage() {
  const [query, setQuery] = useState('');
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [mensajes]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const mensajeUsuario = query.trim();
    setQuery(''); 
    setError(null);

    // Agregar mensaje del usuario
    setMensajes((prev) => [...prev, { role: 'user', content: mensajeUsuario }]);
    setLoading(true);

    try {
      // Nota: Asegúrate de que tu type ChatRespuesta en api.ts tenga 'fuentes'
      // Si te da error aquí, edita services/api.ts y agrega fuentes?: any[]
      const respuesta: any = await enviarMensajeChat({
        mensaje: mensajeUsuario,
        session_id: sessionId,
      });

      // 3. IMPORTANTE: Guardamos las fuentes que vienen del backend
      setMensajes((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: respuesta.respuesta,
          ofertas_encontradas: respuesta.ofertas_encontradas,
          fuentes: respuesta.fuentes, 
        },
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error en el chat');
      setMensajes((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
  };

  return (
    <Layout>
      <div className="container py-8 flex flex-col h-[calc(100vh-4rem)]">
        {/* Header */}
        <div className="flex items-center justify-center gap-2 mb-4">
          <Diamond className="h-6 w-6 text-primary" />
          <span className="text-h3">DevRadar Ecuador</span>
        </div>

        {/* Title */}
        <div className="text-center mb-6">
          <h1 className="text-h1 mb-2">Chat con IA</h1>
          <p className="text-muted-foreground max-w-xl mx-auto text-sm">
            Pregunta sobre el mercado laboral IT en Ecuador: ofertas de trabajo, salarios, tecnologías demandadas y más.
          </p>
        </div>

        {/* Chat Area */}
        <div className="flex-1 max-w-4xl mx-auto w-full overflow-y-auto mb-4 space-y-4 px-4">
          {mensajes.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
              <Bot className="h-16 w-16 text-primary/50" />
              <div>
                <h3 className="text-lg font-semibold mb-2">¡Hola! Soy tu asistente de DevRadar</h3>
                <p className="text-muted-foreground text-sm max-w-md">
                  Pregúntame sobre ofertas de trabajo, salarios, tecnologías más usadas, consejos de carrera y más.
                </p>
              </div>
            </div>
          )}

          {mensajes.map((mensaje, index) => (
            <div
              key={index}
              className={`flex gap-3 ${mensaje.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {mensaje.role === 'assistant' && (
                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center shrink-0">
                  <Sparkles className="h-5 w-5 text-primary-foreground" />
                </div>
              )}
              
              <div
                className={`glass-card p-4 max-w-[85%] ${mensaje.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-card'
                }`}
              >
                {/* 4. IMPORTANTE: Aquí renderizamos el Markdown bonito */}
                {mensaje.role === 'assistant' ? (
                   <div className="prose prose-invert prose-sm max-w-none prose-p:my-1 prose-headings:text-blue-400 prose-headings:my-2 prose-strong:text-purple-400 prose-li:my-0">
                     <ReactMarkdown>{mensaje.content}</ReactMarkdown>
                   </div>
                ) : (
                   <p className="text-sm whitespace-pre-wrap">{mensaje.content}</p>
                )}

                {/* 5. IMPORTANTE: Aquí pintamos los botones de las fuentes */}
                {mensaje.role === 'assistant' && mensaje.fuentes && mensaje.fuentes.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-gray-700/50">
                    <p className="text-xs text-gray-400 mb-2 font-semibold">Ofertas analizadas:</p>
                    <div className="flex flex-wrap gap-2">
                      {mensaje.fuentes.map((fuente, idx) => (
                        <a 
                          key={idx}
                          href={fuente.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 px-3 py-2 rounded-lg transition-colors text-xs text-blue-300 hover:text-blue-200 no-underline"
                        >
                          <span className="font-bold">💼 {fuente.empresa || "Empresa"}</span>
                          <span className="opacity-70">| {fuente.titulo}</span>
                          <span className="ml-1">↗</span>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Contador de ofertas (texto pequeño) */}
                {mensaje.role === 'assistant' && mensaje.ofertas_encontradas !== undefined && mensaje.ofertas_encontradas > 0 && !mensaje.fuentes && (
                  <p className="text-xs text-muted-foreground mt-2 italic">
                    {mensaje.ofertas_encontradas} ofertas relevantes encontradas
                  </p>
                )}
              </div>

              {mensaje.role === 'user' && (
                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                  <User className="h-5 w-5 text-primary" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center shrink-0">
                <Sparkles className="h-5 w-5 text-primary-foreground animate-pulse" />
              </div>
              <div className="glass-card p-4 bg-card">
                <p className="text-sm text-muted-foreground">Analizando mercado...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-lg bg-destructive/10 text-destructive text-sm">
              {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Queries */}
        {mensajes.length === 0 && (
          <div className="max-w-4xl mx-auto w-full mb-4 px-4">
            <div className="flex flex-wrap gap-2 justify-center">
              {suggestedQueries.map((suggestion) => (
                <Button
                  key={suggestion}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="rounded-full text-xs"
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="max-w-4xl mx-auto w-full px-4">
          <form onSubmit={handleSubmit} className="glass-card p-4">
            <div className="flex items-center gap-3">
              <Input
                type="text"
                placeholder="Escribe tu pregunta aquí... (ej: Salarios de Java en Quito)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-1 bg-transparent border-0 focus-visible:ring-0 text-base"
                disabled={loading}
              />
              <Button type="submit" size="lg" disabled={loading || !query.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </form>

          
        </div>
      </div>
    </Layout>
  );
}