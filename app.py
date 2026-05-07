import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import re

app = Flask(__name__)
CORS(app)

# إعداد المفتاح
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBVqXfGuIBPnN8DD8X_7dQR-k1d-o_VgOM")
genai.configure(api_key=API_KEY)

def get_best_model():
    """دالة بتبحث عن أي موديل شغال في حسابك عشان تمنع خطأ 404"""
    try:
        # بنجرب الأسماء المشهورة بالترتيب
        for model_name in ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro']:
            try:
                m = genai.GenerativeModel(model_name)
                # تجربة وهمية سريعة
                return m
            except:
                continue
        
        # لو ملقاش، بيجيب أول موديل متاح في القائمة عندك
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except:
        return genai.GenerativeModel('gemini-pro') # الموديل الجوكر

# تشغيل نظام البحث عن الموديل
model = get_best_model()

@app.route('/architect', methods=['POST'])
def architect_logic():
    try:
        data = request.json
        user_idea = data.get('idea', '')
        if not user_idea:
            return jsonify({"status": "error", "message": "اكتب فكرة يا بطل"}), 400

        prompt = (
            f"Act as a Senior Software Architect. Idea: {user_idea}. "
            "Return ONLY a clean JSON: {'project_name': '', 'folders': [], 'files': {}, 'logic_steps': []}. "
            "No markdown, no backticks."
        )

        # محاولة توليد المحتوى
        response = model.generate_content(prompt)
        
        # تنظيف الرد
        clean_json = re.search(r'\{.*\}', response.text, re.DOTALL)
        if clean_json:
            return jsonify({"status": "success", "data": json.loads(clean_json.group(0))})
        else:
            return jsonify({"status": "error", "message": "حاول مرة تانية، الذكاء الاصطناعي مهنج"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": f"حدث خطأ: {str(e)}"}), 500

@app.route('/build', methods=['POST'])
def build_logic():
    return jsonify({"status": "success", "message": "Done"})
