#!/bin/bash
# Uso: qa.sh out/UT1/UT1.mp4 → hoja de contactos + info de pistas
f=$1; base=${f%.mp4}
ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels -of compact "$f"
d=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$f")
ffmpeg -loglevel error -y -i "$f" -vf "fps=12/$d,scale=480:-1,tile=4x3:padding=6:color=black" -frames:v 1 "${base}_sheet.jpg"
echo "${base}_sheet.jpg"
