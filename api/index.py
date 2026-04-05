from flask import Flask, jsonify, request, render_template_string
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
    1005: {
        "name": "Ayak Sorgu",
        "endpoint": "https://kenevizayaksorguapi.vercel.app/api/sorgula",
        "params": {"tgnick": "", "yas": ""},
        "method": "GET",
        "desc": "Kullanıcı bilgisi sorgular",
        "response_type": "json"
    }
}

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>KENEVIZ API</title>
    <style>
        body { background: #0a0a0a; color: #0f0; font-family: monospace; padding: 20px; }
        .card { background: #111; border: 1px solid #0f0; border-radius: 10px; padding: 15px; margin-bottom: 20px; }
        input, button { background: #000; color: #0f0; border: 1px solid #0f0; padding: 8px; margin: 5px; }
        pre { color: #0f0; }
    </style>
</head>
<body>
    <h1>🔮 KENEVIZ API PORTAL</h1>
    {% for id, api in apis.items() %}
    <div class="card">
        <h3>{{ api.name }} (ID: {{ id }})</h3>
        <p>{{ api.desc }}</p>
        {% for pName in api.params.keys() %}
        <input type="text" id="param-{{ id }}-{{ pName }}" placeholder="{{ pName }}">
        {% endfor %}
        <button onclick="query({{ id }})">SORGULA</button>
        <div id="result-{{ id }}"></div>
    </div>
    {% endfor %}
    <script>
        async function query(id) {
            const params = {};
            document.querySelectorAll(`[id^="param-${id}-"]`).forEach(inp => {
                let key = inp.id.split('-')[2];
                if (inp.value) params[key] = inp.value;
            });
            const res = await fetch('/api/query/' + id, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({params})
            });
            const data = await res.json();
            document.getElementById('result-' + id).innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML, apis=APIS_DB)

@app.route('/api/list')
def list_apis():
    return jsonify(APIS_DB)

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
        else:
            try:
                result = response.json()
            except:
                result = {"raw_text": response.text[:5000]}
            return jsonify({"success": True, "data": result})
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
