"""
Script para agregar embeddings de texto a la colección 'productos'
para búsqueda semántica en MongoDB Atlas.
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
import hashlib
import numpy as np

# 1. Conexión
load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']

# 2. Función de embedding (idéntica a la usada en el buscador)
def generar_embedding_simple(texto):
    hash_obj = hashlib.sha256(texto.encode())
    seed = int(hash_obj.hexdigest(), 16) % (2**32)
    np.random.seed(seed)
    embedding = np.random.randn(384).tolist()
    norm = sum(x*x for x in embedding) ** 0.5
    return [x / norm for x in embedding]

# 3. Procesar todos los productos
total = db.productos.count_documents({})
print(f"Procesando {total} productos...")
procesados = 0
for doc in db.productos.find({}):
    texto = f"{doc.get('nombre_producto','')} {doc.get('marca','')} {doc.get('descripcion','')}"
    embedding = generar_embedding_simple(texto)
    db.productos.update_one({'_id': doc['_id']}, {'$set': {'embedding': embedding}})
    procesados += 1
    if procesados % 10 == 0 or procesados == total:
        print(f" - {procesados}/{total} productos actualizados")

print(f"\n✅ Embeddings agregados a {procesados} productos.")
client.close()
