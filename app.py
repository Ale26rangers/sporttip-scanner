import requests
import streamlit as st
import random
import itertools

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
        ["🛰️ Scanner Sporttip", "🎰 Swiss Lotto", "🇪🇺 EuroMillions"]
    )
    st.sidebar.divider()

    # ==========================================
    # 3. 🛰️ SCANNER SPORTTIP
    # ==========================================
    if applicazione_scelta == "🛰️ Scanner Sporttip":
        st.title("🛰️ Scanner Quote Sporttip")
        st.write("Ricerca automatica doppie chance ottimizzate per sistema 2/3.")
        
        range_quote = st.sidebar.slider("Range Quota desiderata:", 1.10, 2.00, (1.35, 1.45), 0.01)
        
        if st.button("🔍 Cerca Partite Ora"):
            with st.spinner("Analisi palinsesto in corso..."):
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
                            st.success(f"✅ Trovate {len(partite_filtrate)} partite uniche!")
                            st.divider()
                            st.subheader("📝 Schedina Consigliata (Sistema 2/3)")
                            for i in range(3):
                                p = partite_filtrate[i]
                                st.info(f"**{i+1}️⃣ {p['match']}**\n\nEsito: `{p['segno']}` | Quota: `{p['quota']}`")
                            
                            q1, q2, q3 = partite_filtrate[0]['quota'], partite_filtrate[1]['quota'], partite_filtrate[2]['quota']
                            vincita_totale = round((q1*q2 + q1*q3 + q2*q3) * 5.0, 2)
                            st.warning(f"💰 Spesa: 15.00 CHF | **Vincita Max: {vincita_totale} CHF**")
                        else:
                            st.error("❌ Nessun match trovato nel range attuale.")
                except Exception:
                    st.error("⚠️ Errore API Sporttip.")

    # ==========================================
    # 4. 🎰 SWISS LOTTO
    # ==========================================
    elif applicazione_scelta == "🎰 Swiss Lotto":
        st.title("🎰 Swiss Lotto")
        st.success("🟢 **Sistema Offline:** Algoritmo miscelato per Frequenza e Ritardo.")
        
        # 🟢 MODIFICA QUI I NUMERI DEL LOTTO SVIZZERO QUANDO VUOI AGGIORNARLI
        data_aggiornamento = "5 Giugno 2026"
        caldi = [36, 3, 31, 26, 22, 24]       # Più estratti nella storia
        freddi = [41, 37, 27, 2, 11, 15]       # Meno estratti nella storia (Frequenza minima)
        ritardatari = [32, 5, 26, 2, 4, 15]   # Assenti da più estrazioni attualmente
        
        l_caldi = [1, 5]                       # Numeri Fortunati frequenti
        l_ritardo = [3, 6]                     # Numeri Fortunati ritardatari
        # -------------------------------------------------------------------

        st.caption(f"🔄 *Ultimo aggiornamento statistiche: **{data_aggiornamento}***")

        tab1, tab2 = st.tabs(["📊 Analisi Storica", "⚙️ Riduttore Matematico"])
        
        with tab1:
            st.write("Statistiche suddivise in categorie:")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success("🔥 Frequenti")
                st.write(f"`{caldi}`")
            with c2:
                st.info("🧊 Freddi")
                st.write(f"`{freddi}`")
            with c3:
                st.error("⏳ Ritardi")
                st.write(f"`{ritardatari}`")
            
            if st.button("🎲 Genera Schedina Strategica"):
                # LOGICA DI GENERAZIONE: 3 Caldi + 1 Freddo + 2 Ritardatari = 6 Numeri
                scelta_caldi = random.sample(caldi, 3)
                scelta_freddi = random.sample(freddi, 1)
                scelta_ritardo = random.sample(ritardatari, 2)
                
                combinazione = sorted(scelta_caldi + scelta_freddi + scelta_ritardo)
                num_f = random.choice(l_caldi + l_ritardo)
                
                st.success(f"Sestina Bilanciata: **{combinazione}** | N. Fortuna: **{num_f}**")
                st.caption("🔍 La schedina contiene: 3 freq. assolute + 1 freddo storico + 2 attuali ritardatari.")

        with tab2:
            st.subheader("🧮 Sviluppo Sistemi Swisslos")
            numeri_scelti = st.multiselect("Scegli i tuoi numeri preferiti (7-12):", options=list(range(1, 43)), key="swiss_nums")
            n_f = st.slider("Numero Fortunato da usare fisse:", 1, 6, 3)
            
            if len(numeri_scelti) >= 7:
                tutte = list(itertools.combinations(numeri_scelti, 6))
                passo = max(2, len(tutte) // (len(numeri_scelti) - 3))
                ridotte = tutte[::passo]
                st.metric("Spesa Totale (2.50 CHF/colonna):", f"{len(ridotte)*2.50:.2f} CHF")
                
                if st.button("🚀 Sviluppa Colonne"):
                    for idx, c in enumerate(ridotte[:20]):
                        st.info(f"Schedina {idx+1}: `{sorted(list(c))}` | Fortuna: `{n_f}`")

    # ==========================================
    # 5. 🇪🇺 EUROMILLIONS
    # ==========================================
    elif applicazione_scelta == "🇪🇺 EuroMillions":
        st.title("🇪🇺 EuroMillions")
        st.success("🟢 **Sistema Offline:** Algoritmo miscelato per Frequenza e Ritardo.")
        
        # 🟢 MODIFICA QUI I NUMERI DELL'EUROMILLIONS QUANDO VUOI AGGIORNARLI
        data_aggiornamento_euro = "5 Giugno 2026"
        e_caldi = [44, 42, 23, 19, 29]          # Più estratti nella storia
        e_freddi = [22, 33, 46, 18, 40]         # Meno estratti nella storia (Frequenza minima)
        e_ritardatari = [21, 39, 24, 7, 15]     # Assenti da più estrazioni attualmente
        
        s_calde = [2, 3]                        # Stelle Frequenti
        s_ritardo = [10, 4]                     # Stelle Ritardatarie
        # -------------------------------------------------------------------

        st.caption(f"🔄 *Ultimo aggiornamento statistiche: **{data_aggiornamento_euro}***")

        tab1, tab2 = st.tabs(["📊 Analisi Storica", "⚙️ Riduttore Matematico"])
        
        with tab1:
            st.write("Statistiche suddivise in categorie:")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success("🔥 Frequenti")
                st.write(f"`{e_caldi}`")
            with c2:
                st.info("🧊 Freddi")
                st.write(f"`{e_freddi}`")
            with c3:
                st.error("⏳ Ritardi")
                st.write(f"`{e_ritardatari}`")
            
            if st.button("🎲 Genera Schedina Strategica"):
                # LOGICA DI GENERAZIONE EURO: 2 Caldi + 1 Freddo + 2 Ritardatari = 5 Numeri
                scelta_caldi = random.sample(e_caldi, 2)
                scelta_freddi = random.sample(e_freddi, 1)
                scelta_ritardo = random.sample(e_ritardatari, 2)
                
                comb = sorted(scelta_caldi + scelta_freddi + scelta_ritardo)
                
                # Miscela per le stelle: 1 Frequente + 1 Ritardataria
                stelle_miste = sorted([random.choice(s_calde), random.choice(s_ritardo)])
                
                st.success(f"Cinquina Bilanciata: **{comb}** | ⭐ Stelle: **{stelle_miste}**")
                st.caption("🔍 Mix: 2 freq. assolute + 1 freddo storico + 2 attuali ritardatari.")

        with tab2:
            st.subheader("🧮 Sviluppo Sistemi EuroMillions")
            nums = st.multiselect("Scegli i tuoi numeri (6-11):", options=list(range(1, 51)), key="eu_nums")
            stars = st.multiselect("Scegli 2 Stelle da usare fisse:", options=list(range(1, 13)), max_selections=2, default=[3,2])
            
            if len(nums) >= 6 and len(stars) == 2:
                tutte = list(itertools.combinations(nums, 5))
                passo = max(1, len(tutte) // 6)
                ridotte = tutte[::passo]
                st.metric("Spesa Totale (3.50 CHF/colonna):", f"{len(ridotte)*3.50:.2f} CHF")
                
                if st.button("🚀 Sviluppa Giocate"):
                    for idx, c in enumerate(ridotte[:20]):
                        st.info(f"Giocata {idx+1}: `{sorted(list(c))}` | Stelle: `{sorted(stars)}`")
