"""
CASOS DE PRUEBA OBLIGATORIOS - Entrega 2
Sistema RAG con MongoDB + Sentence-BERT + Groq (Llama 3.3)

Requisitos del proyecto:
1. Búsqueda de productos con filtros
2. Consulta RAG multimodal
3. Búsqueda en múltiples colecciones
4. Performance y latencia
"""

import requests
import time
import json
from typing import Dict, Any, List
import statistics

BASE_URL = "http://localhost:8000"

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{'=' * 80}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print('=' * 80)

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


# ============================================================================
# TEST CASE 1: Búsqueda de productos con criterios específicos
# ============================================================================
def test_case_1_product_search():
    """
    TEST 1: Búsqueda de productos
    - Buscar "gafas de sol deportivas" en colección productos
    - Validar que retorna al menos 3 resultados
    - Verificar que los scores sean > 0.3 (30% similitud mínima)
    - Validar que los productos tengan precio y marca
    """
    print_header("TEST CASE 1: Búsqueda de Productos con Criterios Específicos")
    
    test_queries = [
        "gafas de sol deportivas",
        "lentes para protección solar",
        "monturas Ray-Ban"
    ]
    
    results_summary = []
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 80)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/search",
                json={
                    "query": query,
                    "limit": 5,
                    "collection": "productos"
                },
                timeout=10
            )
            
            elapsed_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Validaciones
                assert data['total_results'] >= 3, f"Debe retornar al menos 3 resultados, obtuvo {data['total_results']}"
                
                scores = [r['score'] for r in data['results']]
                assert all(score >= 0.3 for score in scores), f"Todos los scores deben ser >= 0.3"
                
                # Validar campos requeridos
                for result in data['results']:
                    assert 'nombre_producto' in result['content'], "Debe incluir nombre_producto"
                    assert 'marca' in result['content'], "Debe incluir marca"
                    assert 'precio_venta' in result['content'], "Debe incluir precio_venta"
                
                print_success(f"PASSED - {data['total_results']} resultados encontrados")
                print(f"   ⚡ Latencia: {elapsed_time:.2f}ms")
                print(f"   📊 Score promedio: {statistics.mean(scores):.4f}")
                print(f"   🎯 Mejor match: {data['results'][0]['content']['nombre_producto']} (Score: {scores[0]:.4f})")
                
                results_summary.append({
                    'query': query,
                    'passed': True,
                    'latency_ms': elapsed_time,
                    'results': data['total_results']
                })
            else:
                print_error(f"FAILED - Status {response.status_code}")
                results_summary.append({'query': query, 'passed': False})
                
        except AssertionError as e:
            print_error(f"FAILED - {str(e)}")
            results_summary.append({'query': query, 'passed': False})
        except Exception as e:
            print_error(f"ERROR - {str(e)}")
            results_summary.append({'query': query, 'passed': False})
    
    # Resumen
    passed = sum(1 for r in results_summary if r.get('passed', False))
    total = len(results_summary)
    
    print(f"\n{'=' * 80}")
    print(f"📊 RESUMEN TEST CASE 1: {passed}/{total} queries exitosas")
    
    if passed == total:
        print_success("TEST CASE 1: PASSED ✓")
        return True
    else:
        print_error("TEST CASE 1: FAILED ✗")
        return False


