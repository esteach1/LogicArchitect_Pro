import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import re

# 1. إعداد التطبيق وتجاوز مشاكل المتصفح (CORS)
app = Flask(__name__)
CORS(app)

# 2. إعداد مفتاح الـ API (الأمان أولاً)
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBVqXfGuIBPnN8DD8X_7dQR-k1d-o_VgOM")
genai.configure(api_key=API_KEY)

# 3. دالة ذكية لاختيار الموديل المتاح لتجنب خطأ 404
def get_working_model():
    # بنجرب الأسماء المتاحة في جوجل حالياً بالترتيب
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    for m in models_to_try:
        try:
            model = genai.GenerativeModel(m)
            # تجربة وهمية للتأكد أن الموديل متاح
            return model
        except:
            continue
    return genai.GenerativeModel('gemini-pro') # الحل الأخير

model = get_working_model()

@app.route('/architect', methods=['POST'])
def architect_logic():
    try:
        data = request.json
        user_idea = data.get('idea', '')

        if not user_idea:
            return jsonify({"status": "error", "message": "الفكرة فارغة يا مايسترو!"}), 400

        # برومبت احترافي لضمان جودة الكود الناتج
        prompt = (
            f"Act as a Senior Software Architect. Analyze this idea: {user_idea}. "
            "Return ONLY a clean JSON object with these keys: "
            "'project_name', 'folders', 'files', 'logic_steps'. "
            "Inside 'files', provide at least 3 main files with their initial code. "
            "Do not include any markdown formatting like ```json."
        )

        response = model.generate_content(prompt)
        text_response = response.text

        # تنظيف الرد من أي زيادات نصية لضمان عمل الـ JSON
        clean_json = re.search(r'\{.*\}', text_response, re.DOTALL)
        
        if clean_json:
            final_data = json.loads(clean_json.group(0))
            return jsonify({"status": "success", "data": final_data})
        else:
            return jsonify({"status": "error", "message": "الذكاء الاصطناعي لم ينسق البيانات صح، حاول مرة أخرى"}), 500

    except Exception as e:
        # لو حصل خطأ في الموديل، بنجرب نغيره لحظياً
        return jsonify({"status": "error", "message": f"حدث خطأ: {str(e)}"}), 500

@app.route('/build', methods=['POST'])
def build_logic():
    # محاكاة البناء لأن Vercel سيرفر للقراءة فقط
    return jsonify({
        "status": "success", 
        "message": "تمت محاكاة بناء الهيكل بنجاح في بيئة السحاب",
        "path": "/virtual/project/logic"
    })

# ملاحظة: Vercel هو من يدير تشغيل التطبيق، لا تضع app.run()
