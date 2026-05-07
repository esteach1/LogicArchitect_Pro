import os
import requests
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# إعداد البيانات الأساسية
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBVqXfGuIBPnN8DD8X_7dQR-k1d-o_VgOM")
# هنستخدم رابط الـ API المباشر لنسخة v1 المستقرة (مش beta)
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

@app.route('/architect', methods=['POST'])
def architect_logic():
    try:
        data = request.json
        user_idea = data.get('idea', '')
        if not user_idea:
            return jsonify({"status": "error", "message": "اكتب فكرة يا بطل"}), 400

        # تجهيز الطلب لجوجل
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Act as a Senior Software Architect. Idea: {user_idea}. Return ONLY a clean JSON: {{'project_name': '', 'folders': [], 'files': {{}}, 'logic_steps': []}}. No markdown, no backticks."
                }]
            }]
        }

        headers = {'Content-Type': 'application/json'}
        
        # نداء مباشر للسيرفر
        response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(payload))
        result = response.json()

        # استخراج النص من رد جوجل الخام
        if 'candidates' in result:
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            
            # تنظيف الـ JSON
            clean_json = re.search(r'\{.*\}', text_response, re.DOTALL)
            if clean_json:
                return jsonify({"status": "success", "data": json.loads(clean_json.group(0))})
        
        return jsonify({"status": "error", "message": "جوجل ردت بغلط، جرب تاني"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ: {str(e)}"}), 500

@app.route('/build', methods=['POST'])
def build_logic():
    return jsonify({"status": "success", "message": "Done"})
