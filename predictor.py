#!/usr/bin/env python3
"""
World Cup Match Predictor - All 48 Teams
Run: python predictor.py
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import random
import json
import sys

# ---------- ALL 48 WORLD CUP TEAMS WITH STRENGTH RATINGS ----------
TEAM_STRENGTH = {
    # Top Tier (85-92)
    "Brazil": 92, "Argentina": 90, "France": 89, "Germany": 87,
    "England": 86, "Spain": 85, "Netherlands": 84, "Portugal": 83,
    "Croatia": 82, "Belgium": 81, "Italy": 80, "Uruguay": 79,
    
    # Second Tier (75-78)
    "Mexico": 78, "USA": 77, "Senegal": 76, "Japan": 75,
    "Morocco": 74, "Switzerland": 73, "Poland": 72, "Denmark": 71,
    "Colombia": 78, "Chile": 77, "Peru": 76, "Ecuador": 75,
    
    # Third Tier (68-74)
    "Sweden": 74, "Wales": 73, "Serbia": 72, "Nigeria": 71,
    "Cameroon": 70, "Ghana": 69, "Algeria": 68, "Egypt": 67,
    "Tunisia": 66, "Mali": 65, "Burkina Faso": 64, "South Africa": 63,
    
    # Fourth Tier (60-67)
    "South Korea": 67, "Australia": 66, "New Zealand": 65, "Canada": 64,
    "Costa Rica": 63, "Panama": 62, "Honduras": 61, "Jamaica": 60,
    "Saudi Arabia": 62, "Iran": 61, "Iraq": 60, "UAE": 59,
    
    # Lower Tier (50-59)
    "Scotland": 65, "Ireland": 64, "Norway": 63, "Turkey": 62,
    "Russia": 61, "Ukraine": 60, "Czech Republic": 59, "Austria": 58,
    "Greece": 57, "Romania": 56, "Bulgaria": 55, "Hungary": 54
}

# ---------- PREDICTION ENGINE ----------
def poisson_random(lambda_val):
    if lambda_val < 0.01:
        return 0
    L = pow(2.71828, -lambda_val)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1

def predict_match(team1, team2):
    base1 = TEAM_STRENGTH.get(team1, 80)
    base2 = TEAM_STRENGTH.get(team2, 80)
    
    # Random form factor (momentum)
    form1 = 0.85 + (random.random() * 0.45)
    form2 = 0.85 + (random.random() * 0.45)
    
    # Home advantage
    home_boost = 1.04
    
    # Effective strength
    effective1 = base1 * form1 * home_boost
    effective2 = base2 * form2
    
    # Chaos factor (unpredictability)
    chaos = 0.92 + (random.random() * 0.16)
    effective1 *= chaos
    effective2 *= (1.02 - (chaos - 0.92) * 0.5)
    
    # Expected goals
    avg_goals1 = max(0.2, (effective1 / 75) * 1.2)
    avg_goals2 = max(0.2, (effective2 / 75) * 1.2)
    
    # Generate goals
    goals1 = poisson_random(avg_goals1)
    goals2 = poisson_random(avg_goals2)
    
    # Cap at 7 goals (realistic)
    goals1 = min(goals1, 7)
    goals2 = min(goals2, 7)
    
    # Ensure excitement (no 0-0 draws)
    if goals1 == 0 and goals2 == 0 and random.random() < 0.25:
        if random.random() < 0.5:
            goals1 = 1
        else:
            goals2 = 1
    
    return goals1, goals2

# ---------- FULL HTML INTERFACE ----------
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚽ World Cup Match Predictor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, sans-serif; }
        body {
            background: linear-gradient(145deg, #0a1628, #1a2f3f);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 40px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 20px 60px rgba(0,0,0,0.6);
        }
        h1 {
            color: #f0f9ff;
            font-size: 2rem;
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 5px;
        }
        h1 span { color: #f5b042; }
        .subtitle {
            color: #8ab4d6;
            margin-bottom: 25px;
            padding-left: 20px;
            border-left: 3px solid #f5b042;
        }
        .match-area {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 25px;
            padding: 25px;
        }
        .team-selectors {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        .team-box {
            background: rgba(0,0,0,0.3);
            padding: 8px 15px 8px 10px;
            border-radius: 50px;
            display: flex;
            align-items: center;
            gap: 10px;
            border: 1px solid rgba(255,255,255,0.06);
            flex: 1 1 200px;
        }
        .team-box select {
            background: transparent;
            border: none;
            color: #e8f0f8;
            font-size: 1rem;
            padding: 8px 5px;
            width: 100%;
            cursor: pointer;
            outline: none;
        }
        .team-box select option {
            background: #1a2f3f;
            color: white;
        }
        .vs-badge {
            font-size: 1.5rem;
            font-weight: bold;
            color: #f5b042;
            padding: 0 10px;
        }
        .buttons {
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 10px 0 15px 0;
        }
        .btn-predict {
            background: linear-gradient(135deg, #f5b042, #e68a2e);
            border: none;
            padding: 12px 35px;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: bold;
            color: #0a1628;
            cursor: pointer;
            transition: 0.2s;
            display: flex;
            align-items: center;
            gap: 10px;
            border: 1px solid #ffd58c;
        }
        .btn-predict:hover { transform: scale(1.03); }
        .btn-reset {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 12px 25px;
            border-radius: 50px;
            color: #b6d4e8;
            cursor: pointer;
            transition: 0.2s;
        }
        .btn-reset:hover { background: rgba(255,70,70,0.15); border-color: #ff7a7a70; }
        .result-panel {
            background: rgba(0,0,0,0.3);
            border-radius: 20px;
            padding: 20px;
            margin-top: 15px;
            border-left: 5px solid #f5b042;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .result-text {
            color: #f0f9ff;
            font-size: 1.3rem;
            font-weight: 600;
        }
        .result-text i { color: #ffd966; margin-right: 10px; }
        .result-score {
            background: #0a1628;
            padding: 8px 30px;
            border-radius: 50px;
            font-size: 2rem;
            font-weight: bold;
            color: #f5b042;
            border: 1px solid #f5b04260;
        }
        .stats {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
            color: #8ab4d6;
            font-size: 0.9rem;
            border-top: 1px solid rgba(255,255,255,0.05);
            padding-top: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .stats i { color: #f5b042; margin-right: 5px; }
        .team-count {
            background: rgba(245, 176, 66, 0.15);
            padding: 2px 12px;
            border-radius: 20px;
            color: #f5b042;
        }
        @media (max-width: 600px) {
            .container { padding: 15px; }
            .team-box { flex: 1 1 100%; }
            .result-panel { flex-direction: column; align-items: stretch; text-align: center; }
            .result-score { text-align: center; }
        }
    </style>
</head>
<body>
<div class="container">
    <h1>⚽ World Cup <span>·</span> Predictor</h1>
    <div class="subtitle">
        <i>🐍</i> Python-powered simulation · Poisson-based goals · <span class="team-count">48 Teams</span>
    </div>

    <div class="match-area">
        <div class="team-selectors">
            <div class="team-box">
                <span>🏆</span>
                <select id="teamA">{team_options}</select>
            </div>
            <div class="vs-badge">VS</div>
            <div class="team-box">
                <span>🏆</span>
                <select id="teamB">{team_options}</select>
            </div>
        </div>

        <div class="buttons">
            <button class="btn-predict" id="predictBtn">⚡ Predict Match</button>
            <button class="btn-reset" id="resetBtn">⟳ Reset</button>
        </div>

        <div class="result-panel">
            <div class="result-text">
                <i>🏆</i> <span id="resultMessage">Select teams & predict</span>
            </div>
            <div class="result-score" id="resultScore">- : -</div>
        </div>

        <div class="stats">
            <span id="strengthA"><i>🛡️</i> Brazil · 92</span>
            <span id="strengthB"><i>🛡️</i> Argentina · 90</span>
            <span><i>📅</i> FIFA World Cup 2026</span>
        </div>
    </div>
</div>

<script>
    // Team strength data (from Python)
    const teamStrength = {team_strength};

    // DOM elements
    const teamA = document.getElementById('teamA');
    const teamB = document.getElementById('teamB');
    const predictBtn = document.getElementById('predictBtn');
    const resetBtn = document.getElementById('resetBtn');
    const resultMessage = document.getElementById('resultMessage');
    const resultScore = document.getElementById('resultScore');
    const strengthA = document.getElementById('strengthA');
    const strengthB = document.getElementById('strengthB');

    // Update strength display
    function updateStrength() {
        const a = teamA.value;
        const b = teamB.value;
        strengthA.innerHTML = `<i>🛡️</i> ${a} · ${teamStrength[a] || 80}`;
        strengthB.innerHTML = `<i>🛡️</i> ${b} · ${teamStrength[b] || 80}`;
    }

    // Run prediction via API
    async function predict() {
        const a = teamA.value;
        const b = teamB.value;

        if (a === b) {
            resultMessage.textContent = '⚠️ Same team selected!';
            resultScore.textContent = '— : —';
            return;
        }

        try {
            const res = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ team1: a, team2: b })
            });
            const data = await res.json();

            const g1 = data.goals1;
            const g2 = data.goals2;

            let msg = '';
            if (g1 > g2) msg = `🏆 ${a} wins!`;
            else if (g2 > g1) msg = `🏆 ${b} wins!`;
            else msg = `🤝 Draw!`;

            if (g1 + g2 >= 5) msg += ' 🔥 High scoring!';
            else if (g1 + g2 === 0) msg += ' 🧊 Defensive battle.';

            resultMessage.innerHTML = msg;
            resultScore.textContent = `${g1} : ${g2}`;
            updateStrength();
        } catch (e) {
            resultMessage.textContent = '⚠️ Error connecting to server';
        }
    }

    // Reset to default
    function resetDefault() {
        teamA.value = 'Brazil';
        teamB.value = 'Argentina';
        updateStrength();
        predict();
    }

    // Events
    predictBtn.addEventListener('click', predict);
    resetBtn.addEventListener('click', resetDefault);
    teamA.addEventListener('change', updateStrength);
    teamB.addEventListener('change', updateStrength);

    // Init
    window.onload = function() {
        teamA.value = 'Brazil';
        teamB.value = 'Argentina';
        updateStrength();
        predict();
    };
</script>
</body>
</html>'''

# ---------- HTTP SERVER ----------
class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Build options for dropdowns
            options = ''.join([f'<option value="{t}">{t}</option>' for t in sorted(TEAM_STRENGTH.keys())])
            
            # Insert data into template
            html = HTML_TEMPLATE.replace('{team_options}', options)
            html = html.replace('{team_strength}', json.dumps(TEAM_STRENGTH))
            
            self.wfile.write(html.encode('utf-8'))
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/predict':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            g1, g2 = predict_match(data['team1'], data['team2'])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'goals1': g1, 'goals2': g2}).encode())
        else:
            self.send_response(404)
            self.end_headers()

# ---------- RUN SERVER ----------
def run_server(port=8000):
    print(f"\n⚽ World Cup Predictor - 48 Teams")
    print(f"   Server: http://localhost:{port}")
    print(f"   Press Ctrl+C to stop\n")
    
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()
    HTTPServer(('', port), CustomHandler).serve_forever()

if __name__ == '__main__':
    run_server()
