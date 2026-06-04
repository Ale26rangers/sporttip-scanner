import requests
import streamlit as st

# Configurazione grafica della pagina per il telefono
st.set_page_config(page_title="Sporttip Scanner", page_icon="📊", layout="centered")

# ==========================================
# 1. 🔒 SISTEMA DI AUTENTICAZIONE (PASSWORD)
# ==========================================
def controlla_password():
    if "autenticato" not in st.session_state:
        st.session_state["autenticato"] = False

    if not st.session_state["autenticato"]:
        st.subheader("🔒 Accesso Riservato")
        st.write("Questo scanner è privato. Inserisci i dati d'accesso.")
        
        password_inserita = st.text_input("Password personale:", type="password")
        
        if st.button("Accedi ➔"):
            if password_inserita == "Svizzera2026": # Modifica la password qui se vuoi
                st.session_state["autenticato"] = True
                st.rerun()
            else:
                st.error("❌ Password errata!")
        return False
    return True


# ==========================================
# 2. 🛰️ IL PROGRAMMA DELLO SCANNER SPORTTIP
# ==========================================
if controlla_password():
    
    st.title("🛰️ Scanner Autonomo Sporttip")
    st.write("Benvenuto! Lo scanner è sbloccato e pronto all'uso.")
    st.write("Schiaccia il bottone sotto per scansionare il palinsesto in tempo reale.")

    if st.button("🔄 Avvia Scansione Palinsesto"):
        
        with st.spinner("Connessione ai server delle quote in corso..."):
            
            # Recupera l'API Key in modo sicuro dai Secrets
            try:
                API_KEY = st.secrets["MY_API_KEY"]
            except Exception:
                API_KEY = "4cf3c9ba8c89487fa42cbdf57814b7e8" 
                
            # Ora cercherà in TUTTI i campionati di calcio attivi nel mondo per darti più scelta
            URL = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&bookmakers=pinnacle"
            
            try:
                risposta = requests.get(URL)
                dati_server = risposta.json()
                
                # 🛡️ NUOVO CONTROLLO DI SICUREZZA:
                # Se il server risponde con un dizionario anziché una lista, significa che c'è un errore dell'API
                if isinstance(dati_server, dict) and "success" in dati_server and not dati_server["success"]:
                    st.error(f"⚠️ Errore del server delle quote: {dati_server.get('message', 'Chiave API non valida o limite superato')}")
                elif isinstance(dati_server, dict):
                    st.error(f"⚠️ Risposta inaspettata dal server: {dati_server}")
                else:
                    # Se i dati sono corretti (una lista di partite), procediamo con lo scanner
                    partite_valide = []
                    
                    for partita in dati_server:
                        home_team = partita.get('home_team', 'Casa')
                        away_team = partita.get('away_team', 'Fuori')
                        match_name = f"{home_team} - {away_team}"
                        
                        if not partita.get('bookmakers'): continue
                        bookmaker = partita['bookmakers'][0]
                        markets = bookmaker.get('markets', [])
                        
                        for market in markets:
                            if market['key'] == 'h2h':
                                q1, qX, q2 = None, None, None
                                for outcome in market.get('outcomes', []):
                                    if outcome['name'] == home_team: q1 = outcome['price']
                                    elif outcome['name'] == 'Draw': qX = outcome['price']
                                    elif outcome['name'] == away_team: q2 = outcome['price']
                                
                                if q1 and qX and q2:
                                    quota_1X = round((q1 * qX) / (q1 + qX), 2) + 0.35
                                    quota_X2 = round((q2 * qX) / (q2 + qX), 2) + 0.35
                                    
                                    if 1.35 <= quota_1X <= 1.45:
                                        partite_valide.append({"match": match_name, "segno": "1X", "quota": quota_1X})
                                    if 1.35 <= quota_X2 <= 1.45:
                                        partite_valide.append({"match": match_name, "segno": "X2", "quota": quota_X2})

                    # Mostriamo i risultati
                    if len(partite_valide) >= 3:
                        st.success(f"✅ Scansione completata! Trovate {len(partite_valide)} quote idonee.")
                        
                        st.markdown("### 🚀 **SISTEMA MATEMATICO CONSIGLIATO**")
                        for i in range(3):
                            p = partite_valide[i]
                            st.info(f"**{i+1}️⃣ {p['match']}**\n\nEsito: `{p['segno']}` | Quota stima Sporttip: `{p['quota']}`")
                        
                        q1, q2, q3 = partite_valide[0]['quota'], partite_valide[1]['quota'], partite_valide[2]['quota']
                        vincita_max = ((q1*q2) + (q1*q3) + (q2*q3)) * 5.0
                        
                        st.markdown("#### 📊 **Dettagli Schedina Sporttip:**")
                        st.write("• **Tipo:** Sistema 2 su 3")
                        st.write("• **Budget:** 15.00 CHF (5.00 CHF a colonna)")
                        st.metric(label="Vincita Massima Potenziale", value=f"{vincita_max:.2f} CHF", delta=f"+{vincita_max-15.00:.2f} CHF Netti")
                    else:
                        st.warning("❌ Nessun match soddisfa i requisiti di sicurezza (quote tra 1.35 e 1.45) in questo momento nelle partite principali.")
                        
            except Exception as e:
                st.error(f"⚠️ Errore tecnico durante l'analisi: {e}")
