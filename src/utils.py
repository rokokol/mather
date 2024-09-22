import json
import os


def load_json_dict(file_path: str) -> dict:
    if not os.path.exists(file_path):
        # Если файл не существует, создаем пустой словарь и сохраняем его
        with open(file_path, 'w') as file:
            json.dump({}, file)

        return {}
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)


def serialize_to_json(data, file_path: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

