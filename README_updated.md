# Video Scene Analyzer – Quickstart Guide

## Overview
**Video Scene Analyzer** — это инструмент для анализа видеофрагментов, распознавания актёров и отображения сцен с интерактивным интерфейсом на базе Streamlit.

## Features
- Автоматическое разделение видео на сцены.
- Детекция и классификация актёров по изображениям.
- Визуализация сцен и актёров с интерактивным интерфейсом.
- Возможность запуска как локально, так и в Docker.

---

## 1. Prerequisites
- **Python 3.9+**
- **ffmpeg** (для декодирования видео)
- **NVIDIA GPU + CUDA 11.8** (опционально для ускорения)
- **Docker** (если хотите запустить проект в контейнере)

---

## 2. Установка и запуск локально

### 2.1 Создание виртуального окружения
```bash
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

### 2.2 Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2.3 Подготовка данных
- Поместите ваш видеофайл в `data/movie.mp4`.
- Разместите изображения актёров в `data/actors/<actor_name>/*.jpg`.

### 2.4 Обучение классификатора лиц
```bash
python preprocessing/train_face_classifier.py --actors_dir data/actors --out models/actor_classifier.pkl
```

### 2.5 Анализ видео
```bash
python preprocessing/process_video.py --video data/movie.mp4 --scenes data/scenes.json --classifier models/actor_classifier.pkl
```

### 2.6 Запуск веб-интерфейса
```bash
streamlit run app/app.py
```
Интерфейс будет доступен по адресу [http://localhost:8501](http://localhost:8501).

---

## 3. Запуск в Docker

### 3.1 Создание Docker-образа
```bash
docker build -t video-scene-analyzer .
```

### 3.2 Запуск контейнера
Для CPU:
```bash
docker run -p 8501:8501 -v $PWD/data:/app/data video-scene-analyzer
```
Для GPU (при наличии CUDA):
```bash
docker run --gpus all -p 8501:8501 -v $PWD/data:/app/data video-scene-analyzer
```

---

## 4. Публикация на GitHub
1. Создайте новый репозиторий на GitHub.
2. Добавьте все файлы проекта:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Video Scene Analyzer"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
3. Проверьте, что `README.md`, `requirements.txt` и `Dockerfile` загружены.

---

## 5. Рекомендации по улучшению
- Добавьте примеры данных (`data/sample_movie.mp4`) для демонстрации.
- Создайте **GitHub Actions** для автоматической сборки Docker-образа.
- Разместите проект на [Streamlit Community Cloud](https://streamlit.io/cloud) для онлайн-доступа.

---

**Автор:** Команда разработки Video Scene Analyzer.
