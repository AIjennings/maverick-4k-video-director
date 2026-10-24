import json
import os
import subprocess

master = r"./workspace\eden-mazara-commercial\eden-mazara-commercial-v10-4k.mp4"
linkedin_4k = r"~\Downloads\linkedin-maverick-4k-sizzle-45s.mp4"
showcase_4k = r"D:\AI\tech-aria-site\public\media\eden-mazara-4k-showcase-20s.mp4"

print("1. Rendering 20s website showcase in native 3840x2160 4K UHD...")
subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-ss",
        "125",
        "-t",
        "20",
        "-i",
        master,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "21",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        showcase_4k,
    ],
    check=True,
)

print("2. Rendering 45s LinkedIn sizzle in native 3840x2160 4K UHD...")
fc = (
    "[0:v]trim=start=15:end=30,setpts=PTS-STARTPTS,fps=30[v0];"
    "[0:v]trim=start=48:end=63.5,setpts=PTS-STARTPTS,fps=30[v1];"
    "[0:v]trim=start=134.5:end=150,setpts=PTS-STARTPTS,fps=30[v2];"
    "[v0][v1]xfade=transition=fade:duration=0.5:offset=14.5[v01];"
    "[v01][v2]xfade=transition=fade:duration=0.5:offset=29.5[vout];"
    "[0:a]atrim=start=15:end=30,asetpts=PTS-STARTPTS[a0];"
    "[0:a]atrim=start=48:end=63.5,asetpts=PTS-STARTPTS[a1];"
    "[0:a]atrim=start=134.5:end=150,asetpts=PTS-STARTPTS[a2];"
    "[a0][a1]acrossfade=d=0.5[a01];"
    "[a01][a2]acrossfade=d=0.5[aout]"
)
subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-i",
        master,
        "-filter_complex",
        fc,
        "-map",
        "[vout]",
        "-map",
        "[aout]",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        linkedin_4k,
    ],
    check=True,
)

for p in [master, showcase_4k, linkedin_4k]:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,width,height,r_frame_rate:format=duration,size",
            "-of",
            "json",
            p,
        ],
        text=True,
    )
    info = json.loads(out)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    print(
        f"{os.path.basename(p):40s} -> {v['width']}x{v['height']} | dur={float(info['format']['duration']):.2f}s | size={int(info['format']['size'])/1024/1024:.2f} MB"
    )
