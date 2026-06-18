#!/usr/bin/env python3
"""
World Cup Match Predictor - Python/HTML Hybrid
Run this script, then open http://localhost:8000 in your browser.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import random
import json
import os
import sys

# ---------- TEAM STRENGTH DATABASE ----------
TEAM_STRENGTH = {
    "Brazil": 92,
    "Argentina": 90,
    "France": 89,
    "Germany": 87,
    "England": 86,
    "Spain": 85,
    "Netherlands": 84,
    "Portugal": 83,
    "Croatia": 82,
    "Belgium": 81,
    "Italy": 80,
    "Uruguay": 79,
    "Mexico": 78,
    "USA": 77,
    "Senegal": 76,
    "Japan": 75,
    "Morocco": 74,
    "Switzerland": 73,
    "Poland": 72,
    "Denmark": 71
}

# ---------- PREDICTION ENGINE (Python) ----------
def poisson_random(lambda_val):
    """Generate a Poisson-distributed random integer (Knuth's algorithm)."""
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
    """Simulate a match and return goals for each team."""
    base1 = TEAM_STRENGTH.get(team1, 80)
    base2 = TEAM_STRENGTH.get(team2, 80)
    
    # Form factor (random momentum)
    form1 = 0.85 + (random.random() * 0.45)
    form2 = 0.85 + (random.random() * 0.45)
    
    # Home advantage for team1
    home_boost = 1.04
    
    # Effective strength
    effective1 = base1 * form1 * home_boost
    effective2 = base2 * form2
    
    # Chaos factor
    chaos = 0.92 + (random.random() * 0.16)
    effective1 *= chaos
    effective2 *= (1.02 - (chaos - 0.92) * 0.5)
    
    # Expected goals
    avg_goals1 = max(0.2, (effective1 / 75) * 1.2)
    avg_goals2 = max(0.2, (effective2 / 75) * 1.2)
    
    goals1 = poisson_random(avg_goals1)
    goals2 = poisson_random(avg_goals2)
    
    goals1 = min(goals1, 7)
    goals2 = min(goals2, 7)
    
    # Ensure some excitement
    if goals1 == 0 and goals2 == 0 and random.random() < 0.25:
        if random.random() < 0.5:
            goals1 = 1
        else:
            goals2 = 1
    
    return goals1, goals2

# ---------- HTML TEMPLATE (embedded) ----------
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚽ World Cup Match Predictor</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Roboto, sans-serif; }
        body {
            background: linear-gradient(145deg, #0b1a2e 0%, #1a2f3f 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1.5rem;
        }
        .card {
            max-width: 1000px;
            width: 100%;
            background: rgba(255, 255, 255, 0.07);
            backdrop-filter: blur(12px);
            border-radius: 56px;
            padding: 2rem 2.5rem;
            box-shadow: 0 30px 50px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.06);
        }
        h1 {
            font-size: 2.4rem;
            font-weight: 600;
            color: #f0f9ff;
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 0.25rem;
        }
        h1 i { color: #ffd966; font-size: 2.2rem; filter: drop-shadow(0 0 6px #ffb34780); }
        .subhead {
            color: #a0c4e2;
            font-weight: 400;
            font-size: 1rem;
            margin-bottom: 2rem;
            border-left: 4px solid #f5b042;
            padding-left: 18px;
            background: rgba(255, 215, 100, 0.06);
            border-radius: 0 12px 12px 0;
        }
        .match-area {
            background: rgba(12, 28, 40, 0.6);
            border-radius: 40px;
            padding: 1.8rem 2rem;
            box-shadow: inset 0 6px 12px rgba(0,0,0,0.4), 0 10px 20px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.03);
        }
        .team-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
            gap: 0.8rem 1.2rem;
            margin-bottom: 1.8rem;
        }
        .team-box {
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(0,0,0,0.25);
            padding: 0.5rem 1.2rem 0.5rem 0.8rem;
            border-radius: 60px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            flex: 1 1 180px;
        }
        .team-box:hover { background: rgba(255,255,255,0.06); border-color: #f5b04260; }
        .team-box i { font-size: 2rem; width: 40px; text-align: center; color: #e0edf5; }
        .team-box select {
            background: transparent;
            border: none;
            color: #f0f9ff;
            font-size: 1.1rem;
            font-weight: 500;
            padding: 0.4rem 0.2rem;
            width: 130px;
            cursor: pointer;
            outline: none;
            border-bottom: 2px solid transparent;
        }
        .team-box select:focus { border-bottom-color: #f5b042; }
        .team-box select option { background: #1a2f3f; color: #fff; }
        .vs-badge {
            font-size: 1.4rem;
            font-weight: 700;
            color: #f5b042;
            background: rgba(0,0,0,0.3);
            padding: 0.1rem 0.8rem;
            border-radius: 40px;
            letter-spacing: 2px;
        }
        .predict-btn {
            background: linear-gradient(135deg, #f5b042, #e68a2e);
            border: none;
            padding: 0.9rem 2.6rem;
            border-radius: 60px;
            font-weight: 700;
            font-size: 1.3rem;
            color: #0b1a2e;
            display: inline-flex;
            align-items: center;
            gap: 14px;
            box-shadow: 0 8px 18px rgba(245,176,66,0.3);
            cursor: pointer;
            transition: 0.15s;
            border: 1px solid #ffd58c;
            margin: 0.5rem 0 1rem 0;
        }
        .predict-btn:hover {
            transform: scale(1.02);
            background: linear-gradient(135deg, #ffc064, #f0943a);
            box-shadow: 0 10px 28px #f5b04270;
        }
        .predict-btn:active { transform: scale(0.96); }
        .result-panel {
            background: rgba(0,0,0,0.3);
            border-radius: 32px;
            padding: 1.2rem 1.8rem;
            margin-top: 1.8rem;
            border-left: 6px solid #f5b042;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
        }
        .result-text {
            font-size: 1.6rem;
            font-weight: 600;
            color: #f5f9ff;
            display: flex;
            align-items: center;
            gap: 14px;
            flex-wrap: wrap;
        }
        .result-text i { color: #ffd966; font-size: 2rem; }
        .result-score {
            background: #0b1a2e;
            padding: 0.4rem 1.6rem;
            border-radius: 60px;
            font-size: 2rem;
            font-weight: 700;
            color: #f5b042;
            letter-spacing: 1px;
            border: 1px solid #f5b04270;
        }
        .reset-btn {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.1);
            color: #b6d4e8;
            padding: 0.5rem 1.4rem;
            border-radius: 40px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: 0.2s;
        }
        .reset-btn:hover {
            background: rgba(255,70,70,0.15);
            border-color: #ff7a7a70;
            color: #ffbaba;
        }
        .match-stats {
            display: flex;
            justify-content: space-between;
            margin-top: 1.2rem;
            font-size: 0.9rem;
            color: #9bb7d0;
            border-top: 1px solid #ffffff10;
            padding-top: 1rem;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .match-stats span i { margin-right: 6px; color: #f5b042; }
        .footer {
            margin-top: 1.5rem;
            text-align: right;
            color: #6f8fa5;
            font-size: 0.8rem;
        }
        .python-badge {
            display: inline-block;
            background: #306998;
            color: #fff;
            padding: 0.1rem 0.9rem;
            border-radius: 30px;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-left: 8px;
        }
        @media (max-width: 640px) {
            .card { padding: 1.5rem; }
            .team-row { flex-direction: column; }
            .team-box { width: 100%; }
            .vs-badge { margin: 0.2rem 0; }
            .result-panel { flex-direction: column; align-items: stretch; }
            .result-text { font-size: 1.3rem; }
        }
    </style>
</head>
<body>
<div class="card">
    <h1><i class="fas fa-futbol"></i> World Cup · Predictor <span class="python-badge">🐍 Python</span></h1>
    <div class="subhead">
        <i class="fas fa-robot" style="margin-right: 10px;"></i> Python-powered simulation · Poisson-based goals
    </div>

    <div class="match-area">
        <div class="team-row">
            <div class="team-box">
                <i class="fas fa-flag"></i>
                <select id="teamA">
                    {team_options}
                </select>
            </div>
            <div class="vs-badge">VS</div>
            <div class="team-box">
                <i class="fas fa-flag"></i>
                <select id="teamB">
                    {team_options}
                </select>
            </div>
        </div>

        <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; justify-content: center;">
            <button class="predict-btn" id="predictBtn"><i class="fas fa-brain"></i> Predict match</button>
            <button class="reset-btn" id="resetBtn"><i class="fas fa-undo-alt"></i> Reset</button>
        </div>

        <div class="result-panel" id="resultPanel">
            <div class="result-text">
                <i class="fas fa-trophy"></i>
                <span id="resultMessage">⚡ Select teams & predict</span>
            </div>
            <div class="result-score" id="resultScore">- : -</div>
        </div>

        <div class="match-stats">
            <span id="strengthA"><i class="fas fa-shield-alt"></i> Brazil · 92</span>
            <span id="strengthB"><i class="fas fa-shield-alt"></i> Argentina · 90</span>
            <span><i class="fas fa-calendar-alt"></i> FIFA World Cup · 2026</span>
        </div>
    </div>
    <div class="footer">
        <i class="fas fa-microchip"></i> Python backend · {team_count} teams · Poisson distribution
    </div>
</div>

<script>
    (function() {{
        // ---------- TEAM DATA (injected from Python) ----------
        const teamStrength = {team_strength_json};
        const teamNames = Object.keys(teamStrength);

        // DOM refs
        const teamASelect = document.getElementById('teamA');
        const teamBSelect = document.getElementById('teamB');
        const predictBtn = document.getElementById('predictBtn');
        const resetBtn = document.getElementById('resetBtn');
        const resultMessage = document.getElementById('resultMessage');
        const resultScore = document.getElementById('resultScore');
        const strengthASpan = document.getElementById('strengthA');
        const strengthBSpan = document.getElementById('strengthB');

        function updateStrengthDisplay() {{
            const teamA = teamASelect.value;
            const teamB = teamBSelect.value;
            const sA = teamStrength[teamA] || 80;
            const sB = teamStrength[teamB] || 80;
            strengthASpan.innerHTML = `<i class="fas fa-shield-alt"></i> ${{teamA}} · ${{sA}}`;
            strengthBSpan.innerHTML = `<i class="fas fa-shield-alt"></i> ${{teamB}} · ${{sB}}`;
        }}

        // ---------- Call Python backend via fetch ----------
        async function runPrediction() {{
            const teamA = teamASelect.value;
            const teamB = teamBSelect.value;

            if (teamA === teamB) {{
                resultMessage.innerHTML = `⚠️ Same team selected — choose different opponents`;
                resultScore.textContent = `— : —`;
                return;
            }}

            try {{
                const response = await fetch('/predict', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ team1: teamA, team2: teamB }})
                }});
                const data = await response.json();

                const g1 = data.goals1;
                const g2 = data.goals2;

                let message = '';
                if (g1 > g2) message = `🏆 ${{teamA}} wins!`;
                else if (g2 > g1) message = `🏆 ${{teamB}} wins!`;
                else message = `🤝 Draw! (${{g1}} - ${{g2}})`;

                if (g1 + g2 >= 5) message += ` 🔥 High scoring!`;
                else if (g1 + g2 === 0) message += ` 🧊 Defensive battle.`;

                resultMessage.innerHTML = `<i class="fas fa-futbol" style="margin-right: 8px;"></i> ${{message}}`;
                resultScore.textContent = `${{g1}} : ${{g2}}`;
                updateStrengthDisplay();
            }} catch (err) {{
                resultMessage.innerHTML = `⚠️ Error contacting Python backend`;
                console.error(err);
            }}
        }}

        // ---------- Reset ----------
        function resetToDefault() {{
            teamASelect.value = 'Brazil';
            teamBSelect.value = 'Argentina';
            updateStrengthDisplay();
            runPrediction();
        }}

        // ---------- Events ----------
        predictBtn.addEventListener('click', runPrediction);
        resetBtn.addEventListener('click', resetToDefault);
        teamASelect.addEventListener('change', updateStrengthDisplay);
        teamBSelect.addEventListener('change', updateStrengthDisplay);

        // ---------- Init ----------
        window.addEventListener('DOMContentLoaded', function() {{
            teamASelect.value = 'Brazil';
            teamBSelect.value = 'Argentina';
            updateStrengthDisplay();
            runPrediction();
        }});
    }})();
</script>
</body>
</html>
'''

# ---------- CUSTOM HTTP REQUEST HANDLER ----------
class PredictHandler(SimpleHTTPRequestHandler):
    """Handle GET requests for the HTML page and POST requests for predictions."""
    
    def do_GET(self):
        """Serve the HTML page."""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Build HTML with team options and strength data
            team_options = ''
            for team in sorted(TEAM_STRENGTH.keys()):
                selected_a = 'selected' if team == 'Brazil' else ''
                selected_b = 'selected' if team == 'Argentina' else ''
                # We need two separate option lists for each select
                # Actually we'll generate one generic list and use it twice
                team_options += f'<option value="{team}">{team}</option>\n'
            
            # For team A, Brazil selected; for team B, Argentina selected
            # We'll use a different approach: build with selected attributes
            options_a = ''
            options_b = ''
            for team in sorted(TEAM_STRENGTH.keys()):
                sel_a = 'selected' if team == 'Brazil' else ''
                sel_b = 'selected' if team == 'Argentina' else ''
                options_a += f'<option value="{team}" {sel_a}>{team}</option>\n'
                options_b += f'<option value="{team}" {sel_b}>{team}</option>\n'
            
            # Replace placeholders
            html = HTML_TEMPLATE
            html = html.replace('{team_options}', options_a)  # will be replaced twice
            # Better: use two separate placeholders
            html = html.replace('<!-- team_options_A -->', options_a)
            html = html.replace('<!-- team_options_B -->', options_b)
            # But our template uses {team_options} twice. Let's just use one replacement.
            # Actually we need two different selects with different defaults.
            # We'll use a simpler approach: generate two separate option lists.
            # Let's rewrite the template to use {team_options_a} and {team_options_b}
            # Since we already have the HTML, we'll do a string replace with two placeholders.
            
            # We'll rebuild the HTML with two placeholders
            # For simplicity, let's just use the same options and set defaults via JavaScript
            # But we want Brazil in teamA and Argentina in teamB by default.
            # We'll use JavaScript to set defaults after load.
            # So we can just use one option list.
            html_final = HTML_TEMPLATE.replace('{team_options}', options_a)
            # Also replace team_count
            html_final = html_final.replace('{team_count}', str(len(TEAM_STRENGTH)))
            html_final = html_final.replace('{team_strength_json}', json.dumps(TEAM_STRENGTH))
            
            self.wfile.write(html_final.encode('utf-8'))
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests for predictions."""
        if self.path == '/predict':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                team1 = data.get('team1', 'Brazil')
                team2 = data.get('team2', 'Argentina')
                
                goals1, goals2 = predict_match(team1, team2)
                
                response = {
                    'goals1': goals1,
                    'goals2': goals2,
                    'team1': team1,
                    'team2': team2
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

# ---------- SERVER LAUNCH ----------
def run_server(port=8000):
    """Start the HTTP server and open a browser."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, PredictHandler)
    
    url = f'http://localhost:{port}'
    print(f"\n⚽ World Cup Match Predictor")
    print(f"   Server running at {url}")
    print(f"   Press Ctrl+C to stop\n")
    
    # Open browser after a short delay
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
        httpd.shutdown()

if __name__ == '__main__':
    # Use a default port, allow override via command line
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Usage: python {sys.argv[0]} [port]")
            sys.exit(1)
    
    run_server(port)
