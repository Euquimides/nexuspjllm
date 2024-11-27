"use client";
import { useState } from "react";
import { apiService, NodosResponse, SintetizarResponse } from "../../services/api";

export default function Home() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string>("");
  const [selectedOption, setSelectedOption] = useState<number | null>(null);

  const handleSubmit = async () => {
    if (!selectedOption) return;
    
    setLoading(true);
    try {
      let result: NodosResponse | SintetizarResponse;
      
      switch (selectedOption) {
        case 1: // Extraer jurisprudencia
          result = await apiService.extraer(query);
          setResponse(JSON.stringify((result as NodosResponse).nodos, null, 2));
          break;
        
        case 2: // Generar respuesta
          result = await apiService.sintetizar(query);
          setResponse((result as SintetizarResponse).respuesta);
          break;
        
        case 3: // Top 3 relevante
          result = await apiService.buscar(query);
          setResponse(JSON.stringify((result as NodosResponse).nodos, null, 2));
          break;
          
        default:
          throw new Error("Opción inválida");
      }
    } catch (error) {
      console.error(error);
      setResponse("Error: " + (error instanceof Error ? error.message : "Ocurrió un error inesperado"));
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            NexusPJLLM
          </h1>
          <p className="text-gray-600">
            Sistema de consulta y análisis de jurisprudencia inteligente
          </p>
        </div>

        <div className="space-y-4 mb-8">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ingrese su consulta jurídica..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
          />

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {[
              "Extraer jurisprudencia",
              "Generar respuesta",
              "Top 3 relevante",
            ].map((text, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedOption(idx + 1)}
                className={`bg-white p-4 rounded-lg border ${
                  selectedOption === idx + 1 
                    ? 'border-blue-500 ring-2 ring-blue-500' 
                    : 'border-gray-200 hover:border-blue-500'
                } transition-colors`}
              >
                <h3 className="text-lg font-medium text-black mb-2">
                  Opción {idx + 1}
                </h3>
                <p className="text-sm text-black">{text}</p>
              </button>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading || !query || !selectedOption}
            className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Ejecutar
          </button>
        </div>

        {loading && (
          <div className="text-center text-gray-600">Procesando...</div>
        )}

        {response && (
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h2 className="text-lg font-medium mb-4">Resultado</h2>
            <pre className="whitespace-pre-wrap text-sm text-gray-700">
              {response}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}