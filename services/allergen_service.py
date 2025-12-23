from utils.db import supabase

def check_safety(ingredients_text, user_profile):
    """
    Advanced matching: Uses Canonical Database to find hidden allergens.
    """
    if not ingredients_text:
        return False, ["No ingredients found"]

    # 1. Collect user's reported allergens
    reported_allergens = []
    if user_profile.get('common_allergens'):
        reported_allergens.extend(user_profile['common_allergens'])
    if user_profile.get('other_allergens_raw'):
        reported_allergens.extend([x.strip() for x in user_profile['other_allergens_raw'].split(',') if x.strip()])

    # 2. Expand: Query the Canonical Database for synonyms
    search_terms = set()
    for allergen in reported_allergens:
        search_terms.add(allergen.lower()) # Add the base name
        try:
            # Match user input to a canonical name
            res = supabase.table('canonical_allergens').select("synonyms").ilike('name', allergen).execute()
            if res.data:
                # Add all synonyms to our search list
                syns = res.data[0]['synonyms']
                search_terms.update([s.lower() for s in syns])
        except Exception as e:
            print(f"⚠️ Search expansion error: {e}")

    # 3. Analyze ingredients text
    found_triggers = []
    text_to_scan = ingredients_text.lower()
    
    for term in search_terms:
        # Use word boundary-like checking to avoid partial matches (e.g., 'nut' in 'nutrition')
        if term in text_to_scan:
            found_triggers.append(term)

    # 4. Final results
    is_safe = len(found_triggers) == 0
    return is_safe, list(set(found_triggers)) # Unique triggers only