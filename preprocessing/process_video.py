import json
import cv2
import pickle
import argparse
from tqdm import tqdm
import face_recognition

def process_scene(scene, video_path, classifier, fps_sample=1.0):
    start_sec = float(scene.get('start', 0))
    end_sec = float(scene.get('end', 0))
    print(f"[DEBUG] Start scene {scene.get('number', '?')} from {start_sec} to {end_sec} sec")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {video_path}")
        return []

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    start_frame = int(start_sec * video_fps)
    end_frame = int(end_sec * video_fps)
    step = max(int(video_fps / fps_sample), 1)

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frame_num = start_frame
    results = []

    while frame_num < end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model='hog')
        face_encs = face_recognition.face_encodings(rgb_frame, face_locations)

        for (_, _, _, _), face_enc in zip(face_locations, face_encs):
            try:
                pred_label = classifier.predict([face_enc])[0]
                results.append({"scene": scene.get('number', '?'), "frame": frame_num, "actor": pred_label})
                print(f"[DEBUG] Scene {scene.get('number', '?')} Frame {frame_num}: {pred_label}")
            except Exception as e:
                print(f"[ERROR] Predict error at frame {frame_num}: {e}")
        frame_num += step
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    cap.release()
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', required=True)
    parser.add_argument('--scenes', default='data/scenes_wrapped_fixed.json')
    parser.add_argument('--classifier', required=True)
    parser.add_argument('--fps', type=float, default=1.0)
    parser.add_argument('--out', type=str, default='all_scenes_results.json')
    args = parser.parse_args()

    print(f"[DEBUG] Loading classifier from {args.classifier}")
    classifier = pickle.load(open(args.classifier, 'rb'))

    print(f"[DEBUG] Loading scenes from {args.scenes}")
    scenes_data = json.load(open(args.scenes, 'r', encoding='utf-8'))
    scenes = scenes_data['scenes'] if isinstance(scenes_data, dict) else scenes_data

    print(f"[DEBUG] Video: {args.video}, Scenes count: {len(scenes)}")

    all_results = []
    for scene in tqdm(scenes, desc="Scenes"):
        all_results.extend(process_scene(scene, args.video, classifier, fps_sample=args.fps))

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"[DEBUG] All results saved to {args.out}")

if __name__ == "__main__":
    main()
