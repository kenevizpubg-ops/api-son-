from flask import Flask, request, jsonify, render_template_string, session
import requests
import json
import base64
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "keneviz_secret_key_2026"

ADMIN_KEY = "devkeneviz"

if not os.path.exists('data'):
    os.makedirs('data')

def load_counter():
    try:
        with open('data/counter.json', 'r') as f:
            return json.load(f)
    except:
        return {"visitors": 0, "api_usage": {}}

def save_counter(data):
    with open('data/counter.json', 'w') as f:
        json.dump(data, f)

def load_messages():
    try:
        with open('data/messages.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_messages(messages):
    with open('data/messages.json', 'w') as f:
        json.dump(messages, f)

counter_data = load_counter()
messages_data = load_messages()

APIS_DB = {
    1001: {
        "name": "Görsel Üret",
        "endpoint": "https://kenevizimagegenerate.vercel.app/api/generate",
        "params": {"prompt": ""},
        "method": "GET",
        "desc": "Yapay zeka ile görsel oluştur",
        "response_type": "image"
    },
    1002: {
        "name": "Ses Sentez",
        "endpoint": "https://kenevizttsapi.vercel.app/api/tts",
        "params": {"text": "", "lang": "tr"},
        "method": "GET",
        "desc": "Metni sese dönüştür",
        "response_type": "audio"
    },
    1003: {
        "name": "GSM İsim Sorgu",
        "endpoint": "https://kenevizglobalgsm-nameapi.vercel.app/api/gsm-name",
        "params": {"number": ""},
        "method": "GET",
        "desc": "Telefon numarası sahibini sorgula",
        "response_type": "json"
    },
    1004: {
        "name": "Tabii Checker",
        "endpoint": "https://keneviztabiicheckerapi.vercel.app/tabiicheck",
        "params": {"login": ""},
        "method": "GET",
        "desc": "Hesap doğrulama kontrolü",
        "response_type": "json"
    },
    1005: {
        "name": "Ayak Sorgu",
        "endpoint": "https://kenevizayaksorguapi.vercel.app/api/sorgula",
        "params": {"tgnick": "", "yas": ""},
        "method": "GET",
        "desc": "Kullanıcı bilgisi sorgula",
        "response_type": "json"
    },
    1006: {
        "name": "URL IP Çek",
        "endpoint": "https://kenevizurlipcekiciapi.vercel.app/urlipcek",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Domain IP adresini bul",
        "response_type": "json"
    },
    1007: {
        "name": "BIN Sorgu",
        "endpoint": "https://kenevizbinsorguapi.vercel.app/binsorgu",
        "params": {"bin": ""},
        "method": "GET",
        "desc": "Kart BIN sorgulama",
        "response_type": "json"
    },
    1008: {
        "name": "Index Çek",
        "endpoint": "https://kenevizindexcekenapi.vercel.app/index",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Site kaynak kodunu al",
        "response_type": "text"
    },
    1009: {
        "name": "Web MS Analiz",
        "endpoint": "https://kenevizwebmsapi.vercel.app/analyze",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Web sitesi performans analizi",
        "response_type": "json"
    }
}

def generate_api_id():
    new_id = random.randint(1000, 9999)
    while new_id in APIS_DB:
        new_id = random.randint(1000, 9999)
    return new_id

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔮 KENEVIZ API PORTAL</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: #0a0a0a;
            font-family: 'Courier New', 'Share Tech Mono', monospace;
            min-height: 100vh;
            padding: 20px;
            position: relative;
        }
        
        body::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(0deg, rgba(0,255,0,0.03) 0px, rgba(0,255,0,0.03) 2px, transparent 2px, transparent 6px);
            pointer-events: none;
            z-index: 0;
        }
        
        .container { max-width: 1400px; margin: 0 auto; position: relative; z-index: 1; }
        
        .terminal-header {
            background: #000;
            border: 2px solid #0f0;
            border-radius: 10px 10px 0 0;
            padding: 12px 20px;
        }
        
        .terminal-buttons {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #ff5f56;
            border-radius: 50%;
            margin-right: 8px;
            box-shadow: 0 0 5px #ff5f56;
        }
        
        .terminal-buttons:nth-child(2) { background: #ffbd2e; box-shadow: 0 0 5px #ffbd2e; }
        .terminal-buttons:nth-child(3) { background: #27c93f; box-shadow: 0 0 5px #27c93f; }
        .terminal-title { color: #0f0; font-size: 14px; margin-left: 10px; }
        
        .header {
            background: linear-gradient(135deg, #000 0%, #0a2a0a 100%);
            border: 2px solid #0f0;
            border-top: none;
            border-radius: 0 0 10px 10px;
            text-align: center;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 0 20px rgba(0,255,0,0.2);
        }
        
        .header h1 {
            font-size: 2.5em;
            color: #0f0;
            text-shadow: 0 0 10px #0f0;
            letter-spacing: 3px;
        }
        
        .dev-tag {
            color: #0f0;
            font-size: 0.8em;
            margin-top: 10px;
            opacity: 0.7;
        }
        
        .stats-bar {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .stat-card {
            background: #000;
            border: 1px solid #0f0;
            border-radius: 10px;
            padding: 15px 25px;
            flex: 1;
            text-align: center;
            box-shadow: 0 0 10px rgba(0,255,0,0.1);
        }
        
        .stat-card h3 { color: #0f0; font-size: 0.8em; margin-bottom: 5px; }
        .stat-card .number { color: #0f0; font-size: 2em; font-weight: bold; text-shadow: 0 0 5px #0f0; }
        
        .support-section {
            background: #000;
            border: 1px solid #0f0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .support-section h3 { color: #0f0; margin-bottom: 15px; }
        .support-section input, .support-section textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            background: #111;
            border: 1px solid #0f0;
            border-radius: 5px;
            color: #0f0;
            font-family: monospace;
        }
        .support-section button {
            background: #000;
            color: #0f0;
            border: 1px solid #0f0;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .support-section button:hover { background: #0f0; color: #000; }
        
        .message-item {
            background: #111;
            border-left: 3px solid #0f0;
            padding: 10px;
            margin-bottom: 10px;
            font-size: 0.8em;
        }
        .message-name { color: #0f0; font-weight: bold; }
        .message-text { color: #888; margin-top: 5px; }
        .message-date { color: #555; font-size: 0.7em; margin-top: 5px; }
        
        .admin-panel {
            background: #000;
            border: 1px solid #0f0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .admin-toggle {
            background: #000;
            color: #0f0;
            border: 1px solid #0f0;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .admin-toggle:hover { background: #0f0; color: #000; }
        
        .admin-content { display: none; margin-top: 20px; }
        .admin-content.show { display: block; }
        
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 25px;
            margin-top: 20px;
        }
        
        .api-card {
            background: #0a0a0a;
            border: 1px solid #0f0;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s;
        }
        
        .api-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 20px rgba(0,255,0,0.3);
            border-color: #0f0;
        }
        
        .api-card h3 { color: #0f0; margin-bottom: 10px; font-size: 1.2em; }
        .api-id { background: #0f0; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.7em; margin-left: 10px; }
        .api-endpoint { color: #888; font-size: 0.65em; word-break: break-all; background: #111; padding: 5px; border-radius: 5px; margin-bottom: 10px; }
        .api-desc { color: #0f0; font-size: 0.8em; margin-bottom: 15px; opacity: 0.8; }
        .api-stats { color: #555; font-size: 0.65em; margin-bottom: 10px; }
        
        .param-input { margin-bottom: 10px; }
        .param-input label { display: block; font-size: 0.7em; color: #0f0; margin-bottom: 3px; }
        .param-input input {
            width: 100%;
            padding: 8px;
            background: #111;
            border: 1px solid #333;
            border-radius: 5px;
            color: #0f0;
            font-family: monospace;
        }
        .param-input input:focus { outline: none; border-color: #0f0; }
        
        .button-group { display: flex; gap: 10px; margin-top: 15px; }
        .query-btn {
            flex: 2;
            background: #000;
            color: #0f0;
            border: 1px solid #0f0;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
            font-family: monospace;
        }
        .url-btn {
            flex: 1;
            background: #000;
            color: #0ff;
            border: 1px solid #0ff;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
            font-family: monospace;
        }
        .query-btn:hover { background: #0f0; color: #000; }
        .url-btn:hover { background: #0ff; color: #000; }
        
        .result {
            margin-top: 15px;
            padding: 12px;
            background: #000;
            border: 1px solid #0f0;
            border-radius: 5px;
            max-height: 300px;
            overflow-y: auto;
            display: none;
        }
        .result.show { display: block; }
        .result pre { color: #0f0; font-size: 0.75em; white-space: pre-wrap; font-family: monospace; }
        .result-image { max-width: 100%; border-radius: 5px; }
        .result-audio { width: 100%; }
        
        .loading {
            text-align: center;
            padding: 10px;
            display: none;
            color: #0f0;
        }
        .loading.show { display: block; }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #0f0;
            opacity: 0.6;
            font-size: 0.7em;
            border-top: 1px solid #0f0;
        }
        
        hr { border-color: #0f0; margin: 15px 0; }
        
        ::-webkit-scrollbar { width: 8px; background: #000; }
        ::-webkit-scrollbar-thumb { background: #0f0; border-radius: 4px; }
        
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #0f0; }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 10px;
            background: #111;
            border: 1px solid #0f0;
            border-radius: 5px;
            color: #0f0;
        }
        
        .hidden-admin {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            background: transparent;
            cursor: pointer;
            opacity: 0.2;
        }
        
        .admin-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .admin-modal.show { display: flex; }
        .admin-modal-content {
            background: #0a0a0a;
            border: 2px solid #0f0;
            border-radius: 10px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        .admin-modal-content h3 { color: #0f0; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="terminal-header">
            <span class="terminal-buttons"></span>
            <span class="terminal-buttons"></span>
            <span class="terminal-buttons"></span>
            <span class="terminal-title">keneviz@api-portal:~/sorgu$</span>
        </div>
        
        <div class="header">
            <h1>🔮 KENEVIZ API PORTAL</h1>
            <p>&gt; HACKER MODE ACTIVATED | v3.0 | AES-256 SECURE</p>
            <div class="dev-tag">DEV : KENEViZ</div>
        </div>
        
        <div class="stats-bar">
            <div class="stat-card">
                <h3>👥 TOPLAM ZİYARETÇİ</h3>
                <div class="number" id="visitorCount">{{ visitor_count }}</div>
            </div>
            <div class="stat-card">
                <h3>📊 API KULLANIM</h3>
                <div class="number" id="apiUsageCount">{{ total_api_usage }}</div>
            </div>
        </div>
        
        <div class="support-section">
            <h3>💬 DESTEK & MESAJ</h3>
            <input type="text" id="msgName" placeholder="Adınız / Nick">
            <textarea id="msgText" rows="2" placeholder="Mesajınız..."></textarea>
            <button onclick="sendMessage()">📨 MESAJ GÖNDER</button>
            <div id="messagesList" style="margin-top: 15px; max-height: 200px; overflow-y: auto;">
                {% for msg in messages %}
                <div class="message-item">
                    <div class="message-name">{{ msg.name }}</div>
                    <div class="message-text">{{ msg.text }}</div>
                    <div class="message-date">{{ msg.date }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="admin-panel">
            <button class="admin-toggle" onclick="toggleAdmin()">🔐 [ADMIN PANEL]</button>
            <div id="adminContent" class="admin-content">
                <div class="form-group">
                    <label>ADMIN KEY:</label>
                    <input type="password" id="adminKeyInput" placeholder="devkeneviz">
                </div>
                <button onclick="checkAdminKey()">GİRİŞ</button>
                <div id="adminTools" style="display:none; margin-top:20px;">
                    <hr>
                    <h3>➕ YENİ API EKLE</h3>
                    <div class="form-group">
                        <label>API ADI:</label>
                        <input type="text" id="newApiName">
                    </div>
                    <div class="form-group">
                        <label>ENDPOINT URL:</label>
                        <input type="text" id="newApiEndpoint">
                    </div>
                    <div class="form-group">
                        <label>PARAMETRELER (JSON):</label>
                        <textarea id="newApiParams" rows="2" placeholder='{"param": ""}'></textarea>
                    </div>
                    <div class="form-group">
                        <label>METOD (GET/POST):</label>
                        <input type="text" id="newApiMethod" value="GET">
                    </div>
                    <div class="form-group">
                        <label>RESPONSE TİPİ:</label>
                        <input type="text" id="newApiResponseType" value="json">
                    </div>
                    <div class="form-group">
                        <label>AÇIKLAMA:</label>
                        <input type="text" id="newApiDesc">
                    </div>
                    <button onclick="addApi()">➕ EKLE</button>
                    <hr>
                    <h3>🗑️ API SİL</h3>
                    <div class="form-group">
                        <label>API ID:</label>
                        <input type="number" id="deleteApiId">
                    </div>
                    <button onclick="deleteApi()">🗑️ SİL</button>
                    <hr>
                    <h3>📋 TÜM API'LER</h3>
                    <button onclick="listApis()">📋 LİSTELE</button>
                    <pre id="apiListResult" style="margin-top:10px; background:#000; padding:10px; border:1px solid #0f0; border-radius:5px; font-size:10px; display:none;"></pre>
                </div>
            </div>
        </div>
        
        <div class="api-grid" id="apiGrid"></div>
        
        <div class="footer">
            <p>🔥 KENEVIZ API PORTAL | SECURE MODE | v3.0 🔥</p>
            <p>DEV : KENEViZ | Tüm Hakları Saklıdır</p>
        </div>
    </div>
    
    <div class="hidden-admin" onclick="openAdminModal()"></div>
    
    <div id="adminModal" class="admin-modal">
        <div class="admin-modal-content">
            <h3>🔐 ADMIN PANEL</h3>
            <input type="password" id="adminKeyInput2" placeholder="Admin Key">
            <button onclick="checkAdminKey2()">Giriş</button>
            <button onclick="closeAdminModal()">Kapat</button>
            <div id="adminTools2" style="display:none; margin-top:20px;">
                <hr><h3>➕ Yeni API Ekle</h3>
                <input type="text" id="newApiName2" placeholder="API Adı">
                <input type="text" id="newApiEndpoint2" placeholder="Endpoint URL">
                <textarea id="newApiParams2" rows="2" placeholder='{"param":""}'></textarea>
                <input type="text" id="newApiMethod2" value="GET">
                <input type="text" id="newApiResponseType2" value="json">
                <input type="text" id="newApiDesc2" placeholder="Açıklama">
                <button onclick="addApi2()">➕ Ekle</button>
                <hr><h3>🗑️ API Sil</h3>
                <input type="number" id="deleteApiId2" placeholder="API ID">
                <button onclick="deleteApi2()">🗑️ Sil</button>
            </div>
        </div>
    </div>
    
    <script>
        let apisData = {{ apis|tojson|safe }};
        let apiUsage = {{ api_usage|tojson|safe }};
        const ADMIN_KEY = "devkeneviz";
        
        function renderApis() {
            const grid = document.getElementById('apiGrid');
            grid.innerHTML = '';
            for (const [id, api] of Object.entries(apisData)) {
                let paramsHtml = '';
                for (const [pName, pVal] of Object.entries(api.params || {})) {
                    paramsHtml += `<div class="param-input">
                        <label>${pName}:</label>
                        <input type="text" data-param="${pName}" placeholder="${pVal}">
                    </div>`;
                }
                let usageCount = apiUsage[id] || 0;
                grid.innerHTML += `
                    <div class="api-card" data-api-id="${id}">
                        <h3>${api.name} <span class="api-id">ID:${id}</span></h3>
                        <div class="api-endpoint">📡 ${api.endpoint}</div>
                        <div class="api-desc">${api.desc || ''}</div>
                        <div class="api-stats">📊 Kullanım: ${usageCount} kez</div>
                        ${paramsHtml}
                        <div class="button-group">
                            <button class="query-btn" onclick="queryApi(${id})">🚀 SORGULA</button>
                            <button class="url-btn" onclick="openEndpoint(${id})">🔗 URL'DE AÇ</button>
                        </div>
                        <div class="loading" id="loading-${id}">⏳ İşleniyor...</div>
                        <div class="result" id="result-${id}"></div>
                    </div>
                `;
            }
        }
        
        async function queryApi(apiId) {
            const card = document.querySelector(`[data-api-id="${apiId}"]`);
            const params = {};
            card.querySelectorAll('.param-input input').forEach(inp => {
                const pName = inp.getAttribute('data-param');
                if (inp.value && pName) params[pName] = inp.value;
            });
            const loadingDiv = document.getElementById(`loading-${apiId}`);
            const resultDiv = document.getElementById(`result-${apiId}`);
            loadingDiv.classList.add('show');
            resultDiv.classList.remove('show');
            try {
                const res = await fetch(`/api/query/${apiId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ params })
                });
                const data = await res.json();
                if (data.success) {
                    if (data.response_type === 'image') {
                        resultDiv.innerHTML = `<img src="data:${data.content_type};base64,${data.image_base64}" class="result-image">`;
                    } else if (data.response_type === 'audio') {
                        resultDiv.innerHTML = `<audio controls class="result-audio" src="data:${data.content_type};base64,${data.audio_base64}"></audio>`;
                    } else {
                        resultDiv.innerHTML = `<pre>${JSON.stringify(data.data, null, 2)}</pre>`;
                    }
                } else {
                    resultDiv.innerHTML = `<pre style="color:#f00;">❌ HATA: ${data.error}</pre>`;
                }
                resultDiv.classList.add('show');
                updateApiUsage(apiId);
            } catch(e) {
                resultDiv.innerHTML = `<pre style="color:#f00;">❌ BAĞLANTI HATASI: ${e.message}</pre>`;
                resultDiv.classList.add('show');
            } finally {
                loadingDiv.classList.remove('show');
            }
        }
        
        async function updateApiUsage(apiId) {
            await fetch(`/api/usage/${apiId}`, { method: 'POST' });
            const countSpan = document.querySelector(`.api-card[data-api-id="${apiId}"] .api-stats`);
            if (countSpan) {
                let current = apiUsage[apiId] || 0;
                apiUsage[apiId] = current + 1;
                countSpan.innerHTML = `📊 Kullanım: ${apiUsage[apiId]} kez`;
                document.getElementById('apiUsageCount').innerText = Object.values(apiUsage).reduce((a,b) => a+b, 0);
            }
        }
        
        function openEndpoint(apiId) {
            const api = apisData[apiId];
            if (api) window.open(api.endpoint, '_blank');
        }
        
        async function sendMessage() {
            const name = document.getElementById('msgName').value;
            const text = document.getElementById('msgText').value;
            if (!name || !text) { alert('Ad ve mesaj girin!'); return; }
            const res = await fetch('/api/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, text })
            });
            if (res.ok) {
                alert('Mesaj gönderildi!');
                document.getElementById('msgText').value = '';
                location.reload();
            }
        }
        
        function openAdminModal() { document.getElementById('adminModal').classList.add('show'); }
        function closeAdminModal() { document.getElementById('adminModal').classList.remove('show'); }
        
        function checkAdminKey() {
            const key = document.getElementById('adminKeyInput').value;
            if (key === ADMIN_KEY) {
                document.getElementById('adminTools').style.display = 'block';
            } else { alert('Hatalı key!'); }
        }
        
        function checkAdminKey2() {
            const key = document.getElementById('adminKeyInput2').value;
            if (key === ADMIN_KEY) {
                document.getElementById('adminTools2').style.display = 'block';
            } else { alert('Hatalı key!'); }
        }
        
        function toggleAdmin() {
            document.getElementById('adminContent').classList.toggle('show');
        }
        
        async function addApi() {
            const key = document.getElementById('adminKeyInput').value;
            if (key !== ADMIN_KEY) { alert('Admin key hatalı'); return; }
            let params = {};
            try { params = JSON.parse(document.getElementById('newApiParams').value || '{}'); } catch(e) {}
            const res = await fetch('/api/admin/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Admin-Key': key },
                body: JSON.stringify({
                    name: document.getElementById('newApiName').value,
                    endpoint: document.getElementById('newApiEndpoint').value,
                    params: params,
                    method: document.getElementById('newApiMethod').value,
                    desc: document.getElementById('newApiDesc').value,
                    response_type: document.getElementById('newApiResponseType').value
                })
            });
            const data = await res.json();
            if (data.success) { alert('API eklendi! ID: ' + data.api_id); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        async function addApi2() {
            const key = document.getElementById('adminKeyInput2').value;
            if (key !== ADMIN_KEY) { alert('Admin key hatalı'); return; }
            let params = {};
            try { params = JSON.parse(document.getElementById('newApiParams2').value || '{}'); } catch(e) {}
            const res = await fetch('/api/admin/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Admin-Key': key },
                body: JSON.stringify({
                    name: document.getElementById('newApiName2').value,
                    endpoint: document.getElementById('newApiEndpoint2').value,
                    params: params,
                    method: document.getElementById('newApiMethod2').value,
                    desc: document.getElementById('newApiDesc2').value,
                    response_type: document.getElementById('newApiResponseType2').value
                })
            });
            const data = await res.json();
            if (data.success) { alert('API eklendi! ID: ' + data.api_id); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        async function deleteApi() {
            const key = document.getElementById('adminKeyInput').value;
            if (key !== ADMIN_KEY) { alert('Admin key hatalı'); return; }
            const id = document.getElementById('deleteApiId').value;
            if (!id) { alert('ID girin'); return; }
            const res = await fetch(`/api/admin/delete/${id}`, { method: 'DELETE', headers: { 'X-Admin-Key': key } });
            const data = await res.json();
            if (data.success) { alert('Silindi!'); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        async function deleteApi2() {
            const key = document.getElementById('adminKeyInput2').value;
            if (key !== ADMIN_KEY) { alert('Admin key hatalı'); return; }
            const id = document.getElementById('deleteApiId2').value;
            if (!id) { alert('ID girin'); return; }
            const res = await fetch(`/api/admin/delete/${id}`, { method: 'DELETE', headers: { 'X-Admin-Key': key } });
            const data = await res.json();
            if (data.success) { alert('Silindi!'); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        async function listApis() {
            const key = document.getElementById('adminKeyInput').value;
            if (key !== ADMIN_KEY) { alert('Admin key hatalı'); return; }
            const res = await fetch('/api/admin/list?admin_key=' + key);
            const data = await res.json();
            const resultDiv = document.getElementById('apiListResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = JSON.stringify(data, null, 2);
        }
        
        renderApis();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    counter_data['visitors'] += 1
    save_counter(counter_data)
    total_api = sum(counter_data.get('api_usage', {}).values())
    return render_template_string(HTML_TEMPLATE, 
                                  apis=APIS_DB, 
                                  visitor_count=counter_data['visitors'],
                                  total_api_usage=total_api,
                                  messages=messages_data,
                                  api_usage=counter_data.get('api_usage', {}))

@app.route('/api/query/<int:api_id>', methods=['POST'])
def query_api(api_id):
    if api_id not in APIS_DB:
        return jsonify({"error": "API bulunamadı"}), 404
    
    if 'api_usage' not in counter_data:
        counter_data['api_usage'] = {}
    counter_data['api_usage'][str(api_id)] = counter_data['api_usage'].get(str(api_id), 0) + 1
    save_counter(counter_data)
    
    api = APIS_DB[api_id]
    params = request.json.get('params', {})
    params = {k: v for k, v in params.items() if v}
    
    try:
        if api['method'] == 'GET':
            response = requests.get(api['endpoint'], params=params, timeout=30)
        else:
            response = requests.post(api['endpoint'], json=params, timeout=30)
        
        if api.get('response_type') == 'image' and 'image' in response.headers.get('content-type', ''):
            return jsonify({
                "success": True,
                "response_type": "image",
                "image_base64": base64.b64encode(response.content).decode(),
                "content_type": response.headers.get('content-type')
            })
        elif api.get('response_type') == 'audio' and 'audio' in response.headers.get('content-type', ''):
            return jsonify({
                "success": True,
                "response_type": "audio",
                "audio_base64": base64.b64encode(response.content).decode(),
                "content_type": response.headers.get('content-type')
            })
        else:
            try:
                result = response.json()
            except:
                result = {"raw_text": response.text[:5000]}
            return jsonify({"success": True, "response_type": "json", "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/usage/<int:api_id>', methods=['POST'])
def update_usage(api_id):
    if 'api_usage' not in counter_data:
        counter_data['api_usage'] = {}
    counter_data['api_usage'][str(api_id)] = counter_data['api_usage'].get(str(api_id), 0) + 1
    save_counter(counter_data)
    return jsonify({"success": True})

@app.route('/api/message', methods=['POST'])
def add_message():
    data = request.json
    name = data.get('name', 'Anonim')
    text = data.get('text', '')
    if text:
        messages_data.append({
            'name': name,
            'text': text,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_messages(messages_data)
    return jsonify({"success": True})

@app.route('/api/admin/add', methods=['POST'])
def add_api():
    admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Yetkisiz erişim!"}), 401
    
    data = request.json
    if not data.get('endpoint'):
        return jsonify({"error": "Endpoint gerekli"}), 400
    
    new_id = generate_api_id()
    APIS_DB[new_id] = {
        "name": data.get('name', 'Yeni API'),
        "endpoint": data['endpoint'],
        "params": data.get('params', {}),
        "method": data.get('method', 'GET'),
        "desc": data.get('desc', ''),
        "response_type": data.get('response_type', 'json')
    }
    return jsonify({"success": True, "api_id": new_id})

@app.route('/api/admin/delete/<int:api_id>', methods=['DELETE'])
def delete_api(api_id):
    admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Yetkisiz erişim!"}), 401
    
    if api_id not in APIS_DB:
        return jsonify({"error": "API bulunamadı"}), 404
    
    del APIS_DB[api_id]
    return jsonify({"success": True})

@app.route('/api/admin/list', methods=['GET'])
def list_apis():
    admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Yetkisiz erişim!"}), 401
    return jsonify(APIS_DB)

if __name__ == '__main__':
    app.run(debug=True, port=8080)