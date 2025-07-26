
#!/usr/bin/env python
"""Train simple KNN classifier on actor face embeddings."""
import argparse, pickle, pathlib, numpy as np
import face_recognition
from sklearn.neighbors import KNeighborsClassifier
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--actors_dir', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--n_neighbors', type=int, default=3)
args = parser.parse_args()

encodings, labels = [], []
actors_path = pathlib.Path(args.actors_dir)
for actor_dir in actors_path.iterdir():
    if not actor_dir.is_dir():
        continue
    for img_path in actor_dir.glob('*.jpg'):
        img = face_recognition.load_image_file(img_path)
        face_enc = face_recognition.face_encodings(img)
        if face_enc:
            encodings.append(face_enc[0])
            labels.append(actor_dir.name)

if not encodings:
    raise RuntimeError('No face encodings found. Check your actor images.')

print(f'Training on {len(encodings)} face samples from {len(set(labels))} actors')
knn = KNeighborsClassifier(n_neighbors=args.n_neighbors, metric='euclidean')
knn.fit(encodings, labels)

pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
with open(args.out, 'wb') as f:
    pickle.dump(knn, f)

print('Classifier saved to', args.out)
