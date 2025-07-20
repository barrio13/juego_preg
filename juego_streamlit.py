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

# Colores fijos por persona
colores_por_persona = {
    "Barrio": "#b4c28a",
    "Javayah": "#2d9142",
    "Jay": "#17782b",
    "Marc": "#cee751",
    "Santolaya": "#577963",
    "Pedropras": "#4fc24c",
    "Gonsas": "#4a3567",
    "Cuerda": "#34c9d2",
    "Mario": "#cd9a71",
    "Alonshow": "#2b4e30",
    "Sabas": "#be4d3e",
    "Natjan": "#cead77",
    "Max": "#f576f2"
}

# Función principal de la app
def main():
    st.set_page_config(page_title="Pregunta del Día", page_icon="🏉", layout="centered")
    st.title("🏉 Pregunta del Día")

    # Cargar datos
    preguntas_raw = cargar_json(PREGUNTAS_PATH, {})
    jugadores = cargar_json(JUGADORES_PATH, [])
    usadas = cargar_json(USADAS_PATH, [])
    votos = cargar_json(VOTOS_PATH, {})

    preguntas = {k: v for k, v in preguntas_raw.items() if v}
    personas = jugadores

    hoy = datetime.date.today().isoformat()

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

    nombre = st.selectbox("👤 Selecciona tu nombre para votar:", ["-- Elige tu nombre --"] + jugadores)
    if nombre == "-- Elige tu nombre --":
        st.warning("⚠️ Por favor, selecciona tu nombre antes de votar.")
        return

    ya_voto = any((entry["nombre"] == nombre if isinstance(entry, dict) else entry == nombre) for entry in registro)

    if ya_voto:
        st.info("✅ Ya has votado hoy, no hagas trampas, va por ti Juanlu")
    else:
        st.markdown("### 👇 Haz clic en la persona que quieres votar:")
        cols = st.columns(3)
        for i, persona in enumerate(personas):
            color = colores_por_persona.get(persona, "#cccccc")
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <style>
                    div[data-testid=\"stButton\"][key=\"vote_{persona}\"] button {{
                        background-color: {color} !important;
                        color: white !important;
                        width: 100%;
                        border-radius: 8px;
                        margin: 6px 0;
                        border: none;
                        padding: 0.5rem 1rem;
                        font-weight: bold;
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(f"{persona}", key=f"vote_{persona}"):
                    votos[hoy]["resultados"].setdefault(persona, 0)
                    votos[hoy]["resultados"][persona] += 1
                    votos[hoy]["jugadores"].append({"nombre": nombre, "voto": persona})
                    guardar_json(VOTOS_PATH, votos)
                    st.success(f"🎉 Has votado por {persona}!")
                    st.rerun()


    if resultados:
        st.markdown("---")
        st.subheader("📊 Resultados:")
        total = sum(resultados.values())
        for persona, count in resultados.items():
            pct = (count / total) * 100 if total > 0 else 0
            color = colores_por_persona.get(persona, "#999999")
            st.markdown(f"**{persona}** — {count} voto(s) ({pct:.1f}%)")
            st.markdown(f"""
                <div style='background-color:#eee; border-radius:6px;'>
                    <div style='width:{pct}%; background-color:{color}; padding:6px; border-radius:6px;'></div>
                </div>
            """, unsafe_allow_html=True)

        from collections import defaultdict

        st.markdown("---")
        st.subheader("🧾 Quién votó a quién:")

        # Agrupar por persona votada
        votado_por = defaultdict(list)
        for entry in registro:
           if isinstance(entry, dict):
               votado_por[entry["voto"]].append(entry["nombre"])

        # Mostrar agrupado
        for votado, votantes in votado_por.items():
            lista_votantes = ", ".join(votantes)
            st.markdown(f"- **{votado}**: votado por {lista_votantes}")


    with st.expander("🛠️ Admin: Resetear el juego"):
        if st.button("🧼 Borrar votos y preguntas usadas"):
            guardar_json(VOTOS_PATH, {})
            guardar_json(USADAS_PATH, [])
            st.success("✅ Juego reiniciado correctamente.")

if __name__ == "__main__":
    main()
