from flask import Flask, request, jsonify, render_template_string
import requests
import base64
import random

app = Flask(__name__)

ADMIN_KEY = "devkeneviz"

APIS_DB = {
    1001: {
        "name": "Görsel Üret",
        "endpoint": "https://kenevizimagegenerate.vercel.app/api/generate",
        "params": {"prompt": ""},
        "method": "GET",
        "desc": "AI ile görsel oluşturur | prompt: cyberdog, kedi, araba",
        "response_type": "image"
    },
    1002: {
        "name": "Ses Sentez",
        "endpoint": "https://kenevizttsapi.vercel.app/api/tts",
        "params": {"text": "", "lang": "tr"},
        "method": "GET",
        "desc": "Metni sese çevirir | text: Merhaba, lang: tr/en",
        "response_type": "audio"
    },
    1003: {
        "name": "GSM İsim Sorgu",
        "endpoint": "https://kenevizglobalgsm-nameapi.vercel.app/api/gsm-name",
        "params": {"number": ""},
        "method": "GET",
        "desc": "Numara sahibini sorgular | number: 905555555555",
        "response_type": "json"
    },
    1004: {
        "name": "Tabii Checker",
        "endpoint": "https://keneviztabiicheckerapi.vercel.app/tabiicheck",
        "params": {"login": ""},
        "method": "GET",
        "desc": "Hesap doğrulama | login: email:pass",
        "response_type": "json"
    },
    1005: {
        "name": "Ayak Sorgu",
        "endpoint": "https://kenevizayaksorguapi.vercel.app/api/sorgula",
        "params": {"tgnick": "", "yas": ""},
        "method": "GET",
        "desc": "Kullanıcı bilgisi sorgular | tgnick: @kullanici, yas: 25",
        "response_type": "json"
    },
    1006: {
        "name": "URL IP Çek",
        "endpoint": "https://kenevizurlipcekiciapi.vercel.app/urlipcek",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Domain'in IP adresini bulur | url: google.com",
        "response_type": "json"
    },
    1007: {
        "name": "BIN Sorgu",
        "endpoint": "https://kenevizbinsorguapi.vercel.app/binsorgu",
        "params": {"bin": ""},
        "method": "GET",
        "desc": "Kart BIN sorgulama | bin: 123456",
        "response_type": "json"
    },
    1008: {
        "name": "Index Çek",
        "endpoint": "https://kenevizindexcekenapi.vercel.app/index",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Site kaynak kodunu alır | url: https://google.com",
        "response_type": "text"
    },
    1009: {
        "name": "Web MS Analiz",
        "endpoint": "https://kenevizwebmsapi.vercel.app/analyze",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Web sitesi performans analizi | url: siteadi.com",
        "response_type": "json"
    }
}

