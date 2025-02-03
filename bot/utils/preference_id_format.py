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
        if preference.get("sub_category"):

            s += f"{preference.get('category')
                    } > {preference.get('sub_category')}"
        else:

            s += f"{preference.get('category')}"

    if preference.get("state"):
        if preference.get("city"):
            if s:
                s += f" in {preference.get('city')}, {preference.get('state')}"

            else:
                s += f"{preference.get('city')}, {preference.get('state')}"
        else:
            if s:
                s += f" in {preference.get('state')}"
            else:
                s += f"{preference.get('state')}"
    return s


def preference_id_to_name(preference_ids: list, pretify: bool = False) -> list[dict | str]:
    """
        description: Takes a list of preference ids and returns a list of preference names.

        Args:
            preference_ids (list): A list of preference ids in dict format.
            pretify (bool): If True, the results will be in string format.
    """
    result = []

    for item in preference_ids:
        category_id = item.get("category_id")
        state_id = item.get("state_id")
        city_id = item.get("city_id")
        sub_category_id = item.get("sub_category_id")

        category_name = CATEGORY_ID_DICT.get(category_id, "")
        sub_category_name = CATEGORY_ID_DICT.get(
            f"{category_id}#{sub_category_id}", "")
        state_name = LOCATION_ID_DICT.get(state_id, "")
        city_name = LOCATION_ID_DICT.get(
            f"{state_id}#{city_id}", "") if city_id else ""

        pref_dict = {
            # "category": category_name,
            "category": category_name,
            "sub_category": sub_category_name,
            "state": state_name,
            "city": city_name,
            "category_id": category_id,
            "sub_category_id": sub_category_id,
            "state_id": state_id,
            "city_id": city_id,
        }
        if pretify:
            result.append(_pretifer(pref_dict))
        else:
            result.append(pref_dict)

    return result if result else None

    # result = list()
    # for id in user_prefrence_ids:
    #     if id.startswith("c"):
    #         if CATEGORY_ID_DICT.get(id):
    #             category_id = id
    #             pref_dict["category"] = CATEGORY_ID_DICT.get(id)
    #         else:
    #             pref_dict["subcategory"] = CATEGORY_ID_DICT.get(
    #                 f"{category_id}#{id}")
    #     elif id.startswith("l"):
    #         if LOCATION_ID_DICT.get(id):
    #             state_id = id
    #             pref_dict["state"] = LOCATION_ID_DICT.get(id)
    #         else:
    #             pref_dict["city"] = LOCATION_ID_DICT.get(
    #                 f"{state_id}#{id}")
    #     if pretify:
    #         result.append(_pretifer(pref_dict))
    #     else:
    #         result.append(pref_dict)
