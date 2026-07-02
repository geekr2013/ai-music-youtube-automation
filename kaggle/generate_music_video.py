from pathlib import Path
import colorsys
import json
import math
import random
import shutil
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path('/kaggle/working')
ROOT.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
DURATION = 150
FPS = 30

TREND_PROFILES = [
    {
        'genre': 'hyperpop electropop',
        'bpm': 148,
        'language': 'en',
        'mood': 'bright midnight confidence',
        'score': 0.95,
        'root_choices': [49, 51, 54, 56],
        'scale': [0, 2, 4, 7, 9],
        'progression': [0, 4, 5, 3, 1, 5, 4, 2],
        'title_words': ['Glow', 'Voltage', 'Pixel', 'Rush', 'Late'],
        'visuals': ['neon lockers', 'phone glow desk', 'pink subway tiles', 'arcade reflection'],
        'tags': ['hyperpop', 'electropop', 'nightmusic', 'newmusic', 'studyplaylist'],
    },
    {
        'genre': 'uk garage pop',
        'bpm': 134,
        'language': 'ko',
        'mood': 'rainy Seoul late-night crush',
        'score': 0.9,
        'root_choices': [46, 49, 51, 54],
        'scale': [0, 2, 3, 7, 10],
        'progression': [0, 3, 4, 1, 0, 5, 4, 3],
        'title_words': ['Seoul', 'Signal', 'Rainline', 'DM', 'Frequency'],
        'visuals': ['rainy subway', 'wet crosswalk', 'window reflection', 'night bus stop'],
        'tags': ['ukgarage', 'koreanmusic', 'nightvibes', 'newmusic', 'citypop'],
    },
    {
        'genre': 'drum and bass lite',
        'bpm': 170,
        'language': 'en',
        'mood': 'fast main-character energy',
        'score': 0.88,
        'root_choices': [45, 48, 50, 52],
        'scale': [0, 3, 5, 7, 10],
        'progression': [0, 5, 3, 4, 1, 4, 2, 5],
        'title_words': ['Battery', 'Midnight', 'Pulse', 'NoSleep', 'Arcade'],
        'visuals': ['empty arcade', 'dawn convenience store', 'moving train light', 'sports court night'],
        'tags': ['drumandbass', 'nightdrive', 'energymusic', 'electronicmusic', 'newmusic'],
    },
    {
        'genre': 'dreamy electronic pop',
        'bpm': 112,
        'language': 'en',
        'mood': 'soft neon afterglow',
        'score': 0.76,
        'root_choices': [48, 50, 53, 55],
        'scale': [0, 2, 4, 7, 11],
        'progression': [0, 2, 5, 4, 0, 3, 5, 1],
        'title_words': ['Soft', 'Afterglow', 'Lemon', 'Static', 'Window'],
        'visuals': ['sunset bedroom', 'soft cables', 'blue lemonade', 'quiet rooftop'],
        'tags': ['dreampop', 'electronicpop', 'chillmusic', 'nightmusic', 'newmusic'],
    },
]


def midi_to_freq(midi):
    return 440.0 * (2 ** ((midi - 69) / 12))


def weighted_profile():
    total = sum(item['score'] for item in TREND_PROFILES)
    pick = random.random() * total
    cursor = 0
    for item in TREND_PROFILES:
        cursor += item['score']
        if pick <= cursor:
            return item
    return TREND_PROFILES[0]


def add_event(track, start, length, tone_fn):
    start_i = max(0, int(start * SAMPLE_RATE))
    end_i = min(len(track), int((start + length) * SAMPLE_RATE))
    if end_i <= start_i:
        return
    t = np.arange(end_i - start_i, dtype=np.float32) / SAMPLE_RATE
    track[start_i:end_i] += tone_fn(t).astype(np.float32)


def adsr(t, length, attack=0.01, decay=0.08, sustain=0.65, release=0.12):
    env = np.ones_like(t) * sustain
    env = np.where(t < attack, t / max(attack, 0.001), env)
    decay_mask = (t >= attack) & (t < attack + decay)
    env = np.where(decay_mask, 1 - (1 - sustain) * ((t - attack) / decay), env)
    rel_start = max(length - release, 0)
    env = np.where(t > rel_start, sustain * np.maximum(0, (length - t) / max(release, 0.001)), env)
    return np.clip(env, 0, 1)


