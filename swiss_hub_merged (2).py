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

    # === INDICATORE CREDITI API-FOOTBALL (non consuma quota) ===
    with st.sidebar.expander("\U0001f4ca Crediti API-Football"):
        try:
            _hdr = {"x-apisports-key": st.secrets["API_FOOTBALL_KEY"]}
            _st = requests.get("https://v3.football.api-sports.io/status", headers=_hdr).json()
            _req = _st["response"]["requests"]
            _usati = _req["current"]
            _limite = _req["limit_day"]
            _rimasti = _limite - _usati
            st.metric("Rimasti oggi", f"{_rimasti}/{_limite}")
            if _rimasti <= 10:
                st.error("\u26a0\ufe0f Quasi esauriti!")
            elif _rimasti <= 30:
                st.warning("\u26a0\ufe0f Pochi crediti rimasti")
        except Exception as _e:
            st.caption(f"Stato non disponibile: {_e}")

    opzione = st.sidebar.radio("Strumento:", [
        "\U0001f6f0\ufe0f Scanner Sporttip",
        "\U0001f48e Value Bet Finder",
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
                                        partite_filtrate.append({"match": f"{home} - {away}", "segno": "1", "quota": q1_s, "q1": q1_s, "qX": qX_s, "q2": q2_s, "home": home, "away": away})
                                    elif range_q[0] <= qX_s <= range_q[1]:
                                        partite_filtrate.append({"match": f"{home} - {away}", "segno": "X", "quota": qX_s, "q1": q1_s, "qX": qX_s, "q2": q2_s, "home": home, "away": away})
                                    elif range_q[0] <= q2_s <= range_q[1]:
                                        partite_filtrate.append({"match": f"{home} - {away}", "segno": "2", "quota": q2_s, "q1": q1_s, "qX": qX_s, "q2": q2_s, "home": home, "away": away})
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
                                    _home_t = p.get("home", p["match"].split(" - ")[0])
                                    _away_t = p.get("away", p["match"].split(" - ")[-1])
                                    _esiti = [
                                        ("1", f"🏠 {_home_t}", p.get("q1", "-")),
                                        ("X", "🤝 Pareggio",  p.get("qX", "-")),
                                        ("2", f"✈️ {_away_t}",  p.get("q2", "-")),
                                    ]
                                    with st.container(border=True):
                                        st.markdown(f"**🎯 Partita {i+1}: {p['match']}**")
                                        for _s, _label, _q in _esiti:
                                            _perc = round(100 / _q, 1) if isinstance(_q, float) else "-"
                                            _perc_str = f" *({_perc}%)*" if _perc != "-" else ""
                                            _riga = f"`{_s}` {_label} — Quota: **{_q}**{_perc_str}"
                                            if _s == p["segno"]:
                                                st.success(f"⭐ {_riga} ← **CONSIGLIATO**")
                                            else:
                                                st.info(_riga)
                            else:
                                st.error("\u274c Nessun match trovato nel range attuale.")
                except Exception as e:
                    st.error(f"\u26a0\ufe0f Errore API Sporttip: {e}")

    # --- VALUE BET FINDER ---
    elif opzione == "\U0001f48e Value Bet Finder":
        st.title("\U0001f48e Value Bet Finder")
        st.write("Confronta le **quote reali dei bookmaker** con una **stima di probabilita' indipendente** per scovare scommesse di valore (EV positivo).")

        st.info("\U0001f4a1 **Come funziona:** una *value bet* esiste quando la probabilita' reale stimata e' piu' alta di quella implicita nella quota. In quel caso, sul lungo periodo, la scommessa e' matematicamente vantaggiosa.")

        # Avvisi di trasparenza
        with st.expander("\u26a0\ufe0f Leggi prima: limiti e affidabilita'"):
            st.markdown("""
            - Le **stime di probabilita'** vengono da API-Football (`predictions`): sono un modello statistico generico, **non un oracolo**. I bookmaker spesso hanno modelli migliori.
            - Le partite delle due API vengono agganciate per **nome squadra + data**: occasionalmente un match potrebbe non essere abbinato (es. nomi scritti diversamente).
            - **1X2 e Doppia Chance** sono i mercati piu' affidabili.
            - **Over/Under e' una STIMA derivata** dalle previsioni goal: trattalo con molta cautela, e' la parte piu' debole.
            - Nessuno strumento gratuito garantisce profitto. Questo serve a **individuare candidati**, non a stampare denaro. Gioca responsabilmente.
            """)

        st.divider()

        # Catalogo campionati (id, nome leggibile, fascia di inefficienza)
        # Fasce (euristica orientativa, NON misura empirica):
        #   verde = leghe minori/meno coperte -> banco potenzialmente piu' attaccabile
        #   giallo = media copertura
        #   rosso = mercati enormi, banco molto efficiente
        campionati_info = {
            135: {"nome": "\U0001f1ee\U0001f1f9 Serie A", "fascia": "giallo"},
            39:  {"nome": "\U0001f3f4 Premier League", "fascia": "rosso"},
            78:  {"nome": "\U0001f1e9\U0001f1ea Bundesliga", "fascia": "giallo"},
            140: {"nome": "\U0001f1ea\U0001f1f8 La Liga", "fascia": "rosso"},
            61:  {"nome": "\U0001f1eb\U0001f1f7 Ligue 1", "fascia": "giallo"},
            88:  {"nome": "\U0001f1f3\U0001f1f1 Eredivisie", "fascia": "verde"},
            94:  {"nome": "\U0001f1f5\U0001f1f9 Primeira Liga", "fascia": "verde"},
            144: {"nome": "\U0001f1e7\U0001f1ea Jupiler Pro League", "fascia": "verde"},
            203: {"nome": "\U0001f1e8\U0001f1ed Super League CH", "fascia": "verde"},
            2:   {"nome": "\U0001f3c6 Champions League", "fascia": "rosso"},
            3:   {"nome": "\U0001f3c6 Europa League", "fascia": "rosso"},
        }
        fascia_icona = {"verde": "\U0001f7e2", "giallo": "\U0001f7e1", "rosso": "\U0001f534"}

        # Selettore campionati con tag fascia nel nome
        nome_to_id = {f"{fascia_icona[info['fascia']]} {info['nome']}": lid for lid, info in campionati_info.items()}
        scelti_label = st.multiselect(
            "Campionati da interrogare (scegli tu quanti crediti spendere):",
            list(nome_to_id.keys()),
            default=["\U0001f7e2 \U0001f1e8\U0001f1ed Super League CH"],
            help="Ogni campionato costa ~1 + (n. partite) chiamate API. Meno campionati = meno consumo."
        )
        leghe_scelte = [nome_to_id[l] for l in scelti_label]

        # Impostazioni
        col_a, col_b = st.columns(2)
        with col_a:
            soglia_ev = st.slider("Soglia EV minima (%):", 2, 25, 10, 1,
                                  help="Conservativa = 10%+. Piu' alta = meno candidate ma piu' solide.")
        with col_b:
            max_partite = st.slider("Max partite per campionato:", 1, 10, 5, 1,
                                    help="Limita le chiamate API. 5 e' un buon compromesso.")

        mercati_scelti = st.multiselect("Mercati da analizzare:",
                                        ["1X2", "Doppia Chance", "Over/Under 2.5"],
                                        default=["1X2", "Doppia Chance", "Over/Under 2.5"])

        # Stima consumo API in tempo reale
        stima_chiamate = len(leghe_scelte) + (len(leghe_scelte) * max_partite)
        st.caption(f"\U0001f50e Stima consumo: **~{stima_chiamate} chiamate** ad API-Football + 1 a The-Odds-API. (Piano free API-Football = 100/giorno)")
        if stima_chiamate > 80:
            st.warning("\u26a0\ufe0f Consumo elevato: rischi di esaurire la quota giornaliera. Riduci campionati o partite.")

        if not leghe_scelte:
            st.info("\U0001f446 Seleziona almeno un campionato per avviare la ricerca.")

        if st.button("\U0001f48e Cerca Value Bet", type="primary", disabled=(len(leghe_scelte) == 0)):
            with st.spinner("Incrocio quote bookmaker e probabilita' stimate..."):
                try:
                    ODDS_KEY = st.secrets["MY_API_KEY"]
                    FOOT_KEY = st.secrets["API_FOOTBALL_KEY"]
                    headers_f = {"x-apisports-key": FOOT_KEY}

                    # STEP 1: quote bookmaker da The-Odds-API
                    url_odds = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_KEY}&regions=eu&markets=h2h,totals"
                    dati_odds = requests.get(url_odds).json()

                    if not isinstance(dati_odds, list) or len(dati_odds) == 0:
                        st.warning("Nessuna quota disponibile al momento (campionati in pausa?).")
                    else:
                        import difflib

                        def normalizza(nome):
                            n = nome.lower()
                            for tok in ["fc", "ac", "ssc", "as", "us", "calcio", "cf", "sc", "1899", "1900", "1846", "1907"]:
                                n = n.replace(tok, "")
                            return n.replace(".", "").replace("-", " ").replace("  ", " ").strip()

                        # Costruiamo le previsioni MANTENENDO il campionato di provenienza
                        # struttura: lista di dict {home_norm, away_norm, league_id, prob..., match}
                        previsioni_per_lega = {}  # league_id -> lista previsioni

                        for lid in leghe_scelte:
                            try:
                                url_fx = f"https://v3.football.api-sports.io/fixtures?league={lid}&next={max_partite}"
                                fx = requests.get(url_fx, headers=headers_f).json()
                                if "response" not in fx:
                                    continue
                                lista = []
                                for m in fx["response"]:
                                    fix_id = m["fixture"]["id"]
                                    h = m["teams"]["home"]["name"]
                                    a = m["teams"]["away"]["name"]
                                    url_p = f"https://v3.football.api-sports.io/predictions?fixture={fix_id}"
                                    pd = requests.get(url_p, headers=headers_f).json()
                                    if "response" in pd and len(pd["response"]) > 0:
                                        perc = pd["response"][0]["predictions"]["percent"]
                                        goals = pd["response"][0]["predictions"].get("goals", {})
                                        lista.append({
                                            "home_norm": normalizza(h), "away_norm": normalizza(a),
                                            "home": perc.get("home"), "draw": perc.get("draw"),
                                            "away": perc.get("away"), "goals": goals,
                                            "match": f"{h} vs {a}",
                                            "league_id": lid
                                        })
                                if lista:
                                    previsioni_per_lega[lid] = lista
                            except:
                                continue

                        tot_previsioni = sum(len(v) for v in previsioni_per_lega.values())

                        if tot_previsioni == 0:
                            st.warning("Nessuna previsione disponibile da API-Football (campionati in pausa o limite API raggiunto).")
                        else:
                            value_trovate = []

                            def perc_to_float(s):
                                try:
                                    return int(s.replace("%", "").strip()) / 100.0
                                except:
                                    return None

                            # Aggancio FUZZY con doppia conferma casa+trasferta, dentro ogni campionato
                            def trova_match_fuzzy(home_n, away_n):
                                migliore = None
                                miglior_score = 0
                                for lid, lista in previsioni_per_lega.items():
                                    for pv in lista:
                                        s_home = difflib.SequenceMatcher(None, home_n, pv["home_norm"]).ratio()
                                        s_away = difflib.SequenceMatcher(None, away_n, pv["away_norm"]).ratio()
                                        # doppia conferma: media delle due somiglianze
                                        score = (s_home + s_away) / 2
                                        # entrambe devono superare una soglia minima per evitare falsi positivi
                                        if s_home >= 0.6 and s_away >= 0.6 and score > miglior_score:
                                            miglior_score = score
                                            migliore = pv
                                # accettiamo solo se la media combinata e' solida
                                if migliore and miglior_score >= 0.7:
                                    return migliore
                                return None

                            for partita in dati_odds:
                                home = partita.get("home_team")
                                away = partita.get("away_team")
                                if not partita.get("bookmakers"):
                                    continue
                                pv = trova_match_fuzzy(normalizza(home), normalizza(away))
                                if pv is None:
                                    continue
                                fascia = campionati_info[pv["league_id"]]["fascia"]
                                tag_fascia = fascia_icona[fascia]

                                # Raccogli quote h2h medie e totals
                                q1, qX, q2 = [], [], []
                                q_over, q_under = [], []
                                for b in partita["bookmakers"]:
                                    for mk in b.get("markets", []):
                                        if mk["key"] == "h2h":
                                            for o in mk["outcomes"]:
                                                if o["name"] == home: q1.append(o["price"])
                                                elif o["name"] == "Draw": qX.append(o["price"])
                                                elif o["name"] == away: q2.append(o["price"])
                                        elif mk["key"] == "totals":
                                            for o in mk["outcomes"]:
                                                if o.get("point") == 2.5:
                                                    if o["name"] == "Over": q_over.append(o["price"])
                                                    elif o["name"] == "Under": q_under.append(o["price"])

                                # Migliore quota disponibile (la piu' alta = piu' conveniente)
                                best1 = max(q1) if q1 else None
                                bestX = max(qX) if qX else None
                                best2 = max(q2) if q2 else None
                                best_over = max(q_over) if q_over else None
                                best_under = max(q_under) if q_under else None

                                # Probabilita' stimate
                                p1 = perc_to_float(pv["home"])
                                pX = perc_to_float(pv["draw"])
                                p2 = perc_to_float(pv["away"])

                                # --- LETTURA PREDICTOR (stessa logica della sezione Predictor Calcio) ---
                                # Determina l'esito 1X2 piu' probabile e con quale confidenza.
                                # Serve per segnalare la convergenza con la value bet.
                                pred_esito = None      # "1" / "X" / "2"
                                pred_prob = None       # percentuale dell'esito piu' probabile
                                pred_forza = None      # "forte" / "debole" / "incerto"
                                if p1 and pX and p2:
                                    mappa_pred = {"1": p1, "X": pX, "2": p2}
                                    pred_esito = max(mappa_pred, key=mappa_pred.get)
                                    pred_prob = round(mappa_pred[pred_esito] * 100, 1)
                                    if pred_prob >= 55:
                                        pred_forza = "forte"
                                    elif pred_prob >= 40:
                                        pred_forza = "debole"
                                    else:
                                        pred_forza = "incerto"

                                def lettura_predictor(esito_value):
                                    """Restituisce (testo, convergenza_piena) per un dato esito value."""
                                    if pred_esito is None:
                                        return ("Predictor: dati non disponibili", False)
                                    # Esiti su cui il Predictor 'copre' l'esito value:
                                    # per 1X2 deve coincidere; per Doppia Chance basta che l'esito
                                    # piu' probabile sia una delle due componenti; per O/U non si applica.
                                    base = f"Predictor: piu' probabile **{pred_esito}** ({pred_prob}%, segnale {pred_forza})"
                                    conv = False
                                    if esito_value in ("1", "X", "2"):
                                        conv = (esito_value == pred_esito)
                                    elif esito_value in ("1X", "X2", "12"):
                                        conv = (pred_esito in esito_value)
                                    return (base, conv)
                                if "1X2" in mercati_scelti and p1 and pX and p2:
                                    for nome_e, prob_e, quota_e in [("1", p1, best1), ("X", pX, bestX), ("2", p2, best2)]:
                                        if quota_e:
                                            ev = (prob_e * quota_e) - 1
                                            if ev * 100 >= soglia_ev:
                                                _txt, _conv = lettura_predictor(nome_e)
                                                value_trovate.append({
                                                    "match": pv["match"], "mercato": "1X2",
                                                    "esito": nome_e, "quota": round(quota_e, 2),
                                                    "prob": round(prob_e * 100, 1), "ev": round(ev * 100, 1),
                                                    "tag": tag_fascia, "fascia": fascia,
                                                    "pred_txt": _txt, "pred_conv": _conv
                                                })

                                # --- Doppia Chance (derivata da 1X2) ---
                                if "Doppia Chance" in mercati_scelti and p1 and pX and p2 and best1 and bestX and best2:
                                    # prob DC
                                    p_1X = p1 + pX
                                    p_X2 = pX + p2
                                    p_12 = p1 + p2
                                    # quota DC equa derivata dalle singole (approssimazione: 1/(1/qa + 1/qb))
                                    def q_dc(qa, qb):
                                        return round(1 / ((1/qa) + (1/qb)), 2)
                                    for nome_e, prob_e, quota_e in [
                                        ("1X", p_1X, q_dc(best1, bestX)),
                                        ("X2", p_X2, q_dc(bestX, best2)),
                                        ("12", p_12, q_dc(best1, best2))
                                    ]:
                                        ev = (prob_e * quota_e) - 1
                                        if ev * 100 >= soglia_ev:
                                            _txt, _conv = lettura_predictor(nome_e)
                                            value_trovate.append({
                                                "match": pv["match"], "mercato": "Doppia Chance",
                                                "esito": nome_e, "quota": quota_e,
                                                "prob": round(prob_e * 100, 1), "ev": round(ev * 100, 1),
                                                "tag": tag_fascia, "fascia": fascia,
                                                "pred_txt": _txt, "pred_conv": _conv
                                            })

                                # --- Over/Under 2.5 (STIMA) ---
                                if "Over/Under 2.5" in mercati_scelti:
                                    goals = pv.get("goals", {})
                                    # API-Football a volte da' goals.home / goals.away come stringhe tipo "-1.5"
                                    try:
                                        gh = abs(float(str(goals.get("home", "0")).replace("-", "") or 0))
                                        ga = abs(float(str(goals.get("away", "0")).replace("-", "") or 0))
                                        tot_stimato = gh + ga
                                        # stima grezza prob Over 2.5: se tot>2.5 piu' probabile Over
                                        if tot_stimato > 0:
                                            if tot_stimato >= 2.5:
                                                p_over = min(0.5 + (tot_stimato - 2.5) * 0.18, 0.85)
                                            else:
                                                p_over = max(0.5 - (2.5 - tot_stimato) * 0.18, 0.15)
                                            p_under = 1 - p_over
                                            for nome_e, prob_e, quota_e in [("Over 2.5", p_over, best_over), ("Under 2.5", p_under, best_under)]:
                                                if quota_e:
                                                    ev = (prob_e * quota_e) - 1
                                                    if ev * 100 >= soglia_ev:
                                                        value_trovate.append({
                                                            "match": pv["match"], "mercato": "Over/Under (STIMA)",
                                                            "esito": nome_e, "quota": round(quota_e, 2),
                                                            "prob": round(prob_e * 100, 1), "ev": round(ev * 100, 1),
                                                            "tag": tag_fascia, "fascia": fascia,
                                                            "pred_txt": "Predictor: non applicabile ai mercati Over/Under", "pred_conv": False
                                                        })
                                    except:
                                        pass

                            # Risultati
                            if len(value_trovate) == 0:
                                st.warning(f"Nessuna value bet trovata con EV >= {soglia_ev}%. Prova ad abbassare la soglia o riprova quando ci sono piu' partite.")
                                st.caption(f"Partite con previsione disponibili: {tot_previsioni}")
                            else:
                                value_trovate.sort(key=lambda x: x["ev"], reverse=True)
                                st.success(f"\u2705 Trovate {len(value_trovate)} value bet (ordinate per EV decrescente)!")
                                st.caption("\U0001f7e2 lega meno coperta dal banco (piu' attaccabile) \u00b7 \U0001f7e1 media \u00b7 \U0001f534 banco molto efficiente. Indicazione orientativa, non garanzia.")
                                st.caption("\U0001f3af **Doppio segnale** = la value bet coincide con l'esito piu' probabile secondo il Predictor (coerenza, non garanzia: stessa fonte dati).")
                                st.divider()
                                for v in value_trovate:
                                    icona = "\U0001f48e" if "STIMA" not in v["mercato"] else "\u26a0\ufe0f"
                                    # Intestazione con badge doppio segnale se converge
                                    if v.get("pred_conv"):
                                        st.markdown(f"### \U0001f3af DOPPIO SEGNALE")
                                    st.markdown(f"**{icona} {v['tag']} {v['match']}**")
                                    st.markdown(f"Mercato: `{v['mercato']}` | Esito: **{v['esito']}** | Quota: `{v['quota']}` | Prob. stimata: `{v['prob']}%` | **EV: +{v['ev']}%**")
                                    # Lettura Predictor
                                    if v.get("pred_conv"):
                                        st.success(f"\u2705 {v['pred_txt']} \u2014 **converge con la value bet**")
                                    else:
                                        st.caption(f"\u2139\ufe0f {v['pred_txt']}")
                                    st.divider()
                except Exception as e:
                    st.error(f"\u26a0\ufe0f Errore Value Bet Finder: {e}")

    # --- PREDICTOR CALCIO ---
    elif opzione == "\U0001f52e Predictor Calcio":
        st.title("\U0001f52e Predictor Calcio")
        st.write("Analisi avanzata delle probabilita' e calcolo delle **Quote di Valore (Fair Odds)**.")

        # Due modalita': campionati 'preferiti' fissi, oppure ricerca per paese (carica gli ID live)
        modalita = st.radio("Come scegliere il campionato:",
                            ["\u2b50 Preferiti (Europa)", "\U0001f30e Cerca per Paese (carica live)"],
                            horizontal=True)

        league_id = None
        campionato = None
        league_season = None

        if modalita == "\u2b50 Preferiti (Europa)":
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
            # Selettore stagione opzionale: serve per TESTARE su dati storici (free: 2022-2024)
            usa_storico = st.checkbox("\U0001f4da Test su stagione storica (per piano gratuito: 2022-2024)")
            if usa_storico:
                league_season = st.selectbox("Stagione storica da testare:", [2024, 2023, 2022])
                st.caption("Su stagioni passate vedrai partite gia' giocate (coi risultati). Serve a verificare che la chiave acceda ai dati.")
        else:
            # Selettore Paese -> carica campionati live dall'endpoint leagues
            paesi = ["Argentina", "Brazil", "Uruguay", "Chile", "Colombia", "Paraguay",
                     "Peru", "Ecuador", "Bolivia", "Venezuela", "USA", "Mexico", "Japan", "Australia"]
            paese = st.selectbox("Scegli il Paese:", paesi,
                                 help="Carica i campionati attivi di questo paese (1 chiamata API).")
            if st.button("\U0001f50d Carica campionati di " + paese):
                try:
                    API_KEY = st.secrets["API_FOOTBALL_KEY"]
                    headers = {"x-apisports-key": API_KEY}
                    url_lg = f"https://v3.football.api-sports.io/leagues?country={paese}&current=true&type=league"
                    resp_lg = requests.get(url_lg, headers=headers).json()
                    leghe_trovate = {}
                    if "response" in resp_lg:
                        for item in resp_lg["response"]:
                            lg = item["league"]
                            # prendiamo la stagione corrente
                            stagione_corr = None
                            for s in item.get("seasons", []):
                                if s.get("current"):
                                    stagione_corr = s.get("year")
                            leghe_trovate[lg["name"]] = {"id": lg["id"], "season": stagione_corr}
                    if leghe_trovate:
                        st.session_state["leghe_paese"] = leghe_trovate
                        st.session_state["paese_caricato"] = paese
                    else:
                        st.warning(f"Nessun campionato attivo trovato per {paese}.")
                        st.session_state.pop("leghe_paese", None)
                except Exception as e:
                    st.error(f"Errore caricamento campionati: {e}")

            # Se abbiamo campionati caricati in sessione, mostriamo il selettore
            if "leghe_paese" in st.session_state and st.session_state["leghe_paese"]:
                st.caption(f"Campionati attivi caricati per: **{st.session_state.get('paese_caricato', '')}**")
                nomi = list(st.session_state["leghe_paese"].keys())
                campionato = st.selectbox("Scegli il Campionato:", nomi)
                league_id = st.session_state["leghe_paese"][campionato]["id"]
                league_season = st.session_state["leghe_paese"][campionato].get("season")

        avvia = st.button("\U0001f9ee Avvia Motore Predittivo", type="primary", disabled=(league_id is None))
        if league_id is None:
            st.info("\U0001f446 Seleziona (o carica) un campionato per avviare l'analisi.")

        if avvia and league_id is not None:
            try:
                API_KEY = st.secrets["API_FOOTBALL_KEY"]
                headers = {"x-apisports-key": API_KEY}

                # Strategia di ricerca partite robusta:
                # 1) prova next=5 (semplice)
                # 2) se vuoto e abbiamo la stagione, prova per finestra di date (prossimi 30 gg) + season
                import datetime as _dt

                def chiedi_fixtures(url):
                    r = requests.get(url, headers=headers).json()
                    return r

                response = None
                diag = []  # raccoglie info diagnostiche

                # Tentativo 1: next
                url_n = f"https://v3.football.api-sports.io/fixtures?league={league_id}&next=5"
                r1 = chiedi_fixtures(url_n)
                n1 = len(r1.get("response", [])) if isinstance(r1, dict) else 0
                err1 = r1.get("errors") if isinstance(r1, dict) else None
                diag.append(f"Tentativo 'next=5': {n1} partite" + (f" | errori: {err1}" if err1 else ""))
                if n1 > 0:
                    response = r1

                # Tentativo 2: finestra date + season (se disponibile)
                if response is None:
                    oggi = _dt.date.today()
                    fine = oggi + _dt.timedelta(days=30)
                    if league_season:
                        url_d = (f"https://v3.football.api-sports.io/fixtures?league={league_id}"
                                 f"&season={league_season}&from={oggi}&to={fine}")
                    else:
                        url_d = (f"https://v3.football.api-sports.io/fixtures?league={league_id}"
                                 f"&from={oggi}&to={fine}")
                    r2 = chiedi_fixtures(url_d)
                    lista2 = r2.get("response", []) if isinstance(r2, dict) else []
                    # teniamo solo le non ancora giocate (status NS = Not Started)
                    lista2_ns = [m for m in lista2 if m.get("fixture", {}).get("status", {}).get("short") in ("NS", "TBD")]
                    err2 = r2.get("errors") if isinstance(r2, dict) else None
                    diag.append(f"Tentativo 'date+season ({league_season})': {len(lista2)} totali, {len(lista2_ns)} non giocate" + (f" | errori: {err2}" if err2 else ""))
                    if lista2_ns:
                        response = {"response": lista2_ns[:5]}
                    elif lista2:
                        # se ci sono partite ma tutte giocate, mostriamo comunque le prossime per data
                        response = {"response": lista2[:5]}

                # Tentativo 3: stagione intera (utile per TEST STORICO su stagioni passate)
                # Se siamo qui e abbiamo una stagione, chiediamo tutte le partite di quella stagione.
                if response is None and league_season:
                    url_s = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={league_season}"
                    r3 = chiedi_fixtures(url_s)
                    lista3 = r3.get("response", []) if isinstance(r3, dict) else []
                    err3 = r3.get("errors") if isinstance(r3, dict) else None
                    # ordiniamo per data e prendiamo le piu' recenti (le ultime giocate)
                    try:
                        lista3.sort(key=lambda m: m.get("fixture", {}).get("date", ""), reverse=True)
                    except:
                        pass
                    diag.append(f"Tentativo 'stagione intera ({league_season})': {len(lista3)} partite trovate" + (f" | errori: {err3}" if err3 else ""))
                    if lista3:
                        response = {"response": lista3[:5], "_storico": True}

                # Pannello diagnostico (sempre visibile, aiuta a capire)
                with st.expander("\U0001f527 Diagnostica ricerca partite", expanded=True):
                    st.write(f"League ID: `{league_id}` | Stagione: `{league_season}`")
                    for d in diag:
                        st.caption(d)
                    if response and response.get("_storico"):
                        st.info("\U0001f4da Modalita' STORICO: mostro partite gia' giocate di questa stagione (con risultato finale). Le previsioni potrebbero non essere disponibili su gare concluse.")

                if response and len(response.get("response", [])) > 0:
                    for match in response["response"]:
                        fix_id = match["fixture"]["id"]
                        home = match["teams"]["home"]["name"]
                        away = match["teams"]["away"]["name"]
                        url_pred = f"https://v3.football.api-sports.io/predictions?fixture={fix_id}"
                        pred_data = requests.get(url_pred, headers=headers).json()
                        if "response" in pred_data and len(pred_data["response"]) > 0:
                            blocco = pred_data["response"][0]
                            pred = blocco["predictions"]
                            p = pred["percent"]
                            st.divider()
                            st.subheader(f"\u26bd {home} vs {away}")

                            # --- Probabilita' 1X2 ---
                            col1, col2, col3 = st.columns(3)
                            col1.metric("\U0001f3e0 Vittoria Casa", p['home'])
                            col2.metric("\U0001f91d Pareggio", p['draw'])
                            col3.metric("\u2708\ufe0f Vittoria Ospite", p['away'])

                            q_h = percentuale_a_quota(p['home'])
                            q_d = percentuale_a_quota(p['draw'])
                            q_a = percentuale_a_quota(p['away'])
                            if q_h and q_d and q_a:
                                prob_1 = int(p['home'].replace('%',''))
                                prob_x = int(p['draw'].replace('%',''))
                                prob_2 = int(p['away'].replace('%',''))
                                probs = {
                                    f"1 ({home})": prob_1,
                                    "X (Pareggio)": prob_x,
                                    f"2 ({away})": prob_2
                                }
                                consiglio = max(probs, key=probs.get)
                                prob_max = probs[consiglio]

                                # --- Tabella completa 1X2 ---
                                st.markdown("##### \U0001f4ca Riepilogo Quote Equa e Probabilita'")
                                esiti = [
                                    ("1", f"\U0001f3e0 {home}", prob_1, q_h),
                                    ("X", "\U0001f91d Pareggio",  prob_x, q_d),
                                    ("2", f"\u2708\ufe0f {away}",  prob_2, q_a),
                                ]
                                for segno, label, perc, quota in esiti:
                                    # Calcola percentuale implicita nella quota equa (= 100/quota)
                                    perc_quota = round(100 / quota, 1) if quota else 0
                                    riga = (
                                        f"**`{segno}`** &nbsp; {label} &nbsp;&mdash;&nbsp; "
                                        f"Prob. stimata: **{perc}%** &nbsp;|&nbsp; "
                                        f"Quota equa: **{quota}** *(= {perc_quota}%)*"
                                    )
                                    # Evidenzia l'esito consigliato con colore diverso
                                    chiave = f"{segno} ({home})" if segno == "1" else ("X (Pareggio)" if segno == "X" else f"2 ({away})")
                                    if chiave == consiglio:
                                        st.success(f"\u2B50 {riga}")
                                    else:
                                        st.info(riga)

                                # --- Consiglio finale ---
                                st.markdown("---")
                                if prob_max >= 55:
                                    st.success(f"\u2705 **Consiglio Statistico:** Punta su **{consiglio}** ({prob_max}% di probabilita')")
                                elif prob_max >= 40:
                                    st.warning(f"\u26a0\ufe0f **Consiglio Statistico:** Esito piu' probabile **{consiglio}** ({prob_max}%) - partita equilibrata, gioca con cautela")
                                else:
                                    st.error(f"\u274c **Nessun consiglio** - partita troppo incerta (max {prob_max}%)")

                            # --- Consiglio e vincitore secondo l'API ---
                            advice = pred.get("advice")
                            winner = pred.get("winner", {})
                            colw1, colw2 = st.columns(2)
                            with colw1:
                                if winner and winner.get("name"):
                                    commento = winner.get("comment") or ""
                                    st.markdown(f"\U0001f3c6 **Pronostico API:** {winner['name']}" + (f" _{commento}_" if commento else ""))
                            with colw2:
                                wod = pred.get("win_or_draw")
                                if wod is not None:
                                    st.markdown(f"\U0001f6e1\ufe0f **Win or Draw:** {'Si' if wod else 'No'}")
                            if advice:
                                st.markdown(f"\U0001f4a1 **Consiglio API:** `{advice}`")

                            # --- Gol attesi e Under/Over ---
                            goals = pred.get("goals", {})
                            uo = pred.get("under_over")
                            gh = goals.get("home")
                            ga = goals.get("away")
                            riga_gol = []
                            if gh is not None:
                                riga_gol.append(f"Casa attesi: `{gh}`")
                            if ga is not None:
                                riga_gol.append(f"Ospite attesi: `{ga}`")
                            if uo:
                                riga_gol.append(f"Linea goal: `{uo}`")
                            if riga_gol:
                                st.caption("\u26bd Gol attesi \u2192 " + " | ".join(riga_gol))

                            # --- Confronto squadre (comparison) ---
                            comp = blocco.get("comparison", {})
                            if comp:
                                with st.expander("\U0001f4c8 Confronto dettagliato squadre"):
                                    st.caption("Valori in % \u2014 quanto ogni squadra 'pesa' su ciascun fattore secondo il modello (casa vs ospite).")
                                    voci = {
                                        "form": "Forma", "att": "Attacco", "def": "Difesa",
                                        "poisson_distribution": "Distribuzione Poisson",
                                        "h2h": "Scontri diretti", "goals": "Gol", "total": "Totale"
                                    }
                                    for chiave, etichetta in voci.items():
                                        if chiave in comp and isinstance(comp[chiave], dict):
                                            ch = comp[chiave].get("home", "-")
                                            ca = comp[chiave].get("away", "-")
                                            st.markdown(f"**{etichetta}** \u2014 {home}: `{ch}` vs {away}: `{ca}`")

                            # --- Ultimi scontri diretti (h2h) ---
                            h2h = blocco.get("h2h", [])
                            if h2h:
                                with st.expander(f"\U0001f501 Ultimi scontri diretti ({min(len(h2h), 5)})"):
                                    for g in h2h[:5]:
                                        try:
                                            d = g["fixture"]["date"][:10]
                                            th = g["teams"]["home"]["name"]
                                            ta = g["teams"]["away"]["name"]
                                            gh_s = g["goals"]["home"]
                                            ga_s = g["goals"]["away"]
                                            st.markdown(f"`{d}` {th} **{gh_s}-{ga_s}** {ta}")
                                        except:
                                            continue
                else:
                    st.warning("Nessuna partita trovata con nessuno dei due metodi di ricerca. Apri la **Diagnostica** qui sopra per vedere i dettagli (stagione usata, errori API). Il campionato potrebbe essere davvero in pausa, oppure la stagione corrente registrata non ha partite imminenti.")
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
        st.caption("\U0001f4a1 Su piano gratuito la stagione corrente potrebbe essere bloccata. Per un test, prova una stagione passata (es. 2023): vedrai partite gia' giocate.")
        if st.button("\U0001f3d2 Avvia Analisi Hockey", type="primary"):
            try:
                API_KEY_H = st.secrets["API_HOCKEY_KEY"]
                headers_h = {"x-apisports-key": API_KEY_H}

                diag_h = []
                resp_games = None

                # Tentativo 1: next=5 (partite imminenti)
                url_g1 = f"https://v1.hockey.api-sports.io/games?league={league_id_h}&season={stagione}&next=5"
                rg1 = requests.get(url_g1, headers=headers_h).json()
                ng1 = len(rg1.get("response", [])) if isinstance(rg1, dict) else 0
                errg1 = rg1.get("errors") if isinstance(rg1, dict) else None
                diag_h.append(f"Tentativo 'next=5': {ng1} partite" + (f" | errori: {errg1}" if errg1 else ""))
                if ng1 > 0:
                    resp_games = rg1

                # Tentativo 2: stagione intera (test storico) - le piu' recenti per data
                storico_h = False
                if resp_games is None:
                    url_g2 = f"https://v1.hockey.api-sports.io/games?league={league_id_h}&season={stagione}"
                    rg2 = requests.get(url_g2, headers=headers_h).json()
                    lista_g2 = rg2.get("response", []) if isinstance(rg2, dict) else []
                    errg2 = rg2.get("errors") if isinstance(rg2, dict) else None
                    try:
                        lista_g2.sort(key=lambda g: g.get("date", ""), reverse=True)
                    except:
                        pass
                    diag_h.append(f"Tentativo 'stagione intera ({stagione})': {len(lista_g2)} partite" + (f" | errori: {errg2}" if errg2 else ""))
                    if lista_g2:
                        resp_games = {"response": lista_g2[:5]}
                        storico_h = True

                # Pannello diagnostico
                with st.expander("\U0001f527 Diagnostica ricerca partite (Hockey)", expanded=True):
                    st.write(f"League ID: `{league_id_h}` | Stagione: `{stagione}`")
                    for d in diag_h:
                        st.caption(d)
                    if storico_h:
                        st.info("\U0001f4da Modalita' STORICO: mostro partite gia' giocate (coi risultati).")

                if resp_games is None or len(resp_games.get("response", [])) == 0:
                    st.warning("\u26a0\ufe0f Nessuna partita trovata con nessun metodo. Apri la Diagnostica qui sopra per vedere gli errori dell'API (es. blocco stagione sul piano free).")
                else:
                    # Recupero classifica UNA volta sola per dare contesto di forza alle squadre.
                    # (1 sola chiamata extra per tutta la lega, non per partita.)
                    classifica = {}  # team_name -> dict con posizione, punti, ecc.
                    try:
                        url_stand = f"https://v1.hockey.api-sports.io/standings?league={league_id_h}&season={stagione}"
                        resp_stand = requests.get(url_stand, headers=headers_h).json()
                        if "response" in resp_stand and len(resp_stand["response"]) > 0:
                            # standings e' una lista di gruppi, ognuno lista di righe
                            for gruppo in resp_stand["response"]:
                                righe = gruppo if isinstance(gruppo, list) else [gruppo]
                                for r in righe:
                                    try:
                                        nome_team = r["team"]["name"]
                                        classifica[nome_team] = {
                                            "pos": r.get("position"),
                                            "punti": r.get("points"),
                                            "win": r.get("games", {}).get("win", {}).get("total"),
                                            "lose": r.get("games", {}).get("lose", {}).get("total"),
                                        }
                                    except:
                                        continue
                    except:
                        pass

                    for game in resp_games["response"]:
                        game_id = game["id"]
                        home = game["teams"]["home"]["name"]
                        away = game["teams"]["away"]["name"]
                        data_partita = game["date"][:10]
                        st.divider()
                        st.subheader(f"\U0001f3d2 {home} vs {away}")
                        st.caption(f"\U0001f4c5 Data: {data_partita}")

                        # Contesto classifica (se disponibile)
                        ch = classifica.get(home)
                        ca = classifica.get(away)
                        if ch or ca:
                            def fmt_classifica(c):
                                if not c:
                                    return "n/d"
                                parti = []
                                if c.get("pos") is not None: parti.append(f"{c['pos']}\u00b0")
                                if c.get("punti") is not None: parti.append(f"{c['punti']} pti")
                                if c.get("win") is not None and c.get("lose") is not None:
                                    parti.append(f"{c['win']}V-{c['lose']}P")
                                return " \u00b7 ".join(parti) if parti else "n/d"
                            st.caption(f"\U0001f4cb Classifica \u2192 {home}: {fmt_classifica(ch)} | {away}: {fmt_classifica(ca)}")

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
                                _fav_h = home if prob_h >= prob_a else away
                                for _team, _q_bk, _q_eq, _prob in [
                                    (home, q1, q_equa_h, prob_h),
                                    (away, q2, q_equa_a, prob_a),
                                ]:
                                    _riga_h = f"**{_team}** — Quota bookmaker: **{_q_bk}** *({_prob}%)* | Quota equa: **{_q_eq}**"
                                    if _team == _fav_h:
                                        st.success(f"⭐ 🏠 {_riga_h} ← favorito")
                                    else:
                                        st.info(f"✈️ {_riga_h}")
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
        tab1, tab2 = st.tabs(["\U0001f4ca Visione Statistica", "\U0001f9ee Sistemi"])
        with tab1:
            st.subheader("\U0001f522 Numeri Principali (1-42)")
            c1, c2, c3 = st.columns(3)
            with c1: st.success("\U0001f525 Freq"); st.write(f"`{frequenti}`")
            with c2: st.info("\U0001f9ca Freddi"); st.write(f"`{freddi}`")
            with c3: st.error("\u23f3 Ritardi"); st.write(f"`{ritardatari}`")
            st.divider()
            st.subheader("\U0001f340 Numeri Fortunati (1-6)")
            c4, c5, c6 = st.columns(3)
            with c4: st.success("\U0001f525 Freq"); st.write(f"`{l_freq}`")
            with c5: st.info("\U0001f9ca Freddi"); st.write(f"`{l_freddi}`")
            with c6: st.error("\u23f3 Ritardi"); st.write(f"`{l_rit}`")
            st.divider()
            if st.button("\U0001f3b2 Genera Schedina Pesata", use_container_width=True):
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

    # --- EUROMILLIONS ---
    elif opzione == "\U0001f1ea\U0001f1fa EuroMillions":
        st.title("\U0001f1ea\U0001f1fa EuroMillions")
        data_aggiornamento = "5 Giugno 2026"
        st.caption(f"\U0001f504 *Ultimo aggiornamento statistiche: **{data_aggiornamento}***")
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
        tab1, tab2 = st.tabs(["\U0001f4ca Visione Statistica", "\U0001f9ee Sistemi"])
        with tab1:
            st.subheader("\U0001f522 Numeri Principali (1-50)")
            c1, c2, c3 = st.columns(3)
            with c1: st.success("\U0001f525 Freq"); st.write(f"`{frequenti_eu}`")
            with c2: st.info("\U0001f9ca Freddi"); st.write(f"`{freddi_eu}`")
            with c3: st.error("\u23f3 Ritardi"); st.write(f"`{ritardatari_eu}`")
            st.divider()
            st.subheader("\u2b50 Stelle (1-12)")
            c4, c5, c6 = st.columns(3)
            with c4: st.success("\U0001f525 Freq"); st.write(f"`{s_freq}`")
            with c5: st.info("\U0001f9ca Fredde"); st.write(f"`{s_fredde}`")
            with c6: st.error("\u23f3 Ritardi"); st.write(f"`{s_rit}`")
            st.divider()
            if st.button("\U0001f3b2 Genera Schedina Pesata", use_container_width=True):
                comb = genera_pesata(range(1, 51), freddi_eu, ritardatari_eu, 5)
                stelle = genera_pesata(range(1, 13), s_fredde, s_rit, 2)
                st.success(f"Cinquina Strategica: **{comb}** | \u2b50 Stelle: **{stelle}**")
        with tab2:
            st.subheader("Sviluppo Sistemi")
            nums = st.multiselect("Scegli i tuoi numeri (6-11):", options=list(range(1, 51)))
            stars = st.multiselect("Scegli 2 Stelle:", options=list(range(1, 13)), max_selections=2, default=[3,8])
            if len(nums) >= 6 and len(stars) == 2:
                tutte = list(itertools.combinations(nums, 5))
                passo = max(1, len(tutte) // 6)
                for idx, c in enumerate(tutte[::passo][:20]):
                    st.info(f"Giocata {idx+1}: `{sorted(list(c))}` | Stelle: `{sorted(stars)}`")