HTML = '''
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
            font-family: 'Courier New', monospace;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #0f0; font-size: 2em; text-shadow: 0 0 10px #0f0; }
        .dev { color: #0f0; font-size: 0.8em; opacity: 0.7; }
        
        .stats { display: flex; gap: 20px; justify-content: center; margin-bottom: 30px; }
        .stat-card { background: #111; border: 1px solid #0f0; border-radius: 10px; padding: 15px 30px; text-align: center; }
        .stat-card h3 { color: #0f0; font-size: 0.8em; }
        .stat-card .number { color: #0f0; font-size: 2em; font-weight: bold; }
        
        .support { background: #111; border: 1px solid #0f0; border-radius: 10px; padding: 20px; margin-bottom: 30px; }
        .support h3 { color: #0f0; margin-bottom: 15px; }
        .support input, .support textarea { width: 100%; padding: 10px; margin-bottom: 10px; background: #000; border: 1px solid #0f0; color: #0f0; border-radius: 5px; }
        .support button { background: #000; color: #0f0; border: 1px solid #0f0; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        .message-item { background: #000; border-left: 3px solid #0f0; padding: 10px; margin-bottom: 10px; }
        .message-name { color: #0f0; font-weight: bold; }
        .message-text { color: #888; margin-top: 5px; }
        
        .api-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; margin-top: 20px; }
        .api-card { background: #111; border: 1px solid #0f0; border-radius: 10px; padding: 15px; transition: 0.3s; }
        .api-card:hover { transform: translateY(-3px); box-shadow: 0 0 15px rgba(0,255,0,0.2); }
        .api-card h3 { color: #0f0; margin-bottom: 10px; }
        .api-id { background: #0f0; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.7em; margin-left: 10px; }
        .api-endpoint { color: #666; font-size: 0.65em; word-break: break-all; margin-bottom: 10px; }
        .api-desc { color: #0f0; font-size: 0.75em; margin-bottom: 15px; opacity: 0.8; }
        
        .param-input { margin-bottom: 10px; }
        .param-input label { display: block; color: #0f0; font-size: 0.7em; margin-bottom: 3px; }
        .param-input input { width: 100%; padding: 8px; background: #000; border: 1px solid #0f0; color: #0f0; border-radius: 5px; }
        
        .btn-group { display: flex; gap: 10px; margin-top: 15px; }
        .query-btn { flex: 2; background: #000; color: #0f0; border: 1px solid #0f0; padding: 10px; border-radius: 5px; cursor: pointer; }
        .url-btn { flex: 1; background: #000; color: #0ff; border: 1px solid #0ff; padding: 10px; border-radius: 5px; cursor: pointer; }
        .query-btn:hover, .url-btn:hover { background: #0f0; color: #000; }
        
        .result { margin-top: 15px; padding: 10px; background: #000; border: 1px solid #0f0; border-radius: 5px; max-height: 250px; overflow: auto; display: none; }
        .result.show { display: block; }
        .result pre { color: #0f0; font-size: 0.7em; white-space: pre-wrap; }
        .result-image { max-width: 100%; border-radius: 5px; }
        .result-audio { width: 100%; }
        
        .loading { text-align: center; padding: 10px; display: none; color: #0f0; }
        .loading.show { display: block; }
        
        .footer { text-align: center; margin-top: 40px; padding: 20px; color: #0f0; opacity: 0.5; font-size: 0.7em; border-top: 1px solid #0f0; }
        
        .admin-btn { position: fixed; bottom: 20px; right: 20px; width: 40px; height: 40px; background: transparent; cursor: pointer; opacity: 0.2; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center; }
        .modal.show { display: flex; }
        .modal-content { background: #111; border: 2px solid #0f0; border-radius: 10px; padding: 20px; width: 450px; max-height: 80vh; overflow: auto; }
        .modal-content h3 { color: #0f0; margin-bottom: 15px; }
        .modal-content input, .modal-content textarea { width: 100%; padding: 8px; margin-bottom: 10px; background: #000; border: 1px solid #0f0; color: #0f0; border-radius: 5px; }
        .modal-content button { background: #000; color: #0f0; border: 1px solid #0f0; padding: 8px 15px; border-radius: 5px; cursor: pointer; margin-right: 10px; }
        
        hr { border-color: #0f0; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔮 KENEVIZ API PORTAL</h1>
            <div class="dev">DEV : KENEViZ</div>
        </div>
        
        <div class="stats">
            <div class="stat-card"><h3>📊 TOPLAM API</h3><div class="number" id="totalApi">0</div></div>
        </div>
        
        <div class="support">
            <h3>💬 DESTEK MESAJI</h3>
            <input type="text" id="msgName" placeholder="Adınız">
            <textarea id="msgText" rows="2" placeholder="Mesajınız..."></textarea>
            <button onclick="sendMessage()">📨 GÖNDER</button>
            <div id="msgList" style="margin-top: 15px; max-height: 150px; overflow: auto;"></div>
        </div>
        
        <div class="api-grid" id="apiGrid"></div>
        
        <div class="footer">
            <p>🔥 KENEVIZ API PORTAL | v3.0 | HACKER MODE 🔥</p>
        </div>
    </div>
    
    <div class="admin-btn" onclick="openModal()"></div>
    
    <div id="adminModal" class="modal">
        <div class="modal-content">
            <h3>🔐 ADMIN PANEL</h3>
            <input type="password" id="adminKey" placeholder="Admin Key">
            <button onclick="checkKey()">GİRİŞ</button>
            <div id="adminPanel" style="display:none; margin-top:15px;">
                <hr><h4>➕ YENİ API EKLE</h4>
                <input type="text" id="apiName" placeholder="API Adı">
                <input type="text" id="apiEndpoint" placeholder="Endpoint URL">
                <textarea id="apiParams" rows="2" placeholder='{"param": ""}'></textarea>
                <input type="text" id="apiMethod" value="GET">
                <input type="text" id="apiType" value="json">
                <input type="text" id="apiDesc" placeholder="Açıklama">
                <button onclick="addApi()">➕ EKLE</button>
                <hr><h4>🗑️ API SİL</h4>
                <input type="number" id="delId" placeholder="API ID">
                <button onclick="deleteApi()">🗑️ SİL</button>
                <hr><h4>📋 TÜM API'LER</h4>
                <button onclick="listApis()">📋 LİSTELE</button>
                <pre id="apiList" style="margin-top:10px; background:#000; padding:10px; font-size:10px; display:none;"></pre>
            </div>
            <button onclick="closeModal()">KAPAT</button>
        </div>
    </div>
    
    <script>
        let apis = {{ apis|tojson|safe }};
        let messages = {{ messages|tojson|safe }};
        let apiUsage = {{ api_usage|tojson|safe }};
        
        function render() {
            const grid = document.getElementById('apiGrid');
            grid.innerHTML = '';
            let total = 0;
            for (const [id, api] of Object.entries(apis)) {
                total++;
                let paramsHtml = '';
                for (const [pName, pVal] of Object.entries(api.params || {})) {
                    paramsHtml += `<div class="param-input">
                        <label>${pName}:</label>
                        <input type="text" data-param="${pName}" placeholder="${pVal}">
                    </div>`;
                }
                let usage = apiUsage[id] || 0;
                grid.innerHTML += `
                    <div class="api-card">
                        <h3>${api.name} <span class="api-id">ID:${id}</span></h3>
                        <div class="api-endpoint">📡 ${api.endpoint}</div>
                        <div class="api-desc">${api.desc || ''}</div>
                        <div class="api-desc" style="color:#555;">📊 Kullanım: ${usage} kez</div>
                        ${paramsHtml}
                        <div class="btn-group">
                            <button class="query-btn" onclick="queryApi(${id})">🚀 SORGULA</button>
                            <button class="url-btn" onclick="window.open('${api.endpoint}','_blank')">🔗 URL'DE AÇ</button>
                        </div>
                        <div class="loading" id="load-${id}">⏳ İşleniyor...</div>
                        <div class="result" id="result-${id}"></div>
                    </div>
                `;
            }
            document.getElementById('totalApi').innerHTML = total;
            
            const msgDiv = document.getElementById('msgList');
            msgDiv.innerHTML = '';
            for (const msg of messages.slice(-5)) {
                msgDiv.innerHTML += `<div class="message-item">
                    <div class="message-name">${msg.name}</div>
                    <div class="message-text">${msg.text}</div>
                </div>`;
            }
        }
        
        async function queryApi(id) {
            const card = document.querySelector(`.api-card:has(button[onclick="queryApi(${id})"])`);
            const params = {};
            card.querySelectorAll('.param-input input').forEach(inp => {
                const pName = inp.getAttribute('data-param');
                if (inp.value) params[pName] = inp.value;
            });
            
            const loadDiv = document.getElementById(`load-${id}`);
            const resultDiv = document.getElementById(`result-${id}`);
            loadDiv.classList.add('show');
            resultDiv.classList.remove('show');
            
            try {
                const res = await fetch(`/api/query/${id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ params })
                });
                const data = await res.json();
                if (data.success) {
                    if (data.response_type === 'image') {
                        resultDiv.innerHTML = `<img src="data:${data.content_type};base64,${data.image_base64}" class="result-image">`;
                    } else if (data.response_type === 'audio') {
                        resultDiv.innerHTML = `<audio controls src="data:${data.content_type};base64,${data.audio_base64}" class="result-audio"></audio>`;
                    } else {
                        resultDiv.innerHTML = `<pre>${JSON.stringify(data.data, null, 2)}</pre>`;
                    }
                    await fetch(`/api/usage/${id}`, { method: 'POST' });
                } else {
                    resultDiv.innerHTML = `<pre style="color:red;">❌ ${data.error}</pre>`;
                }
                resultDiv.classList.add('show');
            } catch(e) {
                resultDiv.innerHTML = `<pre style="color:red;">❌ HATA: ${e.message}</pre>`;
                resultDiv.classList.add('show');
            } finally {
                loadDiv.classList.remove('show');
            }
        }
        
        async function sendMessage() {
            const name = document.getElementById('msgName').value;
            const text = document.getElementById('msgText').value;
            if (!name || !text) { alert('Ad ve mesaj girin!'); return; }
            await fetch('/api/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, text })
            });
            alert('Mesaj gönderildi!');
            document.getElementById('msgText').value = '';
            location.reload();
        }
        
        function openModal() { document.getElementById('adminModal').classList.add('show'); }
        function closeModal() { document.getElementById('adminModal').classList.remove('show'); }
        
        function checkKey() {
            const key = document.getElementById('adminKey').value;
            if (key === 'devkeneviz') {
                document.getElementById('adminPanel').style.display = 'block';
            } else { alert('Hatali key!'); }
        }
        
        async function addApi() {
            const key = document.getElementById('adminKey').value;
            if (key !== 'devkeneviz') { alert('Admin key hatali'); return; }
            let params = {};
            try { params = JSON.parse(document.getElementById('apiParams').value || '{}'); } catch(e) {}
            const res = await fetch('/api/admin/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Admin-Key': key },
                body: JSON.stringify({
                    name: document.getElementById('apiName').value,
                    endpoint: document.getElementById('apiEndpoint').value,
                    params: params,
                    method: document.getElementById('apiMethod').value,
                    desc: document.getElementById('apiDesc').value,
                    response_type: document.getElementById('apiType').value
                })
            });
            const data = await res.json();
            if (data.success) { alert('Eklendi! ID: ' + data.api_id); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        async function deleteApi() {
            const key = document.getElementById('adminKey').value;
            if (key !== 'devkeneviz') { alert('Admin key hatali'); return; }
            const id = document.getElementById('delId').value;
            const res = await fetch(`/api/admin/delete/${id}`, {
                method: 'DELETE',
                headers: { 'X-Admin-Key': key }
            });
            const data = await res.json();
            if (data.success) { alert('Silindi!'); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        async function listApis() {
            const key = document.getElementById('adminKey').value;
            if (key !== 'devkeneviz') { alert('Admin key hatali'); return; }
            const res = await fetch('/api/admin/list?admin_key=' + key);
            const data = await res.json();
            const div = document.getElementById('apiList');
            div.style.display = 'block';
            div.innerHTML = JSON.stringify(data, null, 2);
        }
        
        render();
    </script>
</body>
</html>
'''