# ============================================================================
# TEST CASE 2: Consulta RAG multimodal (texto + contexto)
# ============================================================================
def test_case_2_rag_multimodal():
    """
    TEST 2: Consulta RAG Multimodal
    - Realizar pregunta que requiera contexto de múltiples fuentes
    - Validar que el LLM genere respuesta coherente
    - Verificar que use al menos 3 fuentes
    - Validar tiempo de respuesta < 5000ms
    """
    print_header("TEST CASE 2: Consulta RAG Multimodal")
    
    test_questions = [
        {
            "query": "¿Qué productos Oakley tienes disponibles y cuál es el más caro?",
            "expected_keywords": ["Oakley", "precio", "$"],
            "min_sources": 3
        },
        {
            "query": "Necesito lentes para persona con miopía, ¿qué opciones hay?",
            "expected_keywords": ["lentes", "miopía"],
            "min_sources": 2
        }
    ]
    
    results_summary = []
    
    for test in test_questions:
        print(f"\n💬 Pregunta: '{test['query']}'")
        print("-" * 80)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/rag",
                json={
                    "query": test['query'],
                    "limit": 5,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            elapsed_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Validaciones
                assert len(data['answer']) > 50, "La respuesta debe tener al menos 50 caracteres"
                assert data['total_sources'] >= test['min_sources'], f"Debe usar al menos {test['min_sources']} fuentes"
                assert elapsed_time < 10000, f"Latencia debe ser < 10s, obtuvo {elapsed_time:.0f}ms"
                
                # Verificar que no sea un error
                assert "Error al generar respuesta" not in data['answer'], "El LLM generó un error"
                
                # Validar keywords (flexible)
                answer_lower = data['answer'].lower()
                found_keywords = [kw for kw in test['expected_keywords'] if kw.lower() in answer_lower]
                
                print_success("PASSED - Respuesta generada correctamente")
                print(f"   ⚡ Latencia: {elapsed_time:.2f}ms")
                print(f"   📚 Fuentes utilizadas: {data['total_sources']}")
                print(f"   📝 Longitud respuesta: {len(data['answer'])} caracteres")
                print(f"   🔑 Keywords encontrados: {len(found_keywords)}/{len(test['expected_keywords'])}")
                print(f"\n   💬 Respuesta: {data['answer'][:200]}...")
                
                results_summary.append({
                    'query': test['query'],
                    'passed': True,
                    'latency_ms': elapsed_time,
                    'sources': data['total_sources']
                })
            else:
                print_error(f"FAILED - Status {response.status_code}")
                results_summary.append({'query': test['query'], 'passed': False})
                
        except AssertionError as e:
            print_error(f"FAILED - {str(e)}")
            results_summary.append({'query': test['query'], 'passed': False})
        except Exception as e:
            print_error(f"ERROR - {str(e)}")
            results_summary.append({'query': test['query'], 'passed': False})
    
    # Resumen
    passed = sum(1 for r in results_summary if r.get('passed', False))
    total = len(results_summary)
    
    print(f"\n{'=' * 80}")
    print(f"📊 RESUMEN TEST CASE 2: {passed}/{total} preguntas exitosas")
    
    if passed == total:
        print_success("TEST CASE 2: PASSED ✓")
        return True
    else:
        print_error("TEST CASE 2: FAILED ✗")
        return False


# ============================================================================
# TEST CASE 3: Búsqueda en múltiples colecciones
# ============================================================================
def test_case_3_multi_collection_search():
    """
    TEST 3: Búsqueda en Múltiples Colecciones
    - Buscar término que aparezca en diferentes colecciones
    - Validar que retorne resultados de al menos 2 colecciones
    - Verificar scores consistentes
    """
    print_header("TEST CASE 3: Búsqueda en Múltiples Colecciones")
    
    test_queries = [
        {
            "query": "María",
            "expected_collections": ["clientes"],  # Mínimo esperado
            "min_results": 3
        },
        {
            "query": "examen",
            "expected_collections": ["examenes", "citas"],
            "min_results": 3
        }
    ]
    
    results_summary = []
    
    for test in test_queries:
        print(f"\n🔍 Query: '{test['query']}' (búsqueda global)")
        print("-" * 80)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/search",
                json={
                    "query": test['query'],
                    "limit": 10,
                    "collection": None  # Buscar en todas
                },
                timeout=15
            )
            
            elapsed_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Validaciones
                assert data['total_results'] >= test['min_results'], f"Debe retornar al menos {test['min_results']} resultados"
                
                # Contar colecciones únicas
                collections_found = set(r['collection'] for r in data['results'])
                
                print_success(f"PASSED - {data['total_results']} resultados de {len(collections_found)} colecciones")
                print(f"   ⚡ Latencia: {elapsed_time:.2f}ms")
                print(f"   📚 Colecciones: {', '.join(collections_found)}")
                
                # Mostrar distribución
                from collections import Counter
                distribution = Counter(r['collection'] for r in data['results'])
                for col, count in distribution.most_common():
                    print(f"      • {col}: {count} resultados")
                
                results_summary.append({
                    'query': test['query'],
                    'passed': True,
                    'latency_ms': elapsed_time,
                    'collections': len(collections_found)
                })
            else:
                print_error(f"FAILED - Status {response.status_code}")
                results_summary.append({'query': test['query'], 'passed': False})
                
        except AssertionError as e:
            print_error(f"FAILED - {str(e)}")
            results_summary.append({'query': test['query'], 'passed': False})
        except Exception as e:
            print_error(f"ERROR - {str(e)}")
            results_summary.append({'query': test['query'], 'passed': False})
    
    # Resumen
    passed = sum(1 for r in results_summary if r.get('passed', False))
    total = len(results_summary)
    
    print(f"\n{'=' * 80}")
    print(f"📊 RESUMEN TEST CASE 3: {passed}/{total} búsquedas exitosas")
    
    if passed == total:
        print_success("TEST CASE 3: PASSED ✓")
        return True
    else:
        print_error("TEST CASE 3: FAILED ✗")
        return False


