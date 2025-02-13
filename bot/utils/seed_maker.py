from core.redis_client import RedisClient


def seed_data():
    """Seed Redis with test data."""
    user_ids = ["6794168529" , "7902410444", "333949195"]
    categorys = {
       "c161#c176" : "Elektronik,Haushaltsgerate",
        "c80#c86": "Haus & Garten, Küche & Esszimmer",
        "c80#c82": "Haus & Garten, Lampen & Licht",
        "c80#c81": "Haus & Garten, Schlafzimmer",
    }
    locations = {
        "l4938#l5315": "Mainz",
        "l4279#l4897": "Wiesbaden",
        "l285#l382": "Saarbrücken",
        "l4279#l4888": "Darmstadt",
    }
        
    
    # Connect to db0
    RedisClient.add_user_preference()
    RedisClient.set_chat_ids()
    RedisClient.set("7902410444", '["l4938_l5315#c80_c86", "l3331_l17083#c80_c82"]', ex=-1)
    RedisClient.set("6794168529", '["l4938_l5315#c80_c86"]', ex=-1)
    
    # Connect to db1
    RedisClient.select(1)
    RedisClient.set("l4938_l5315#c80_c86", '["6794168529", "7902410444"]', ex=-1)
    RedisClient.set("l3331_l17083#c80_c82", '["7902410444"]', ex=-1)
    # Seed additional data for db0
    RedisClient.select(0)
    RedisClient.set("333949195", '["l4279_l4897#c80_c81"]', ex=-1)
    
    # Seed additional data for db1
    RedisClient.select(1)
    RedisClient.set("l4279_l4897#c80_c81", '["333949195"]', ex=-1)