import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import re

# تعريف التطبيق وتفعيل الـ CORS عشان المتصفح ميعملش مشاكل في الاتصال
app = Flask(__name__)
CORS(app)

# جلب مفتاح الـ API من إعدادات Vercel
# لو مش موجود في الإعدادات هيستخدم المفتاح ده كاحتياطي
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBVqXfGuIBPnN8DD8X_7dQR-k1d-o_VgOM")
genai.configure(api_key=API_KEY)

# استخدام موديل gemini-pro (النسخة الأكثر استقراراً وقبولاً للأوامر)
model = genai.GenerativeModel('gemini-pro')

@app.route('/architect', methods=['POST'])
def architect_logic():
    try:
        data = request.json
        user_idea = data.get('idea', '')

        if not user_idea:
            return jsonify({"status": "error", "message": "الفكرة فارغة!"}), 400

        # البرومبت اللي بيخلي الذكاء الاصطناعي يرد بـ JSON فقط بدون كلام جانبي
        prompt = (
            f"Act as a Senior Software Architect. Analyze this idea: {user_idea}. "
            "Return ONLY a clean JSON object with these keys: "
            "'project_name', 'folders', 'files', 'logic_steps'. "
            "Inside 'files', provide at least 3 main files with their initial code. "
            "Do not include any markdown formatting or backticks like ```json."
        )

        response = model.generate_content(prompt)
        text_response = response.text

        # تنظيف الرد باستخدام Regex لضمان استخراج الـ JSON فقط
        clean_json = re.search(r'\{.*\}', text_response, re.DOTALL)
        
        if clean_json:
            final_data = json.loads(clean_json.group(0))
            return jsonify({"status": "success", "data": final_data})
        else:
            return jsonify({"status": "error", "message": "لم يتمكن الذكاء الاصطناعي من تنسيق البيانات بشكل صحيح"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/build', methods=['POST'])
def build_logic():
    # في السيرفرات السحابية زي Vercel، الكتابة على الهارد ديسك ممنوعة
    # بنرجع رسالة نجاح لمحاكاة العملية أمام المستخدم
    return jsonify({
        "status": "success", 
        "message": "تمت محاكاة بناء المشروع بنجاح في بيئة Vercel السحابية",
        "path": "/virtual/project/build"
    })

# ملاحظة هامة: في Vercel لا نستخدم app.run() إطلاقاً
# السيرفر بيشغل الـ app أوتوماتيكياً
