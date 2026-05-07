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

# الضربة القاضية: إجبار الكود على استخدام الموديل المستقر
genai.configure(api_key=API_KEY)

@app.route('/architect', methods=['POST'])
def architect_logic():
    try:
        data = request.json
        user_idea = data.get('idea', '')

        if not user_idea:
            return jsonify({"status": "error", "message": "الفكرة فارغة"}), 400

        # هنستخدم gemini-1.5-flash كاسم أساسي لأنه الأحدث
        # لو جوجل لسه معاندة، الكود هيرجع للموديل الأساسي المستقر
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            model = genai.GenerativeModel('gemini-pro')

        prompt = (
            f"Act as a Senior Software Architect. Analyze this idea: {user_idea}. "
            "Return ONLY a clean JSON object with: "
            "'project_name', 'folders', 'files', 'logic_steps'. "
            "No markdown, No backticks."
        )

        response = model.generate_content(prompt)
        text_response = response.text

        # تنظيف الرد عشان نضمن إنه JSON سليم
        clean_json = re.search(r'\{.*\}', text_response, re.DOTALL)
        
        if clean_json:
            return jsonify({"status": "success", "data": json.loads(clean_json.group(0))})
        else:
            return jsonify({"status": "error", "message": "الذكاء الاصطناعي هنج، جرب تاني"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": f"حدث خطأ: {str(e)}"}), 500

@app.route('/build', methods=['POST'])
def build_logic():
    return jsonify({"status": "success", "message": "محاكاة البناء تمت"})
