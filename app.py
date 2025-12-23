from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.db import supabase
from services.ocr_service import extract_text
from services.product_service import decode_barcode, fetch_product_metadata, get_alternatives
from services.allergen_service import check_safety
import bcrypt  # Security tool
import json

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "NutriShield Backend Running"})

# ===========================
# 1. AUTHENTICATION (New & Secure)
# ===========================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')

    # 1. Check if user already exists
    check_user = supabase.table('users').select("*").eq('email', email).execute()
    if check_user.data:
        return jsonify({"error": "User with this email already exists"}), 400

    # 2. Hash the password (Security step)
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        # 3. Create the User
        user_payload = {
            "email": email,
            "full_name": full_name,
            "username": email.split('@')[0],
            "password_hash": hashed_pw
        }
        user_res = supabase.table('users').insert(user_payload).execute()
        user_id = user_res.data[0]['id']

        return jsonify({"message": "User created successfully", "user_id": user_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        # 1. Find user by email
        user_res = supabase.table('users').select("*").eq('email', email).execute()
        if not user_res.data:
            return jsonify({"error": "User not found"}), 404
        
        user = user_res.data[0]
        stored_hash = user.get('password_hash')

        # 2. Check Password
        if not stored_hash:
             return jsonify({"error": "Invalid account setup"}), 400

        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return jsonify({"message": "Login successful", "user_id": user['id'], "full_name": user['full_name']}), 200
        else:
            return jsonify({"error": "Wrong password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/save_allergens', methods=['POST'])
def save_allergens():
    """ Called AFTER signup to save allergies """
    data = request.json
    user_id = data.get('user_id')
    common_allergens = data.get('common_allergens', []) 
    other_allergens = data.get('other_allergens_raw', "") 

    try:
        profile_payload = {
            "user_id": user_id,
            "common_allergens": common_allergens,
            "other_allergens_raw": other_allergens
        }
        supabase.table('allergen_profiles').upsert(profile_payload, on_conflict='user_id').execute()
        return jsonify({"message": "Allergens saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===========================
# 2. SCAN: BARCODE
# ===========================
@app.route('/api/scan/barcode', methods=['POST'])
def scan_barcode_route():
    if 'image' not in request.files or 'user_id' not in request.form:
        return jsonify({"error": "Missing image or user_id"}), 400

    image_file = request.files['image'].read()
    user_id = request.form['user_id']

    code = decode_barcode(image_file)
    if not code:
        return jsonify({"status": "error", "message": "No barcode detected"}), 400

    product = fetch_product_metadata(code)
    prod_name = product['name'] if product else "Unknown Product"
    ingredients = product['ingredients'] if product else ""

    prof_res = supabase.table('allergen_profiles').select("*").eq('user_id', user_id).execute()
    
    if not prof_res.data:
        is_safe = True 
        found = []
    else:
        is_safe, found = check_safety(ingredients, prof_res.data[0])

    try:
        hist_entry = {
            "user_id": user_id,
            "scan_type": "barcode",
            "barcode_value": code,
            "product_name": prod_name,
            "product_ingredients_raw": ingredients,
            "matched_allergens": found,
            "decision_safe": is_safe,
            "status": "completed"
        }
        supabase.table('scan_history').insert(hist_entry).execute()
        # Not returning ID to keep response simple
    except:
        pass

    return jsonify({
        "safe": is_safe,
        "product": product,
        "allergens_found": found,
        "alternatives": get_alternatives(found) if not is_safe else []
    })

# ===========================
# 3. SCAN: OCR
# ===========================
@app.route('/api/scan/ocr', methods=['POST'])
def scan_ocr_route():
    if 'image' not in request.files or 'user_id' not in request.form:
        return jsonify({"error": "Missing image or user_id"}), 400

    image_file = request.files['image'].read()
    user_id = request.form['user_id']

    ocr_result = extract_text(image_file)
    if not ocr_result:
        return jsonify({"error": "Failed to read image"}), 400

    prof_res = supabase.table('allergen_profiles').select("*").eq('user_id', user_id).execute()
    
    if not prof_res.data:
        is_safe = True
        found = []
    else:
        is_safe, found = check_safety(ocr_result['text'], prof_res.data[0])

    try:
        hist_entry = {
            "user_id": user_id,
            "scan_type": "ocr",
            "tesseract_output": ocr_result['tesseract_output'],
            "gemini_output": ocr_result['gemini_output'],
            "engine_used": ocr_result['engine'],
            "matched_allergens": found,
            "decision_safe": is_safe,
            "status": "completed"
        }
        supabase.table('scan_history').insert(hist_entry).execute()
    except:
        pass

    return jsonify({
        "safe": is_safe,
        "extracted_text": ocr_result['text'],
        "allergens_found": found,
        "alternatives": get_alternatives(found) if not is_safe else []
    })

# ===========================
# 4. REVIEW
# ===========================
@app.route('/api/review', methods=['POST'])
def add_review():
    data = request.json
    try:
        scan_id = data.get('scan_id')
        if scan_id == "": scan_id = None
        review_entry = {
            "user_id": data.get('user_id'),
            "scan_id": scan_id,
            "rating": int(data.get('rating', 5)),
            "comment": data.get('comment', "")
        }
        supabase.table('reviews').insert(review_entry).execute()
        return jsonify({"message": "Review saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)