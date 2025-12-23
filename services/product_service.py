import requests
from pyzbar.pyzbar import decode
from PIL import Image, ImageEnhance
import io

def decode_barcode(image_bytes):
    """Reads barcode from image (With Image Enhancement)"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # TRICK: Convert to grayscale and sharpen image to help reader
        image = image.convert('L') 
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        decoded = decode(image)
        if not decoded:
            return None
        return decoded[0].data.decode("utf-8")
    except Exception as e:
        print(f"Error decoding barcode: {e}")
        return None

def fetch_product_metadata(barcode):
    """Gets product name and ingredients from OpenFoodFacts"""
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        headers = {"User-Agent": "NutriShield-StudentProject/1.0"}
        res = requests.get(url, headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            if data.get('status') == 1:
                prod = data['product']
                return {
                    "name": prod.get("product_name", "Unknown Product"),
                    "brand": prod.get("brands", "Unknown Brand"),
                    "ingredients": prod.get("ingredients_text", ""),
                    "image": prod.get("image_url", "")
                }
    except Exception:
        pass
    return None

def get_alternatives(found_allergens):
    """
    Matches detected triggers to healthy Blinkit replacements.
    """
    suggestions = []
    # Map allergen categories to specific Blinkit queries
    category_map = {
        "milk": [{"name": "Lactose-Free Milk", "q": "lactose free milk"}, {"name": "Oat Milk", "q": "oat milk"}],
        "egg": [{"name": "Eggless Mayo", "q": "eggless mayonnaise"}, {"name": "Vegan Egg Substitute", "q": "vegan egg"}],
        "wheat": [{"name": "Gluten-Free Atta", "q": "gluten free flour"}, {"name": "Quinoa", "q": "quinoa"}],
        "peanut": [{"name": "Almond Butter", "q": "almond butter"}, {"name": "Sunflower Seeds", "q": "sunflower seeds"}],
        "soy": [{"name": "Coconut Aminos", "q": "coconut aminos"}, {"name": "Chickpea Miso", "q": "miso alternative"}]
    }

    found_lower = [f.lower() for f in found_allergens]
    
    for category, products in category_map.items():
        # If any found allergen (like 'casein') is part of a category (like 'milk')
        if any(category in f for f in found_lower):
            for p in products:
                suggestions.append({
                    "name": p['name'],
                    "reason": f"Safe alternative for {category} allergy",
                    "link": f"https://blinkit.com/s/?q={p['q'].replace(' ', '%20')}"
                })

    # Generic fallback
    if not suggestions and found_allergens:
        suggestions.append({
            "name": "Healthy Organic Snacks",
            "reason": "Safe general recommendation",
            "link": "https://blinkit.com/s/?q=healthy%20organic%20snacks"
        })

    return suggestions[:4]