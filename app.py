import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json, re

# مهم جداً لـ Vercel: تعريف التطبيق باسم app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# قراءة المفتاح من الإعدادات اللي حطيناها في Vercel
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBVqXfGuIBPnN8DD8X_7dQR-k1d-o_VgOM")
genai.configure(api_key=API_KEY)

# اختيار الموديل
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def home():
    return "Server is running!"

@app.route('/architect', methods=['POST'])
def architect_logic():
    try:
        user_idea = request.json.get('idea')
        prompt = f"Act as a Senior Developer. Analyze this idea: {user_idea}. Return ONLY a JSON object with structure: {{'project_name': 'name', 'folders': [], 'files': {{'file': 'code'}}, 'logic_steps': []}}. No markdown."
        
        response = model.generate_content(prompt)
        text = response.text
        
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return jsonify({"status": "success", "data": json.loads(match.group(0))})
        return jsonify({"status": "error", "message": "Invalid AI response"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ملاحظة: في Vercel إحنا مش محتاجين app.run() 
# السيرفر بيشغل الـ app أوتوماتيكياً
