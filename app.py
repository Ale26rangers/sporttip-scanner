import requests
import streamlit as st
import random
import itertools
import pandas as pd

# Configurazione grafica ottimizzata per Smartphone
st.set_page_config(page_title="Swiss Betting & Lotto Hub", page_icon="🇨🇭", layout="centered")

# ==========================================
# 1. 🔒 SISTEMA DI AUTENTICAZIONE
# ==========================================
def controlla_password():
    if "autenticato_globale" not in st.session_state:
        st.session_state["autenticato_globale"] = False

    if not st.session_state["autenticato_globale"]:
        st.subheader("🔒 Accesso Riservato")
        password_inserita = st.text_input("Password:", type="password")
        if st.button("Accedi ➔"):
            if password_inserita == "Svizzera2026":
                st.session_state["autenticato_globale"] = True
                st.rerun()
            else:
                st.error("❌ Password errata!")
        return False
    return True

if controlla_password():
    
    st.sidebar.title("🇨🇭 Swiss Hub")
    applicazione_scelta = st.sidebar.radio(
        "Strumento:",
        ["🛰️ Scanner Sporttip", "🎰 Swiss Lotto Dinamico", "🇪🇺 EuroMillions Dinamico"]
    )
    st.sidebar.divider()

    # ==========================================
    # 3. 🛰️ SCANNER SPORTTIP
    # ==========================================
    if applicazione_scelta == "🛰️ Scanner Sporttip":
        st.title("🛰️ Scanner Quote Sporttip")
        range_quote = st.sidebar.slider("Range Quota desiderata:", 1.10, 2.00, (1.35, 1.45), 0.01)
        
        if st.button("🔍 Cerca Partite Ora"):
            with st.spinner("Analisi palinsesto globale in corso..."):
                try:
                    API_KEY = st.secrets["MY_API_KEY"]
                    URL = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
                    dati = requests.get(URL).json()
                    partite_filtrate = []
                    
                    if isinstance(dati, list):
                        for partita in dati:
                            home, away = partita.get('home_team'), partita.get('away_team')
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
                                dc1X = round(((avg1 * avgX) / (avg1 + avgX)) * 0.92, 2)
                                dcX2 = round(((avg2 * avgX) / (avg2 + avgX)) * 0.92, 2)
                                if range_quote[0] <= dc1X <= range_quote[1]:
                                    partite_filtrate.append({"match": f"{home} - {away}", "segno": "1X", "quota": dc1X})
                                elif range_quote[0] <= dcX2 <= range_quote[1]:
                                    partite_filtrate.append({"match": f"{home} - {away}", "segno": "X2", "quota": dcX2})

                        if len(partite_filtrate) >= 3:
                            st.success(f"✅ Trovate {len(partite_filtrate)} partite!")
                            for i in range(3):
                                p = partite_filtrate[i]
                                st.info(f"**{i+1}️⃣ {p['match']}**\n\nEsito: `{p['segno']}` | Quota: `{p['quota']}`")
                            
                            q1, q2, q3 = partite_filtrate[0]['quota'], partite_filtrate[1]['quota'], partite_filtrate[2]['quota']
                            vincita_totale = round((q1*q2 + q1*q3 + q2*q3) * 5.0, 2)
                            st.warning(f"💰 Spesa: 15.00 CHF | **Vincita Max: {vincita_totale} CHF**")
                        else:
                            st.error("❌ Nessun match trovato nel range.")
                except Exception as e:
                    st.error("⚠️ Errore API Sporttip.")

    # ==========================================
    # 4. 🎰 SWISS LOTTO (Scraper Dinamico)
    # ==========================================
    elif applicazione_scelta == "🎰 Swiss Lotto Dinamico":
        st.title("🎰 Swiss Lotto Dinamico")
        
        @st.cache_data(ttl=43200) # Cerca i dati nuovi ogni 12 ore
        def scraper_swiss_lotto():
            try:
                # Il ragnetto va a leggere le tabelle HTML di un portale statistico neutrale
                url = "https://www.lotto.net/swiss-lotto/statistics"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                html = requests.get(url, headers=headers, timeout=8).text
                tabelle = pd.read_html(html)
                
                # Cerca di estrarre la prima colonna (i numeri) dalle tabelle statistiche web
                caldi_web = tabelle[0].iloc[:, 0].head(6).tolist()
                freddi_web = tabelle[1].iloc[:, 0].head(6).tolist()
                return [int(x) for x in caldi_web], [int(x) for x in freddi_web], [4, 2], True
            except:
                # Se i firewall bloccano la richiesta, usa i calcoli assoluti
                return [18, 32, 22, 38, 26, 11], [42, 9, 28, 14, 30, 36], [5, 2], False

        with st.spinner("Scansione web dei database in corso..."):
            caldi, freddi, l_caldi, ok_lotto = scraper_swiss_lotto()

        if ok_lotto:
            st.success("🟢 **Web Scraping Riuscito:** Frequenze scaricate in tempo reale da internet.")
        else:
            st.warning("⚠️ **Firewall Incontrato:** Lettura web bloccata. Sono mostrati i dati storici matematici di base.")

        tab1, tab2 = st.tabs(["📊 Analisi Storica", "⚙️ Generatore Sistemi Ridotti"])
        
        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                st.success("🔥 Numeri Caldi Aggiornati")
                st.write(f"`{caldi}`")
            with c2:
                st.error("⏳ Maggiori Ritardi")
                st.write(f"`{freddi}`")
            
            if st.button("🎲 Genera Schedina Statistica"):
                combinazione = sorted(random.sample(caldi[:4] + freddi[:2], 6))
                st.success(f"**{combinazione}** | N. Fortunato: **{random.choice(l_caldi)}**")

        with tab2:
            st.subheader("🧮 Riduttore Matematico")
            numeri_scelti = st.multiselect("Scegli i numeri (7-12):", options=list(range(1, 43)), key="swiss_nums")
            if len(numeri_scelti) >= 7:
                tutte = list(itertools.combinations(numeri_scelti, 6))
                passo = max(2, len(tutte) // (len(numeri_scelti) - 3))
                for idx, c in enumerate(tutte[::passo][:20]):
                    st.info(f"Schedina {idx+1}: `{sorted(list(c))}`")

    # ==========================================
    # 5. 🇪🇺 EUROMILLIONS (Scraper Dinamico)
    # ==========================================
    elif applicazione_scelta == "🇪🇺 EuroMillions Dinamico":
        st.title("🇪🇺 EuroMillions Dinamico")
        
        @st.cache_data(ttl=43200)
        def scraper_euro_millions():
            try:
                # Il ragnetto esplora il sito statistico di EuroMillions
                url = "https://www.euro-millions.com/statistics"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                html = requests.get(url, headers=headers, timeout=8).text
                tabelle = pd.read_html(html)
                
                caldi_web = []
                freddi_web = []
                # Analizza le decine di tabelle della pagina per trovare quelle dei numeri
                for df in tabelle:
                    if 'Number' in df.columns or 'Numero' in df.columns:
                        numeri = df.iloc[:, 0].head(5).tolist()
                        if not caldi_web: caldi_web = numeri
                        elif not freddi_web: 
                            freddi_web = numeri
                            break
                            
                if caldi_web and freddi_web:
                    return [int(x) for x in caldi_web], [int(x) for x in freddi_web], [3, 8], True
                raise Exception("Tabelle strutturate non trovate")
            except:
                return [23, 44, 50, 19, 37], [33, 41, 13, 48, 22], [3, 2], False

        with st.spinner("Scansione dei portali europei in corso..."):
            e_caldi, e_freddi, s_calde, ok_euro = scraper_euro_millions()

        if ok_euro:
            st.success("🟢 **Web Scraping Riuscito:** Dati europei estratti in tempo reale.")
        else:
            st.warning("⚠️ **Firewall Incontrato:** Scansione respinta dai server web. Applicati dati storici di sistema.")

        tab1, tab2 = st.tabs(["📊 Analisi Storica", "⚙️ Generatore Sistemi Ridotti"])
        
        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                st.success("🔥 Più Estratti")
                st.write(f"`{e_caldi}`")
            with c2:
                st.error("⏳ Grandi Ritardi")
                st.write(f"`{e_freddi}`")
            
            if st.button("🎲 Genera Schedina EuroMillions"):
                comb = sorted(random.sample(e_caldi[:3] + e_freddi[:2], 5))
                st.success(f"🔢 Numeri: **{comb}** | ⭐ Stelle: **{s_calde}**")

        with tab2:
            st.subheader("🧮 Riduttore EuroMillions")
            nums = st.multiselect("Scegli i numeri (6-11):", options=list(range(1, 51)), key="eu_nums")
            stars = st.multiselect("Scegli 2 Stelle:", options=list(range(1, 13)), max_selections=2, default=[3,2])
            if len(nums) >= 6 and len(stars) == 2:
                tutte = list(itertools.combinations(nums, 5))
                passo = max(1, len(tutte) // 6)
                for idx, c in enumerate(tutte[::passo][:20]):
                    st.info(f"Giocata {idx+1}: `{sorted(list(c))}` | Stelle: `{sorted(stars)}`")
