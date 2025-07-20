import streamlit as st
import json
import random
import datetime
import os

# Rutas de archivos
PREGUNTAS_PATH = "preguntas.json"
USADAS_PATH = "usadas.json"
VOTOS_PATH = "votos.json"
JUGADORES_PATH = "jugadores.json"

# Funciones para leer y guardar JSON
def cargar_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Elegir pregunta aleatoria no usada
def elegir_pregunta(preguntas, usadas):
    todas = [(autor, p) for autor, ps in preguntas.items() for p in ps]
    restantes = [p for p in todas if p[1] not in usadas]
    if not restantes:
        return None, None
    return random.choice(restantes)

# Función principal de la app
def main():
    st.set_page_config(page_title="Pregunta del Día", page_icon="🏉", layout="centered")
    st.title("🏉 Pregunta del Día")

    # Cargar datos
    preguntas_raw = cargar_json(PREGUNTAS_PATH, {})
    jugadores = cargar_json(JUGADORES_PATH, [])
    usadas = cargar_json(USADAS_PATH, [])
    votos = cargar_json(VOTOS_PATH, {})

    # Filtrar personas que sí tienen preguntas
    preguntas = {k: v for k, v in preguntas_raw.items() if v}
    personas = jugadores

    # Obtener fecha actual
    hoy = datetime.date.today().isoformat()

    # Recuperar o generar la pregunta del día
    if hoy in votos:
        pregunta = votos[hoy]["pregunta"]
        resultados = votos[hoy]["resultados"]
        registro = votos[hoy].get("jugadores", [])
    else:
        autor, pregunta = elegir_pregunta(preguntas, usadas)
        if not pregunta:
            st.warning("⚠️ No quedan preguntas nuevas.")
            return
        usadas.append(pregunta)
        votos[hoy] = {
            "pregunta": pregunta,
            "resultados": {},
            "jugadores": []
        }
        guardar_json(USADAS_PATH, usadas)
        guardar_json(VOTOS_PATH, votos)
        resultados = {}
        registro = []

    st.markdown(f"### ❓ {pregunta}")

    # Nombre del votante (sin preselección)
    nombre = st.selectbox("👤 Selecciona tu nombre para votar:", ["-- Elige tu nombre --"] + jugadores)

    if nombre == "-- Elige tu nombre --":
        st.warning("⚠️ Por favor, selecciona tu nombre antes de votar.")
        return

    # Verificar si ya ha votado
    ya_voto = any(
        (entry["nombre"] == nombre if isinstance(entry, dict) else entry == nombre)
        for entry in registro
    )

    if ya_voto:
        st.info("✅ Ya has votado hoy, no hagas trampas, va por ti Juanlu")
    else:
        st.markdown("### 👇 Haz clic en la persona que quieres votar:")
        for persona in personas:
            if st.button(f"🗳️ Votar por {persona}", key=persona):
                votos[hoy]["resultados"].setdefault(persona, 0)
                votos[hoy]["resultados"][persona] += 1
                votos[hoy]["jugadores"].append({"nombre": nombre, "voto": persona})
                guardar_json(VOTOS_PATH, votos)
                st.success(f"🎉 Has votado por {persona}!")
                st.stop()

    # Mostrar resultados
    if resultados:
        st.markdown("---")
        st.subheader("📊 Resultados:")
        total = sum(resultados.values())
        for persona, count in resultados.items():
            pct = (count / total) * 100 if total > 0 else 0
            st.markdown(f"**{persona}** — {count} voto(s) ({pct:.1f}%)")
            st.progress(pct / 100)

        st.markdown("---")
        st.subheader("🧾 Quién votó a quién:")
        for entry in registro:
            if isinstance(entry, dict):
                st.markdown(f"🧍 **{entry['nombre']}** votó por **{entry['voto']}**")
            elif isinstance(entry, str):
                st.markdown(f"⚠️ {entry} (voto antiguo sin destino)")

    # Admin: Reset
    with st.expander("🛠️ Admin: Resetear el juego"):
        if st.button("🧼 Borrar votos y preguntas usadas"):
            guardar_json(VOTOS_PATH, {})
            guardar_json(USADAS_PATH, [])
            st.success("✅ Juego reiniciado correctamente.")

if __name__ == "__main__":
    main()
