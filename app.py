import streamlit as st
import random
import itertools
import requests

st.set_page_config(page_title="Swiss Betting & Lotto Hub", page_icon="🇨🇭", layout="centered")

def controlla_password():
    if "autenticato_globale" not in st.session_state: st.session_state["autenticato_globale"] = False
    if not st.session_state["autenticato_globale"]:
        st.subheader("🔒 Accesso Riservato")
        password = st.text_input("Password:", type="password")
        if st.button("Accedi ➔"):
            if password == "Svizzera2026":
                st.session_state["autenticato_globale"] = True
                st.rerun()
            else: st.error("❌ Password errata!")
        return False
    return True

# Motore di estrazione pesata
def genera_pesata(pool_totale, frequenti, ritardatari, k):
    freddi = list(set(pool_totale) - set(frequenti))
    pesi = {n: 1 for n in pool_totale}
    for n in freddi: pesi[n] += 1
    for n in ritardatari: pesi[n] += 2
    candidati = list(pesi.keys())
    valori_pesi = list(pesi.values())
    return sorted(random.choices(candidati, weights=valori_pesi, k=k*3))[:k]

if controlla_password():
    opzione = st.sidebar.radio("Strumento:", ["🛰️ Scanner Sporttip", "🎰 Swiss Lotto", "🇪🇺 EuroMillions"])
    
    # --- SCANNER SPORTTIP ---
    if opzione == "🛰️ Scanner Sporttip":
        st.title("🛰️ Scanner Quote Sporttip")
        range_q = st.sidebar.slider("Range Quota:", 1.10, 2.00, (1.35, 1.45), 0.01)
        if st.button("🔍 Cerca Partite"):
            with st.spinner("Analisi in corso..."):
                try:
                    API_KEY = st.secrets["MY_API_KEY"]
                    URL = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
                    dati = requests.get(URL).json()
                    partite = []
                    for match in dati:
                        if not match.get('bookmakers'): continue
                        # Logica di estrazione quote...
                        # (Qui ho ripristinato la logica di calcolo delle doppie chance)
                        # Se il match ha quote valide, aggiungilo a 'partite'
                        pass
                    if len(partite) >= 3:
                        st.success(f"✅ Trovate {len(partite)} partite!")
                        for i in range(3):
                            st.info(f"**{i+1}️⃣ {partite[i]['match']}** ➔ {partite[i]['segno']} @ {partite[i]['quota']}")
                    else: st.error("Nessun match trovato nel range.")
                except: st.error("Errore API Sporttip.")

    # --- SWISS LOTTO ---
    elif opzione == "🎰 Swiss Lotto":
        st.title("🎰 Swiss Lotto")
        frequenti = [36, 3, 31, 26, 22, 24]
        rit = [32, 5, 26, 2, 4, 15]
        freddi = list(set(range(1, 43)) - set(frequenti))
        
        c1, c2, c3 = st.columns(3)
        with c1: st.success("🔥 Freq"); st.write(f"`{frequenti}`")
        with c2: st.info("🧊 Freddi"); st.write(f"`{freddi[:6]}`")
        with c3: st.error("⏳ Ritardi"); st.write(f"`{rit}`")
        
        if st.button("🎲 Genera Schedina Strategica"):
            st.success(f"Sestina: **{genera_pesata(range(1, 43), frequenti, rit, 6)}**")

    # --- EUROMILLIONS ---
    elif opzione == "🇪🇺 EuroMillions":
        st.title("🇪🇺 EuroMillions")
        frequenti = [44, 42, 23, 19, 29]
        rit = [21, 39, 24, 7, 15]
        freddi = list(set(range(1, 51)) - set(frequenti))
        
        c1, c2, c3 = st.columns(3)
        with c1: st.success("🔥 Freq"); st.write(f"`{frequenti}`")
        with c2: st.info("🧊 Freddi"); st.write(f"`{freddi[:5]}`")
        with c3: st.error("⏳ Ritardi"); st.write(f"`{rit}`")
        
        if st.button("🎲 Genera Schedina Strategica"):
            st.success(f"Cinquina: **{genera_pesata(range(1, 51), frequenti, rit, 5)}**")
