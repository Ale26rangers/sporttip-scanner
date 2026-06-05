import streamlit as st
import random
import itertools
import requests

# Configurazione grafica
st.set_page_config(page_title="Swiss Betting & Lotto Hub", page_icon="🇨🇭", layout="centered")

# ==========================================
# 1. AUTENTICAZIONE
# ==========================================
def controlla_password():
    if "autenticato_globale" not in st.session_state:
        st.session_state["autenticato_globale"] = False
    if not st.session_state["autenticato_globale"]:
        st.subheader("🔒 Accesso Riservato")
        password = st.text_input("Password:", type="password")
        if st.button("Accedi ➔"):
            if password == "Svizzera2026":
                st.session_state["autenticato_globale"] = True
                st.rerun()
            else:
                st.error("❌ Password errata!")
        return False
    return True

# ==========================================
# 2. MOTORE STATISTICO PESATO
# ==========================================
def genera_pesata(pool_totale, frequenti, ritardatari, k):
    # Derivazione automatica Freddi
    freddi = list(set(pool_totale) - set(frequenti))
    
    # Assegna Pesi: Base 1, +1 se Freddo, +2 se Ritardatario
    pesi = {n: 1 for n in pool_totale}
    for n in freddi: pesi[n] += 1
    for n in ritardatari: pesi[n] += 2
    
    candidati = list(pesi.keys())
    valori_pesi = list(pesi.values())
    
    return sorted(random.choices(candidati, weights=valori_pesi, k=k*3))[:k]

# ==========================================
# 3. INTERFACCIA PRINCIPALE
# ==========================================
if controlla_password():
    st.sidebar.title("🇨🇭 Swiss Hub")
    opzione = st.sidebar.radio("Strumento:", ["🛰️ Scanner Sporttip", "🎰 Swiss Lotto", "🇪🇺 EuroMillions"])
    st.sidebar.divider()

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
                    risultati = []
                    
                    if isinstance(dati, list):
                        for match in dati:
                            if not match.get('bookmakers'): continue
                            # Logica di calcolo (omessa per brevità, stessa di prima)
                            # ... (inserisci qui la logica di calcolo quote 1X/X2)
                            pass
                        st.success("✅ Analisi completata!")
                except:
                    st.error("⚠️ Errore API Sporttip.")

    # --- SWISS LOTTO ---
    elif opzione == "🎰 Swiss Lotto":
        st.title("🎰 Swiss Lotto (Sistema a Pesi)")
        # 🟢 AGGIORNA QUI
        frequenti = [36, 3, 31, 26, 22, 24]
        ritardatari = [32, 5, 26, 2, 4, 15]
        l_fortuna = [5, 2, 6, 1, 3, 4]
        
        if st.button("🎲 Genera Schedina Strategica"):
            comb = genera_pesata(range(1, 43), frequenti, ritardatari, 6)
            st.success(f"Sestina: **{comb}** | Fortuna: **{random.choice(l_fortuna)}**")
            st.caption("Algoritmo: Priorità ai Ritardatari.")

    # --- EUROMILLIONS ---
    elif opzione == "🇪🇺 EuroMillions":
        st.title("🇪🇺 EuroMillions (Sistema a Pesi)")
        # 🟢 AGGIORNA QUI
        frequenti = [44, 42, 23, 19, 29]
        ritardatari = [21, 39, 24, 7, 15]
        stelle = [3, 8, 12, 5, 1, 10]
        
        if st.button("🎲 Genera Schedina Strategica"):
            comb = genera_pesata(range(1, 51), frequenti, ritardatari, 5)
            st.success(f"Cinquina: **{comb}** | Stelle: **{sorted(random.sample(stelle, 2))}**")
            st.caption("Algoritmo: Priorità ai Ritardatari.")
