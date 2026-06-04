import requests
import streamlit as st  # <--- NUOVO: Gestisce l'interfaccia grafica

# Configurazione grafica della pagina per il telefono
st.set_page_config(page_title="Sporttip Scanner", page_icon="📊", layout="centered")

st.title("🛰️ Scanner Autonomo Sporttip")
st.write("Schiaccia il bottone sotto per scansionare il palinsesto in tempo reale.")

# Creiamo un bottone interattivo sullo schermo del telefono
if st.button("🔄 Avvia Scansione Palinsesto"):
    
    with st.spinner("Connessione ai server delle quote in corso..."):
        # L'applicazione cercherà la chiave nella cassaforte privata di Streamlit
        API_KEY = st.secrets["MY_API_KEY"]
        URL = f"https://api.the-odds-api.com/v4/sports/soccer_uefa_champs_league/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
        
        try:
            risposta = requests.get(URL)
            partite = risposta.json()
            partite_valide = []
            
            for partita in partite:
                home_team = partita['home_team']
                away_team = partita['away_team']
                match_name = f"{home_team} - {away_team}"
                
                if not partita['bookmakers']: continue
                bookmaker = partita['bookmakers'][0]
                markets = bookmaker['markets']
                
                for market in markets:
                    if market['key'] == 'h2h':
                        q1, qX, q2 = None, None, None
                        for outcome in market['outcomes']:
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

            # Mostriamo i risultati graficamente sullo smartphone
            if len(partite_valide) >= 3:
                st.success(f"✅ Scansione completata! Trovate {len(partite_valide)} quote idonee.")
                
                st.markdown("### 🚀 **SISTEMA MATEMATICO CONSIGLIATO**")
                for i in range(3):
                    p = partite_valide[i]
                    st.info(f"**{i+1}️⃣ {p['match']}**\n\nEsito: `{p['segno']}` | Quota: `{p['quota']}`")
                
                q1, q2, q3 = partite_valide[0]['quota'], partite_valide[1]['quota'], partite_valide[2]['quota']
                vincita_max = ((q1*q2) + (q1*q3) + (q2*q3)) * 5.0
                
                st.markdown("#### 📊 **Dettagli Schedina Sporttip:**")
                st.write("• **Tipo:** Sistema 2 su 3")
                st.write("• **Budget:** 15.00 CHF (5.00 CHF a colonna)")
                st.metric(label="Vincita Massima Potenziale", value=f"{vincita_max:.2f} CHF", delta=f"+{vincita_max-15.00:.2f} CHF Netti")
            else:
                st.warning("❌ Nessun match soddisfa i requisiti di sicurezza in questo momento.")
                
        except Exception as e:
            st.error(f"⚠️ Errore di lettura dati: {e}")
