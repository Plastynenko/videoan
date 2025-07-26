import streamlit as st
import json
from pathlib import Path
from PIL import Image
import base64
from io import BytesIO

# Пути к данным
DATA_DIR = Path(__file__).parent.parent / 'data'
VIDEO_FILE = DATA_DIR / 'movie.mp4'
SCENES_FILE = DATA_DIR / 'scenes_wrapped_fixed_jpg.json'
BANNER_FILE = DATA_DIR / 'banner.jpg'

st.set_page_config(layout="wide")

# Устанавливаем фон-баннер с затемнением
if BANNER_FILE.exists():
    banner_base64 = base64.b64encode(open(BANNER_FILE, "rb").read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
                        url("data:image/jpg;base64,{banner_base64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        .block-container {{
            background: rgba(0, 0, 0, 0.55);
            padding: 1.5rem;
            border-radius: 12px;
        }}
        .scene-container {{
            display: inline-block;
            text-align: center;
            margin: 3px;
            padding: 3px;
            border-radius: 6px;
            transition: border 0.3s ease-in-out;
            background: rgba(0, 0, 0, 0.5);
        }}
        .scene-container.active {{
            border: 3px solid #00cc00;
            transform: scale(1.05);
        }}
        .scene-caption {{
            font-size: 20px;
            font-weight: 700;
            margin-top: 5px;
            color: #ffffff;
        }}
        .scene-time {{
            font-size: 18px;
            color: #cccccc;
        }}
        .actor-block {{
            background: rgba(30, 30, 30, 0.8);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
            text-align: center;
            transition: transform 0.2s;
        }}
        .actor-block:hover {{
            transform: scale(1.05);
        }}
        .actor-caption {{
            font-size: 26px;
            font-weight: 700;
            color: #ffffff;
        }}
        h1, h2, h3, label, .stSlider {{
            color: #ffffff !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("Баннер не найден!")

st.title('🎬 К/Ф "Иван Васильевич меняет профессию" ')

def image_to_base64(img_path):
    img = Image.open(img_path).convert("RGB")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

MOVIE_DESCRIPTION = (
    "Инженер-изобретатель Тимофеев сконструировал машину времени, "
    "которая соединила его квартиру с XVI веком — точнее, с палатами "
    "государя Ивана Грозного. Туда-то и попадают тёзка царя пенсионер-общественник "
    "Иван Васильевич Бунша и квартирный вор Жорж Милославский, "
    "а сам великий государь оказывается в квартире Тимофеева."
)

# Загружаем сцены
if not SCENES_FILE.exists():
    st.error(f"Файл {SCENES_FILE} не найден!")
    SCENES = []
else:
    with open(SCENES_FILE, encoding='utf-8') as f:
        data = json.load(f)
        SCENES = data['scenes'] if isinstance(data, dict) else data

def get_scene_for_time(time_sec: float, scenes: list):
    for s in scenes:
        if float(s.get('start', 0)) <= time_sec < float(s.get('end', 0)):
            return s
    return scenes[-1] if scenes else None

def jump_to_scene(scene_start):
    st.session_state["current_time"] = float(scene_start)

if SCENES:
    max_time = float(SCENES[-1].get('end', 0))
    if "current_time" not in st.session_state:
        st.session_state["current_time"] = 0.0

    col_video, col_info = st.columns([2, 1])

    with col_video:
        if VIDEO_FILE.exists():
            st.video(str(VIDEO_FILE))
        else:
            st.warning("Видео файл не найден.")

        current_time = st.slider(
            "Время (сек.):",
            0.0,
            max_time,
            float(st.session_state["current_time"]),
            step=0.25
        )
        st.session_state["current_time"] = current_time
        current_scene = get_scene_for_time(current_time, SCENES)

        # Навигация
        col_nav1, col_nav2 = st.columns([1, 1])
        if col_nav1.button("⏮ Предыдущая сцена"):
            prev_scenes = [s for s in SCENES if s.get('start', 0) < current_time]
            if prev_scenes:
                jump_to_scene(prev_scenes[-1].get('start'))
        if col_nav2.button("Следующая сцена ⏭"):
            next_scenes = [s for s in SCENES if s.get('start', 0) > current_time]
            if next_scenes:
                jump_to_scene(next_scenes[0].get('start'))

    with col_info:
        if current_scene:
            st.subheader(f"Сцена {current_scene.get('number', '?')} из {len(SCENES)}")
            st.markdown(f"<div style='font-size:28px;'><b>Описание сцены:</b> {current_scene.get('description','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:24px;'><b>Время:</b> {current_scene.get('start',0)} - {current_scene.get('end',0)} сек.</div>", unsafe_allow_html=True)
            st.subheader("Актёры в сцене:")

            actors = current_scene.get('image_act_link', [])
            if isinstance(actors, str):
                actors = [actors]
            if actors:
                cols = st.columns(min(len(actors), 3))
                for idx, actor_path_str in enumerate(actors):
                    actor_path = (DATA_DIR / actor_path_str).resolve()
                    if actor_path.exists():
                        with cols[idx % len(cols)]:
                            st.markdown("<div class='actor-block'>", unsafe_allow_html=True)
                            st.image(Image.open(actor_path), width=110, caption=None, use_container_width=False)
                            st.markdown(f"<div class='actor-caption'>{Path(actor_path).stem}</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.write(f"Нет изображения для {actor_path_str}")
            else:
                st.write("Нет данных об актёрах.")

            with st.expander("Описание фильма", expanded=False):
                st.markdown(f"<div style='font-size:24px; text-align:justify;'><b>Описание фильма:</b> {MOVIE_DESCRIPTION}</div>", unsafe_allow_html=True)
        else:
            st.write("Нет данных о текущей сцене.")

    st.markdown("---")
    st.markdown("<div style='margin-top:-15px'></div>", unsafe_allow_html=True)
    st.subheader("Сцены:")

    cols = st.columns(len(SCENES))
    for i, scene in enumerate(SCENES):
        is_active = current_scene and scene.get('number') == current_scene.get('number')
        container_class = "scene-container active" if is_active else "scene-container"
        with cols[i]:
            img_path = (DATA_DIR / scene.get('image_link', '')).resolve()
            if img_path.exists():
                img_b64 = image_to_base64(img_path)
                st.markdown(
                    f'<div class="{container_class}">'
                    f'<img src="data:image/png;base64,{img_b64}" width="120">'
                    f'<div class="scene-caption">Сцена {scene.get("number")}</div>'
                    f'<div class="scene-time">{scene.get("start",0)}–{scene.get("end",0)} сек.</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                st.write(f"Сцена {scene.get('number')}")

            if st.button(f"▶ {scene.get('number')}", key=f"btn_scene_{i}"):
                jump_to_scene(scene.get('start'))
else:
    st.warning("Нет данных о сценах для отображения.")
