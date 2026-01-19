import os
import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError
from pathlib import Path

# ==========================
# CONFIG
# ==========================
MODEL_NAME = "gemini-2.5-flash"
CN_DIR = Path("cn_chapters")
EN_DIR = Path("en_chapters")
EARLY_GLOSSARY = Path("early gloss.txt").read_text(encoding="utf-8")
LATE_GLOSSARY = Path("Late gloss.txt").read_text(encoding="utf-8")
STYLE_REFERENCE = Path("Style_reference.txt").read_text(encoding="utf-8")


# Safety threshold: if output is suspiciously short, stop
MIN_OUTPUT_CHARS = 500

# Retry settings
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 10  # seconds

# ==========================
# SETUP
# ==========================
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

EN_DIR.mkdir(exist_ok=True)

# ==========================
# PROMPT TEMPLATE
# ==========================
def build_prompt(chinese_text):
    return f"""
You are a professional web-novel translator.

TASK:
Translate the following Chinese text into fluent, natural English suitable for continuous reading.

STYLE REQUIREMENT:
Match the WRITING STYLE, FORMATTING, PARAGRAPH STRUCTURE, and DIALOGUE PRESENTATION
of the provided STYLE REFERENCE.
- The style reference is for format and tone only.
- Do NOT reuse or paraphrase its content.

STRICT RULES:
1. Use glossary terms EXACTLY as defined.
2. If a term appears in both glossaries, use the LATE glossary.
3. Do NOT invent names, realms, races, or titles.
4. Preserve pacing and paragraph structure.
5. Do NOT summarize or modernize.
6. If a proper noun, cultivation term, race, realm, title, or place is NOT in any glossary:
   - Transliterate conservatively
   - List it at the end under [UNMAPPED_TERMS]

STYLE REFERENCE (FORMAT & TONE ONLY):
{STYLE_REFERENCE}

GLOSSARY (LATE — highest priority):
{LATE_GLOSSARY}

GLOSSARY (EARLY — fallback):
{EARLY_GLOSSARY}

CHINESE TEXT:
{chinese_text}
""".strip()

# ==========================
# TRANSLATION LOOP
# ==========================
for cn_file in sorted(CN_DIR.glob("ch_*.txt")):
    out_file = EN_DIR / cn_file.name

    # Skip already translated chapters
    if out_file.exists():
        print(f"Skipping {cn_file.name} (already translated)")
        continue

    print(f"Translating {cn_file.name}...")

    cn_text = cn_file.read_text(encoding="utf-8")
    prompt = build_prompt(cn_text)

    # Retry loop for API calls
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=8192
                )
            )
            
            if not response.text:
                raise RuntimeError(f"Empty response for {cn_file.name}")
            
            # Success - break out of retry loop
            break
            
        except (ServerError, ClientError) as e:
            if attempt < MAX_RETRIES - 1:
                delay = INITIAL_RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                print(f"⚠️ API Error: {e}")
                print(f"Retrying in {delay} seconds... (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(delay)
            else:
                print(f"❌ Failed after {MAX_RETRIES} attempts.")
                raise

    translated_text = response.text.strip()

    # Safety check for truncation
    if len(translated_text) < MIN_OUTPUT_CHARS:
        print("⚠️ WARNING: Output unusually short.")
        print("Stopping to avoid silent truncation.")
        break

    out_file.write_text(translated_text, encoding="utf-8")
    print(f"Saved {out_file.name}")

print("Done.")
