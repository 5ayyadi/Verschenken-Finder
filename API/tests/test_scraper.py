from app.scraper import find_offers

def test_find_offers_no_filters():
    offers = find_offers()
    print(offers)
    assert len(offers) >= 1
   

def test_find_offers_with_category():
    offers = find_offers(category="Lampen & Licht")
    assert len(offers) >= 1
   

def test_find_offers_with_city():
    offers = find_offers(state_city=("Rheinland-Pfalz","Mainz"))
    assert len(offers) >= 1

def test_find_offers_with_category_and_city():
    offers = find_offers(state_city=("Rheinland-Pfalz","Mainz"), category="Lampen & Licht")
    assert len(offers) >= 1

def test_find_offers_no_verschenken():
    """Tests case where no "Zu verschenken" offers are present."""
    offers = find_offers(state_city=("Rheinland-Pfalz","Mainz"), category="Reparaturen & Dienstleistungen")
    assert len(offers) == 0
