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
# 2. MOTORE STATISTICO PESATO (Nessun doppione)
# ==========================================
def genera_pesata(pool_totale, freddi, ritardatari, k):
    pesi = {n: 1 for n in pool_totale}
    for n in freddi: pesi[n] += 1       
    for n in ritardatari: pesi[n] += 2  
    
    candidati = list(pesi.keys())
    valori_pesi = list(pesi.values())
    
    estratti = set()
    while len(estratti) < k:
        scelta = random.choices(candidati, weights=valori_pesi, k=1)[0]
        estratti.add(scelta)
        
    return sorted(list(estratti))

# ==========================================
# 3. INTERFACCIA E STRUMENTI
# ==========================================
if controlla_password():
    st.sidebar.title("🇨🇭 Swiss Hub")
    
    # 🔴 AGGIUNTA LA QUARTA OPZIONE QUI:
    opzione = st.sidebar.radio("Strumento:", [
        "🛰️ Scanner Sporttip", 
        "🔮 Predictor Professionale", 
        "🎰 Swiss Lotto", 
        "🇪🇺 EuroMillions"
    ])
    st.sidebar.divider()

    # ---------------------------------------------------------
    # 🛰️ SCANNER SPORTTIP (Lascialo esattamente come prima)
    # ---------------------------------------------------------
    if opzione == "🛰️ Scanner Sporttip":
        # ... (Tutto il codice dello scanner vecchio rimane qui) ...
        st.title("🛰️ Scanner Quote Sporttip")
        st.write("Scanner attivo. Seleziona il Predictor per l'analisi avanzata.")

    # ---------------------------------------------------------
    # 🔮 PREDICTOR PROFESSIONALE (IL NUOVO MOTORE)
    # ---------------------------------------------------------
    elif opzione == "🔮 Predictor Professionale":
        st.title("🔮 Predictor Matematico")
        st.write("Analisi avanzata delle probabilità e calcolo delle **Quote di Valore (Fair Odds)**.")
        
        campionato = st.selectbox("Scegli il Campionato da analizzare:", 
                                  ["🇨🇭 Super League Svizzera", "🇳🇱 Eredivisie (Olanda)", "🇩🇪 Bundesliga"])
        
        # ID ufficiali di API-Football per questi campionati
        league_ids = {"🇨🇭 Super League Svizzera": 202, "🇳🇱 Eredivisie (Olanda)": 88, "🇩🇪 Bundesliga": 78}
        league_id = league_ids[campionato]
        
        if st.button("🧮 Avvia Motore Predittivo", type="primary"):
            with st.spinner("Scaricamento dati e calcolo probabilità in corso..."):
                try:
                    API_FOOTBALL_KEY = st.secrets["API_FOOTBALL_KEY"]
                    headers = {
                        "X-RapidAPI-Key": API_FOOTBALL_KEY,
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
                    }
                    
                    # 1. Scarica le prossime 5 partite di questo campionato
                    url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&next=5"
                    response = requests.get(url_fixtures, headers=headers).json()
                    
                    if "response" in response and len(response["response"]) > 0:
                        st.success(f"✅ Trovati {len(response['response'])} match imminenti. Elaborazione in corso...")
                        
                        for match in response["response"]:
                            fix_id = match["fixture"]["id"]
                            home = match["teams"]["home"]["name"]
                            away = match["teams"]["away"]["name"]
                            data_match = match["fixture"]["date"][:10] # Prende solo YYYY-MM-DD
                            
                            # 2. Interroga il motore per le Predizioni di questa partita
                            url_pred = f"https://api-football-v1.p.rapidapi.com/v3/predictions?fixture={fix_id}"
                            pred_data = requests.get(url_pred, headers=headers).json()
                            
                            if "response" in pred_data and len(pred_data["response"]) > 0:
                                p = pred_data["response"][0]["predictions"]
                                
                                # Probabilità pure
                                p_home = p["percent"]["home"]
                                p_draw = p["percent"]["draw"]
                                p_away = p["percent"]["away"]
                                advice = p["advice"]
                                
                                st.divider()
                                st.subheader(f"⚽ {home} vs {away}")
                                st.caption(f"📅 Data: {data_match}")
                                
                                # Colonne Visive con le Probabilità
                                col1, col2, col3 = st.columns(3)
                                col1.metric(label=f"Vittoria {home}", value=p_home)
                                col2.metric(label="Pareggio (X)", value=p_draw)
                                col3.metric(label=f"Vittoria {away}", value=p_away)
                                
                                st.info(f"💡 **Verdetto dell'Algoritmo:** {advice}")
                                
                                # 3. Il vero segreto: Calcolo delle Fair Odds (Quote Matematiche)
                                # (Formula = 100 / Percentuale)
                                num_h = float(p_home.replace('%', ''))
                                num_d = float(p_draw.replace('%', ''))
                                num_a = float(p_away.replace('%', ''))
                                
                                q_home = round(100 / num_h, 2) if num_h > 0 else 0
                                q_draw = round(100 / num_d, 2) if num_d > 0 else 0
                                q_away = round(100 / num_a, 2) if num_a > 0 else 0
                                
                                st.markdown("### ⚖️ Quote Matematiche Reali (Fair Odds)")
                                st.markdown(f"**1:** `{q_home}` | **X:** `{q_draw}` | **2:** `{q_away}`")
                                st.caption("🔍 **Regola d'oro:** Apri l'app di Sporttip. Se Sporttip offre una quota *SUPERIORE* a queste quote matematiche, hai trovato una **Value Bet**! Scommetti in Singola.")
                    else:
                        st.warning("Nessuna partita imminente trovata per questo campionato al momento.")
                
                except KeyError:
                    st.error("⚠️ Chiave API mancante! Assicurati di aver aggiunto 'API_FOOTBALL_KEY' nei secrets di Streamlit.")
                except Exception as e:
                    st.error(f"⚠️ Errore di connessione: {e}")


    # ---------------------------------------------------------
    # 🎰 SWISS LOTTO
    # ---------------------------------------------------------
    elif opzione == "🎰 Swiss Lotto":
        st.title("🎰 Swiss Lotto")
        
        data_aggiornamento = "5 Giugno 2026"
        st.caption(f"🔄 *Ultimo aggiornamento statistiche: **{data_aggiornamento}***")
        
        swiss_freq_full = [36, 3, 31, 26, 22, 24, 13, 18, 17, 1, 8, 6, 4, 9, 32, 21, 42, 5, 7, 14, 40, 38, 12, 19, 28, 35, 30, 10, 34, 23, 33, 39, 16, 20, 29, 25, 15, 11, 2, 27, 37, 41]
        swiss_fort_full = [1, 5, 4, 6, 2, 3]
        swiss_rit_full = [28, 11, 23, 2, 41, 15, 33, 4, 30, 8, 36, 17, 34, 16, 27, 26, 42, 29, 3, 25, 39, 13, 22, 19, 14, 21, 10, 5, 24, 7, 32, 40, 20, 18, 12, 1, 38, 9, 31, 37, 35, 6]
        swiss_fort_rit_full = [5, 2, 6, 1, 4, 3]
        
        frequenti = swiss_freq_full[:6]
        freddi = swiss_freq_full[-6:]
        ritardatari = swiss_rit_full[:6]
        
        l_freq = swiss_fort_full[:2]
        l_freddi = swiss_fort_full[-2:]
        l_rit = swiss_fort_rit_full[:2]

        tab1, tab2 = st.tabs(["📊 Visione Statistica", "🧮 Sistemi"])
        
        with tab1:
            st.subheader("🔢 Numeri Principali (1-42)")
            c1, c2, c3 = st.columns(3)
            with c1: st.success("🔥 Freq"); st.write(f"`{frequenti}`")
            with c2: st.info("🧊 Freddi"); st.write(f"`{freddi}`")
            with c3: st.error("⏳ Ritardi"); st.write(f"`{ritardatari}`")
            
            st.divider()
            
            st.subheader("🍀 Numeri Fortunati (1-6)")
            c4, c5, c6 = st.columns(3)
            with c4: st.success("🔥 Freq"); st.write(f"`{l_freq}`")
            with c5: st.info("🧊 Freddi"); st.write(f"`{l_freddi}`")
            with c6: st.error("⏳ Ritardi"); st.write(f"`{l_rit}`")
            
            st.divider()
            
            if st.button("🎲 Genera Schedina Pesata", use_container_width=True):
                comb = genera_pesata(range(1, 43), freddi, ritardatari, 6)
                f_num = genera_pesata(range(1, 7), l_freddi, l_rit, 1)[0]
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
        
        euro_freq_full = [44, 42, 23, 19, 29, 17, 10, 21, 50, 37, 27, 35, 25, 26, 20, 45, 13, 14, 4, 5, 15, 24, 38, 7, 12, 34, 49, 30, 6, 11, 16, 39, 48, 3, 28, 8, 1, 9, 31, 36, 47, 2, 41, 43, 32, 40, 18, 46, 33, 22]
        euro_stelle_full = [2, 3, 8, 9, 6, 5, 7, 1, 4, 10, 11, 12]
        euro_rit_full = [39, 30, 2, 11, 33, 14, 25, 41, 27, 47, 5, 44, 23, 29, 36, 17, 43, 20, 48, 12, 1, 7, 21, 4, 13, 16, 45, 10, 31, 8, 40, 38, 32, 24, 26, 34, 15, 18, 37, 9, 49, 19, 35, 3, 6, 42, 50, 46, 28, 22]
        euro_stelle_rit_full = [7, 8, 10, 1, 11, 5, 2, 4, 3, 6, 12, 9]
        
        frequenti_eu = euro_freq_full[:5]
        freddi_eu = euro_freq_full[-5:]
        ritardatari_eu = euro_rit_full[:5]
        
        s_freq = euro_stelle_full[:2]
        s_fredde = euro_stelle_full[-2:]
        s_rit = euro_stelle_rit_full[:2]

        tab1, tab2 = st.tabs(["📊 Visione Statistica", "🧮 Sistemi"])
        
        with tab1:
            st.subheader("🔢 Numeri Principali (1-50)")
            c1, c2, c3 = st.columns(3)
            with c1: st.success("🔥 Freq"); st.write(f"`{frequenti_eu}`")
            with c2: st.info("🧊 Freddi"); st.write(f"`{freddi_eu}`")
            with c3: st.error("⏳ Ritardi"); st.write(f"`{ritardatari_eu}`")
            
            st.divider()
            
            st.subheader("⭐ Stelle (1-12)")
            c4, c5, c6 = st.columns(3)
            with c4: st.success("🔥 Freq"); st.write(f"`{s_freq}`")
            with c5: st.info("🧊 Fredde"); st.write(f"`{s_fredde}`")
            with c6: st.error("⏳ Ritardi"); st.write(f"`{s_rit}`")
            
            st.divider()
            
            if st.button("🎲 Genera Schedina Pesata", use_container_width=True):
                comb = genera_pesata(range(1, 51), freddi_eu, ritardatari_eu, 5)
                stelle = genera_pesata(range(1, 13), s_fredde, s_rit, 2)
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
