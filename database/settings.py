from database import db

users_collection = db["settings"]

USER_SETTINGS = ["uploader"]


def update_user_setting(user_id, setting_key, setting_value):
    if setting_key in USER_SETTINGS:
        update_result = users_collection.update_one(
            {"_id": user_id},
            {"$set": {f"settings.{setting_key}": setting_value}},
            upsert=True,
        )
        if update_result.modified_count > 0 or update_result.upserted_id is not None:
            return
        else:
            return
    else:
        return


def get_user_settings(user_id):
    user_doc = users_collection.find_one({"_id": user_id})
    if user_doc:
        return user_doc.get("settings", {})
    return {}
