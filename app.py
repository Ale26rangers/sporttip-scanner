import requests
import streamlit as st

# Configurazione grafica
st.set_page_config(page_title="Sporttip Scanner Pro", page_icon="📊", layout="centered")

# ==========================================
# 1. 🔒 SISTEMA DI AUTENTICAZIONE
# ==========================================
def controlla_password():
    if "autenticato" not in st.session_state:
        st.session_state["autenticato"] = False

    if not st.session_state["autenticato"]:
        st.subheader("🔒 Accesso Riservato")
        password_inserita = st.text_input("Password personale:", type="password")
        if st.button("Accedi ➔"):
            if password_inserita == "Svizzera2026": # Mantieni o cambia la tua password
                st.session_state["autenticato"] = True
                st.rerun()
            else:
                st.error("❌ Password errata!")
        return False
    return True

if controlla_password():
    
    st.title("🛰️ Scanner Autonomo Sporttip")
    
    # ==========================================
    # 2. ⚙️ SETTAGGI DINAMICI (Barra Laterale)
    # ==========================================
    st.sidebar.header("Filtri di Ricerca")
    st.sidebar.write("Regola il range delle quote doppie chance:")
    
    # Cursore per impostare il range (Min e Max)
    range_quote = st.sidebar.slider(
        "Range Quota (es. 1.35 - 1.45)",
        min_value=1.10,
        max_value=2.00,
        value=(1.35, 1.45), # Valore di default
        step=0.01
    )
    
    quota_min = range_quote[0]
    quota_max = range_quote[1]

    st.write(f"Criterio attuale: Quote comprese tra **{quota_min}** e **{quota_max}**")

    # ==========================================
    # 3. 🚀 ESECUZIONE SCANNER
    # ==========================================
    if st.button("🔄 Avvia Scansione Palinsesto"):
        
        with st.spinner("Analisi del mercato globale..."):
            
            try:
                API_KEY = st.secrets["MY_API_KEY"]
            except Exception:
                API_KEY = "4cf3c9ba8c89487fa42cbdf57814b7e8" 
                
            # URL ottimizzato per cercare in tutti i campionati
            URL = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
            
            try:
                risposta = requests.get(URL)
                dati_server = risposta.json()
                
                if isinstance(dati_server, dict) and "success" in dati_server and not dati_server["success"]:
                    st.error(f"⚠️ Errore API: {dati_server.get('message')}")
                else:
                    partite_valide = []
                    
                    for partita in dati_server:
                        home_team = partita.get('home_team')
                        away_team = partita.get('away_team')
                        
                        if not partita.get('bookmakers'): continue
                        
                        # Usiamo la media dei bookmaker per una stima più stabile
                        for bookmaker in partita['bookmakers']:
                            markets = bookmaker.get('markets', [])
                            for market in markets:
                                if market['key'] == 'h2h':
                                    q1, qX, q2 = None, None, None
                                    for outcome in market.get('outcomes', []):
                                        if outcome['name'] == home_team: q1 = outcome['price']
                                        elif outcome['name'] == 'Draw': qX = outcome['price']
                                        elif outcome['name'] == away_team: q2 = outcome['price']
                                    
                                    if q1 and qX and q2:
                                        # Calcolo Doppia Chance stimata
                                        quota_1X = round((q1 * qX) / (q1 + qX), 2) + 0.35
                                        quota_X2 = round((q2 * qX) / (q2 + qX), 2) + 0.35
                                        
                                        # APPLICAZIONE FILTRI DINAMICI RICEVUTI DALLO SLIDER
                                        if quota_min <= quota_1X <= quota_max:
                                            partite_valide.append({"match": f"{home_team} - {away_team}", "segno": "1X", "quota": quota_1X})
                                        if quota_min <= quota_X2 <= quota_max:
                                            partite_valide.append({"match": f"{home_team} - {away_team}", "segno": "X2", "quota": quota_X2})

                    # Visualizzazione Risultati
                    if len(partite_valide) >= 3:
                        st.success(f"✅ Trovate {len(partite_valide)} quote idonee!")
                        # Mostriamo solo le prime 3 o tutte? Facciamo tutte quelle trovate
                        for p in partite_valide[:10]: # Limite a 10 per non affollare lo schermo
                            st.info(f"⚽ **{p['match']}**\n\nSegno: `{p['segno']}` | Quota: `{p['quota']}`")
                    else:
                        st.warning(f"❌ Nessun match tra {quota_min} e {quota_max}.")
                        st.write("👉 Prova ad allargare il range dei filtri nella barra laterale (sidebar) e clicca di nuovo sul bottone.")
                        
            except Exception as e:
                st.error(f"⚠️ Errore tecnico: {e}")
