import requests
import streamlit as st

# Configurazione grafica per Smartphone
st.set_page_config(page_title="Sporttip Scanner Svizzera", page_icon="🇨🇭", layout="centered")

def controlla_password():
    if "autenticato" not in st.session_state:
        st.session_state["autenticato"] = False
    if not st.session_state["autenticato"]:
        st.subheader("🔒 Accesso Riservato")
        password_inserita = st.text_input("Inserisci Password:", type="password")
        if st.button("Accedi"):
            if password_inserita == "Svizzera2026":
                st.session_state["autenticato"] = True
                st.rerun()
            else:
                st.error("Password errata")
        return False
    return True

if controlla_password():
    st.title("🛰️ Scanner Quote Sporttip")
    st.write("Ricerca automatica doppie chance per sistema 2/3.")

    # --- BARRA LATERALE PER FILTRI ---
    st.sidebar.header("Impostazioni Sporttip")
    range_quote = st.sidebar.slider(
        "Range Quota desiderata:",
        min_value=1.10,
        max_value=2.00,
        value=(1.35, 1.45),
        step=0.01
    )
    q_min, q_max = range_quote[0], range_quote[1]

    if st.button("🔍 Cerca Partite Ora"):
        with st.spinner("Analisi palinsesto in corso..."):
            try:
                API_KEY = st.secrets["MY_API_KEY"]
                # Interroghiamo i mercati per avere i dati base
                URL = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
                
                risposta = requests.get(URL)
                dati = risposta.json()
                
                partite_filtrate = []
                
                if isinstance(dati, list):
                    for partita in dati:
                        home = partita.get('home_team')
                        away = partita.get('away_team')
                        
                        if not partita.get('bookmakers'): continue
                        
                        # Prendiamo la media dei dati per simulare la quota fissa Sporttip
                        m_q1, m_qX, m_q2 = [], [], []
                        for b in partita['bookmakers']:
                            for m in b.get('markets', []):
                                if m['key'] == 'h2h':
                                    for o in m.get('outcomes', []):
                                        if o['name'] == home: m_q1.append(o['price'])
                                        elif o['name'] == 'Draw': m_qX.append(o['price'])
                                        elif o['name'] == away: m_q2.append(o['price'])
                        
                        if m_q1 and m_qX and m_q2:
                            avg1, avgX, avg2 = sum(m_q1)/len(m_q1), sum(m_qX)/len(m_qX), sum(m_q2)/len(m_q2)
                            
                            # FORMULA DEDICATA SPORTTIP:
                            # Trasformiamo la quota 1X2 nel valore Doppia Chance tipico di Sporttip (considerando l'aggio svizzero)
                            dc1X = round(((avg1 * avgX) / (avg1 + avgX)) * 0.92, 2)
                            dcX2 = round(((avg2 * avgX) / (avg2 + avgX)) * 0.92, 2)
                            
                            if q_min <= dc1X <= q_max:
                                partite_filtrate.append({"match": f"{home} - {away}", "segno": "1X", "quota": dc1X})
                            elif q_min <= dcX2 <= q_max:
                                partite_filtrate.append({"match": f"{home} - {away}", "segno": "X2", "quota": dcX2})

                    if len(partite_filtrate) >= 3:
                        st.success(f"Trovate {len(partite_filtrate)} partite per il tuo range!")
                        
                        # SISTEMA 2 SU 3 PRINCIPALE
                        st.divider()
                        st.subheader("📝 Schedina Consigliata (Sistema 2/3)")
                        
                        vincite_parziali = []
                        for i in range(3):
                            p = partite_filtrate[i]
                            st.info(f"**{p['match']}**\n\nEsito: `{p['segno']}` | Quota: `{p['quota']}`")
                        
                        # Calcolo Vincita Massima (Somma delle 3 combinazioni possibili)
                        q1, q2, q3 = partite_filtrate[0]['quota'], partite_filtrate[1]['quota'], partite_filtrate[2]['quota']
                        c1 = q1 * q2 * 5.0
                        c2 = q1 * q3 * 5.0
                        c3 = q2 * q3 * 5.0
                        vincita_totale = round(c1 + c2 + c3, 2)
                        
                        st.warning(f"💰 Spesa: 15.00 CHF | **Vincita Max: {vincita_totale} CHF**")
                        
                        if len(partite_filtrate) > 3:
                            with st.expander("Altre opzioni per oggi"):
                                for p in partite_filtrate[3:10]:
                                    st.write(f"⚽ {p['match']} ({p['segno']}) -> {p['quota']}")
                    else:
                        st.error("Nessun match trovato. Prova ad allargare il range nella barra laterale.")
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
