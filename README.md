# 🛡️ NutriShield: AI-Powered Allergen Defense

**NutriShield** is a comprehensive full-stack health-tech application designed to protect individuals from accidental allergen exposure. By combining Computer Vision, Generative AI, and real-time product databases, NutriShield analyzes food labels to detect hidden triggers and suggests safe, accessible alternatives.

---

## 👥 Meet the Team & Contributions

| Member | Role | Key Working & Implementation |
| :--- | :--- | :--- |
| **Shagun Tiwari** | **Lead Backend & OCR Engineer** | Developed the dual-engine OCR pipeline and managed full system integration within the Flask framework. |
| **Sagun Yadav** | **Frontend Developer** | Built the responsive user interface and dashboard using modern CSS/JS for a seamless user experience. |
| **Sanya Dubey** | **Security & Database Lead** | Orchestrated the Supabase schema and implemented secure authentication using Bcrypt password hashing. |
| **Saumya Mishra** | **Product Strategist** | Engineered the safe alternative recommendation engine with automated Blinkit purchase integration. |
| **Saumya Singh** | **Barcode Logic Engineer** | Implemented image-enhanced barcode decoding and integrated the OpenFoodFacts API for metadata retrieval. |

---

## 🌟 Key Features

* **🔐 Secure Ecosystem:** A robust authentication system utilizing **Bcrypt** for password hashing and **Supabase** for secure cloud storage of user profiles and history.
* **📸 Advanced OCR Pipeline:** Uses **OpenCV** for image preprocessing (Denoising, Otsu’s Thresholding) to enhance text clarity before extraction via **Tesseract**.
* **🧠 AI Fallback Logic:** Automatically triggers **Google Gemini 2.5 Flash** if standard OCR confidence is low, ensuring high-accuracy ingredient reading even from blurry images.
* **🔍 Barcode Intelligence:** Decodes EAN-13 barcodes to instantly pull ingredient lists and brand data from global databases.
* **🛒 Smart Replacements:** Identifies unsafe ingredients and immediately suggests allergen-free alternatives with direct shopping links to **Blinkit**.

---

## 🛠️ Tech Stack

### **Backend**
* **Framework:** Flask (Python)
* **Database:** Supabase (PostgreSQL)
* **AI/ML:** Google Generative AI (Gemini API)
* **Computer Vision:** OpenCV (`opencv-python`), Pytesseract, Pyzbar

### **Frontend**
* **Languages:** HTML5, CSS3, JavaScript (ES6+)
* **Styling:** Poppins Typography, FontAwesome Icons

---

## 🏗️ Project Structure

Based on the modular architecture of the repository:

├── services/
│   ├── allergen_service.py   # Synonym matching & safety logic
│   ├── ocr_service.py        # OpenCV pipeline & Gemini integration
│   ├── product_service.py    # Barcode decoding & OpenFoodFacts API
├── utils/
│   └── db.py                 # Supabase client & environment config
├── app.py                    # Flask API routes & Authentication logic
├── frontend.html             # Single-page application interface
├── requirements.txt          # Project dependencies
└── .gitignore                # Version control exclusions 

---

## 🚀 Getting Started

### 1. **Prerequisites**
Python 3.10+
Tesseract OCR installed on your system
A Supabase project and Google Gemini API Key


### 2. **Installation**

Clone the repository:
git clone [https://github.com/your-username/NutriShield.git](https://github.com/your-username/NutriShield.git)
cd NutriShield

Install Dependencies:
pip install -r requirements.txt
Configure Environment: Create a .env file in the root and add your keys:

*Code snippet*
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
GEMINI_API_KEY=your_gemini_key
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe


### 3. **Running the Application**

Start the Flask backend: python app.py
Open frontend.html in your preferred browser.
Developed by Team NutriShield Empowering safer food choices through Artificial Intelligence.
