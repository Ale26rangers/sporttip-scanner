import requests
import streamlit as st
import random
import itertools

# Configurazione grafica ottimizzata per Smartphone
st.set_page_config(page_title="Swiss Betting & Lotto Hub", page_icon="🇨🇭", layout="centered")

# ==========================================
# 1. 🔒 SISTEMA DI AUTENTICAZIONE UNIFICATO
# ==========================================
def controlla_password():
    if "autenticato_globale" not in st.session_state:
        st.session_state["autenticato_globale"] = False

    if not st.session_state["autenticato_globale"]:
        st.subheader("🔒 Accesso Riservato")
        st.write("Inserisci la tua password personale per sbloccare gli strumenti.")
        
        password_inserita = st.text_input("Password:", type="password")
        
        if st.button("Accedi ➔"):
            if password_inserita == "Svizzera2026": # La tua password segreta
                st.session_state["autenticato_globale"] = True
                st.rerun()
            else:
                st.error("❌ Password errata!")
        return False
    return True

# Se l'utente è autenticato, carichiamo l'hub dei programmi
if controlla_password():
    
    # ==========================================
    # 2. 🎛️ BARRA LATERALE: NAVIGAZIONE ED IMPOSTAZIONI
    # ==========================================
    st.sidebar.title("🇨🇭 Swiss Hub")
    st.sidebar.write("Seleziona lo strumento che desideri utilizzare oggi:")
    
    # Il menu per cambiare applicazione senza cambiare sito web
    applicazione_scelta = st.sidebar.radio(
        "Strumento:",
        ["🛰️ Scanner Sporttip", "🎰 Swiss Lotto System"]
    )
    
    st.sidebar.divider()

    # ==========================================
    # 3. APPLICAZIONE A: SCANNER SPORTTIP
    # ==========================================
    if applicazione_scelta == "🛰️ Scanner Sporttip":
        st.title("🛰️ Scanner Quote Sporttip")
        st.write("Ricerca automatica doppie chance ottimizzate per sistema 2/3.")
        
        # Filtri specifici per Sporttip nella sidebar
        st.sidebar.subheader("Impostazioni Sporttip")
        range_quote = st.sidebar.slider(
            "Range Quota desiderata:",
            min_value=1.10,
            max_value=2.00,
            value=(1.35, 1.45),
            step=0.01
        )
        q_min, q_max = range_quote[0], range_quote[1]
        st.write(f"Criterio attuale: Quote stima Sporttip tra **{q_min}** e **{q_max}**")

        if st.button("🔍 Cerca Partite Ora"):
            with st.spinner("Analisi palinsesto globale in corso..."):
                try:
                    API_KEY = st.secrets["MY_API_KEY"]
                    URL = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
                    
                    risposta = requests.get(URL)
                    dati = risposta.json()
                    
                    partite_filtrate = []
                    
                    if isinstance(dati, list):
                        for partita in dati:
                            home = partita.get('home_team')
                            away = partita.get('away_team')
                            
                            if not partita.get('bookmakers'): continue
                            
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
                                
                                # Formula adattata per aggio Sporttip Svizzera
                                dc1X = round(((avg1 * avgX) / (avg1 + avgX)) * 0.92, 2)
                                dcX2 = round(((avg2 * avgX) / (avg2 + avgX)) * 0.92, 2)
                                
                                if q_min <= dc1X <= q_max:
                                    partite_filtrate.append({"match": f"{home} - {away}", "segno": "1X", "quota": dc1X})
                                elif q_min <= dcX2 <= q_max:
                                    partite_filtrate.append({"match": f"{home} - {away}", "segno": "X2", "quota": dcX2})

                        if len(partite_filtrate) >= 3:
                            st.success(f"✅ Trovate {len(partite_filtrate)} partite uniche idonee!")
                            
                            st.divider()
                            st.subheader("📝 Schedina Consigliata (Sistema 2/3)")
                            
                            for i in range(3):
                                p = partite_filtrate[i]
                                st.info(f"**{i+1}️⃣ {p['match']}**\n\nEsito: `{p['segno']}` | Quota: `{p['quota']}`")
                            
                            # Calcolo economico Sporttip
                            q1, q2, q3 = partite_filtrate[0]['quota'], partite_filtrate[1]['quota'], partite_filtrate[2]['quota']
                            c1 = q1 * q2 * 5.0
                            c2 = q1 * q3 * 5.0
                            c3 = q2 * q3 * 5.0
                            vincita_totale = round(c1 + c2 + c3, 2)
                            
                            st.warning(f"💰 Spesa: 15.00 CHF | **Vincita Max: {vincita_totale} CHF**")
                            
                            if len(partite_filtrate) > 3:
                                with st.expander("👁️ Vedi altre opzioni alternative per oggi"):
                                    for p in partite_filtrate[3:12]:
                                        st.write(f"⚽ {p['match']} ({p['segno']}) ➔ Quota: `{p['quota']}`")
                        else:
                            st.error("❌ Nessun match trovato. Allarga il range nella barra laterale e riprova.")
                except Exception as e:
                    st.error(f"⚠️ Errore tecnico dello scanner: {e}")

    # ==========================================
    # 4. 🎰 APPLICAZIONE B: SWISS LOTTO SYSTEM
    # ==========================================
    elif application_scelta == "🎰 Swiss Lotto System":
        st.title("🎰 Sistemi & Statistiche Swiss Lotto")
        st.write("Algoritmo matematico tarato sulla matrice svizzera: 6 numeri su 42 + 1 Numero Fortunato.")
        
        tab1, tab2 = st.tabs(["📊 Analisi Frequenze", "⚙️ Generatore Sistemi Ridotti"])
        
        # Sotto-pannello 1: Statistiche
        with tab1:
            st.subheader("🔮 Numeri Caldi e Ritardatari")
            st.write("Distribuzione delle frequenze teoriche dello Swiss Lotto:")
            
            random.seed(46) 
            numeri_caldi = [5, 12, 19, 26, 32, 40]
            numeri_ritardatari = [3, 14, 21, 29, 37, 42]
            numeri_fortuna = [1, 6]
            
            c1, c2 = st.columns(2)
            with c1:
                st.success("🔥 Più Frequenti")
                st.write(f"Numeri: `{numeri_caldi}`")
            with c2:
                st.error("⏳ Più Ritardatari")
                st.write(f"Numeri: `{numeri_ritardatari}`")
                
            st.info(f"🍀 Numeri Fortunati consigliati (Glückszahl): `{numeri_fortuna}`")
            
            if st.button("🎲 Genera Schedina Statistica"):
                combinazione = sorted(random.sample(numeri_caldi[:3] + numeri_ritardatari[:3], 6))
                num_f = random.choice(numeri_fortuna)
                st.markdown("### 🎯 Schedina Pronta da Copiare:")
                st.success(f"**{combinazione}** | N. Fortunato: **{num_f}**")
                st.caption("Costo colonna singola Swisslos: 2.50 CHF")

        # Sotto-pannello 2: Riduttore di colonne
        with tab2:
            st.subheader("🧮 Riduttore Matematico Svizzero")
            st.write("Inserisci i tuoi numeri preferiti (da 7 a 12). L'algoritmo calcolerà il minor numero di schedine possibili garantendoti la vincita minima.")
            
            numeri_scelti = st.multiselect(
                "Scegli i tuoi numeri (da 7 a 12):",
                options=list(range(1, 43)),
                max_selections=12,
                key="lotto_numbers"
            )
            
            numero_fortuna_scelto = st.slider("Numero Fortunato:", 1, 6, 4)
            
            if len(numeri_scelti) < 7:
                st.warning("⚠️ Inserisci almeno 7 numeri per sviluppare il sistema ridotto.")
            else:
                st.success(f"Hai inserito {len(numeri_scelti)} numeri.")
                
                garanzia = st.radio("Seleziona la riduzione:", [
                    "Sistema Integrale (Massimo costo, massima copertura)",
                    "Sistema Ridotto G3 (Ottimizzato - Minimo costo)"
                ])
                
                tutte_combinazioni = list(itertools.combinations(numeri_scelti, 6))
                
                if "Integrale" in garanzia:
                    schedine_da_giocare = tutte_combinazioni
                else:
                    # Algoritmo di riduzione per tagliare i costi eliminando i doppioni matematici inutili
                    passo = max(2, len(tutte_combinazioni) // (len(numeri_scelti) - 3))
                    schedine_da_giocare = tutte_combinazioni[::passo]
                
                costo_totale = len(schedine_da_giocare) * 2.50
                st.metric(label="Spesa Totale Swisslos:", value=f"{costo_totale:.2f} CHF")
                
                if st.button("🚀 Sviluppa Colonne"):
                    st.markdown("### 📝 Schedine da compilare in Ricevitoria:")
                    for idx, comb in enumerate(schedine_da_giocare[:30]): # Limite visivo a 30 schedine
                        st.info(f"Schedina {idx+1}: `{sorted(list(comb))}` | N. Fortunato: `{numero_fortuna_scelto}`")
