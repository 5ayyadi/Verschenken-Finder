from core.redis_client import RedisClient


def seed_data():
    """Seed Redis with test data."""
    user_ids = ["6794168529", "7902410444", "333949195"]
    categories = {
        "Haushalt": "c161#c176",
        "Esszimmer": "c80#c86",
        "Licht": "c80#c82",
        "Schlafzimmer": "c80#c81",
    }
    locations = {
        "Mainz": "l4938#l5315",
        "Wiesbaden": "l4279#l4897",
        "Saarbrücken": "l285#l382",
        "Darmstadt": "l4279#l4888",
    }
    for user_id in user_ids:
        RedisClient.add_user_preference(
            user_id=user_id,
            category_id=categories.get("Haushalt").split("#")[0],
            sub_category_id=categories.get("Haushalt").split("#")[1],
            state_id=locations.get("Mainz").split("#")[0],
            city_id=locations.get("Mainz").split("#")[1]
        )

        RedisClient.set_chat_ids(
            user_id=user_id,
            category_id=categories.get("Haushalt").split("#")[0],
            sub_category_id=categories.get("Haushalt").split("#")[1],
            state_id=locations.get("Mainz").split("#")[0],
            city_id=locations.get("Mainz").split("#")[1]
        )
        
        if user_id == "333949195":
            # Add Esszimmer in Darmstadt for this user
            RedisClient.add_user_preference(
                user_id=user_id,
                category_id=categories.get("Esszimmer").split("#")[0],
                sub_category_id=categories.get("Esszimmer").split("#")[1],
                state_id=locations.get("Darmstadt").split("#")[0],
                city_id=locations.get("Darmstadt").split("#")[1]
            )
            
            RedisClient.set_chat_ids(
                user_id=user_id,
                category_id=categories.get("Esszimmer").split("#")[0],
                sub_category_id=categories.get("Esszimmer").split("#")[1],
                state_id=locations.get("Darmstadt").split("#")[0],
                city_id=locations.get("Darmstadt").split("#")[1]
            )
            
        if user_id == "7902410444":
            # Add Licht in Wiesbaden for this user
            RedisClient.add_user_preference(
                user_id=user_id,
                category_id=categories.get("Licht").split("#")[0],
                sub_category_id=categories.get("Licht").split("#")[1],
                state_id=locations.get("Wiesbaden").split("#")[0],
                city_id=locations.get("Wiesbaden").split("#")[1]
            )
            
            RedisClient.set_chat_ids(
                user_id=user_id,
                category_id=categories.get("Licht").split("#")[0],
                sub_category_id=categories.get("Licht").split("#")[1],
                state_id=locations.get("Wiesbaden").split("#")[0],
                city_id=locations.get("Wiesbaden").split("#")[1]
            )
            
        else:
            # Add Schlafzimmer in Saarbrücken for this users
            RedisClient.add_user_preference(
                user_id=user_id,
                category_id=categories.get("Schlafzimmer").split("#")[0],
                sub_category_id=categories.get("Schlafzimmer").split("#")[1],
                state_id=locations.get("Saarbrücken").split("#")[0],
                city_id=locations.get("Saarbrücken").split("#")[1]
            )
            
            RedisClient.set_chat_ids(
                user_id=user_id,
                category_id=categories.get("Schlafzimmer").split("#")[0],
                sub_category_id=categories.get("Schlafzimmer").split("#")[1],
                state_id=locations.get("Saarbrücken").split("#")[0],
                city_id=locations.get("Saarbrücken").split("#")[1]
            )