def generate_audio(profile, seed):
    random.seed(seed)
    np.random.seed(seed)
    bpm = profile['bpm']
    beat = 60.0 / bpm
    bars = int(DURATION / (beat * 4))
    root = random.choice(profile['root_choices'])
    scale = profile['scale']
    progression = profile['progression']

    total = int(DURATION * SAMPLE_RATE)
    track = np.zeros(total, dtype=np.float32)

    melody_pattern = [0, 2, 4, 2, 5, 4, 2, 1, 0, 4, 5, 7, 5, 4, 2, 1]
    arp_pattern = [0, 2, 4, 7, 4, 2, 5, 7]

    for bar in range(bars):
        bar_start = bar * beat * 4
        section = (bar // 8) % 4
        energy = [0.45, 0.75, 1.0, 0.82][section]
        degree = progression[bar % len(progression)]
        base_note = root + scale[degree % len(scale)]

        for step in range(16):
            pos = bar_start + step * beat / 4
            if step in [0, 4, 8, 12]:
                add_event(track, pos, beat * 0.55, lambda t: 0.75 * energy * np.sin(2 * np.pi * (46 + 78 * np.exp(-t * 18)) * t) * np.exp(-t * 9))
            if step in [4, 12] or (profile['genre'] == 'uk garage pop' and step in [6, 14]):
                add_event(track, pos, beat * 0.34, lambda t: 0.24 * energy * np.random.uniform(-1, 1, len(t)) * np.exp(-t * 22))
            if step % 2 == 0:
                add_event(track, pos, beat * 0.12, lambda t: 0.035 * np.random.uniform(-1, 1, len(t)) * np.exp(-t * 55))

        for note_step in range(4):
            pos = bar_start + note_step * beat
            bass_note = base_note - 24 + (12 if note_step == 3 and section > 0 else 0)
            freq = midi_to_freq(bass_note)
            add_event(track, pos, beat * 0.88, lambda t, f=freq: 0.22 * energy * np.tanh(2.2 * np.sin(2 * np.pi * f * t)) * adsr(t, beat * 0.88, 0.005, 0.06, 0.5, 0.18))

        chord_notes = [base_note + 12, base_note + 12 + scale[2 % len(scale)], base_note + 12 + scale[4 % len(scale)]]
        for cn in chord_notes:
            freq = midi_to_freq(cn)
            add_event(track, bar_start, beat * 3.8, lambda t, f=freq: 0.055 * np.sin(2 * np.pi * f * t + 0.18 * np.sin(2 * np.pi * 5 * t)) * adsr(t, beat * 3.8, 0.12, 0.3, 0.7, 0.4))

        if section in [1, 2, 3]:
            for step in range(8):
                pos = bar_start + step * beat / 2
                arp_note = root + 12 + scale[arp_pattern[(step + bar) % len(arp_pattern)] % len(scale)]
                freq = midi_to_freq(arp_note)
                add_event(track, pos, beat * 0.28, lambda t, f=freq: 0.08 * energy * np.sin(2 * np.pi * f * t) * adsr(t, beat * 0.28, 0.005, 0.02, 0.4, 0.07))

        if section == 2:
            for step in range(4):
                pos = bar_start + step * beat
                melody_note = root + 24 + scale[melody_pattern[(bar + step) % len(melody_pattern)] % len(scale)]
                freq = midi_to_freq(melody_note)
                add_event(track, pos, beat * 0.7, lambda t, f=freq: 0.12 * np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * 2 * t)) * adsr(t, beat * 0.7, 0.02, 0.08, 0.65, 0.16))

    # Gentle mastering: soft clip, normalize, and leave headroom.
    track = np.tanh(track * 1.35)
    peak = float(np.max(np.abs(track))) or 1.0
    return (track / peak * 0.92).astype(np.float32)


def write_wav(path, samples):
    with wave.open(str(path), 'w') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        stereo = np.column_stack([samples, samples])
        wav.writeframes((stereo * 32767).astype('<i2').tobytes())


