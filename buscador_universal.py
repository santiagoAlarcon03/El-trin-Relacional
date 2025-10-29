"""
Buscador Universal de Imágenes
Busca en TODAS las colecciones que tengan imágenes usando Vector Search
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']

def generar_embedding_simple(texto):
    """Genera embedding de 384 dimensiones basado en texto"""
    import hashlib
    import numpy as np
    
    hash_obj = hashlib.sha256(texto.encode())
    seed = int(hash_obj.hexdigest(), 16) % (2**32)
    np.random.seed(seed)
    
    embedding = np.random.randn(384).tolist()
    norm = sum(x*x for x in embedding) ** 0.5
    return [x / norm for x in embedding]


class BuscadorImagenesUniversal:
    """
    Clase única para buscar imágenes en todas las colecciones
    """
    
    def __init__(self, db):
        self.db = db
        # Definir colecciones y sus campos de imagen
        self.colecciones = {
            'productos': {
                'campo_imagen': 'imagenes',  # Array de imágenes
                'campos_busqueda': ['nombre_producto', 'marca', 'descripcion'],
                'campos_mostrar': ['nombre_producto', 'marca', 'precio_venta']
            },
            'clientes': {
                'campo_imagen': 'foto_perfil',  # Imagen única
                'campos_busqueda': ['nombre_completo', 'email'],
                'campos_mostrar': ['nombre_completo', 'email']
            },
            'asesores': {
                'campo_imagen': 'foto_perfil',
                'campos_busqueda': ['nombre_completo', 'especialidad'],
                'campos_mostrar': ['nombre_completo', 'especialidad']
            },
            'especialistas': {
                'campo_imagen': 'foto_perfil',
                'campos_busqueda': ['nombre_completo', 'especialidad'],
                'campos_mostrar': ['nombre_completo', 'especialidad', 'numero_licencia']
            },
            'proveedores': {
                'campo_imagen': 'logo',
                'campos_busqueda': ['nombre_proveedor', 'ciudad'],
                'campos_mostrar': ['nombre_proveedor', 'telefono']
            },
            'laboratorios': {
                'campo_imagen': 'logo',
                'campos_busqueda': ['nombre_laboratorio', 'ciudad'],
                'campos_mostrar': ['nombre_laboratorio', 'telefono']
            }
        }
    
    def buscar(self, query, limit=10, colecciones=None):
        """
        Busca en todas las colecciones (o las especificadas)
        
        Args:
            query: Texto a buscar
            limit: Resultados por colección
            colecciones: Lista de colecciones específicas o None para todas
        
        Returns:
            Dict con resultados por colección
        """
        query_embedding = generar_embedding_simple(query)
        resultados_totales = {}
        
        colecciones_buscar = colecciones or list(self.colecciones.keys())
        
        for col_name in colecciones_buscar:
            if col_name not in self.colecciones:
                continue
                
            config = self.colecciones[col_name]
            resultados = self._buscar_en_coleccion(
                col_name, 
                query_embedding, 
                config,
                limit
            )
            
            if resultados:
                resultados_totales[col_name] = resultados
        
        return resultados_totales
    
    def _buscar_en_coleccion(self, col_name, query_embedding, config, limit):
        """Busca en una colección específica"""
        try:
            # Buscar todos los documentos con embedding
            documentos = list(self.db[col_name].find({
                'embedding': {'$exists': True}
            }))
            
            if not documentos:
                return []
            
            # Calcular similitud
            def cosine_similarity(v1, v2):
                return sum(a*b for a, b in zip(v1, v2))
            
            resultados = []
            for doc in documentos:
                # Verificar que tenga imagen
                campo_img = config['campo_imagen']
                imagen = doc.get(campo_img)
                
                # Filtrar si no tiene imagen o está vacío
                if not imagen or (isinstance(imagen, list) and len(imagen) == 0):
                    continue
                
                score = cosine_similarity(query_embedding, doc['embedding'])
                
                # Construir resultado
                resultado = {
                    '_id': doc['_id'],
                    'coleccion': col_name,
                    'score': score,
                    'imagen': imagen
                }
                
                # Agregar campos de búsqueda
                for campo in config['campos_mostrar']:
                    if campo in doc:
                        resultado[campo] = doc[campo]
                
                resultados.append(resultado)
            
            # Ordenar por score
            resultados.sort(key=lambda x: x['score'], reverse=True)
            return resultados[:limit]
            
        except Exception as e:
            print(f"⚠️ Error en {col_name}: {e}")
            return []
    
    def buscar_todo(self, query, limit_por_coleccion=5):
        """
        Busca en todas las colecciones y devuelve resultados unificados
        """
        resultados = self.buscar(query, limit=limit_por_coleccion)
        
        # Unificar y ordenar por score
        todos = []
        for col, items in resultados.items():
            todos.extend(items)
        
        todos.sort(key=lambda x: x['score'], reverse=True)
        return todos
    
    def buscar_solo_productos(self, query, limit=10):
        """Atajo para buscar solo en productos"""
        return self.buscar(query, limit, colecciones=['productos'])
    
    def buscar_solo_personas(self, query, limit=10):
        """Busca solo en colecciones de personas (clientes, asesores, especialistas)"""
        return self.buscar(query, limit, colecciones=['clientes', 'asesores', 'especialistas'])
    
    def buscar_solo_empresas(self, query, limit=10):
        """Busca solo en empresas (proveedores, laboratorios)"""
        return self.buscar(query, limit, colecciones=['proveedores', 'laboratorios'])


def mostrar_resultados(resultados, mostrar_imagenes=True):
    """Muestra resultados de forma bonita"""
    if isinstance(resultados, dict):
        # Resultados por colección
        total = sum(len(items) for items in resultados.values())
        print(f"\n✅ Encontrados {total} resultados en {len(resultados)} colecciones\n")
        
        for col, items in resultados.items():
            print(f"\n{'='*80}")
            print(f"📁 {col.upper()} ({len(items)} resultados)")
            print('='*80)
            
            for i, r in enumerate(items, 1):
                _mostrar_item(r, i, mostrar_imagenes)
    
    elif isinstance(resultados, list):
        # Resultados unificados
        print(f"\n✅ Encontrados {len(resultados)} resultados totales\n")
        
        for i, r in enumerate(resultados, 1):
            _mostrar_item(r, i, mostrar_imagenes)
    
    else:
        print("❌ Sin resultados")


def _mostrar_item(r, numero, mostrar_imagenes):
    """Muestra un item individual"""
    print(f"\n{numero}. [{r['coleccion'].upper()}]")
    print(f"   Score: {r['score']:.4f}")
    
    # Mostrar campos relevantes
    for key, value in r.items():
        if key not in ['_id', 'coleccion', 'score', 'imagen', 'embedding']:
            print(f"   {key}: {value}")
    
    # Mostrar imágenes
    if mostrar_imagenes:
        imagen = r.get('imagen')
        if isinstance(imagen, list):
            print(f"   📷 Imágenes ({len(imagen)}):")
            for idx, img in enumerate(imagen, 1):
                print(f"      {idx}. {img[:75]}...")
        elif imagen:
            print(f"   📷 Imagen: {imagen[:75]}...")


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🔍 BUSCADOR UNIVERSAL DE IMÁGENES")
    print("=" * 80)
    
    buscador = BuscadorImagenesUniversal(db)
    
    # Ejemplo 1: Buscar en TODAS las colecciones
    print("\n\n📸 Ejemplo 1: Buscar 'sol' en TODAS las colecciones")
    print("-" * 80)
    resultados = buscador.buscar('sol', limit=3)
    mostrar_resultados(resultados)
    
    # Ejemplo 2: Buscar solo en productos
    print("\n\n📸 Ejemplo 2: Buscar 'Oakley' solo en productos")
    print("-" * 80)
    resultados = buscador.buscar_solo_productos('Oakley', limit=3)
    mostrar_resultados(resultados)
    
    # Ejemplo 3: Buscar en personas
    print("\n\n📸 Ejemplo 3: Buscar 'Ana' en personas")
    print("-" * 80)
    resultados = buscador.buscar_solo_personas('Ana', limit=3)
    mostrar_resultados(resultados)
    
    # Ejemplo 4: Resultados unificados (todos mezclados)
    print("\n\n📸 Ejemplo 4: Top 10 resultados de 'gafas' (todas las colecciones mezcladas)")
    print("-" * 80)
    resultados = buscador.buscar_todo('gafas', limit_por_coleccion=5)
    mostrar_resultados(resultados[:10])
    
    print("\n" + "=" * 80)
    print("✅ BÚSQUEDAS COMPLETADAS")
    print("=" * 80)
    
    print("""
    
💡 USO INTERACTIVO:

from buscador_universal import BuscadorImagenesUniversal, mostrar_resultados
from pymongo import MongoClient
import os

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']
buscador = BuscadorImagenesUniversal(db)

# Buscar en todas las colecciones
resultados = buscador.buscar('sol', limit=5)
mostrar_resultados(resultados)

# Buscar solo productos
resultados = buscador.buscar_solo_productos('Ray-Ban', limit=5)

# Buscar solo personas
resultados = buscador.buscar_solo_personas('María', limit=5)

# Top 10 de todo
resultados = buscador.buscar_todo('gafas', limit_por_coleccion=10)
mostrar_resultados(resultados[:10])
    """)
    
    client.close()
