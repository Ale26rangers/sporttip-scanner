import streamlit as st
import random
import itertools
import requests

st.set_page_config(page_title="Swiss Betting & Lotto Hub", page_icon="\U0001f1e8\U0001f1ed", layout="centered")

def controlla_password():
    if "autenticato_globale" not in st.session_state:
        st.session_state["autenticato_globale"] = False
    if not st.session_state["autenticato_globale"]:
        st.subheader("\U0001f512 Accesso Riservato")
        password = st.text_input("Password:", type="password")
        if st.button("Accedi \u27a4"):
            if password == "Svizzera2026":
                st.session_state["autenticato_globale"] = True
                st.rerun()
            else:
                st.error("\u274c Password errata!")
        return False
    return True

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

def percentuale_a_quota(perc_str):
    try:
        p = int(perc_str.replace("%", "").strip())
        if p <= 0: return None
        return round(100 / p, 2)
    except:
        return None

if controlla_password():
    st.sidebar.title("\U0001f1e8\U0001f1ed Swiss Hub")
    opzione = st.sidebar.radio("Strumento:", [
        "\U0001f6f0\ufe0f Scanner Sporttip",
        "\U0001f52e Predictor Calcio",
        "\U0001f3d2 Predictor Hockey",
        "\U0001f3b0 Swiss Lotto",
        "\U0001f1ea\U0001f1fa EuroMillions"
    ])
    st.sidebar.divider()

    # --- SCANNER SPORTTIP ---
    if opzione == "\U0001f6f0\ufe0f Scanner Sporttip":
        st.title("\U0001f6f0\ufe0f Scanner Quote Sporttip")
        strategia = st.radio("Seleziona la Strategia Matematica:",
                             ["\U0001f3af Giocate Singole (Esiti Secchi)", "\U0001f4dd Sistema 2/3 (Doppie Chance)"],
                             horizontal=True)
        st.divider()
        if strategia == "\U0001f4dd Sistema 2/3 (Doppie Chance)":
            st.write("Ricerca automatica doppie chance ottimizzate per sistema 2/3.")
            range_q = st.sidebar.slider("Range Quota desiderata:", 1.10, 2.00, (1.35, 1.45), 0.01)
        else:
            st.write("Ricerca di quote di valore secche (1, X, 2) da giocare esclusivamente in **Singola**.")
            range_q = st.sidebar.slider("Range Quota (Singole):", 1.50, 4.00, (1.80, 2.20), 0.05)
        if st.button("\U0001f50d Cerca Partite Ora"):
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
                                if strategia == "\U0001f3af Giocate Singole (Esiti Secchi)":
                                    q1_s = round(avg1 * 0.92, 2)
                                    qX_s = round(avgX * 0.92, 2)
                                    q2_s = round(avg2 * 0.92, 2)
                                    if range_q[0] <= q1_s <= range_q[1]:
                                        partite_filtrate.append({"match": f"{home} - {away}", "segno": "1", "quota": q1_s})
                                    elif range_q[0] <= qX_s <= range_q[1]:
                                        partite_filtrate.append({"match": f"{home} - {away}", "segno": "X", "quota": qX_s})
                                    elif range_q[0] <= q2_s <= range_q[1]:
                                        partite_filtrate.append({"match": f"{home} - {away}", "segno": "2", "quota": q2_s})
                                else:
                                    dc1X = round(((avg1 * avgX) / (avg1 + avgX)) * 0.92, 2)
                                    dcX2 = round(((avg2 * avgX) / (avg2 + avgX)) * 0.92, 2)
                                    if range_q[0] <= dc1X <= range_q[1]:
                                        partite_filtrate.append({"match": f"{home} - {away}", "segno": "1X", "quota": dc1X})
                                    elif range_q[0] <= dcX2 <= range_q[1]:
                                        partite_filtrate.append({"match": f"{home} - {away}", "segno": "X2", "quota": dcX2})
                        if strategia == "\U0001f4dd Sistema 2/3 (Doppie Chance)":
                            if len(partite_filtrate) >= 3:
                                st.success(f"\u2705 Trovate {len(partite_filtrate)} partite idonee!")
                                st.subheader("\U0001f4dd Schedina Consigliata (Sistema 2/3)")
                                for i in range(3):
                                    p = partite_filtrate[i]
                                    st.info(f"**{i+1}\ufe0f\u20e3 {p['match']}**\n\nEsito: `{p['segno']}` | Quota: `{p['quota']}`")
                                q1, q2, q3 = partite_filtrate[0]['quota'], partite_filtrate[1]['quota'], partite_filtrate[2]['quota']
                                vincita_totale = round((q1*q2 + q1*q3 + q2*q3) * 5.0, 2)
                                st.warning(f"\U0001f4b0 Spesa: 15.00 CHF | **Vincita Max: {vincita_totale} CHF**")
                            else:
                                st.error("\u274c Nessun match trovato nel range attuale.")
                        elif strategia == "\U0001f3af Giocate Singole (Esiti Secchi)":
                            if len(partite_filtrate) > 0:
                                st.success(f"\u2705 Trovate {len(partite_filtrate)} occasioni per Singole!")
                                st.subheader("\U0001f3af Consigli per Giocate Singole (Stake Fisso)")
                                st.caption("Gioca ogni evento su una schedina separata con lo stesso importo (es. 5 CHF l'una).")
                                for i, p in enumerate(partite_filtrate[:5]):
                                    st.info(f"**Partita:** {p['match']} \n\n**Pronostico:** Esito `{p['segno']}` \n\n**Quota:** `{p['quota']}`")
                            else:
                                st.error("\u274c Nessun match trovato nel range attuale.")
                except Exception as e:
                    st.error(f"\u26a0\ufe0f Errore API Sporttip: {e}")

    # --- PREDICTOR CALCIO ---
    elif opzione == "\U0001f52e Predictor Calcio":
        st.title("\U0001f52e Predictor Calcio")
        st.write("Analisi avanzata delle probabilita' e calcolo delle **Quote di Valore (Fair Odds)**.")
        league_ids = {
            "\U0001f1e8\U0001f1ed Super League Svizzera": 202,
            "\U0001f1ee\U0001f1f9 Serie A": 135,
            "\U0001f3f4 Premier League": 39,
            "\U0001f1e9\U0001f1ea Bundesliga": 78,
            "\U0001f1ea\U0001f1f8 La Liga": 140,
            "\U0001f1eb\U0001f1f7 Ligue 1": 61,
            "\U0001f1f3\U0001f1f1 Eredivisie (Olanda)": 88,
            "\U0001f1f5\U0001f1f9 Primeira Liga": 94,
            "\U0001f1e7\U0001f1ea Jupiler Pro League": 144,
            "\U0001f3c6 Champions League": 2,
            "\U0001f3c6 Europa League": 3,
        }
        campionato = st.selectbox("Scegli il Campionato da analizzare:", list(league_ids.keys()))
        league_id = league_ids[campionato]
        if st.button("\U0001f9ee Avvia Motore Predittivo", type="primary"):
            try:
                API_KEY = st.secrets["API_FOOTBALL_KEY"]
                headers = {"x-apisports-key": API_KEY}
                url_fixtures = f"https://v3.football.api-sports.io/fixtures?league={league_id}&next=5"
                response = requests.get(url_fixtures, headers=headers).json()
                if "response" in response and len(response["response"]) > 0:
                    for match in response["response"]:
                        fix_id = match["fixture"]["id"]
                        home = match["teams"]["home"]["name"]
                        away = match["teams"]["away"]["name"]
                        url_pred = f"https://v3.football.api-sports.io/predictions?fixture={fix_id}"
                        pred_data = requests.get(url_pred, headers=headers).json()
                        if "response" in pred_data and len(pred_data["response"]) > 0:
                            p = pred_data["response"][0]["predictions"]["percent"]
                            st.divider()
                            st.subheader(f"\u26bd {home} vs {away}")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("\U0001f3e0 Vittoria Casa", p['home'])
                            col2.metric("\U0001f91d Pareggio", p['draw'])
                            col3.metric("\u2708\ufe0f Vittoria Ospite", p['away'])
                            q_h = percentuale_a_quota(p['home'])
                            q_d = percentuale_a_quota(p['draw'])
                            q_a = percentuale_a_quota(p['away'])
                            if q_h and q_d and q_a:
                                probs = {
                                    f"1 ({home})": int(p['home'].replace('%','')),
                                    "X (Pareggio)": int(p['draw'].replace('%','')),
                                    f"2 ({away})": int(p['away'].replace('%',''))
                                }
                                consiglio = max(probs, key=probs.get)
                                prob_max = probs[consiglio]
                                st.info(f"\U0001f4ca Quote Equa \u2192 1: `{q_h}` | X: `{q_d}` | 2: `{q_a}`")
                                if prob_max >= 55:
                                    st.success(f"\u2705 **Consiglio Statistico:** Punta su **{consiglio}** ({prob_max}% di probabilita')")
                                elif prob_max >= 40:
                                    st.warning(f"\u26a0\ufe0f **Consiglio Statistico:** Esito piu' probabile **{consiglio}** ({prob_max}%) - partita equilibrata, gioca con cautela")
                                else:
                                    st.error(f"\u274c **Nessun consiglio** - partita troppo incerta (max {prob_max}%)")
                else:
                    st.warning("Nessuna partita imminente trovata. Il campionato potrebbe essere in pausa stagionale.")
            except Exception as e:
                st.error(f"Errore di connessione: {e}")

    # --- PREDICTOR HOCKEY ---
    elif opzione == "\U0001f3d2 Predictor Hockey":
        st.title("\U0001f3d2 Predictor Hockey su Ghiaccio")
        st.write("Analisi predittiva, quote equa e **testa a testa** per i principali campionati di hockey.")
        hockey_leagues = {
            "\U0001f1fa\U0001f1f8\U0001f1e8\U0001f1e6 NHL": 57,
            "\U0001f1f8\U0001f1ea SHL (Svezia)": 46,
            "\U0001f1eb\U0001f1ee Liiga (Finlandia)": 44,
            "\U0001f1e8\U0001f1ed NLA (Svizzera)": 64,
            "\U0001f1e9\U0001f1ea DEL (Germania)": 36,
            "\U0001f1f7\U0001f1fa KHL (Russia)": 28,
            "\U0001f1e8\U0001f1ff Extraliga (Rep. Ceca)": 39,
            "\U0001f1e6\U0001f1f9 ICEHL (Austria)": 23,
        }
        campionato_h = st.selectbox("Scegli la Lega Hockey:", list(hockey_leagues.keys()))
        league_id_h = hockey_leagues[campionato_h]
        stagione = st.number_input("Stagione (anno di inizio):", min_value=2020, max_value=2026, value=2025, step=1)
        if st.button("\U0001f3d2 Avvia Analisi Hockey", type="primary"):
            try:
                API_KEY_H = st.secrets["API_HOCKEY_KEY"]
                headers_h = {"x-apisports-key": API_KEY_H}
                url_games = f"https://v1.hockey.api-sports.io/games?league={league_id_h}&season={stagione}&next=5"
                resp_games = requests.get(url_games, headers=headers_h).json()
                if "response" not in resp_games or len(resp_games["response"]) == 0:
                    st.warning("\u26a0\ufe0f Nessuna partita imminente trovata. La lega potrebbe essere in pausa stagionale.")
                else:
                    for game in resp_games["response"]:
                        game_id = game["id"]
                        home = game["teams"]["home"]["name"]
                        away = game["teams"]["away"]["name"]
                        data_partita = game["date"][:10]
                        st.divider()
                        st.subheader(f"\U0001f3d2 {home} vs {away}")
                        st.caption(f"\U0001f4c5 Data: {data_partita}")
                        url_odds = f"https://v1.hockey.api-sports.io/odds?game={game_id}"
                        resp_odds = requests.get(url_odds, headers=headers_h).json()
                        q1, q2 = None, None
                        if "response" in resp_odds and len(resp_odds["response"]) > 0:
                            try:
                                bets = resp_odds["response"][0]["bookmakers"][0]["bets"]
                                for bet in bets:
                                    if bet["name"] in ["Match Winner", "Home/Away"]:
                                        for val in bet["values"]:
                                            if val["value"] == "Home": q1 = float(val["odd"])
                                            elif val["value"] == "Away": q2 = float(val["odd"])
                            except:
                                pass
                        home_id = game["teams"]["home"]["id"]
                        away_id = game["teams"]["away"]["id"]
                        url_h2h = f"https://v1.hockey.api-sports.io/games/h2h?h2h={home_id}-{away_id}"
                        resp_h2h = requests.get(url_h2h, headers=headers_h).json()
                        wins_home, wins_away, totali = 0, 0, 0
                        if "response" in resp_h2h:
                            for g in resp_h2h["response"][:10]:
                                totali += 1
                                s_home = g["scores"]["home"]
                                s_away = g["scores"]["away"]
                                if s_home is not None and s_away is not None:
                                    if s_home > s_away: wins_home += 1
                                    elif s_away > s_home: wins_away += 1
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**\U0001f4ca Quote Bookmaker**")
                            if q1 and q2:
                                prob_h = round(100 / q1, 1)
                                prob_a = round(100 / q2, 1)
                                q_equa_h = round(1 / (prob_h / 100), 2)
                                q_equa_a = round(1 / (prob_a / 100), 2)
                                st.metric(f"\U0001f3e0 {home}", f"{q1}")
                                st.metric(f"\u2708\ufe0f {away}", f"{q2}")
                                st.info(f"\u2696\ufe0f Quota Equa \u2192 {home}: `{q_equa_h}` | {away}: `{q_equa_a}`")
                            else:
                                st.caption("Quote non disponibili per questa partita.")
                                prob_h, prob_a = None, None
                        with col2:
                            st.markdown("**\U0001f501 Testa a Testa (ultimi 10)**")
                            if totali > 0:
                                st.metric(f"\U0001f3c6 Vittorie {home}", f"{wins_home}/{totali}")
                                st.metric(f"\U0001f3c6 Vittorie {away}", f"{wins_away}/{totali}")
                                pareggi = totali - wins_home - wins_away
                                if pareggi > 0:
                                    st.caption(f"Overtime/Parita': {pareggi}")
                            else:
                                st.caption("Nessun dato H2H disponibile.")
                        st.markdown("---")
                        if prob_h and prob_a and totali > 0:
                            perc_h2h_home = round((wins_home / totali) * 100, 1)
                            perc_h2h_away = round((wins_away / totali) * 100, 1)
                            score_home = (prob_h * 0.6) + (perc_h2h_home * 0.4)
                            score_away = (prob_a * 0.6) + (perc_h2h_away * 0.4)
                            if score_home > score_away:
                                delta = round(score_home - score_away, 1)
                                if delta >= 15:
                                    st.success(f"\u2705 **Consiglio:** Punta su **{home}** - vantaggio composito solido (+{delta} pts)")
                                else:
                                    st.warning(f"\u26a0\ufe0f **Consiglio:** Lieve favore a **{home}** (+{delta} pts) - partita equilibrata")
                            elif score_away > score_home:
                                delta = round(score_away - score_home, 1)
                                if delta >= 15:
                                    st.success(f"\u2705 **Consiglio:** Punta su **{away}** - vantaggio composito solido (+{delta} pts)")
                                else:
                                    st.warning(f"\u26a0\ufe0f **Consiglio:** Lieve favore a **{away}** (+{delta} pts) - partita equilibrata")
                            else:
                                st.error("\u274c **Nessun consiglio** - probabilita' perfettamente bilanciate")
                        elif prob_h and prob_a:
                            if prob_h > prob_a + 10:
                                st.success(f"\u2705 **Consiglio (solo quote):** Punta su **{home}** ({prob_h}% probabilita' implicita)")
                            elif prob_a > prob_h + 10:
                                st.success(f"\u2705 **Consiglio (solo quote):** Punta su **{away}** ({prob_a}% probabilita' implicita)")
                            else:
                                st.warning("\u26a0\ufe0f Partita equilibrata - nessun consiglio sicuro")
                        else:
                            st.caption("Dati insufficienti per un consiglio statistico.")
            except Exception as e:
                st.error(f"\u26a0\ufe0f Errore connessione API Hockey: {e}")
                st.info("\U0001f4a1 Assicurati di aver aggiunto **API_HOCKEY_KEY** nei Secrets di Streamlit.")

    # --- SWISS LOTTO ---
    elif opzione == "\U0001f3b0 Swiss Lotto":
        st.title("\U0001f3b0 Swiss Lotto")
        data_aggiornamento = "5 Giugno 2026"
        st.caption(f"\U0001f504 *Ultimo aggiornamento statistiche: **{data_aggiornamento}***")
        swiss_freq_full = [36, 3, 31, 26, 22, 24, 13, 18, 17, 1, 8, 6, 4, 9, 32, 21, 42, 5, 7, 14, 40, 38, 12, 19, 28, 35, 30, 10, 34
