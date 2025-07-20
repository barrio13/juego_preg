import streamlit as st
import json
import random
import datetime
import os

# Paths
PREGUNTAS_PATH = "preguntas.json"
USADAS_PATH = "usadas.json"
VOTOS_PATH = "votos.json"

# Funciones utilitarias
def cargar_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def elegir_pregunta(preguntas, usadas):
    todas = [(autor, p) for autor, ps in preguntas.items() for p in ps]
    restantes = [p for p in todas if p[1] not in usadas]
    if not restantes:
        return None, None
    return random.choice(restantes)

def main():
    st.set_page_config(page_title="Pregunta del Día", page_icon="🎲", layout="centered")
    st.title("🎲 Pregunta del Día")

    preguntas = cargar_json(PREGUNTAS_PATH, {})
    usadas = cargar_json(USADAS_PATH, [])
    votos = cargar_json(VOTOS_PATH, {})

    hoy = datetime.date.today().isoformat()
    if hoy in votos:
        pregunta = votos[hoy]["pregunta"]
        resultados = votos[hoy]["resultados"]
        jugadores = votos[hoy].get("jugadores", [])
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
        jugadores = []

    st.markdown(f"### ❓ {pregunta}")
    nombre = st.text_input("👤 Escribe tu nombre para votar:")

    personas = list(preguntas.keys())

    if nombre:
        if nombre in jugadores:
            st.info("Ya has votado hoy. ¡Gracias!")
        else:
            seleccion = st.radio("¿A quién votas?", personas)
            if st.button("✅ Votar"):
                votos[hoy]["resultados"].setdefault(seleccion, 0)
                votos[hoy]["resultados"][seleccion] += 1
                votos[hoy]["jugadores"].append(nombre)
                guardar_json(VOTOS_PATH, votos)
                st.success(f"Has votado por {seleccion} ✅")

    if resultados:
        st.markdown("### 📊 Resultados:")
        for persona, count in resultados.items():
            st.write(f"- {persona}: {count} voto(s)")

    st.markdown("---")
    st.caption("Creado por tu grupo 🧠")

if __name__ == "__main__":
    main()
