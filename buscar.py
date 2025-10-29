"""
Buscador Interactivo de Imágenes
Interfaz de usuario con input para buscar en todas las colecciones
"""

from buscador_universal import BuscadorImagenesUniversal, mostrar_resultados
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Configurar conexión
load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']
buscador = BuscadorImagenesUniversal(db)

def menu_principal():
    """Muestra el menú principal"""
    print("\n" + "="*80)
    print("🔍 BUSCADOR INTERACTIVO DE IMÁGENES")
    print("="*80)
    print("\nOpciones de búsqueda:")
    print("  1. Buscar en TODAS las colecciones")
    print("  2. Buscar solo en PRODUCTOS")
    print("  3. Buscar solo en PERSONAS (clientes, asesores, especialistas)")
    print("  4. Buscar solo en EMPRESAS (proveedores, laboratorios)")
    print("  5. Top resultados unificados")
    print("  0. Salir")
    print("-"*80)

def buscar_interactivo():
    """Función principal interactiva"""
    
    while True:
        menu_principal()
        
        try:
            opcion = input("\n➤ Selecciona una opción (0-5): ").strip()
            
            if opcion == '0':
                print("\n👋 ¡Hasta luego!")
                break
            
            if opcion not in ['1', '2', '3', '4', '5']:
                print("❌ Opción inválida. Intenta de nuevo.")
                continue
            
            # Pedir query de búsqueda
            query = input("\n🔎 ¿Qué quieres buscar?: ").strip()
            
            if not query:
                print("❌ Debes ingresar algo para buscar.")
                continue
            
            # Pedir límite de resultados
            try:
                limit_input = input("📊 ¿Cuántos resultados quieres ver? (por defecto 5): ").strip()
                limit = int(limit_input) if limit_input else 5
                
                if limit <= 0:
                    print("❌ El límite debe ser mayor a 0. Usando 5.")
                    limit = 5
            except ValueError:
                print("⚠️  Valor inválido. Usando límite de 5 resultados.")
                limit = 5
            
            # Ejecutar búsqueda según opción
            print(f"\n🔍 Buscando '{query}'...\n")
            
            if opcion == '1':
                resultados = buscador.buscar(query, limit=limit)
                mostrar_resultados(resultados)
                
            elif opcion == '2':
                resultados = buscador.buscar_solo_productos(query, limit=limit)
                mostrar_resultados(resultados)
                
            elif opcion == '3':
                resultados = buscador.buscar_solo_personas(query, limit=limit)
                mostrar_resultados(resultados)
                
            elif opcion == '4':
                resultados = buscador.buscar_solo_empresas(query, limit=limit)
                mostrar_resultados(resultados)
                
            elif opcion == '5':
                resultados = buscador.buscar_todo(query, limit_por_coleccion=limit)
                print(f"\n✅ Encontrados {len(resultados)} resultados totales\n")
                mostrar_resultados(resultados[:limit])
            
            # Preguntar si quiere ver más detalles o continuar
            input("\n[Presiona ENTER para continuar...]")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\n[Presiona ENTER para continuar...]")
    
    client.close()

# Ejecutar el buscador interactivo
if __name__ == "__main__":
    try:
        buscar_interactivo()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        client.close()