def make_backgrounds(profile, seed, title):
    random.seed(seed)
    paths = []
    for idx in range(8):
        visual = profile['visuals'][idx % len(profile['visuals'])]
        hue = (random.random() + idx * 0.105) % 1
        base = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.45, 0.14))
        accent = tuple(int(c * 255) for c in colorsys.hsv_to_rgb((hue + 0.38) % 1, 0.72, 0.92))
        warm = tuple(int(c * 255) for c in colorsys.hsv_to_rgb((hue + 0.08) % 1, 0.55, 0.75))
        img = Image.new('RGB', (1920, 1080), base)
        draw = ImageDraw.Draw(img, 'RGBA')

        for y in range(0, 1080, 54):
            shade = int(18 + y / 1080 * 45)
            draw.rectangle((0, y, 1920, y + 54), fill=(shade, shade, shade + 10, 20))

        for _ in range(120):
            x = random.randint(-240, 1920)
            y = random.randint(-120, 1080)
            w = random.randint(90, 620)
            h = random.randint(5, 32)
            color = random.choice([accent, warm]) + (random.randint(18, 76),)
            draw.rounded_rectangle((x, y, x + w, y + h), radius=10, fill=color)

        for _ in range(34):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            r = random.randint(40, 180)
            color = random.choice([accent, warm]) + (random.randint(12, 42),)
            draw.ellipse((x-r, y-r, x+r, y+r), fill=color)

        for x in range(80, 1920, 180):
            draw.line((x, 0, x + random.randint(-220, 220), 1080), fill=accent + (20,), width=2)

        draw.rectangle((0, 812, 1920, 1080), fill=(0, 0, 0, 92))
        draw.text((80, 858), title.upper()[:48], fill=(246, 248, 255, 220))
        draw.text((80, 916), f"{profile['genre']} / {visual}", fill=(246, 248, 255, 145))
        draw.text((80, 968), profile['mood'], fill=(246, 248, 255, 115))
        img = img.filter(ImageFilter.GaussianBlur(radius=0.45))
        path = ROOT / f'background_{idx+1}.jpg'
        img.save(path, quality=93)
        paths.append(path)
    return paths


def make_video(backgrounds, audio_path, output_path):
    list_path = ROOT / 'images.txt'
    each = DURATION / len(backgrounds)
    with list_path.open('w', encoding='utf-8') as f:
        for bg in backgrounds:
            f.write(f"file '{bg}'\n")
            f.write(f'duration {each}\n')
        f.write(f"file '{backgrounds[-1]}'\n")

    silent_video = ROOT / 'silent_video.mp4'
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(list_path),
        '-vf', "scale=1920:1080,zoompan=z='min(zoom+0.00065,1.07)':d=125:s=1920x1080:fps=30,format=yuv420p",
        '-t', str(DURATION), str(silent_video)
    ], check=True)
    subprocess.run([
        'ffmpeg', '-y', '-i', str(silent_video), '-i', str(audio_path),
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
        '-c:a', 'aac', '-b:a', '192k', '-shortest', str(output_path)
    ], check=True)


def main():
    seed = random.randint(100000, 999999)
    profile = weighted_profile()
    first = random.choice(profile['title_words'])
    second = random.choice([w for w in profile['title_words'] if w != first])
    title = f"{first} {second}"
    safe_id = title.lower().replace(' ', '-') + f'-{seed}'

    audio = generate_audio(profile, seed)
    audio_path = ROOT / 'track.wav'
    write_wav(audio_path, audio)

    backgrounds = make_backgrounds(profile, seed, title)
    video_path = ROOT / 'final_video.mp4'
    make_video(backgrounds, audio_path, video_path)

    thumbnail = ROOT / 'thumbnail.jpg'
    shutil.copyfile(backgrounds[0], thumbnail)

    description = (
        f"{title} is an original {profile['genre']} instrumental built for late-night focus, short-form discovery, "
        f"and high-energy playlist moments.\n\n"
        f"Mood: {profile['mood']}\n"
        f"Best part: 0:18\n\n"
        + ' '.join(f"#{tag}" for tag in profile['tags'][:5])
    )

    metadata = {
        'id': safe_id,
        'title': f"{title} - Original {profile['genre'].title()} Mix",
        'description': description,
        'tags': profile['tags'],
        'categoryId': '10',
        'language': profile['language'],
        'videoFile': 'final_video.mp4',
        'thumbnailFile': 'thumbnail.jpg',
        'seed': seed,
        'genre': profile['genre'],
        'mood': profile['mood'],
        'generation_method': 'trend-weighted original synthesis; no artist imitation; no sampled copyrighted audio',
    }
    (ROOT / 'metadata.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
