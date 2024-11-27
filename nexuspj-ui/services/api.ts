
export interface ApiError {
  message: string;
  code?: string;
}

export interface NodosResponse {
  nodos: Array<{
    metadata: any;
    texto: string;
  }>;
}

export interface SintetizarResponse {
  respuesta: string;
}

interface ConsultaRequest {
  consulta: string;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiService = {
  async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: `HTTP error! status: ${response.status}`
      }));
      throw new Error(error.message || `Error: ${response.status}`);
    }
    return response.json();
  },

  // Sanitize input to handle special characters
  sanitizeInput(text: string): string {
    return text.normalize('NFKD')
              .replace(/[\u2011-\u2015]/g, '-') // Replace various hyphens with standard hyphen
              .replace(/[^\x00-\x7F]/g, ''); // Remove non-ASCII characters
  },

  async extraer(consulta: string): Promise<NodosResponse> {
    const sanitizedConsulta = this.sanitizeInput(consulta);
    const response = await fetch(`${BASE_URL}/extraer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept-Charset': 'UTF-8',
      },
      body: JSON.stringify({ consulta: sanitizedConsulta } as ConsultaRequest),
    });
    return this.handleResponse<NodosResponse>(response);
  },

  async sintetizar(consulta: string): Promise<SintetizarResponse> {
    const sanitizedConsulta = this.sanitizeInput(consulta);
    const response = await fetch(`${BASE_URL}/sintetizar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept-Charset': 'UTF-8',
      },
      body: JSON.stringify({ consulta: sanitizedConsulta } as ConsultaRequest),
    });
    return this.handleResponse<SintetizarResponse>(response);
  },

  async buscar(consulta: string): Promise<NodosResponse> {
    const sanitizedConsulta = this.sanitizeInput(consulta);
    const response = await fetch(`${BASE_URL}/buscar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept-Charset': 'UTF-8',
      },
      body: JSON.stringify({ consulta: sanitizedConsulta } as ConsultaRequest),
    });
    return this.handleResponse<NodosResponse>(response);
  },
};