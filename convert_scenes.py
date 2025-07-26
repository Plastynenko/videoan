import json, pathlib, sys

src = pathlib.Path('data/scenes.json')
dst = pathlib.Path('data/scenes.json')   # или scenes_list.json

data = json.load(src.open(encoding='utf-8'))
if isinstance(data, dict):
    try:
        items = sorted(data.items(), key=lambda kv: int(kv[0]))
    except ValueError:
        items = data.items()
    data = [scene for _, scene in items]

dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Сохранено {len(data)} сцен в', dst)