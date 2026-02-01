"""
Clase para testear la conexión a Supabase
"""
import os
import sys

# Permitir ejecutar directamente desde db/ o como módulo
if __name__ == "__main__":
    _scraper_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _scraper_root not in sys.path:
        sys.path.insert(0, _scraper_root)
    from db.supabase_helper import supabase
else:
    from .supabase_helper import supabase

from dotenv import load_dotenv

load_dotenv()

class TestSupabase:
    """Clase para probar la conexión y operaciones con Supabase"""
    
    def __init__(self):
        self.supabase = supabase
        print("=" * 70)
        print("🔌 TEST DE CONEXIÓN A SUPABASE")
        print("=" * 70)
    
    def test_conexion(self):
        """Prueba la conexión básica a Supabase"""
        print("\n[1/5] 🔗 Probando conexión básica...")
        try:
            # Intentar una consulta simple
            response = self.supabase.table('jobs_raw').select('id').limit(1).execute()
            print("✅ Conexión exitosa a Supabase")
            return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_tablas_existen(self):
        """Verifica que las tablas necesarias existan"""
        print("\n[2/5] 📋 Verificando existencia de tablas...")
        tablas = ['jobs_raw', 'jobs_clean', 'jobs']
        tablas_existentes = []
        tablas_faltantes = []
        
        for tabla in tablas:
            try:
                self.supabase.table(tabla).select('id').limit(1).execute()
                tablas_existentes.append(tabla)
                print(f"   ✅ Tabla '{tabla}' existe")
            except Exception as e:
                tablas_faltantes.append(tabla)
                print(f"   ❌ Tabla '{tabla}' NO existe: {str(e)[:80]}")
        
        if tablas_faltantes:
            print(f"\n⚠️ Tablas faltantes: {', '.join(tablas_faltantes)}")
            print("   Ejecuta el script create_tables.sql en Supabase")
            return False
        return True
    
    def test_insertar_dato(self):
        """Prueba insertar un dato de prueba en jobs_raw"""
        print("\n[3/5] 📝 Probando inserción de datos...")
        try:
            dato_prueba = {
                'plataforma': 'test',
                'rol_busqueda': 'test',
                'fecha_publicacion': '2024-01-01',
                'oferta_laboral': 'Oferta de Prueba - Puede Eliminarse',
                'locacion': 'Ecuador',
                'descripcion': 'Esta es una oferta de prueba',
                'sueldo': None,
                'compania': 'Test Company',
                'url_publicacion': 'https://test.com/prueba-12345'
            }
            
            response = self.supabase.table('jobs_raw').upsert(
                dato_prueba, 
                on_conflict='url_publicacion'
            ).execute()
            
            print("✅ Inserción exitosa")
            print(f"   ID del registro: {response.data[0]['id'] if response.data else 'N/A'}")
            return True
        except Exception as e:
            print(f"❌ Error en inserción: {e}")
            return False
    
    def test_leer_datos(self):
        """Prueba leer datos de las tablas"""
        print("\n[4/5] 📖 Probando lectura de datos...")
        try:
            # Leer de jobs_raw
            response = self.supabase.table('jobs_raw').select('*').limit(5).execute()
            count = len(response.data) if response.data else 0
            print(f"✅ Lectura exitosa de jobs_raw: {count} registros encontrados")
            
            # Leer de jobs_clean
            try:
                response = self.supabase.table('jobs_clean').select('*').limit(5).execute()
                count = len(response.data) if response.data else 0
                print(f"✅ Lectura exitosa de jobs_clean: {count} registros encontrados")
            except:
                print("⚠️ jobs_clean está vacía o no tiene datos")
            
            # Leer de jobs
            try:
                response = self.supabase.table('jobs').select('*').limit(5).execute()
                count = len(response.data) if response.data else 0
                print(f"✅ Lectura exitosa de jobs: {count} registros encontrados")
            except:
                print("⚠️ jobs está vacía o no tiene datos")
            
            return True
        except Exception as e:
            print(f"❌ Error en lectura: {e}")
            return False
    
    def test_eliminar_dato_prueba(self):
        """Elimina el dato de prueba insertado"""
        print("\n[5/5] 🗑️  Eliminando dato de prueba...")
        try:
            response = self.supabase.table('jobs_raw').delete().eq(
                'url_publicacion', 
                'https://test.com/prueba-12345'
            ).execute()
            print("✅ Dato de prueba eliminado")
            return True
        except Exception as e:
            print(f"⚠️ No se pudo eliminar dato de prueba: {e}")
            return False
    
    def ejecutar_todos_los_tests(self):
        """Ejecuta todos los tests"""
        resultados = []
        
        resultados.append(("Conexión", self.test_conexion()))
        resultados.append(("Tablas", self.test_tablas_existen()))
        resultados.append(("Inserción", self.test_insertar_dato()))
        resultados.append(("Lectura", self.test_leer_datos()))
        resultados.append(("Limpieza", self.test_eliminar_dato_prueba()))
        
        # Resumen
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE TESTS")
        print("=" * 70)
        
        exitosos = sum(1 for _, resultado in resultados if resultado)
        total = len(resultados)
        
        for nombre, resultado in resultados:
            estado = "✅" if resultado else "❌"
            print(f"{estado} {nombre}")
        
        print(f"\n{'=' * 70}")
        print(f"Resultado: {exitosos}/{total} tests exitosos")
        print("=" * 70)
        
        if exitosos == total:
            print("\n🎉 ¡Todos los tests pasaron! La conexión a Supabase está funcionando correctamente.")
        else:
            print("\n⚠️ Algunos tests fallaron. Revisa los errores arriba.")
        
        return exitosos == total


if __name__ == "__main__":
    tester = TestSupabase()
    tester.ejecutar_todos_los_tests()
