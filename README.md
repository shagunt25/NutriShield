# 🛡️ NutriShield - AI-Powered Allergen Detection System

**NutriShield** is a comprehensive backend system designed to ensure food safety for individuals with allergies. It combines **Computer Vision**, **Generative AI**, and **Real-time Market Data** to detect allergens and suggest instant, purchasable alternatives.

---

## 🚀 Key Features

### 1. 🔐 Secure Authentication
-   **Split Architecture**: Dedicated Signup and Login flows.
-   **Enterprise Security**: Passwords are **salted and hashed using Bcrypt** ($2b$).
-   **Duplicate Protection**: Prevents multiple accounts with the same email.

### 2. 👁️ Advanced Hybrid OCR Engine
-   **Stage 1: Computer Vision (OpenCV)**:
    -   *Grayscale Conversion*: Removes color noise.
    -   *Upscaling*: 2x resizing to enhance small text.
    -   *Otsu's Binarization*: Converts image to strict Black/White for high contrast.
-   **Stage 2: Optical Character Recognition**: Tesseract attempts to read the clean image.
-   **Stage 3: AI Fail-Safe**: If Tesseract fails, the system auto-switches to **Google Gemini 2.5 Flash** for deep-learning extraction.

### 3. 🛒 Smart Recommendations (Blinkit Integration)
-   If an unsafe product is found, the system identifies the specific allergen (e.g., "Milk").
-   It queries a knowledge base of real market substitutes (e.g., "Sofit Soya Milk").
-   **Dynamic Linking**: Generates direct **Blinkit search links**, allowing the user to buy the safe alternative instantly.

---

## 🛠️ Tech Stack

-   **Core**: Python 3.11, Flask (REST API)
-   **Database**: Supabase (PostgreSQL)
-   **AI & Vision**: Google Gemini 2.5 Flash, OpenCV (`cv2`), Tesseract OCR
-   **Security**: Bcrypt
-   **External APIs**: OpenFoodFacts, Blinkit (Deep links)

---

## ⚙️ Installation & Setup

### 1. Prerequisites
-   Python 3.10 or higher.
-   [Tesseract OCR Installed](https://github.com/UB-Mannheim/tesseract/wiki) (Note the path).
-   [Visual C++ Redistributable 2013](https://www.microsoft.com/en-us/download/details.aspx?id=40784) (Required for Barcode engine on Windows).

### 2. Install Libraries
Open your terminal in this folder and run:
```bash
pip install -r requirements.txt