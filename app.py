from fileinput import filename
import os, json, requests, time, re, random
from flask import Flask, render_template, request, jsonify, send_from_directory, Response, stream_with_context
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# --- KONFIGURASI ---
OUTPUT_DIR = "output"
LOG_DIR = "logs"
PROMPT_DIR = "prompts"
FALLBACK_MODEL = "stepfun/step-3.5-flash:free"
URL = "https://openrouter.ai/api/v1/chat/completions"

# Pastikan folder ada
for d in [OUTPUT_DIR, LOG_DIR, PROMPT_DIR]:
    os.makedirs(d, exist_ok=True)

# --- UTILS (DIADAPTASI DARI KODEMU) ---
def load_prompt_file(name, default=""):
    path = os.path.join(PROMPT_DIR, name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return f.read()
    return default

def sanitize_filename(text):
    text = text.lower().strip()
    text = re.sub(r"[\\/*?:\"<>|]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text

def count_words(text):
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))

# --- CORE API CALL (ROBUST VERSION) ---
def call_openrouter(token, model, prompt, retries=3):
    current_model = model
    for attempt in range(retries):
        try:
            payload = {
                "model": current_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1200
            }
            res = requests.post(URL, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=payload, timeout=40)
            data = res.json()
            
            if "choices" in data:
                return data["choices"][0]["message"]["content"].strip()
            
            if "error" in data and data["error"].get("code") == 429:
                time.sleep(10) # Rate limit hit
            
            if attempt == retries - 2: # Last attempt, switch to fallback
                current_model = FALLBACK_MODEL
        except:
            time.sleep(2)
    return None

# --- FLASK ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-articles', methods=['POST'])
def generate_articles():
    data = request.json
    token = data.get('token')
    model = data.get('model')
    titles = data.get('titles')

    # Load Templates
    outline_temp = load_prompt_file("outline_prompt.txt", "Create an outline for {TOPIC}")
    section_temp = load_prompt_file("section_prompt.txt", "Write section {SECTION} for {TOPIC}")
    style = load_prompt_file("style.txt", "Technical, clear, professional.")

    generated_count = 0

    for topic in titles:
        # STEP 1: GENERATE OUTLINE
        prompt_outline = outline_temp.replace("{TOPIC}", topic)
        outline_raw = call_openrouter(token, model, prompt_outline)
        
        if not outline_raw: continue

        # FORCE CONTROL: Parse & Limit Sections
        # Kita ambil baris yang terlihat seperti list (1. Judul atau - Judul)
        lines = outline_raw.split('\n')
        sections = []
        for line in lines:
            clean = re.sub(r'^\d+\.\s*|^\-\s*', '', line).strip()
            if clean and len(clean) > 5: # Hindari baris sampah
                sections.append(clean)
        
        # --- THE GUARDRAIL ---
        if len(sections) > 8:
            sections = sections[:8] # Potong paksa jika AI labil
        
        # STEP 2: GENERATE SECTIONS
        article_body = f"# {topic}\n\n"
        start_time = time.time()
        
        for sec_title in sections:
            prompt_sec = section_temp.replace("{TOPIC}", topic).replace("{SECTION}", sec_title).replace("{STYLE}", style)
            content = call_openrouter(token, model, prompt_sec)
            if content:
                article_body += f"## {sec_title}\n\n{content}\n\n"
                time.sleep(random.uniform(2, 4)) # Delay antar section agar aman

        # STEP 3: METADATA & SAVE (PERSIS GAYA KODEMU)
        total_time = time.time() - start_time
        words = count_words(article_body)
        metadata = f"> **AI Metadata**\n> - Model: {model}\n> - Time: {int(total_time)}s\n> - Words: {words}\n> - Sections: {len(sections)}\n\n"
        
        final_md = metadata + article_body
        filename = sanitize_filename(topic) + ".md"
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(final_md)
        
        generated_count += 1

    # Update JSON Index Otomatis
    sync_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".md")]
    with open(os.path.join(OUTPUT_DIR, "articles.json"), "w") as f:
        json.dump({"articles": sync_files}, f, indent=2)

    return jsonify({"status": "success", "count": generated_count})

@app.route('/sync-archive', methods=['POST'])
def sync_archive():
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".md")]
    with open(os.path.join(OUTPUT_DIR, "articles.json"), "w") as f:
        json.dump({"articles": files}, f, indent=2)
    return jsonify({"status": "success", "count": len(files)})

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)
@app.route('/generate-stream')
def generate_stream():
    token = request.args.get('token')
    model = request.args.get('model')
    raw_titles = request.args.get('titles', '')
    titles = [t.strip() for t in raw_titles.split(',') if t.strip()]

    def generate():
        yield f"data: {json.dumps({'msg': '🚀 ENGINE STARTED', 'type': 'success'})}\n\n"
        
        outline_temp = load_prompt_file("outline_prompt.txt")
        section_temp = load_prompt_file("section_prompt.txt")
        style_guide = load_prompt_file("style.txt")

        for topic in titles:
            yield f"data: {json.dumps({'msg': f'📌 WORKING ON: {topic}', 'type': 'info'})}\n\n"
            
            # STEP 1: OUTLINE
            yield f"data: {json.dumps({'msg': 'Step 1: Generating Outline...', 'type': 'warn'})}\n\n"
            outline_raw = call_openrouter(token, model, outline_temp.replace("{TOPIC}", topic))
            
            if not outline_raw:
                yield f"data: {json.dumps({'msg': f'❌ Failed to get outline for {topic}', 'type': 'err'})}\n\n"
                continue

            # Parse & Force Control (Max 8 Sections)
            sections = [re.sub(r'^\d+\.\s*|^\-\s*', '', line).strip() 
                        for line in outline_raw.split('\n') if len(line.strip()) > 5]
            if len(sections) > 8:
                sections = sections[:8]
                yield f"data: {json.dumps({'msg': '⚠️ Sections truncated to 8 (Force Control)', 'type': 'warn'})}\n\n"

            # STEP 2: SECTIONS
            full_article = f"# {topic}\n\n"
            start_time = time.time()
            
            for i, sec in enumerate(sections, 1):
                yield f"data: {json.dumps({'msg': f'✍️ Writing [{i}/{len(sections)}]: {sec}', 'type': 'info'})}\n\n"
                p_sec = section_temp.replace("{TOPIC}", topic).replace("{SECTION}", sec).replace("{STYLE}", style_guide)
                content = call_openrouter(token, model, p_sec)
                
                if content:
                    full_article += f"## {sec}\n\n{content}\n\n"
                
                # Small delay to prevent rate limit
                time.sleep(random.uniform(1, 3))

            # STEP 3: SAVE (Inside the topic loop!)
            duration = int(time.time() - start_time)
            words = count_words(full_article)
            metadata = f"> **Metadata**\n> - Model: {model}\n> - Time: {duration}s\n> - Words: {words}\n\n"
            
            filename = sanitize_filename(topic) + ".md"
            with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
                f.write(metadata + full_article)
            
            yield f"data: {json.dumps({'msg': f'💾 SAVED: {filename}', 'type': 'success'})}\n\n"

        # FINAL SYNC
        sync_archive()
        yield f"data: {json.dumps({'msg': '🏁 ALL TASKS FINISHED', 'type': 'success'})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=False)