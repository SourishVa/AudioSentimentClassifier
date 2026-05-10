"""
Audio Sentiment Classification
CREMA-D subset — 49 files, 1 speaker, 6 emotions
Models: Logistic Regression, Naive Bayes, Random Forest, SVM, Gradient Boosting
"""

import os, warnings, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import librosa
from pathlib import Path
from collections import Counter

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import (classification_report, confusion_matrix,
                              ConfusionMatrixDisplay, accuracy_score)
from sklearn.decomposition import PCA

warnings.filterwarnings("ignore")

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR = Path(r"C:\Users\neel4\AudioSentimentClassifier\SubSetAudioWAV")
OUT_DIR = Path(r"C:\Users\neel4\AudioSentimentClassifier\outputs")
OUT_DIR.mkdir(exist_ok=True)
SR        = 22050
N_MFCC    = 40
LABEL_MAP = {"ANG": "Angry", "DIS": "Disgust", "FEA": "Fear",
             "HAP": "Happy",  "NEU": "Neutral", "SAD": "Sad"}

# ── 1. Feature Extraction ─────────────────────────────────────────────────────
def extract_features(path):
    y, sr = librosa.load(path, sr=SR)

    # MFCCs (mean + std) → 80
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
    mfcc_feat = np.hstack([mfcc.mean(axis=1), mfcc.std(axis=1)])

    # Delta MFCCs → 80
    delta = librosa.feature.delta(mfcc)
    delta_feat = np.hstack([delta.mean(axis=1), delta.std(axis=1)])

    # Chroma → 24
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_feat = np.hstack([chroma.mean(axis=1), chroma.std(axis=1)])

    # Mel spectrogram → 256
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_feat = np.hstack([mel_db.mean(axis=1), mel_db.std(axis=1)])

    # Spectral features → 12
    sc   = librosa.feature.spectral_centroid(y=y, sr=sr)
    sb   = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    sr_  = librosa.feature.spectral_rolloff(y=y, sr=sr)
    zcr  = librosa.feature.zero_crossing_rate(y)
    rms  = librosa.feature.rms(y=y)
    spec = np.array([sc.mean(), sc.std(), sb.mean(), sb.std(),
                     sr_.mean(), sr_.std(), zcr.mean(), zcr.std(),
                     rms.mean(), rms.std()])

    # Pitch stats → 4
    f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz("C2"),
                             fmax=librosa.note_to_hz("C7"))
    f0_vals  = f0[~np.isnan(f0)]
    pitch = np.array([f0_vals.mean() if len(f0_vals) else 0,
                      f0_vals.std()  if len(f0_vals) else 0,
                      f0_vals.max()  if len(f0_vals) else 0,
                      f0_vals.min()  if len(f0_vals) else 0])

    return np.hstack([mfcc_feat, delta_feat, chroma_feat, mel_feat, spec, pitch])


def extract_f0_contour(path):
    """Return (times, f0) for prosody plotting."""
    y, sr = librosa.load(path, sr=SR)
    f0, voiced, _ = librosa.pyin(y, fmin=librosa.note_to_hz("C2"),
                                   fmax=librosa.note_to_hz("C7"))
    times = librosa.times_like(f0, sr=sr)
    return times, f0


print("Extracting features …")
records = []
for i, wav in enumerate(sorted(DATA_DIR.glob("*.wav"))):
    print(f"  Processing {i+1}/48: {wav.name}")
    parts = wav.stem.split("_")
    raw_label = parts[2]
    label = LABEL_MAP.get(raw_label, raw_label)
    feats = extract_features(wav)
    records.append({"file": wav.name, "label": label, "features": feats})

df_meta = pd.DataFrame([{"file": r["file"], "label": r["label"]} for r in records])
X = np.vstack([r["features"] for r in records])
y_raw = [r["label"] for r in records]
le = LabelEncoder()
y = le.fit_transform(y_raw)
classes = le.classes_
print(f"  {len(records)} samples  |  {X.shape[1]} features  |  {len(classes)} classes")
print("  Distribution:", Counter(y_raw))

# ── 2. Models ─────────────────────────────────────────────────────────────────
models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=2000, C=1.0, random_state=42))
    ]),
    "Naive Bayes": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GaussianNB())
    ]),
    "Random Forest": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=200, random_state=42))
    ]),
    "SVM (RBF)": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", SVC(kernel="rbf", C=10, gamma="scale", random_state=42,
                    decision_function_shape="ovr"))
    ]),
    "Gradient Boosting": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(n_estimators=150, learning_rate=0.1,
                                           max_depth=3, random_state=42))
    ]),
}

# Leave-one-out is most robust with tiny datasets; use 7-fold stratified CV
cv = StratifiedKFold(n_splits=7, shuffle=True, random_state=42)
scoring = ["accuracy", "f1_macro", "f1_weighted"]

results = {}
print("\nCross-validation (7-fold stratified) …")
for name, pipe in models.items():
    scores = cross_validate(pipe, X, y, cv=cv, scoring=scoring, n_jobs=-1)
    results[name] = {
        "acc_mean":  scores["test_accuracy"].mean(),
        "acc_std":   scores["test_accuracy"].std(),
        "f1_macro":  scores["test_f1_macro"].mean(),
        "f1_weighted": scores["test_f1_weighted"].mean(),
    }
    print(f"  {name:<22} acc={results[name]['acc_mean']:.3f}±{results[name]['acc_std']:.3f}"
          f"  F1-macro={results[name]['f1_macro']:.3f}")

