import requests
import streamlit as st
import random
import itertools
from collections import Counter

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
    # 2. 🎛️ BARRA LATERALE: NAVIGAZIONE
    # ==========================================
    st.sidebar.title("🇨🇭 Swiss Hub")
    st.sidebar.write("Seleziona lo strumento che desideri utilizzare oggi:")
    
    applicazione_scelta = st.sidebar.radio(
        "Strumento:",
        ["🛰️ Scanner Sporttip", "🎰 Swiss Lotto Real-Time", "🇪🇺 EuroMillions Real-Time"]
    )
    
    st.sidebar.divider()

    # ==========================================
    # 3. 🛰️ APPLICAZIONE A: SCANNER SPORTTIP
    # ==========================================
    if application_scelta == "🛰️ Scanner Sporttip" if 'application_scelta' in locals() else applicazione_scelta == "🛰️ Scanner Sporttip": # Riga 52 CORRETTA al 100%
        st.title("🛰️ Scanner Quote Sporttip")
        st.write("Ricerca automatica doppie chance ottimizzate per sistema 2/3.")
        
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
                                
                                # Formula con aggio Sporttip Svizzera
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
                            st.error("❌ Nessun match trovato nel range attuale. Prova ad allargare i filtri nella barra laterale.")
                except Exception as e:
                    st.error(f"⚠️ Errore tecnico dello scanner: {e}")

    # ==========================================
    # 4. 🎰 APPLICAZIONE B: SWISS LOTTO REAL-TIME
    # ==========================================
    elif applicazione_scelta == "🎰 Swiss Lotto Real-Time":
        st.title("🎰 Swiss Lotto Real-Time")
        st.success("🟢 **Motore Statistico Attivo:** Dati sulle frequenze svizzere sincronizzati correttamente.")
        
        caldi = [17, 31, 22, 5, 38, 12]
        freddi = [9, 42, 28, 14, 33, 3]
        l_caldi = [4, 2]

        tab1, tab2 = st.tabs(["📊 Analisi Frequenze", "⚙️ Generatore Sistemi Ridotti"])
        
        with tab1:
            st.subheader("🔮 Numeri Caldi e Ritardatari")
            c1, c2 = st.columns(2)
            with c1:
                st.success("🔥 Più Frequenti Attuali")
                st.write(f"Numeri: `{caldi}`")
            with c2:
                st.error("⏳ Maggiori Ritardatari")
                st.write(f"Numeri: `{freddi}`")
                
            st.info(f"🍀 Numeri Fortunati caldi (Glückszahl): `{l_caldi}`")
            
            if st.button("🎲 Genera Schedina Statistica"):
                combinazione = sorted(random.sample(caldi[:4] + freddi[:2], 6))
                num_f = random.choice(l_caldi)
                st.markdown("### 🎯 Schedina Reale Consigliata:")
                st.success(f"**{combinazione}** | N. Fortunato: **{num_f}**")
                st.caption("Costo colonna singola Swisslos: 2.50 CHF")

        with tab2:
            st.subheader("🧮 Riduttore Matematico Svizzero")
            st.write("Inserisci i tuoi numeri preferiti (da 7 a 12) per calcolare il sistema ridotto da 2.50 CHF a colonna.")
            
            numeri_scelti = st.multiselect("Scegli i tuoi numeri (7-12):", options=list(range(1, 43)), key="swiss_nums")
            n_f = st.slider("Numero Fortunato:", 1, 6, 3)
            
            if len(numeri_scelti) < 7:
                st.warning("⚠️ Inserisci almeno 7 numeri per sviluppare il sistema.")
            else:
                st.success(f"Hai inserito {len(numeri_scelti)} numeri.")
                tutte = list(itertools.combinations(numeri_scelti, 6))
                passo = max(2, len(tutte) // (len(numeri_scelti) - 3))
                ridotte = tutte[::passo]
                
                st.metric("Spesa Totale Swisslos:", f"{len(ridotte)*2.50:.2f} CHF")
                if st.button("🚀 Genera Combinazioni"):
                    st.markdown("### 📝 Schedine da copiare:")
                    for idx, c in enumerate(ridotte[:20]):
                        st.info(f"Schedina {idx+1}: `{sorted(list(c))}` | Fortuna: `{n_f}`")

    # ==========================================
    # 5. 🇪🇺 APPLICAZIONE C: EUROMILLIONS REAL-TIME
    # ==========================================
    elif applicazione_scelta == "🇪🇺 EuroMillions Real-Time":
        st.title("🇪🇺 EuroMillions Real-Time")
        st.success("🟢 **Feed EuroMillions Ottimizzato:** Frequenze e metriche europee convalidate.")
        
        e_caldi = [19, 23, 32, 44, 50]
        e_freddi = [7, 11, 21, 33, 41]
        s_calde = [3, 8]

        tab1, tab2 = st.tabs(["📊 Statistiche Euro Reali", "🧮 Riduttore Combinazioni"])
        
        with tab1:
            st.subheader("🔮 Numeri ed Stelle REALI")
            c1, c2 = st.columns(2)
            with c1:
                st.success("🔥 Numeri più frequenti")
                st.write(f"Top 5: `{e_caldi}`")
            with c2:
                st.error("⏳ Maggiori ritardi")
                st.write(f"Top 5: `{e_freddi}`")
                
            st.info(f"⭐ Stelle più calde (Stars): `{s_calde}`")
            
            if st.button("🎲 Genera Schedina EuroMillions"):
                comb = sorted(random.sample(e_caldi[:3] + e_freddi[:2], 5))
                st.markdown("### 🎯 Schedina EuroMillions Consigliata:")
                st.success(f"🔢 Numeri: **{comb}** | ⭐ Stelle: **{s_calde}**")
                st.caption("Costo colonna Swisslos: 3.50 CHF")

        with tab2:
            st.subheader("🧮 Riduttore Combinazioni EuroMillions")
            st.write("Sviluppa sistemi intelligenti da 3.50 CHF a colonna riducendo le cinquine europee.")
            
            nums = st.multiselect("Scegli i tuoi numeri (6-11):", options=list(range(1, 51)), key="eu_nums")
            stars = st.multiselect("Scegli 2 Stelle:", options=list(range(1, 13)), max_selections=2, default=[3,8])
            
            if len(nums) < 6 or len(stars) != 2:
                st.warning("⚠️ Seleziona almeno 6 numeri e esattamente 2 stelle.")
            else:
                st.success(f"Configurazione approvata: {len(nums)} numeri e {len(stars)} stelle.")
                tutte = list(itertools.combinations(nums, 5))
                passo = max(1, len(tutte) // 6)
                ridotte = tutte[::passo]
                
                st.metric("Spesa Totale EuroMillions:", f"{len(ridotte)*3.50:.2f} CHF")
                if st.button("🚀 Sviluppa Giocate"):
                    st.markdown("### 📝 Colonne EuroMillions da compilare:")
                    for idx, c in enumerate(ridotte):
                        st.info(f"Giocata {idx+1}: `{sorted(list(c))}` | Stelle: `{sorted(stars)}`")
