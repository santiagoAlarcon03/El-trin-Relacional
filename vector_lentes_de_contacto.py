"""
Script para generar el vector de búsqueda para Atlas Search
a partir del texto 'lentes de contacto'.
"""

import hashlib
import numpy as np

# Texto de búsqueda
consulta = "lentes de contacto"

# Función de embedding (idéntica a la usada en tus productos)
def generar_embedding_simple(texto):
    hash_obj = hashlib.sha256(texto.encode())
    seed = int(hash_obj.hexdigest(), 16) % (2**32)
    np.random.seed(seed)
    embedding = np.random.randn(384).tolist()
    norm = sum(x*x for x in embedding) ** 0.5
    return [x / norm for x in embedding]

vector = generar_embedding_simple(consulta)

# Imprimir el vector en formato listo para pegar en Atlas
import json
print("\nCopia este vector en tu pipeline de Atlas:")
print(json.dumps(vector))