# ── 3. Full-data confusion matrix for best model ───────────────────────────────
best_name = max(results, key=lambda k: results[k]["acc_mean"])
best_pipe  = models[best_name]
best_pipe.fit(X, y)
y_pred = best_pipe.predict(X)

print(f"\nBest model (train-set report for reference): {best_name}")
print(classification_report(y, y_pred, target_names=classes))

# ── 4. Plots ───────────────────────────────────────────────────────────────────
palette = ["#4C72B0","#DD8452","#55A868","#C44E52","#8172B2","#937860"]

# --- Fig 1: Model comparison bar chart ---
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
names   = list(results.keys())
accs    = [results[n]["acc_mean"] for n in names]
stds    = [results[n]["acc_std"]  for n in names]
f1s     = [results[n]["f1_macro"] for n in names]

axes[0].barh(names, accs, xerr=stds, color=palette[:len(names)], alpha=0.85, capsize=5)
axes[0].set_xlabel("CV Accuracy (7-fold)", fontsize=12)
axes[0].set_title("Model Comparison — Accuracy", fontsize=13, fontweight="bold")
axes[0].axvline(max(accs), color="red", linestyle="--", alpha=0.5, label=f"Best: {max(accs):.3f}")
axes[0].legend(); axes[0].set_xlim(0, 1)

axes[1].barh(names, f1s, color=palette[:len(names)], alpha=0.85)
axes[1].set_xlabel("CV F1-Macro (7-fold)", fontsize=12)
axes[1].set_title("Model Comparison — F1 Macro", fontsize=13, fontweight="bold")
axes[1].axvline(max(f1s), color="red", linestyle="--", alpha=0.5, label=f"Best: {max(f1s):.3f}")
axes[1].legend(); axes[1].set_xlim(0, 1)

plt.tight_layout()
plt.savefig(OUT_DIR / "model_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved model_comparison.png")

# --- Fig 2: Confusion matrix of best model ---
cm = confusion_matrix(y, y_pred)
fig, ax = plt.subplots(figsize=(8, 6))
disp = ConfusionMatrixDisplay(cm, display_labels=classes)
disp.plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title(f"Confusion Matrix — {best_name} (full training data)", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(OUT_DIR / "confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved confusion_matrix.png")

# --- Fig 3: PCA 2D scatter of feature space coloured by emotion ---
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(StandardScaler().fit_transform(X))
fig, ax = plt.subplots(figsize=(8, 6))
for i, cls in enumerate(classes):
    idx = np.where(y == i)
    ax.scatter(X_pca[idx, 0], X_pca[idx, 1], label=cls,
               color=palette[i], s=80, alpha=0.85, edgecolors="w", linewidths=0.5)
ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
ax.set_title("PCA of Audio Features (coloured by emotion)", fontsize=13, fontweight="bold")
ax.legend(title="Emotion", bbox_to_anchor=(1.01, 1), loc="upper left")
plt.tight_layout()
plt.savefig(OUT_DIR / "pca_scatter.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved pca_scatter.png")

# --- Fig 4: F0 Pitch Contours per emotion ---
fig, axes = plt.subplots(2, 3, figsize=(15, 7), sharey=False)
axes = axes.flatten()
emotion_files = {}
for wav in sorted(DATA_DIR.glob("*.wav")):
    lbl = LABEL_MAP.get(wav.stem.split("_")[2], "?")
    emotion_files.setdefault(lbl, []).append(wav)

for i, (emo, color) in enumerate(zip(classes, palette)):
    ax = axes[i]
    for wav in emotion_files.get(emo, []):
        t, f0 = extract_f0_contour(wav)
        ax.plot(t, f0, alpha=0.5, color=color, linewidth=1)
    ax.set_title(emo, fontsize=12, fontweight="bold")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("F0 (Hz)")
    ax.set_ylim(50, 400)
    ax.grid(alpha=0.3)
fig.suptitle("F0 Pitch Contours by Emotion Class", fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(OUT_DIR / "f0_contours.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved f0_contours.png")

# --- Fig 5: MFCC mean heatmap per class ---
mfcc_means = {}
for emo in classes:
    idxs = [i for i, r in enumerate(records) if r["label"] == emo]
    mfcc_means[emo] = X[idxs, :N_MFCC].mean(axis=0)   # first 40 = MFCC means

df_mfcc = pd.DataFrame(mfcc_means, index=[f"MFCC-{i+1}" for i in range(N_MFCC)])
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(df_mfcc, cmap="coolwarm", center=0, ax=ax,
            linewidths=0.3, cbar_kws={"label": "Mean Coefficient"})
ax.set_title("Mean MFCC Coefficients per Emotion Class", fontsize=13, fontweight="bold")
ax.set_xlabel("Emotion"); ax.set_ylabel("MFCC Coefficient")
plt.tight_layout()
plt.savefig(OUT_DIR / "mfcc_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved mfcc_heatmap.png")

# ── 5. Save numeric results ────────────────────────────────────────────────────
summary = []
for name, res in results.items():
    summary.append({
        "Model": name,
        "CV Accuracy (mean)": round(res["acc_mean"], 4),
        "CV Accuracy (std)":  round(res["acc_std"],  4),
        "CV F1-Macro":        round(res["f1_macro"],  4),
        "CV F1-Weighted":     round(res["f1_weighted"], 4),
    })
df_summary = pd.DataFrame(summary).sort_values("CV Accuracy (mean)", ascending=False)
df_summary.to_csv(OUT_DIR / "results_summary.csv", index=False)
print("\nResults summary:")
print(df_summary.to_string(index=False))
print("\nDone! All outputs saved to", OUT_DIR)
