import pandas as pd
import os
import time
from  salarios import extraer_salario_con_ia # <--- AQUÍ IMPORTAMOS A TU EXPERTO 🦁

# =============================================================================
# ⚙️ CONFIGURACIÓN
# =============================================================================
print("💰 INICIANDO FASE 2: ENRIQUECIMIENTO DE SALARIOS...")

def procesar_salarios():
    archivo_entrada = "DATA_LIMPIA_SIN_SUELDOS.xlsx"
    archivo_salida = "DATA_FINAL_CON_SUELDOS.xlsx"

    if not os.path.exists(archivo_entrada):
        print(f"❌ No existe '{archivo_entrada}'. \n⚠️ EJECUTA PRIMERO: python limpiador_fase1.py")
        return

    print(f"📂 Leyendo archivo: {archivo_entrada}")
    df = pd.read_excel(archivo_entrada).fillna("")
    
    # Métricas
    ya_tenian = 0
    encontrados_ia = 0
    ignorados = 0
    
    print(f"🔄 Procesando {len(df)} ofertas...")

    for index, row in df.iterrows():
        salario_actual = str(row['salario']).strip()
        raw_text = str(row['raw_text'])
        titulo = str(row['titulo'])

        # 1. ¿YA TIENE SUELDO? (Ahorramos plata)
        if salario_actual and salario_actual.lower() not in ["nan", "", "no especificado", "none", "0"]:
            ya_tenian += 1
            continue

        # 2. FILTRO ANTI-JOOBLE (Si está bloqueado, saltamos)
        es_basura_jooble = "registrese" in raw_text.lower() or "verificar que usted" in raw_text.lower() or len(raw_text) < 50
        if es_basura_jooble:
            ignorados += 1
            continue

        # 3. FILTRO DE PALABRAS CLAVE (Solo si huele a dinero)
        palabras_dinero = ["$", "usd", "sueldo", "salario", "remuneracion", "pago", "mensual", "competitivo", "ofrecemos", "básico"]
        if not any(p in raw_text.lower() for p in palabras_dinero):
            ignorados += 1
            continue

        # 🔥 4. LLAMADA AL MÓDULO EXPERTO
        print(f"   🤖 Consultando IA: {titulo[:30]}...", end="\r")
        
        # Aquí usamos tu función importada del otro archivo
        nuevo_salario = extraer_salario_con_ia(raw_text)
        
        if "No especificado" not in nuevo_salario:
            df.at[index, 'salario'] = nuevo_salario
            print(f"      💰 ¡CAMPEÓN! {titulo[:20]} -> {nuevo_salario}" + " " * 20)
            encontrados_ia += 1
        
        # Pausa técnica para evitar saturación (Rate Limit)
        time.sleep(1.0)

    # GUARDAR
    print("\n💾 Guardando Excel final...")
    df.to_excel(archivo_salida, index=False)
    
    print("\n✨ REPORTE FINAL FASE 2 ✨")
    print(f"✅ Ya tenían dato: {ya_tenian}")
    print(f"🤖 Recuperados por IA: {encontrados_ia}")
    print(f"⏭️ Ignorados (sin info/bloqueados): {ignorados}")
    print(f"📂 LISTO PARA SUPABASE: {archivo_salida}")

if __name__ == "__main__":
    procesar_salarios()