import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json, re

app = Flask(__name__)
# تفعيل الـ CORS للسماح للمتصفح بالوصول للسيرفر من أي مكان
CORS(app, resources={r"/*": {"origins": "*"}})

# --- حماية مفتاح الـ API ---
# الكود بيبحث عن المفتاح في بيئة النظام، لو مش موجود بيستخدم المفتاح بتاعك (كاحتياط)
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBVqXfGuIBPnN8DD8X_7dQR-k1d-o_VgOM")
genai.configure(api_key=API_KEY)

# البحث التلقائي عن أحدث موديل متاح في حسابك (Gemini 2.5 Flash أو غيره)
selected_model = None
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            selected_model = m.name
            break
except Exception as e:
    print(f"Model search error: {e}")

model = genai.GenerativeModel(selected_model if selected_model else 'gemini-1.5-flash')

# مكان حفظ المشاريع التي سيقوم الـ AI ببنائها
BASE_PROJECTS_DIR = "Generated_Projects"

@app.route('/architect', methods=['POST'])
def architect_logic():
    try:
        user_idea = request.json.get('idea')
        
        # برومبت هندسي صارم لضمان الحصول على كود احترافي و JSON سليم
        prompt = f"""
        Act as a Senior Full-Stack Developer. Analyze the following idea: {user_idea}.
        Your task is to generate a complete project structure and professional code.
        
        Return ONLY a strictly formatted JSON object:
        {{
            "project_name": "Unique_Project_Name",
            "folders": ["list_of_all_required_folders"],
            "files": {{ 
                "path/to/file.extension": "Full Professional Clean Code Content" 
            }},
            "logic_steps": ["Step 1", "Step 2", "Step 3"]
        }}
        
        Rules:
        1. Code must be production-ready and professional.
        2. Do NOT use markdown backticks (```) inside the JSON.
        3. Escape any special characters to keep JSON valid.
        4. Language: Arabic for descriptions, English for Code.
        """
        
        response = model.generate_content(prompt)
        text = response.text
        
        # استخراج الـ JSON فقط من رد الـ AI
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            return jsonify({"status": "success", "data": data})
        
        return jsonify({"status": "error", "message": "The AI response was not in a valid JSON format."}), 500
        
    except Exception as e:
        print(f"Error in /architect: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/build', methods=['POST'])
def build_files():
    try:
        data = request.json.get('data')
        proj_name = data.get('project_name', 'My_AI_Project').replace(" ", "_")
        project_path = os.path.join(BASE_PROJECTS_DIR, proj_name)

        # إنشاء المجلد الرئيسي للمشروع
        os.makedirs(project_path, exist_ok=True)

        # إنشاء المجلدات الفرعية
        for folder in data.get('folders', []):
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)

        # حقن الكود داخل الملفات
        for filename, content in data.get('files', {}).items():
            # تنظيف الكود من أي علامات Markdown قد تظهر بالخطأ
            clean_content = re.sub(r'^```[a-z]*\n', '', content, flags=re.MULTILINE)
            clean_content = re.sub(r'\n```$', '', clean_content, flags=re.MULTILINE)
            
            file_full_path = os.path.join(project_path, filename)
            
            # التأكد من إنشاء المجلدات الأب للملف إذا كانت مفقودة
            os.makedirs(os.path.dirname(file_full_path), exist_ok=True)
            
            # كتابة الكود الفعلي مع دعم اللغة العربية (UTF-8)
            with open(file_full_path, 'w', encoding='utf-8') as f:
                f.write(clean_content)
                f.flush()
                os.fsync(f.fileno())

        return jsonify({
            "status": "success", 
            "message": "Project built successfully!",
            "path": os.path.abspath(project_path)
        })
        
    except Exception as e:
        print(f"Error in /build: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # التأكد من وجود مجلد المشاريع قبل البدء
    if not os.path.exists(BASE_PROJECTS_DIR):
        os.makedirs(BASE_PROJECTS_DIR)
        
    # تشغيل السيرفر (على بورت 5000 كما هو معتاد)
    app.run(debug=True, host='0.0.0.0', port=5000)