from pathlib import Path
import colorsys
import json
import math
import random
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path('/kaggle/working')
ROOT.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
DURATION = 138
FPS = 30

GENRES = [
    {
        'genre': 'hyperpop electropop',
        'bpm': 146,
        'language': 'en',
        'mood': 'bright midnight confidence',
        'title_words': ['Glow', 'Voltage', 'Afterclass', 'Pixel', 'Rush'],
        'tags': ['hyperpop', 'electropop', 'nightmusic', 'newmusic', 'studyplaylist'],
    },
    {
        'genre': 'uk garage pop',
        'bpm': 132,
        'language': 'ko',
        'mood': 'rainy Seoul late-night crush',
        'title_words': ['Seoul', 'Signal', 'Rainline', 'DM', 'Frequency'],
        'tags': ['ukgarage', 'koreanmusic', 'nightvibes', 'newmusic', 'citypop'],
    },
    {
        'genre': 'drum and bass lite',
        'bpm': 168,
        'language': 'en',
        'mood': 'fast main-character energy',
        'title_words': ['Battery', 'Midnight', 'Pulse', 'NoSleep', 'Arcade'],
        'tags': ['drumandbass', 'nightdrive', 'energymusic', 'electronicmusic', 'newmusic'],
    },
    {
        'genre': 'dreamy electronic pop',
        'bpm': 104,
        'language': 'en',
        'mood': 'soft neon afterglow',
        'title_words': ['Soft', 'Afterglow', 'Lemon', 'Static', 'Window'],
        'tags': ['dreampop', 'electronicpop', 'chillmusic', 'nightmusic', 'newmusic'],
    },
]

SCALES = {
    'major': [0, 2, 4, 7, 9],
    'minor': [0, 3, 5, 7, 10],
    'pentatonic': [0, 2, 5, 7, 9],
}


def write_wav(path, samples):
    with wave.open(str(path), 'w') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample in samples:
            value = max(-1.0, min(1.0, sample))
            integer = int(value * 32767)
            frames += integer.to_bytes(2, 'little', signed=True)
            frames += integer.to_bytes(2, 'little', signed=True)
        wav.writeframes(frames)


def sine(freq, t):
    return math.sin(2 * math.pi * freq * t)


def square(freq, t):
    return 1.0 if sine(freq, t) >= 0 else -1.0


def envelope(pos, length, attack=0.02, release=0.08):
    if pos < attack:
        return pos / attack
    if pos > length - release:
        return max(0.0, (length - pos) / release)
    return 1.0


def generate_audio(profile, seed):
    random.seed(seed)
    bpm = profile['bpm']
    beat = 60.0 / bpm
    total = int(DURATION * SAMPLE_RATE)
    samples = [0.0] * total
    root = random.choice([48, 50, 53, 55, 57])
    scale = random.choice(list(SCALES.values()))
    progression = [0, 3, 4, 1, 5, 4, 2, 3]

    def midi_to_freq(m):
        return 440.0 * (2 ** ((m - 69) / 12))

    for i in range(total):
        t = i / SAMPLE_RATE
        beat_index = int(t / beat)
        beat_pos = (t % beat) / beat
        bar = beat_index // 4
        degree = progression[bar % len(progression)]
        note = root + scale[degree % len(scale)]
        bass_freq = midi_to_freq(note - 12)
        chord_freq = midi_to_freq(note + 12)

        kick = math.exp(-beat_pos * 18) * sine(48 + 70 * math.exp(-beat_pos * 18), t) if beat_pos < 0.35 else 0
        snare_pos = abs((beat_index % 4) - 2)
        snare = (random.random() * 2 - 1) * 0.22 * math.exp(-beat_pos * 35) if snare_pos == 0 and beat_pos < 0.25 else 0
        hat = (random.random() * 2 - 1) * 0.045 if (beat_index * 2 + int(beat_pos * 2)) % 2 == 0 else 0
        bass = 0.19 * square(bass_freq, t) * (0.65 + 0.35 * sine(0.5, t))
        pad = 0.08 * (sine(chord_freq, t) + sine(chord_freq * 1.25, t) + sine(chord_freq * 1.5, t))

        hook_note = root + 12 + scale[(beat_index + bar) % len(scale)]
        hook = 0
        if 8 <= bar % 16 <= 15:
            hook = 0.11 * sine(midi_to_freq(hook_note), t) * envelope(t % (beat * 2), beat * 2, 0.01, 0.12)

        samples[i] = 0.42 * kick + snare + hat + bass + pad + hook

    return samples


def make_backgrounds(profile, seed):
    random.seed(seed)
    themes = ['neon hallway', 'rainy subway', 'late desk', 'empty arcade', 'night convenience store']
    theme = random.choice(themes)
    paths = []
    for idx in range(6):
        hue = (random.random() + idx * 0.12) % 1
        base = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.55, 0.18))
        accent = tuple(int(c * 255) for c in colorsys.hsv_to_rgb((hue + 0.42) % 1, 0.75, 0.9))
        img = Image.new('RGB', (1920, 1080), base)
        draw = ImageDraw.Draw(img, 'RGBA')

        for _ in range(90):
            x = random.randint(-200, 1920)
            y = random.randint(-200, 1080)
            w = random.randint(120, 520)
            h = random.randint(6, 34)
            color = accent + (random.randint(22, 80),)
            draw.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=color)

        for _ in range(28):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            r = random.randint(60, 180)
            color = accent + (random.randint(18, 52),)
            draw.ellipse((x-r, y-r, x+r, y+r), fill=color)

        draw.rectangle((0, 820, 1920, 1080), fill=(0, 0, 0, 70))
        title = profile['mood'].upper()
        draw.text((80, 865), title[:42], fill=(240, 245, 255, 205))
        draw.text((80, 925), theme, fill=(240, 245, 255, 135))
        img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
        path = ROOT / f'background_{idx+1}.jpg'
        img.save(path, quality=92)
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
        '-vf', "scale=1920:1080,zoompan=z='min(zoom+0.0007,1.08)':d=125:s=1920x1080:fps=30,format=yuv420p",
        '-t', str(DURATION), str(silent_video)
    ], check=True)
    subprocess.run([
        'ffmpeg', '-y', '-i', str(silent_video), '-i', str(audio_path),
        '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k', '-shortest', str(output_path)
    ], check=True)


def main():
    seed = random.randint(100000, 999999)
    profile = random.choice(GENRES)
    title = f"{random.choice(profile['title_words'])} {random.choice(profile['title_words'])}"
    safe_id = title.lower().replace(' ', '-') + f'-{seed}'

    audio = generate_audio(profile, seed)
    audio_path = ROOT / 'track.wav'
    write_wav(audio_path, audio)

    backgrounds = make_backgrounds(profile, seed)
    video_path = ROOT / 'final_video.mp4'
    make_video(backgrounds, audio_path, video_path)

    thumbnail = ROOT / 'thumbnail.jpg'
    backgrounds[0].replace(thumbnail)

    description = (
        f"{title} is an original {profile['genre']} track built for late-night focus, short-form discovery, "
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
    }
    (ROOT / 'metadata.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
