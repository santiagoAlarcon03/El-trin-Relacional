"""
Script para vectorizar las imágenes de productos usando CLIP
Genera embeddings de 512 dimensiones para cada imagen de producto
"""

import sys
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import time
import ast

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.embeddings import generar_embedding_imagen

# Cargar variables de entorno
load_dotenv()

# Conexión a MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']


def vectorizar_productos():
    """
    Vectoriza todas las imágenes de productos en la colección
    """
    print("=" * 80)
    print("🖼️  VECTORIZACIÓN DE IMÁGENES CON CLIP")
    print("=" * 80)
    
    # Obtener productos con imágenes
    productos = list(db.productos.find({
        'imagenes': {'$exists': True, '$ne': None, '$ne': []}
    }))
    
    print(f"\n📊 Productos con imágenes: {len(productos)}")
    
    if not productos:
        print("⚠️  No hay productos con imágenes para vectorizar")
        return
    
    # Contar imágenes totales
    total_imagenes = 0
    for prod in productos:
        imagenes = prod.get('imagenes', [])
        if isinstance(imagenes, list):
            total_imagenes += len(imagenes)
        elif isinstance(imagenes, str):
            try:
                imagenes_list = ast.literal_eval(imagenes)
                total_imagenes += len(imagenes_list)
            except:
                pass
    
    print(f"📸 Total de imágenes a procesar: {total_imagenes}")
    print("\n" + "-" * 80)
    
    # Procesar cada producto
    productos_actualizados = 0
    imagenes_vectorizadas = 0
    errores = 0
    
    start_time = time.time()
    
    for i, producto in enumerate(productos, 1):
        producto_id = producto['_id']
        nombre = producto.get('nombre_producto', 'Sin nombre')
        
        print(f"\n[{i}/{len(productos)}] 🔄 Procesando: {nombre}")
        print(f"   ID: {producto_id}")
        
        try:
            # Obtener lista de imágenes del producto
            imagenes = producto.get('imagenes', [])
            
            # Si está como string, convertir a lista
            if isinstance(imagenes, str):
                try:
                    imagenes = ast.literal_eval(imagenes)
                except:
                    print(f"   ⚠️  Error parseando lista de imágenes")
                    continue
            
            if not imagenes or not isinstance(imagenes, list) or len(imagenes) == 0:
                print(f"   ⏭️  Sin imágenes válidas")
                continue
            
            # Usar la primera imagen como representativa
            imagen_principal = imagenes[0]
            
            # Generar embedding de la imagen principal
            print(f"   🖼️  Generando embedding de imagen principal ({len(imagenes)} disponibles)...")
            print(f"   📍 URL: {imagen_principal[:60]}...")
            
            image_embedding = generar_embedding_imagen(imagen_principal)
            
            # Verificar que no sea vector cero
            if not image_embedding or all(v == 0.0 for v in image_embedding):
                print(f"   ❌ Error: Embedding nulo o cero")
                errores += 1
                continue
            
            # Actualizar documento en MongoDB
            db.productos.update_one(
                {'_id': producto_id},
                {
                    '$set': {
                        'image_embedding': image_embedding,
                        'image_embedding_model': 'CLIP-ViT-B/32',
                        'image_embedding_dims': len(image_embedding),
                        'image_embedding_source': imagen_principal,
                        'vectorizado_imagen_fecha': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
            )
            
            print(f"   ✅ Embedding guardado: {len(image_embedding)} dims")
            productos_actualizados += 1
            imagenes_vectorizadas += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            errores += 1
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE VECTORIZACIÓN")
    print("=" * 80)
    print(f"✅ Productos actualizados: {productos_actualizados}/{len(productos)}")
    print(f"🖼️  Imágenes vectorizadas: {imagenes_vectorizadas}")
    print(f"❌ Errores: {errores}")
    print(f"⏱️  Tiempo total: {elapsed_time:.2f}s")
    if len(productos) > 0:
        print(f"⚡ Promedio por producto: {elapsed_time/len(productos):.2f}s")
    print("=" * 80)
    
    # Verificar estado de vectorización
    verificar_vectorizacion()


def verificar_vectorizacion():
    """
    Verifica el estado de vectorización de las imágenes
    """
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN DE VECTORIZACIÓN")
    print("=" * 80)
    
    total_productos = db.productos.count_documents({})
    con_imagenes = db.productos.count_documents({'imagenes': {'$exists': True, '$ne': None, '$ne': []}})
    vectorizados = db.productos.count_documents({'image_embedding': {'$exists': True}})
    
    print(f"\n📦 Total de productos: {total_productos}")
    print(f"🖼️  Productos con imágenes: {con_imagenes}")
    print(f"✅ Productos vectorizados: {vectorizados}")
    
    if con_imagenes > 0:
        cobertura = (vectorizados / con_imagenes) * 100
        print(f"📊 Cobertura: {cobertura:.1f}%")
        
        if cobertura < 100:
            print(f"\n⚠️  Faltan {con_imagenes - vectorizados} productos por vectorizar")
    
    # Mostrar ejemplo de embedding
    ejemplo = db.productos.find_one({'image_embedding': {'$exists': True}})
    if ejemplo:
        print(f"\n📄 Ejemplo de producto vectorizado:")
        print(f"   Nombre: {ejemplo.get('nombre_producto', 'N/A')}")
        print(f"   Marca: {ejemplo.get('marca', 'N/A')}")
        print(f"   Dimensiones embedding: {len(ejemplo['image_embedding'])}")
        print(f"   Modelo: {ejemplo.get('image_embedding_model', 'N/A')}")
        print(f"   Fecha: {ejemplo.get('vectorizado_imagen_fecha', 'N/A')}")
    
    print("\n" + "=" * 80)


def listar_productos_sin_vectorizar():
    """
    Lista los productos con imágenes que aún no han sido vectorizados
    """
    print("\n" + "=" * 80)
    print("📋 PRODUCTOS SIN VECTORIZAR")
    print("=" * 80)
    
    sin_vectorizar = list(db.productos.find({
        '$and': [
            {'imagenes': {'$exists': True, '$ne': None, '$ne': []}},
            {'image_embedding': {'$exists': False}}
        ]
    }))
    
    if not sin_vectorizar:
        print("\n✅ Todos los productos con imágenes están vectorizados")
    else:
        print(f"\n⚠️  {len(sin_vectorizar)} productos sin vectorizar:\n")
        for i, prod in enumerate(sin_vectorizar, 1):
            print(f"{ i}. {prod.get('nombre_producto', 'Sin nombre')} - {prod.get('marca', 'Sin marca')}")
            imagenes = prod.get('imagenes', [])
            if isinstance(imagenes, str):
                try:
                    imagenes = ast.literal_eval(imagenes)
                except:
                    pass
            if imagenes and isinstance(imagenes, list):
                for j, img_url in enumerate(imagenes, 1):
                    print(f"   Imagen {j}: {img_url[:60]}...")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Vectorizar imágenes de productos con CLIP')
    parser.add_argument('--verificar', action='store_true', help='Solo verificar estado de vectorización')
    parser.add_argument('--listar', action='store_true', help='Listar productos sin vectorizar')
    
    args = parser.parse_args()
    
    if args.verificar:
        verificar_vectorizacion()
    elif args.listar:
        listar_productos_sin_vectorizar()
    else:
        vectorizar_productos()