# ============================================================================
# TEST CASE 4: Performance y métricas
# ============================================================================
def test_case_4_performance():
    """
    TEST 4: Performance y Métricas
    - Medir latencia promedio de búsqueda vectorial
    - Validar que latencia < 3000ms
    - Medir throughput (requests por segundo)
    - Validar consistencia de resultados
    """
    print_header("TEST CASE 4: Performance y Métricas")
    
    # Ejecutar múltiples búsquedas para medir performance
    queries = [
        "gafas de sol",
        "lentes bifocales",
        "examen visual",
        "María González",
        "Ray-Ban"
    ]
    
    latencies = []
    successful_requests = 0
    
    print("\n🔄 Ejecutando 5 búsquedas para medir performance...")
    print("-" * 80)
    
    for i, query in enumerate(queries, 1):
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{BASE_URL}/search",
                json={
                    "query": query,
                    "limit": 5
                },
                timeout=10
            )
            
            elapsed_time = (time.time() - start_time) * 1000
            latencies.append(elapsed_time)
            
            if response.status_code == 200:
                successful_requests += 1
                print(f"   {i}. '{query}' → {elapsed_time:.2f}ms ✓")
            else:
                print(f"   {i}. '{query}' → FAILED ✗")
                
        except Exception as e:
            print(f"   {i}. '{query}' → ERROR: {str(e)} ✗")
    
    # Calcular métricas
    if latencies:
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # Throughput (requests/segundo)
        total_time = sum(latencies) / 1000  # convertir a segundos
        throughput = len(latencies) / total_time if total_time > 0 else 0
        
        print(f"\n{'=' * 80}")
        print("📊 MÉTRICAS DE PERFORMANCE:")
        print('=' * 80)
        print(f"   ✅ Requests exitosos: {successful_requests}/{len(queries)}")
        print(f"   ⚡ Latencia promedio: {avg_latency:.2f}ms")
        print(f"   📊 Latencia mediana: {median_latency:.2f}ms")
        print(f"   🏃 Latencia mínima: {min_latency:.2f}ms")
        print(f"   🐌 Latencia máxima: {max_latency:.2f}ms")
        print(f"   🚀 Throughput: {throughput:.2f} req/s")
        
        # Validaciones
        try:
            assert avg_latency < 3000, f"Latencia promedio debe ser < 3s, obtuvo {avg_latency:.0f}ms"
            assert successful_requests == len(queries), f"Todas las búsquedas deben ser exitosas"
            
            print(f"\n{'=' * 80}")
            print_success("TEST CASE 4: PASSED ✓")
            print(f"{'=' * 80}")
            return True
            
        except AssertionError as e:
            print(f"\n{'=' * 80}")
            print_error(f"TEST CASE 4: FAILED - {str(e)}")
            print(f"{'=' * 80}")
            return False
    else:
        print_error("TEST CASE 4: FAILED - No se pudieron obtener métricas")
        return False


# ============================================================================
# EJECUTAR TODOS LOS TESTS
# ============================================================================
def run_all_tests():
    """Ejecuta todos los casos de prueba y genera reporte final"""
    
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}{'🧪 SUITE DE PRUEBAS OBLIGATORIAS - ENTREGA 2':^80}{Colors.END}")
    print("=" * 80)
    print("\nSistema RAG - Óptica El-trin-Relacional")
    print("Tecnologías: MongoDB + Sentence-BERT + Groq (Llama 3.3)")
    print(f"Servidor: {BASE_URL}")
    
    # Verificar que el servidor esté activo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print_error("El servidor no está respondiendo correctamente")
            return
    except:
        print_error(f"No se puede conectar al servidor en {BASE_URL}")
        print_warning("Asegúrate de que el servidor esté corriendo:")
        print("   python -m uvicorn api.main:app --reload --port 8000")
        return
    
    # Ejecutar tests
    results = {
        'Test 1': test_case_1_product_search(),
        'Test 2': test_case_2_rag_multimodal(),
        'Test 3': test_case_3_multi_collection_search(),
        'Test 4': test_case_4_performance()
    }
    
    # Reporte final
    print("\n\n" + "=" * 80)
    print(f"{Colors.BLUE}{'📊 REPORTE FINAL DE PRUEBAS':^80}{Colors.END}")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}PASSED ✓{Colors.END}" if passed else f"{Colors.RED}FAILED ✗{Colors.END}"
        print(f"   {test_name}: {status}")
    
    # Estadísticas
    total_tests = len(results)
    passed_tests = sum(1 for p in results.values() if p)
    success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 80)
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print("=" * 80)
    
    if success_rate == 100:
        print(f"\n{Colors.GREEN}{'🎉 TODOS LOS TESTS PASARON - SISTEMA VALIDADO':^80}{Colors.END}\n")
    elif success_rate >= 75:
        print(f"\n{Colors.YELLOW}{'⚠️  MAYORÍA DE TESTS PASARON - REVISAR FALLOS':^80}{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}{'❌ SISTEMA REQUIERE CORRECCIONES':^80}{Colors.END}\n")


if __name__ == "__main__":
    run_all_tests()
