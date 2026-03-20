import requests
import os
import time
import re
import random
from datetime import datetime

# ==============================
# CONFIG
# ==============================

API_KEY = ""
MODEL = None
FALLBACK_MODEL = "stepfun/step-3.5-flash:free"

URL = "https://openrouter.ai/api/v1/chat/completions"

OUTPUT_DIR = "output"
LOG_DIR = "logs"

# global log file path
LOG_FILE = None

# stats global per artikel
CURRENT_ARTICLE_STATS = None


# ==============================
# LOGGER
# ==============================

def setup_logger():
    global LOG_FILE
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    LOG_FILE = os.path.join(LOG_DIR, f"run-log-{timestamp}.txt")


def log(message, also_print=True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"

    if also_print:
        print(message)

    if LOG_FILE:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")


# ==============================
# MODEL SELECTION
# ==============================

def choose_model():
    while True:
        log("\n=== CHOOSE MODEL ===")
        log("1. Gemma 12B")
        log("2. Gemma 4B")
        log("3. StepFun")

        choice = input("Input Number (1/2/3): ").strip()

        if choice == "1":
            return "google/gemma-3-12b-it:free"
        elif choice == "2":
            return "google/gemma-3-4b-it:free"
        elif choice == "3":
            return "stepfun/step-3.5-flash:free"
        else:
            log("❌ Invalid selection, please try again.")


# ==============================
# MODEL TYPE
# ==============================

def get_model_type(model_name):
    model_name = model_name.lower()
    if "step" in model_name:
        return "stepfun"
    elif "gemma" in model_name:
        return "gemma"
    return "default"


# ==============================
# MODEL CONFIG
# ==============================

def get_model_config(model_name):
    model_type = get_model_type(model_name)

    if model_type == "stepfun":
        return {
            "temperature": 0.7,
            "top_p": 0.9,
            "presence_penalty": 0.4,
            "frequency_penalty": 0.4,
            "max_tokens": 1200
        }

    elif model_type == "gemma":
        return {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 900
        }

    return {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 1000
    }


# ==============================
# TEXT UTILS
# ==============================

def sanitize_filename(text):
    text = text.lower().strip()
    text = re.sub(r"[\\/*?:\"<>|]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def count_words(text):
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def estimate_tokens_from_text(text):
    # estimasi kasar: 1 token ~ 0.75 kata bahasa Inggris,
    # atau praktis pakai ~1.3 x jumlah kata
    words = count_words(text)
    return int(words * 1.3)


def format_seconds(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


# ==============================
# CLEAN OUTPUT
# ==============================

def clean_content(message, model_name):
    model_type = get_model_type(model_name)
    content = message.get("content")

    if isinstance(content, list):
        content = "".join([
            c.get("text", "") for c in content if isinstance(c, dict)
        ])

    if content:
        content = re.sub(r"\\\\n", "\n", content)
        return content.strip()

    if model_type == "stepfun":
        reasoning = message.get("reasoning")
        if reasoning:
            return reasoning.strip()

    return "[No content]"


# ==============================
# STATS
# ==============================

def init_article_stats(topic):
    return {
        "topic": topic,
        "model_requested": MODEL,
        "model_actuals": [],
        "api_calls": 0,
        "success_calls": 0,
        "failed_calls": 0,
        "rate_limit_hits": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "estimated_tokens": 0,
        "start_time": time.time(),
        "end_time": None
    }


def add_model_actual(stats, model_name):
    if model_name not in stats["model_actuals"]:
        stats["model_actuals"].append(model_name)


# ==============================
# API CALL
# ==============================

def call_api(prompt, retries=5):
    global CURRENT_ARTICLE_STATS

    model_to_use = MODEL
    rate_limit_retry = 0

    for attempt in range(retries):
        config = get_model_config(model_to_use)

        payload = {
            "model": model_to_use,
            "messages": [{"role": "user", "content": prompt}],
            **config
        }

        if CURRENT_ARTICLE_STATS is not None:
            CURRENT_ARTICLE_STATS["api_calls"] += 1

        log(f"🌐 API CALL | attempt={attempt + 1}/{retries} | model={model_to_use}")

        try:
            response = requests.post(
                URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )

            log(f"📡 HTTP Status: {response.status_code}")

            data = response.json()

            # ==============================
            # SUCCESS
            # ==============================
            if "choices" in data:
                message = data["choices"][0]["message"]
                content = clean_content(message, model_to_use)

                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)

                if CURRENT_ARTICLE_STATS is not None:
                    add_model_actual(CURRENT_ARTICLE_STATS, model_to_use)
                    CURRENT_ARTICLE_STATS["success_calls"] += 1
                    CURRENT_ARTICLE_STATS["prompt_tokens"] += prompt_tokens
                    CURRENT_ARTICLE_STATS["completion_tokens"] += completion_tokens
                    CURRENT_ARTICLE_STATS["total_tokens"] += total_tokens

                    # fallback kalau usage tidak ada
                    if total_tokens == 0:
                        estimated = estimate_tokens_from_text(prompt + "\n" + content)
                        CURRENT_ARTICLE_STATS["estimated_tokens"] += estimated

                log(
                    f"✅ SUCCESS | model={model_to_use} | "
                    f"prompt_tokens={prompt_tokens} | completion_tokens={completion_tokens} | total_tokens={total_tokens}"
                )
                return content

            # ==============================
            # ERROR HANDLING
            # ==============================
            if "error" in data:
                error_code = data["error"].get("code")
                error_message = data["error"].get("message", "Unknown error")

                log(f"❌ API ERROR | code={error_code} | message={error_message}")

                if error_code == 429:
                    rate_limit_retry += 1

                    if CURRENT_ARTICLE_STATS is not None:
                        CURRENT_ARTICLE_STATS["rate_limit_hits"] += 1

                    if rate_limit_retry <= 5:
                        log(f"🚫 Rate limit hit! ({rate_limit_retry}/5)")
                        log("⏳ Forced delay 10 seconds...\n")
                        time.sleep(10)
                        continue
                    else:
                        if CURRENT_ARTICLE_STATS is not None:
                            CURRENT_ARTICLE_STATS["failed_calls"] += 1
                        log("❌ Failed: too many rate limits.")
                        return "[RATE LIMIT FAILED]"

                if CURRENT_ARTICLE_STATS is not None:
                    CURRENT_ARTICLE_STATS["failed_calls"] += 1
                return "[ERROR]"

        except Exception as e:
            wait = (2 ** attempt) + random.uniform(1, 3)
            log(f"⚠️ Exception: {e} | retry in {wait:.1f}s...")
            time.sleep(wait)

        # ==============================
        # FALLBACK MODEL
        # ==============================
        if attempt == retries - 2:
            log(f"🔁 Switching to fallback model: {FALLBACK_MODEL}")
            model_to_use = FALLBACK_MODEL

    if CURRENT_ARTICLE_STATS is not None:
        CURRENT_ARTICLE_STATS["failed_calls"] += 1

    return "[FAILED AFTER RETRIES]"


# ==============================
# FILE HELPER
# ==============================

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ==============================
# TEST CONNECTION
# ==============================

def test_connection():
    log("🔌 Testing connection...")
    result = call_api("Say hello briefly")
    log(f"Response: {result}")

    if "[ERROR]" in result or "[FAILED" in result or "[RATE LIMIT FAILED]" in result:
        log("❌ Connection failed\n")
        return False

    log("✅ Connection OK\n")
    return True


# ==============================
# GENERATE OUTLINE
# ==============================

def generate_outline(topic, template):
    prompt = template.replace("{TOPIC}", topic)
    result = call_api(prompt)

    sections = [
        line.strip()
        for line in result.split("\n")
        if line.strip()
    ]

    log(f"🧩 Outline generated | total_sections={len(sections)}")
    for i, section in enumerate(sections, 1):
        log(f"   {i}. {section}")

    return sections


# ==============================
# GENERATE SECTION
# ==============================

def generate_section(topic, section, style, template):
    prompt = (
        template
        .replace("{TOPIC}", topic)
        .replace("{SECTION}", section)
        .replace("{STYLE}", style)
    )

    return call_api(prompt)


# ==============================
# GENERATE FULL ARTICLE
# ==============================

def generate_full_article(topic, style, outline_template, section_template):
    global CURRENT_ARTICLE_STATS

    CURRENT_ARTICLE_STATS = init_article_stats(topic)

    log(f"\n📌 Generating article: {topic}")
    article_start = time.time()

    sections = generate_outline(topic, outline_template)
    article = f"# {topic}\n\n"

    total_sections = len(sections)

    for i, section in enumerate(sections, 1):
        section_start = time.time()
        log(f"✍️ [{i}/{total_sections}] Writing section: {section}")

        content = generate_section(topic, section, style, section_template)

        article += f"## {section}\n\n{content}\n\n"

        section_words = count_words(content)
        section_time = time.time() - section_start

        log(
            f"📝 Section done | section={i}/{total_sections} | "
            f"words={section_words} | time={format_seconds(section_time)}"
        )

        delay = random.uniform(8, 12)
        log(f"⏳ Delay {delay:.1f}s\n")
        time.sleep(delay)

    total_time = time.time() - article_start
    CURRENT_ARTICLE_STATS["end_time"] = time.time()

    # final words / estimated tokens
    article_words = count_words(article)
    if CURRENT_ARTICLE_STATS["total_tokens"] == 0:
        CURRENT_ARTICLE_STATS["estimated_tokens"] = estimate_tokens_from_text(article)

    log(
        f"✅ Article complete | topic={topic} | words={article_words} | total_time={format_seconds(total_time)}"
    )

    final_article = build_article_with_metadata(article, CURRENT_ARTICLE_STATS)
    return final_article


# ==============================
# BUILD ARTICLE WITH METADATA
# ==============================

def build_article_with_metadata(article_text, stats):
    body_words = count_words(article_text)
    total_time_seconds = (stats["end_time"] - stats["start_time"]) if stats["end_time"] else 0

    models_used = ", ".join(stats["model_actuals"]) if stats["model_actuals"] else stats["model_requested"]

    if stats["total_tokens"] > 0:
        token_info = (
            f"- Prompt tokens: {stats['prompt_tokens']}\n"
            f"- Completion tokens: {stats['completion_tokens']}\n"
            f"- Total tokens: {stats['total_tokens']}\n"
        )
    else:
        token_info = f"- Estimated tokens: {stats['estimated_tokens']}\n"

    metadata = (
        f"> Generated with AI Article Generator\n>\n"
        f"> **Metadata**\n"
        f"> - Requested model: {stats['model_requested']}\n"
        f"> - Model used: {models_used}\n"
        f"> - Total generate time: {format_seconds(total_time_seconds)}\n"
        f"> - Total words: {body_words}\n"
        f"> - API calls: {stats['api_calls']}\n"
        f"> - Successful calls: {stats['success_calls']}\n"
        f"> - Failed calls: {stats['failed_calls']}\n"
        f"> - Rate limit hits: {stats['rate_limit_hits']}\n"
        f"> {token_info.replace(chr(10), chr(10) + '> ')}\n\n"
    )

    return metadata + article_text


# ==============================
# SAVE FILE
# ==============================

def save_markdown(topic, text):
    filename = sanitize_filename(topic)
    path = os.path.join(OUTPUT_DIR, f"{filename}.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    log(f"💾 Markdown saved: {path}")


# ==============================
# MAIN
# ==============================

def main():
    global MODEL

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    setup_logger()

    log("========== AI ARTICLE GENERATOR START ==========")

    # ==============================
    # CHOOSE MODEL + TEST
    # ==============================

    while True:
        MODEL = choose_model()
        log(f"\n🔍 Testing model: {MODEL}\n")

        # temporary dummy stats for test
        global CURRENT_ARTICLE_STATS
        CURRENT_ARTICLE_STATS = init_article_stats("connection_test")

        if test_connection():
            log("🚀 Ready to use model!\n")
            break
        else:
            log("🔁 Connection failed. Please select another model...\n")

    # ==============================
    # START GENERATION
    # ==============================

    log("🚀 Start generating articles...\n")

    topics = load_file("topics.txt").splitlines()
    style = load_file("style.txt")
    outline_template = load_file("outline_prompt.txt")
    section_template = load_file("section_prompt.txt")

    cleaned_topics = [topic.strip() for topic in topics if topic.strip()]
    total_topics = len(cleaned_topics)

    log(f"📚 Total topics: {total_topics}")

    for index, topic in enumerate(cleaned_topics, 1):
        log(f"\n==============================")
        log(f"📌 Topic Progress: {index}/{total_topics}")
        log(f"📌 Topic: {topic}")
        log(f"==============================")

        article = generate_full_article(
            topic,
            style,
            outline_template,
            section_template
        )

        save_markdown(topic, article)

        log(f"✅ Saved: {topic}")

    log("\n========== ALL TASKS FINISHED ==========")
    log(f"📝 Verbose log saved at: {LOG_FILE}")


# ==============================

if __name__ == "__main__":
    main()