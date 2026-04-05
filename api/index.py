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
        "desc": "AI ile görsel oluşturur",
        "response_type": "image"
    },
    1002: {
        "name": "Ses Sentez",
        "endpoint": "https://kenevizttsapi.vercel.app/api/tts",
        "params": {"text": "", "lang": "tr"},
        "method": "GET",
        "desc": "Metni sese çevirir",
        "response_type": "audio"
    },
    1003: {
        "name": "GSM İsim Sorgu",
        "endpoint": "https://kenevizglobalgsm-nameapi.vercel.app/api/gsm-name",
        "params": {"number": ""},
        "method": "GET",
        "desc": "Numara sahibini sorgular",
        "response_type": "json"
    },
    1004: {
        "name": "Tabii Checker",
        "endpoint": "https://keneviztabiicheckerapi.vercel.app/tabiicheck",
        "params": {"login": ""},
        "method": "GET",
        "desc": "Hesap doğrulama",
        "response_type": "json"
    },
    1005: {
        "name": "Ayak Sorgu",
        "endpoint": "https://kenevizayaksorguapi.vercel.app/api/sorgula",
        "params": {"tgnick": "", "yas": ""},
        "method": "GET",
        "desc": "Kullanıcı bilgisi sorgular",
        "response_type": "json"
    },
    1006: {
        "name": "URL IP Çek",
        "endpoint": "https://kenevizurlipcekiciapi.vercel.app/urlipcek",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Domain'in IP adresini bulur",
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
        "desc": "Site kaynak kodunu alır",
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

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>KENEVIZ API PORTAL</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            font-family: monospace;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #0f0; text-align: center; margin-bottom: 20px; }
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 20px;
        }
        .api-card {
            background: #111;
            border: 1px solid #0f0;
            border-radius: 10px;
            padding: 15px;
        }
        .api-card h3 { color: #0f0; margin-bottom: 10px; }
        .api-endpoint { color: #888; font-size: 11px; word-break: break-all; }
        .param-input { margin: 10px 0; }
        .param-input input {
            width: 100%;
            padding: 8px;
            background: #000;
            border: 1px solid #0f0;
            color: #0f0;
            border-radius: 5px;
        }
        button {
            background: #000;
            color: #0f0;
            border: 1px solid #0f0;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover { background: #0f0; color: #000; }
        .result {
            margin-top: 10px;
            padding: 10px;
            background: #000;
            border: 1px solid #0f0;
            border-radius: 5px;
            display: none;
            max-height: 200px;
            overflow: auto;
        }
        .result.show { display: block; }
        .result pre { color: #0f0; font-size: 11px; white-space: pre-wrap; }
        .result-image { max-width: 100%; }
        .result-audio { width: 100%; }
        .footer { text-align: center; color: #0f0; margin-top: 30px; opacity: 0.6; }
        .admin-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 30px;
            height: 30px;
            background: #0f0;
            border-radius: 50%;
            cursor: pointer;
            opacity: 0.3;
        }
        .modal {
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
        .modal.show { display: flex; }
        .modal-content {
            background: #111;
            border: 2px solid #0f0;
            border-radius: 10px;
            padding: 20px;
            width: 400px;
        }
        .modal-content input, .modal-content textarea {
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            background: #000;
            border: 1px solid #0f0;
            color: #0f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 KENEVIZ API PORTAL</h1>
        <p style="color:#0f0; text-align:center; margin-bottom:20px;">DEV: KENEViZ</p>
        
        <div class="api-grid" id="apiGrid"></div>
        <div class="footer">🔥 KENEVIZ API PORTAL v3.0 🔥</div>
    </div>
    
    <div class="admin-btn" onclick="openModal()"></div>
    
    <div id="adminModal" class="modal">
        <div class="modal-content">
            <h3 style="color:#0f0;">ADMIN PANEL</h3>
            <input type="password" id="adminKey" placeholder="Admin Key">
            <button onclick="checkKey()">Giriş</button>
            <div id="adminPanel" style="display:none; margin-top:15px;">
                <hr style="border-color:#0f0;">
                <h4>Yeni API Ekle</h4>
                <input type="text" id="apiName" placeholder="API Adı">
                <input type="text" id="apiEndpoint" placeholder="Endpoint">
                <textarea id="apiParams" placeholder='{"param":""}'></textarea>
                <input type="text" id="apiMethod" value="GET">
                <input type="text" id="apiType" value="json">
                <button onclick="addApi()">Ekle</button>
                <hr style="border-color:#0f0;">
                <h4>API Sil</h4>
                <input type="number" id="delId" placeholder="API ID">
                <button onclick="deleteApi()">Sil</button>
            </div>
            <button onclick="closeModal()">Kapat</button>
        </div>
    </div>
    
    <script>
        let apis = {{ apis|tojson|safe }};
        
        function render() {
            const grid = document.getElementById('apiGrid');
            grid.innerHTML = '';
            for (const [id, api] of Object.entries(apis)) {
                let paramsHtml = '';
                for (const [pName] of Object.entries(api.params || {})) {
                    paramsHtml += `<div class="param-input">
                        <label style="color:#0f0;">${pName}:</label>
                        <input type="text" data-param="${pName}">
                    </div>`;
                }
                grid.innerHTML += `
                    <div class="api-card">
                        <h3>${api.name} <span style="color:#888;">ID:${id}</span></h3>
                        <div class="api-endpoint">${api.endpoint}</div>
                        <div class="api-desc" style="color:#888;">${api.desc || ''}</div>
                        ${paramsHtml}
                        <button onclick="queryApi(${id})">SORGULA</button>
                        <button onclick="window.open('${api.endpoint}','_blank')">URL AÇ</button>
                        <div class="result" id="result-${id}"></div>
                    </div>
                `;
            }
        }
        
        async function queryApi(id) {
            const card = document.querySelector(`.api-card:has(button[onclick="queryApi(${id})"])`);
            const params = {};
            card.querySelectorAll('.param-input input').forEach(inp => {
                const pName = inp.getAttribute('data-param');
                if (inp.value) params[pName] = inp.value;
            });
            
            const resultDiv = document.getElementById(`result-${id}`);
            resultDiv.innerHTML = '⏳ İşleniyor...';
            resultDiv.classList.add('show');
            
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
                } else {
                    resultDiv.innerHTML = `<pre style="color:red;">HATA: ${data.error}</pre>`;
                }
            } catch(e) {
                resultDiv.innerHTML = `<pre style="color:red;">HATA: ${e.message}</pre>`;
            }
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
                    response_type: document.getElementById('apiType').value
                })
            });
            const data = await res.json();
            if (data.success) { alert('Eklendi! ID: ' + data.api_id); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        async function deleteApi() {
            const key = document.getElementById('adminKey').value;
            const id = document.getElementById('delId').value;
            const res = await fetch(`/api/admin/delete/${id}`, {
                method: 'DELETE',
                headers: { 'X-Admin-Key': key }
            });
            const data = await res.json();
            if (data.success) { alert('Silindi!'); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        render();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML, apis=APIS_DB)

@app.route('/api/query/<int:api_id>', methods=['POST'])
def query_api(api_id):
    if api_id not in APIS_DB:
        return jsonify({"error": "API bulunamadı"}), 404
    
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

if __name__ == '__main__':
    app.run(port=8080)
