from core.constants import GENERAL_KEYBOARD, CITIES_DICT

def pagination(page_number: int, state: str) -> list[list[str]]:
    cities = list(CITIES_DICT.get(state, {}).get("cities", {}).keys())
    start_index = page_number * 50
    end_index = start_index + 50
    cities_keyboard = GENERAL_KEYBOARD.copy()
    cities_keyboard.append([f"All Cities of {state} State"])
    next_50_cities = cities[start_index:end_index]
    cities_keyboard += [next_50_cities[i:i + 2] for i in range(0, len(next_50_cities), 2)]
    if end_index < len(cities):
        cities_keyboard.append(["Next Page"])
    if start_index > 0:
        cities_keyboard.append(["Previous Page"])
    return cities_keyboard