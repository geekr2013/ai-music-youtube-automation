from pathlib import Path
import json
import wave


ROOT = Path("/kaggle/working")
REPORT = ROOT / "quality_report.md"


def inspect_wav(path: Path):
    with wave.open(str(path), "rb") as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        channels = audio.getnchannels()
        duration = frames / float(rate) if rate else 0
        return {
            "file": str(path),
            "duration_seconds": round(duration, 2),
            "sample_rate": rate,
            "channels": channels,
        }


def main():
    input_root = Path("/kaggle/input")
    wav_files = list(input_root.rglob("*.wav")) if input_root.exists() else []

    report = [
        "# AI Music Quality Report",
        "",
        "This report is generated in a Kaggle free Notebook.",
        "If WAV files are connected as a Kaggle Dataset, it checks duration, sample rate, and channel count.",
        "",
    ]

    if not wav_files:
        report.extend([
            "## Result",
            "",
            "No connected WAV files found.",
            "Connect completed or draft WAV files as a Kaggle Dataset to run audio quality checks.",
        ])
    else:
        rows = []
        for wav_file in wav_files:
            rows.append(inspect_wav(wav_file))

        report.extend([
            "## WAV Check Result",
            "",
            "| File | Duration | Sample Rate | Channels |",
            "|---|---:|---:|---:|",
        ])

        for row in rows:
            report.append(
                f"| {row['file']} | {row['duration_seconds']} | {row['sample_rate']} | {row['channels']} |"
            )

        (ROOT / "quality_report.json").write_text(
            json.dumps(rows, indent=2),
            encoding="utf-8",
        )

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Saved {REPORT}")


if __name__ == "__main__":
    main()
