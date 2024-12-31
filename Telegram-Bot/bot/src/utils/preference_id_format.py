from core.constants import (
    CATEGORY_ID_DICT,
    LOCATION_ID_DICT)

def _pretifer(preference: dict) -> str:
    """
        description: Takes a preference dict and returns a pretified string.
        
        Args:
            preference (dict): A preference dictionary.
    """
    s = ""
    if preference.get("category"):
        if preference.get("subcategory"):
            s += f"{preference.get('category')} > {preference.get('subcategory')}"
        else:
            s += f"{preference.get('category')}"
    if preference.get("state"):
        if preference.get("city"):
            s += f" in {preference.get('city')}, {preference.get('state')}"
        else:
            s += f" in {preference.get('state')}"
    return s

def preference_id_to_name(preference_ids: list, pretify: bool = False) -> list[dict|str]:
    """
        description: Takes a list of preference ids and returns a list of preference names.
        
        Args:
            preference_ids (list): A list of preference ids in dict format.
            pretify (bool): If True, the results will be in string format.
    """
    # example input: 
    # c1#c2#l1#l2 -> category c1, subcategory c2, state l1, city l2
    # c1#c2 -> category c1, subcategory c2
    # c1#l1#l2 -> category c1, state l1, city l2

    for preference in preference_ids:
        preference_ids = preference.split("#")
        category_id = None
        state_id = None
        pref_dict = {}
        result = list()
        for id in preference_ids:
            if id.startswith("c"):
                if CATEGORY_ID_DICT.get(id):
                    category_id = id
                    pref_dict["category"] = CATEGORY_ID_DICT.get(id)
                else:
                    pref_dict["subcategory"] = CATEGORY_ID_DICT.get(f"{category_id}#{id}")
            elif id.startswith("l"):
                if LOCATION_ID_DICT.get(id):
                    state_id = id
                    pref_dict["state"] = LOCATION_ID_DICT.get(id)
                else:
                    pref_dict["city"] = LOCATION_ID_DICT.get(f"{state_id}#{id}")
            if pretify:
                result.append(_pretifer(pref_dict))
            else:
                result.append(pref_dict)
        return result

