from db.db_manager import DB
from utils.config import Config

if __name__ == '__main__':
    config = Config()
    db = DB(config)
    for user in db.users_schema.get_users_by_names(["SDR"]):
        print(user.id, user.name)