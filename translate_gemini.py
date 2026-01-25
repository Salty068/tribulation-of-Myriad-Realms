import os
import time
import re
import google.generativeai as genai
from pathlib import Path

# ==========================
# CONFIG
# ==========================
MODEL_NAME = "gemini-1.5-flash"  # or "gemini-1.5-pro" for better quality
CN_DIR = Path("cn_chapters")
EN_DIR = Path("en_chapters")
EARLY_GLOSSARY = Path("early gloss.txt").read_text(encoding="utf-8")
LATE_GLOSSARY = Path("Late gloss.txt").read_text(encoding="utf-8")
STYLE_REFERENCE = Path("Style_reference.txt").read_text(encoding="utf-8")
UPDATE_GLOSS_FILE = Path("update_gloss.txt")

# Load update glossary if it exists
try:
    UPDATE_GLOSSARY = UPDATE_GLOSS_FILE.read_text(encoding="utf-8")
except FileNotFoundError:
    UPDATE_GLOSSARY = ""

# Retry settings
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 10  # seconds

# Translation settings
MAX_OUTPUT_TOKENS = 8192  # Gemini's max output tokens
CHUNK_SIZE = 3000  # characters per chunk for fallback mode

# ==========================
# SETUP
# ==========================
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Configure the model
generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": MAX_OUTPUT_TOKENS,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config=generation_config,
    safety_settings=safety_settings,
)

EN_DIR.mkdir(exist_ok=True)

# ==========================
# PROMPT TEMPLATE
# ==========================
def build_prompt(chinese_text, is_continuation=False, previous_context=""):
    if is_continuation:
        return f"""
Continue translating from where you left off. The previous section ended with:
---
{previous_context}
---

Continue translating the following Chinese text, maintaining consistency:

STRICT RULES:
1. Use glossary terms EXACTLY as defined.
2. If a term appears in both glossaries, use the LATE glossary.
3. Do NOT invent names, realms, races, or titles.
4. Preserve pacing and paragraph structure.
5. Do NOT summarize or modernize.

GLOSSARY (LATE — highest priority):
{LATE_GLOSSARY}

GLOSSARY (EARLY — fallback):
{EARLY_GLOSSARY}

GLOSSARY (UPDATE — recently added terms):
{UPDATE_GLOSSARY}

CHINESE TEXT TO CONTINUE:
{chinese_text}
""".strip()
    else:
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

GLOSSARY (UPDATE — recently added terms):
{UPDATE_GLOSSARY}

CHINESE TEXT:
{chinese_text}
""".strip()

# ==========================
# TRANSLATION HELPERS
# ==========================
def translate_with_retry(prompt, attempt_label=""):
    """Translate with automatic retry on errors"""
    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(prompt)
            
            # Check if response was blocked
            if not response.text:
                if hasattr(response, 'prompt_feedback'):
                    raise RuntimeError(f"Response blocked: {response.prompt_feedback}")
                raise RuntimeError("Empty response from API")
            
            return response.text.strip()
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle rate limiting
            if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                if attempt < MAX_RETRIES - 1:
                    delay = INITIAL_RETRY_DELAY * (2 ** attempt)
                    print(f"  ⚠️ Rate limit hit{attempt_label}")
                    print(f"  Retrying in {delay}s... (attempt {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(delay)
                else:
                    print(f"  ❌ Failed after {MAX_RETRIES} attempts due to rate limiting")
                    raise
            else:
                if attempt < MAX_RETRIES - 1:
                    delay = INITIAL_RETRY_DELAY * (2 ** attempt)
                    print(f"  ⚠️ API Error{attempt_label}: {error_msg[:100]}")
                    print(f"  Retrying in {delay}s... (attempt {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(delay)
                else:
                    print(f"  ❌ Failed after {MAX_RETRIES} attempts")
                    raise

def is_truncated(text, original_length):
    """Check if translation seems truncated"""
    # If output is very short compared to input
    if len(text) < original_length * 0.3:
        return True
    # If ends mid-sentence (no proper ending punctuation)
    if text and not text[-1] in '.!?"\'':
        return True
    return False

def split_into_paragraphs(text):
    """Split Chinese text into natural paragraph chunks"""
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        para_length = len(para)
        
        if current_length + para_length > CHUNK_SIZE and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [para]
            current_length = para_length
        else:
            current_chunk.append(para)
            current_length += para_length
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def translate_chapter_hybrid(cn_text, chapter_name):
    """
    Chunk-based translation strategy:
    Split chapter into paragraphs and translate each chunk
    """
    print(f"  Strategy: Chunk-based translation...")
    
    # Split into chunks
    chunks = split_into_paragraphs(cn_text)
    print(f"  Split into {len(chunks)} chunks")
    
    translations = []
    unmapped_terms_list = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"  Translating chunk {i}/{len(chunks)}...")
        chunk_prompt = build_prompt(chunk)
        chunk_translation = translate_with_retry(chunk_prompt, f" (chunk {i})")
        
        # Extract unmapped terms if present
        if "[UNMAPPED_TERMS]" in chunk_translation:
            parts = chunk_translation.split("[UNMAPPED_TERMS]")
            clean_translation = parts[0].strip()
            unmapped_section = parts[1].strip() if len(parts) > 1 else ""
            
            # Add to translations without the unmapped section
            translations.append(clean_translation)
            
            # Collect unmapped terms
            if unmapped_section:
                unmapped_terms_list.append(f"\n--- From {chapter_name} (chunk {i}) ---\n{unmapped_section}")
        else:
            translations.append(chunk_translation)
        
        time.sleep(2)  # Small delay between chunks to avoid rate limiting
    
    # Save unmapped terms to file if any were found
    if unmapped_terms_list:
        try:
            with open(UPDATE_GLOSS_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n\n=== {chapter_name} ===\n")
                f.write("".join(unmapped_terms_list))
            print(f"  📝 Saved unmapped terms to {UPDATE_GLOSS_FILE}")
        except Exception as e:
            print(f"  ⚠️ Could not save unmapped terms: {e}")
    
    print(f"  ✓ Complete via chunking")
    return "\n\n".join(translations)

# ==========================
# TRANSLATION LOOP
# ==========================
for cn_file in sorted(CN_DIR.glob("ch_*.txt")):
    out_file = EN_DIR / cn_file.name
    
    # Extract chapter number
    chapter_num = int(cn_file.stem.split('_')[1])
    
    # Skip chapters before 673
    if chapter_num < 673:
        continue

    # Skip already translated chapters
    if out_file.exists():
        print(f"Skipping {cn_file.name} (already translated)")
        continue

    print(f"\nTranslating {cn_file.name}...")
    
    cn_text = cn_file.read_text(encoding="utf-8")
    print(f"  Input: {len(cn_text)} characters")
    
    try:
        # Use hybrid translation strategy
        translated_text = translate_chapter_hybrid(cn_text, cn_file.name)
        
        # Save result
        out_file.write_text(translated_text, encoding="utf-8")
        print(f"  ✓ Saved {out_file.name} ({len(translated_text)} characters)")
        
    except Exception as e:
        print(f"  ❌ Error translating {cn_file.name}: {e}")
        print(f"  Stopping to prevent data loss")
        break

print("\n✓ Translation complete!")
