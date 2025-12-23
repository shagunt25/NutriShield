import pytesseract
from PIL import Image
import google.generativeai as genai
import os
import io
import cv2 # Computer Vision Library
import numpy as np

# Setup Gemini (Updated to your best model)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Setup Tesseract
tesseract_path = os.environ.get("TESSERACT_CMD")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def preprocess_image_advanced(image_bytes):
    """
    Applies Computer Vision techniques to prepare image for OCR.
    """
    # 1. Convert bytes to OpenCV format
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # 2. Grayscale (Remove color interference)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Upscaling (Resize x2 to help read small text)
    # Tesseract works best with larger images
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 4. Denoising (Remove graininess)
    # fastNlMeansDenoising is a powerful algorithm to smooth images
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # 5. Binarization (Otsu's Thresholding)
    # Converts image to pure Black and White dynamically
    _, threshold_img = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return threshold_img

def extract_text(image_bytes):
    """
    Advanced Pipeline: 
    Raw Image -> OpenCV Preprocessing -> Tesseract -> Gemini (Fallback)
    """
    tess_text = ""
    gem_text = ""
    engine_used = "tesseract_advanced"
    final_text = ""

    # --- PHASE 1: ADVANCED COMPUTER VISION OCR ---
    try:
        # A. Pre-process the image using OpenCV
        processed_img_cv = preprocess_image_advanced(image_bytes)
        
        # Convert back to PIL for Tesseract
        processed_pil = Image.fromarray(processed_img_cv)

        # B. Configure Tesseract for blocks of text (PSM 6)
        custom_config = r'--oem 3 --psm 6' 
        tess_text = pytesseract.image_to_string(processed_pil, config=custom_config)

        # C. Validation Logic
        cleaned_text = tess_text.strip()
        
        # If we got substantial text, we accept it
        if len(cleaned_text) > 15:
            final_text = cleaned_text
            engine_used = "tesseract_cv_enhanced"
            print("✅ Advanced Tesseract scan successful")
        else:
            print("⚠️ Tesseract result poor even after processing. Switching to AI...")
            raise Exception("Low confidence")
            
    except Exception as e:
        # --- PHASE 2: GEMINI AI FALLBACK ---
        try:
            print(f"🔄 Attempting Gemini 2.5 Flash fallback...")
            
            # Using original image for AI (AI is smart enough to handle noise)
            original_img = Image.open(io.BytesIO(image_bytes))
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            response = model.generate_content([
                "Extract ONLY the ingredients list from this image. Return just the comma separated text. Do not add markdown or explanations.", 
                original_img
            ])
            
            gem_text = response.text
            final_text = gem_text
            engine_used = "gemini_flash"
            print("✅ Gemini scan successful")
            
        except Exception as ai_error:
            print(f"❌ Both engines failed. Error: {ai_error}")
            return None

    return {
        "text": final_text,
        "engine": engine_used,
        "tesseract_output": tess_text,
        "gemini_output": gem_text
    }

