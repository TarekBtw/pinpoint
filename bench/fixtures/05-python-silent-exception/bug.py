import json


def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def get_max_users(path):
    config = load_config(path)
    return config["max_users"]


if __name__ == "__main__":
    print(get_max_users("config.json"))