messages_db = []
counter_data = {"api_usage": {}}

@app.route('/')
def index():
    return render_template_string(HTML, apis=APIS_DB, messages=messages_db, api_usage=counter_data.get('api_usage', {}))

@app.route('/api/query/<int:api_id>', methods=['POST'])
def query_api(api_id):
    if api_id not in APIS_DB:
        return jsonify({"error": "API bulunamadı"}), 404
    
    if 'api_usage' not in counter_data:
        counter_data['api_usage'] = {}
    counter_data['api_usage'][str(api_id)] = counter_data['api_usage'].get(str(api_id), 0) + 1
    
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
    return jsonify({"success": True})

@app.route('/api/message', methods=['POST'])
def add_message():
    data = request.json
    messages_db.append({
        'name': data.get('name', 'Anonim'),
        'text': data.get('text', '')
    })
    if len(messages_db) > 20:
        messages_db.pop(0)
    return jsonify({"success": True})

@app.route('/api/admin/add', methods=['POST'])
def add_api():
    admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Yetkisiz erişim!"}), 401
    
    data = request.json
    if not data.get('endpoint'):
        return jsonify({"error": "Endpoint gerekli"}), 400
    
    new_id = random.randint(1000, 9999)
    while new_id in APIS_DB:
        new_id = random.randint(1000, 9999)
    
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
    app.run(port=8080)
