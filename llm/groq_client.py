"""
Cliente para Groq API - Integración con Llama 3.1
"""

import os
from groq import Groq
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class GroqLLMClient:
    """
    Cliente para generar respuestas usando Groq + Llama 3.1
    """
    
    def __init__(self, api_key: str = None):
        """
        Inicializa cliente de Groq
        
        Args:
            api_key: API key de Groq (si no se provee, usa variable de entorno)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY no encontrada. Configúrala en .env o pásala como parámetro")
        
        self.client = Groq(api_key=self.api_key)
        # Modelos disponibles: llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768
        self.model = "llama-3.3-70b-versatile"
        logger.info(f"✅ Cliente Groq inicializado con modelo: {self.model}")
    
    def generar_respuesta(
        self, 
        pregunta: str, 
        contexto: List[Dict], 
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Genera respuesta usando RAG (Retrieval-Augmented Generation)
        
        Args:
            pregunta: Pregunta del usuario
            contexto: Lista de documentos recuperados
            temperature: Temperatura del modelo [0.0-2.0]
            max_tokens: Máximo de tokens a generar
            
        Returns:
            Respuesta generada por el LLM
        """
        # Construir contexto formateado
        contexto_texto = self._formatear_contexto(contexto)
        
        # Crear prompt con contexto
        prompt = self._crear_prompt(pregunta, contexto_texto)
        
        try:
            logger.info(f"🤖 Generando respuesta con Groq (temp={temperature})...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en óptica y gestión de clientes. Responde basándote ÚNICAMENTE en el contexto proporcionado. Si no tienes información suficiente, dilo claramente."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=False
            )
            
            respuesta = response.choices[0].message.content
            logger.info(f"✅ Respuesta generada ({len(respuesta)} caracteres)")
            
            return respuesta
            
        except Exception as e:
            logger.error(f"❌ Error en Groq API: {e}")
            return f"Error al generar respuesta: {str(e)}"
    
    def _formatear_contexto(self, contexto: List[Dict]) -> str:
        """
        Formatea documentos recuperados en texto legible
        
        Args:
            contexto: Lista de documentos con score y contenido
            
        Returns:
            Contexto formateado como string
        """
        if not contexto:
            return "No se encontró información relevante."
        
        lineas = ["INFORMACIÓN DISPONIBLE EN LA BASE DE DATOS:\n"]
        
        for i, doc in enumerate(contexto, 1):
            coleccion = doc.get('collection', 'desconocida')
            contenido = doc.get('content', {})
            score = doc.get('score', 0.0)
            
            lineas.append(f"\n[Documento {i} - {coleccion} - Relevancia: {score:.2f}]")
            
            # Extraer campos relevantes según la colección
            if coleccion == 'productos':
                lineas.append(f"Producto: {contenido.get('nombre_producto', 'N/A')}")
                lineas.append(f"Marca: {contenido.get('marca', 'N/A')}")
                lineas.append(f"Descripción: {contenido.get('descripcion', 'N/A')}")
                lineas.append(f"Precio: ${contenido.get('precio_venta', 0):,.0f}")
            
            elif coleccion in ['clientes', 'asesores', 'especialistas']:
                lineas.append(f"Nombre: {contenido.get('nombre', '')} {contenido.get('apellido', '')}")
                lineas.append(f"Email: {contenido.get('email', 'N/A')}")
                if 'especialidad' in contenido:
                    lineas.append(f"Especialidad: {contenido.get('especialidad', 'N/A')}")
            
            elif coleccion == 'examenes':
                lineas.append(f"Tipo: {contenido.get('tipo_examen', 'Examen general')}")
                diagnostico = contenido.get('diagnostico', {})
                if isinstance(diagnostico, dict):
                    lineas.append(f"Diagnóstico: {diagnostico.get('descripcion', 'N/A')}")
            
            elif coleccion == 'citas':
                lineas.append(f"Motivo: {contenido.get('motivo', 'N/A')}")
                lineas.append(f"Estado: {contenido.get('estado', 'N/A')}")
                if 'notas' in contenido:
                    lineas.append(f"Notas: {contenido.get('notas', 'N/A')}")
        
        return "\n".join(lineas)
    
    def _crear_prompt(self, pregunta: str, contexto: str) -> str:
        """
        Crea prompt optimizado para RAG
        
        Args:
            pregunta: Pregunta del usuario
            contexto: Contexto formateado
            
        Returns:
            Prompt completo
        """
        return f"""Contexto de la base de datos:

{contexto}

---

Pregunta del usuario: {pregunta}

Instrucciones:
- Responde ÚNICAMENTE basándote en la información del contexto proporcionado
- Si no tienes información suficiente, dilo claramente
- Sé conciso y preciso
- Si mencionas productos o servicios, incluye precios y marcas cuando estén disponibles
- Usa un tono profesional pero amigable

Respuesta:"""


# Instancia global (singleton)
_groq_client = None


def get_groq_client() -> GroqLLMClient:
    """Obtiene instancia única del cliente Groq"""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqLLMClient()
    return _groq_client


if __name__ == "__main__":
    # Prueba del cliente
    print("=" * 80)
    print("🧪 PRUEBA DE CLIENTE GROQ")
    print("=" * 80)
    
    try:
        client = GroqLLMClient()
        
        # Contexto de prueba
        contexto_prueba = [
            {
                'collection': 'productos',
                'score': 0.85,
                'content': {
                    'nombre_producto': 'Ray-Ban Aviator',
                    'marca': 'Ray-Ban',
                    'descripcion': 'Gafas de sol clásicas con protección UV400',
                    'precio_venta': 250000
                }
            }
        ]
        
        pregunta = "¿Qué gafas tienes disponibles?"
        
        print(f"\n📝 Pregunta: {pregunta}")
        print("\n🔄 Generando respuesta...\n")
        
        respuesta = client.generar_respuesta(pregunta, contexto_prueba)
        
        print("=" * 80)
        print("💬 RESPUESTA DEL LLM:")
        print("=" * 80)
        print(respuesta)
        print("\n" + "=" * 80)
        print("✅ PRUEBA COMPLETADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nAsegúrate de tener GROQ_API_KEY configurada en .env")
