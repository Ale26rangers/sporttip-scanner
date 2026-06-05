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
# 2. MOTORE STATISTICO PESATO (Priorità Ritardi/Freddi)
# ==========================================
def genera_pesata(pool_totale, freddi, ritardatari, k):
    pesi = {n: 1 for n in pool_totale}
    for n in freddi: pesi[n] += 1       # Bonus se Freddo
    for n in ritardatari: pesi[n] += 2  # Bonus Doppio se Ritardatario
    
    candidati = list(pesi.keys())
    valori_pesi = list(pesi.values())
    
    return sorted(random.choices(candidati, weights=valori_pesi, k=k*3))[:k]

# ==========================================
# 3. INTERFACCIA E STRUMENTI
# ==========================================
if controlla_password():
    st.sidebar.title("🇨🇭 Swiss Hub")
    opzione = st.sidebar.radio("Strumento:", ["🛰️ Scanner Sporttip", "🎰 Swiss Lotto", "🇪🇺 EuroMillions"])
    st.sidebar.divider()

    # ---------------------------------------------------------
    # 🛰️ SCANNER SPORTTIP
    # ---------------------------------------------------------
    if opzione == "🛰️ Scanner Sporttip":
        st.title("🛰️ Scanner Quote Sporttip")
        st.write("Ricerca automatica doppie chance ottimizzate per sistema 2/3.")
        
        range_q = st.sidebar.slider("Range Quota desiderata:", 1.10, 2.00, (1.35, 1.45), 0.01)
        
        if st.button("🔍 Cerca Partite Ora"):
            with st.spinner("Analisi palinsesto globale in corso..."):
                try:
                    API_KEY = st.secrets["MY_API_KEY"]
                    URL = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
                    dati = requests.get(URL).json()
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
                                avg1 = sum(m_q1)/len(m_q1)
                                avgX = sum(m_qX)/len(m_qX)
                                avg2 = sum(m_q2)/len(m_q2)
                                
                                dc1X = round(((avg1 * avgX) / (avg1 + avgX)) * 0.92, 2)
                                dcX2 = round(((avg2 * avgX) / (avg2 + avgX)) * 0.92, 2)
                                
                                if range_q[0] <= dc1X <= range_q[1]:
                                    partite_filtrate.append({"match": f"{home} - {away}", "segno": "1X", "quota": dc1X})
                                elif range_q[0] <= dcX2 <= range_q[1]:
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
                            st.error("❌ Nessun match trovato nel range attuale. Prova ad allargare le quote.")
                except Exception as e:
                    st.error(f"⚠️ Errore API Sporttip: {e}")

    # ---------------------------------------------------------
    # 🎰 SWISS LOTTO
    # ---------------------------------------------------------
    elif opzione == "🎰 Swiss Lotto":
        st.title("🎰 Swiss Lotto")
        
        data_aggiornamento = "5 Giugno 2026"
        st.caption(f"🔄 *Ultimo aggiornamento statistiche: **{data_aggiornamento}***")
        
        # 🟢 LISTE COMPLETE REGISTRATE (Frequenza decrescente)
        swiss_freq_full = [36, 3, 31, 26, 22, 24, 13, 18, 17, 1, 8, 6, 4, 9, 32, 21, 42, 5, 7, 14, 40, 38, 12, 19, 28, 35, 30, 10, 34, 23, 33, 39, 16, 20, 29, 25, 15, 11, 2, 27, 37, 41]
        swiss_fort_full = [1, 5, 4, 6, 2, 3]
        swiss_rit = [32, 5, 26, 2, 4, 15]
        swiss_fort_rit = [3, 4]
        
        # Derivazione automatica tramite slicing
        frequenti = swiss_freq_full[:6]  # I primi 6
        freddi = swiss_freq_full[-6:]    # Gli ultimi 6
        l_freq = swiss_fort_full[:2]     # I primi 2
        l_freddi = swiss_fort_full[-2:]  # Gli ultimi 2

        tab1, tab2 = st.tabs(["📊 Visione Statistica", "🧮 Sistemi"])
        
        with tab1:
            st.subheader("🔢 Numeri Principali (1-42)")
            c1, c2, c3 = st.columns(3)
            with c1: st.success("🔥 Freq"); st.write(f"`{frequenti}`")
            with c2: st.info("🧊 Freddi"); st.write(f"`{freddi}`")
            with c3: st.error("⏳ Ritardi"); st.write(f"`{swiss_rit}`")
            
            st.divider()
            
            st.subheader("🍀 Numeri Fortunati (1-6)")
            c4, c5, c6 = st.columns(3)
            with c4: st.success("🔥 Freq"); st.write(f"`{l_freq}`")
            with c5: st.info("🧊 Freddi"); st.write(f"`{l_freddi}`")
            with c6: st.error("⏳ Ritardi"); st.write(f"`{swiss_fort_rit}`")
            
            st.divider()
            
            if st.button("🎲 Genera Schedina Pesata", use_container_width=True):
                comb = genera_pesata(range(1, 43), freddi, swiss_rit, 6)
                f_num = genera_pesata(range(1, 7), l_freddi, swiss_fort_rit, 1)[0]
                st.success(f"Sestina Strategica: **{comb}** | N. Fortuna: **{f_num}**")

        with tab2:
            st.subheader("Sviluppo Sistemi")
            numeri_scelti = st.multiselect("Scegli i tuoi numeri (7-12):", options=list(range(1, 43)))
            n_f = st.slider("Numero Fortunato Fisso:", 1, 6, 3)
            if len(numeri_scelti) >= 7:
                tutte = list(itertools.combinations(numeri_scelti, 6))
                passo = max(2, len(tutte) // (len(numeri_scelti) - 3))
                for idx, c in enumerate(tutte[::passo][:20]):
                    st.info(f"Schedina {idx+1}: `{sorted(list(c))}` | Fortuna: `{n_f}`")

    # ---------------------------------------------------------
    # 🇪🇺 EUROMILLIONS
    # ---------------------------------------------------------
    elif opzione == "🇪🇺 EuroMillions":
        st.title("🇪🇺 EuroMillions")
        
        data_aggiornamento = "5 Giugno 2026"
        st.caption(f"🔄 *Ultimo aggiornamento statistiche: **{data_aggiornamento}***")
        
        # 🟢 LISTE COMPLETE REGISTRATE (Frequenza decrescente)
        euro_freq_full = [44, 42, 23, 19, 29, 17, 10, 21, 50, 37, 27, 35, 25, 26, 20, 45, 13, 14, 4, 5, 15, 24, 38, 7, 12, 34, 49, 30, 6, 11, 16, 39, 48, 3, 28, 8, 1, 9, 31, 36, 47, 2, 41, 43, 32, 40, 18, 46, 33, 22]
        euro_stelle_full = [2, 3, 8, 9, 6, 5, 7, 1, 4, 10, 11, 12]
        euro_rit = [21, 39, 24, 7, 15]
        euro_stelle_rit = [1, 10]
        
        # Derivazione automatica tramite slicing
        frequenti_eu = euro_freq_full[:5]  # I primi 5
        freddi_eu = euro_freq_full[-5:]    # Gli ultimi 5
        s_freq = euro_stelle_full[:2]      # Le prime 2
        s_fredde = euro_stelle_full[-2:]   # Le ultime 2

        tab1, tab2 = st.tabs(["📊 Visione Statistica", "🧮 Sistemi"])
        
        with tab1:
            st.subheader("🔢 Numeri Principali (1-50)")
            c1, c2, c3 = st.columns(3)
            with c1: st.success("🔥 Freq"); st.write(f"`{frequenti_eu}`")
            with c2: st.info("🧊 Freddi"); st.write(f"`{freddi_eu}`")
            with c3: st.error("⏳ Ritardi"); st.write(f"`{euro_rit}`")
            
            st.divider()
            
            st.subheader("⭐ Stelle (1-12)")
            c4, c5, c6 = st.columns(3)
            with c4: st.success("🔥 Freq"); st.write(f"`{s_freq}`")
            with c5: st.info("🧊 Fredde"); st.write(f"`{s_fredde}`")
            with c6: st.error("⏳ Ritardi"); st.write(f"`{euro_stelle_rit}`")
            
            st.divider()
            
            if st.button("🎲 Genera Schedina Pesata", use_container_width=True):
                comb = genera_pesata(range(1, 51), freddi_eu, euro_rit, 5)
                stelle = genera_pesata(range(1, 13), s_fredde, euro_stelle_rit, 2)
                st.success(f"Cinquina Strategica: **{comb}** | ⭐ Stelle: **{stelle}**")

        with tab2:
            st.subheader("Sviluppo Sistemi")
            nums = st.multiselect("Scegli i tuoi numeri (6-11):", options=list(range(1, 51)))
            stars = st.multiselect("Scegli 2 Stelle:", options=list(range(1, 13)), max_selections=2, default=[3,8])
            if len(nums) >= 6 and len(stars) == 2:
                tutte = list(itertools.combinations(nums, 5))
                passo = max(1, len(tutte) // 6)
                for idx, c in enumerate(tutte[::passo][:20]):
                    st.info(f"Giocata {idx+1}: `{sorted(list(c))}` | Stelle: `{sorted(stars)}`")
