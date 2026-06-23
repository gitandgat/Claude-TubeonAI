# Avatar Engine — local talking-head ($0 HeyGen/Higgsfield alternative)

Animates a single front-facing photo to lip-sync a generated voiceover, fully locally.
Used to produce talking-head intro hooks (one per content vertical) that fix the high
skip rate on pure-animation videos.

Pipeline: **vertical hook script → VoiSpark voiceover (onyx) → SadTalker talking head → mp4**

## Files (tracked)
- `avatar_hook.py` — the pipeline. Generates a voiceover + renders one talking head.
- `avatar_batch.py` — overnight runner: renders all 5 vertical hooks, resumable, skips done.
- `com.crosswalk.avatar-batch.plist` — LaunchAgent (2 AM daily) that runs the batch.

## One-time setup (not in git — heavy)
```bash
# 1. ffmpeg
brew install ffmpeg

# 2. isolated env (SadTalker needs old pins; system py 3.13/3.14 won't take them)
conda create -n avatar python=3.10 -y
PY=/opt/anaconda3/envs/avatar/bin/python

# 3. torch 2.0.1 + tv 0.15.2 — the combo with Apple-Silicon wheels that keeps
#    torchvision.transforms.functional_tensor (basicsr 1.4.2 imports it)
$PY -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2

# 4. numba/llvmlite from wheels (else llvmlite builds from source and fails)
$PY -m pip install --only-binary=:all: llvmlite==0.40.1 numba==0.57.1

# 5. SadTalker + its deps + runtime deps
git clone --depth 1 https://github.com/OpenTalker/SadTalker.git
$PY -m pip install numpy==1.23.4
$PY -m pip install -r SadTalker/requirements.txt
$PY -m pip install requests python-dotenv
bash SadTalker/scripts/download_models.sh   # ~1.5GB checkpoints
```
Then drop a clear, front-facing selfie at `faces/sahawat.jpg`.

`VOISPARK_API_KEY` is read from the repo root `.env`.

## Usage
```bash
PY=/opt/anaconda3/envs/avatar/bin/python
$PY avatar_hook.py crosswalk                 # one vertical
$PY avatar_hook.py all                        # all 5
$PY avatar_hook.py mind --text "custom..."    # arbitrary script
$PY avatar_batch.py                           # render all pending (what the 2 AM job runs)
```

## Caveats learned the hard way
- **Run SadTalker with cwd = `SadTalker/`** — it resolves `./checkpoints` relative to CWD.
  `avatar_hook.py` does this; a manual run from elsewhere falls out of the safetensor
  branch and dies on `epoch_20.pth`.
- **No `--enhancer gfpgan` on a low-RAM machine** — GFPGAN took ~5.5h for a 6s clip under
  memory pressure. Off by default; opt in with `--enhancer` only when RAM is free.
- **RAM-bound:** 16GB Mac with apps open ≈ 12 s/frame; with RAM free ≈ 1-2 s/frame.
  That's why the batch runs overnight — close apps before bed for it to finish.
- **VoiSpark schema** (Jun 2026): body uses `model_id` + `voice:{type:"preset",voice_id:"onyx"}`.

## Install the overnight job
```bash
cp com.crosswalk.avatar-batch.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.crosswalk.avatar-batch.plist
```
