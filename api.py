# StyleTTS 2 HTTP Streaming API by @fakerybakery - Copyright (c) 2023 mrfakename. All rights reserved.
# Docs: API_DOCS.md
# To-Do:
# * Support voice cloning
# * Implement authentication, user "credits" system w/ SQLite3
import io
import os
import hashlib
import threading
import markdown
import re
import json
from tortoise.utils.text import split_and_recombine_text
from flask import Flask, Response, request, jsonify
from scipy.io.wavfile import write

import ljinference
import msinference
import torch


def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000 * 10**6
    o = bytes("RIFF", "ascii")
    o += (datasize + 36).to_bytes(4, "little")
    o += bytes("WAVE", "ascii")
    o += bytes("fmt ", "ascii")
    o += (16).to_bytes(4, "little")
    o += (1).to_bytes(2, "little")
    o += (channels).to_bytes(2, "little")
    o += (sampleRate).to_bytes(4, "little")
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4, "little")
    o += (channels * bitsPerSample // 8).to_bytes(2, "little")
    o += (bitsPerSample).to_bytes(2, "little")
    o += bytes("data", "ascii")
    o += (datasize).to_bytes(4, "little")
    return o

voicelist = ['f-us-1', 'f-us-2', 'f-us-3', 'f-us-4', 'm-us-1', 'm-us-2', 'm-us-3', 'm-us-4']
voices = {}
import phonemizer
global_phonemizer = phonemizer.backend.EspeakBackend(language='en-us', preserve_punctuation=True,  with_stress=True)
print("Computing voices")
for v in voicelist:
    voices[v] = msinference.compute_style(f'voices/{v}.wav')
print("Starting Flask app")

app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def index():
    with open('API_DOCS.md', 'r') as f:
        return markdown.markdown(f.read())

def synthesize(text, voice, steps):
    v = voice.lower()
    return msinference.inference(t, voices[v], alpha=0.3, beta=0.7, diffusion_steps=lngsteps, embedding_scale=1)
def ljsynthesize(text, steps):
    return ljinference.inference(text, torch.randn(1,1,256).to('cuda' if torch.cuda.is_available() else 'cpu'), diffusion_steps=7, embedding_scale=1)
# def ljsynthesize(text):
#     texts = split_and_recombine_text(text)
#     v = voice.lower()
#     audios = []
#     noise = torch.randn(1,1,256).to('cuda' if torch.cuda.is_available() else 'cpu')
#     for t in texts:
#         audios.append(ljinference.inference(text, noise, diffusion_steps=7, embedding_scale=1))
#     return np.concatenate(audios)

# @cross_origin()
# @app.route("/api/v1/stream/<voice>/<hash>")
# def serve_wav_stream(voice, hash):
#     h = re.sub(r"[^a-zA-Z0-9]", "", hash)
#     voice = re.sub(r"[^a-zA-Z0-9_]", "", voice)
#     if not os.path.isfile(f"cache/{h}.txt"):
#         return "NO TEXT PATH"
#     txt = err_msg
#     with open(f"cache/{h}.txt", "r") as f:
#         txt = f.read()
#     texts = split_and_recombine_text(txt, 100, 200)

#     def generate():
#         print("Request sent")
#         is_first_chunk = True
#         wav_header = genHeader(44100, 16, 1)
#         for j, text in enumerate(texts):
#             # for i in range(3):
#             print(f"GENERATING {j}/{len(texts)}")
#             path = do_tts(text, voice)
#             print("{DONE}")
#             with open(path, "rb") as wav_file:
#                 wav_file.read(44)
#                 if is_first_chunk:
#                     data = wav_header + wav_file.read()
#                     is_first_chunk = False
#                 else:
#                     data = wav_file.read()
#                 yield data

#     return Response(generate(), mimetype="audio/x-wav")


@cross_origin()
@app.route("/api/v1/static", methods=['POST'])
def serve_wav(voice, hash):
    if 'text' not in request.form or 'voice' not in request.form:
        error_response = {'error': 'Missing required fields. Please include "text" and "voice" in your request.'}
        return jsonify(error_response), 400
    text = request.form['text'].strip()
    voice = request.form['voice'].strip().lower()
    if not voice in voices:
        error_response = {'error': 'Invalid voice selected'}
        return jsonify(error_response), 400
    v = voices[voice]
    texts = split_and_recombine_text(txt)
    audios = []

    output_buffer = io.BytesIO()
    concatenated_audio.export(output_buffer, format="wav")

    # Set the response headers
    response = Response(output_buffer.getvalue())
    response.headers["Content-Type"] = "audio/wav"

    return response


print("=== STEP 3: STARTING SERVER ===")
if __name__ == "__main__":
    # app.run(debug=True)
    app.config["TEMPLATES_AUTO_RELOAD"] = use_debug
    app.run("0.0.0.0", port=port)