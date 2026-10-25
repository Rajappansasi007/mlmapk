import re

MALAYALAM_MAP = {
    'അ': 'a', 'ആ': 'aa', 'ഇ': 'i', 'ഈ': 'ee', 'ഉ': 'u', 'ഊ': 'oo', 'ഋ': 'ru',
    'എ': 'e', 'ഏ': 'e', 'ഐ': 'ai', 'ഒ': 'o', 'ഓ': 'o', 'ഔ': 'au', 'അം': 'am', 'അഃ': 'ah',
    'ക': 'ka', 'ഖ': 'kha', 'ഗ': 'ga', 'ഘ': 'gha', 'ങ': 'nga',
    'ച': 'cha', 'ഛ': 'chha', 'ജ': 'ja', 'ഝ': 'jha', 'ഞ': 'nya',
    'ട': 'ta', 'ഠ': 'tha', 'ഡ': 'da', 'ഢ': 'dha', 'ണ': 'na',
    'ത': 'tha', 'ഥ': 'thha', 'ദ': 'dha', 'ധ': 'dhha', 'ന': 'na',
    'പ': 'pa', 'ഫ': 'pha', 'ബ': 'ba', 'ഭ': 'bha', 'മ': 'ma',
    'യ': 'ya', 'ര': 'ra', 'ല': 'la', 'വ': 'va', 'ശ': 'sha',
    'ഷ': 'sha', 'സ': 'sa', 'ഹ': 'ha', 'ള': 'la', 'ഴ': 'zha', 'റ': 'ra',
    'ാ': 'aa', 'ി': 'i', 'ീ': 'ee', 'ു': 'u', 'ൂ': 'oo', 'ൃ': 'ru',
    'െ': 'e', 'േ': 'e', 'ൈ': 'ai', 'ൊ': 'o', 'ോ': 'o', 'ൌ': 'au',
    '്': '', 'ം': 'm', 'ഃ': 'h',
    'ൺ': 'n', 'ൻ': 'n', 'ർ': 'r', 'ൽ': 'l', 'ൾ': 'l', 'ൿ': 'k'
}

CHORDS_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
CHORDS_FLAT  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

NOTE_MAP = {
    'C': 0, 'B#': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4,
    'Fb': 4, 'F': 5, 'E#': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10, 'B': 11, 'Cb': 11
}

MONTH_TO_SIG = {
    'apr': '4', 'aug': '8', 'mar': '3', 'may': '5', 'jun': '6',
    'jul': '7', 'sep': '9', 'oct': '10', 'nov': '11', 'dec': '12',
    'jan': '1', 'feb': '2'
}

def clean_time_signature(val):
    if not val or str(val).lower() == 'nan':
        return ""
    s = str(val).strip()
    m = re.match(r'^0?(\d+)-([a-zA-Z]{3})$', s)
    if m:
        numerator = m.group(1)
        month_code = m.group(2).lower()
        if month_code in MONTH_TO_SIG:
            return f"{numerator}/{MONTH_TO_SIG[month_code]}"
    return s

def transliterate_malayalam_to_english(text):
    if not text:
        return ""
    output = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in MALAYALAM_MAP:
            base_rom = MALAYALAM_MAP[char]
            if i + 1 < len(text):
                next_char = text[i + 1]
                if next_char == '്':
                    if base_rom.endswith('a'):
                        base_rom = base_rom[:-1]
                    output.append(base_rom)
                    i += 2
                    continue
                elif next_char in ['ാ', 'ി', 'ീ', 'ു', 'ൂ', 'ൃ', 'െ', 'േ', 'ൈ', 'ൊ', 'ോ', 'ൌ']:
                    if base_rom.endswith('a'):
                        base_rom = base_rom[:-1]
                    output.append(base_rom + MALAYALAM_MAP[next_char])
                    i += 2
                    continue
            output.append(base_rom)
        else:
            output.append(char)
        i += 1
    return "".join(output)

def convert_to_db_format(raw_text):
    if not raw_text or not raw_text.strip():
        return ""
    normalized = raw_text.replace('\r\n', '\n').strip()
    slides = [s.strip() for s in re.split(r'\n\s*\n', normalized) if s.strip()]
    formatted_slides = []
    for slide in slides:
        lines = [line.strip() for line in slide.split('\n') if line.strip()]
        formatted_slides.append("<BR>".join(lines))
    return "<slide>".join(formatted_slides)

def convert_from_db_format(db_text):
    if not db_text or str(db_text).lower() == 'nan':
        return ""
    return str(db_text).replace('<BR>', '\n').replace('<slide>', '\n\n').strip()

def extract_root_and_suffix(key_str):
    if not key_str:
        return 'C', ''
    m = re.match(r'^([A-G][#b]?)(.*)$', str(key_str).strip())
    return (m.group(1), m.group(2)) if m else ('C', '')

def get_keys_for_base(orig_key_str):
    if not orig_key_str or str(orig_key_str).lower() == 'nan':
        return ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'], 0
    root, suffix = extract_root_and_suffix(orig_key_str)
    scale_names = CHORDS_FLAT if 'b' in root else CHORDS_SHARP
    key_options = [f"{n}{suffix}" for n in scale_names]
    curr_key_name = f"{root}{suffix}"
    if curr_key_name in key_options:
        default_idx = key_options.index(curr_key_name)
    else:
        key_options.insert(0, curr_key_name)
        default_idx = 0
    return key_options, default_idx

def calculate_semitones(from_key, to_key):
    r1, _ = extract_root_and_suffix(from_key)
    r2, _ = extract_root_and_suffix(to_key)
    return (NOTE_MAP.get(r2, 0) - NOTE_MAP.get(r1, 0)) % 12

def transpose_single_chord(chord_str, semitones):
    if semitones == 0 or not chord_str:
        return chord_str
    def shift_note(root_note):
        idx = NOTE_MAP.get(root_note)
        if idx is not None:
            new_idx = (idx + semitones) % 12
            return CHORDS_FLAT[new_idx] if 'b' in chord_str else CHORDS_SHARP[new_idx]
        return root_note

    pattern = r'^([A-G][#b]?)(.*)$'
    if '/' in chord_str:
        return "/".join(
            shift_note(m.group(1)) + m.group(2) if (m := re.match(pattern, p.strip())) else p.strip()
            for p in chord_str.split('/')
        )
    m = re.match(pattern, chord_str)
    return shift_note(m.group(1)) + m.group(2) if m else chord_str

def format_chords(text, semitones=0):
    if not text:
        return ""
    if semitones != 0:
        def replace_bracket(match):
            return f"[{' '.join(transpose_single_chord(c, semitones) for c in match.group(1).split())}]"
        text = re.sub(r'\[([^\]]+)\]', replace_bracket, text)

    lines = text.split('\n')
    formatted = []
    for line in lines:
        if '[' in line and ']' in line:
            chord_line, lyric_line, i = "", "", 0
            while i < len(line):
                if line[i] == '[':
                    end = line.find(']', i)
                    if end != -1:
                        chord = line[i+1:end]
                        pad = len(lyric_line) - len(chord_line)
                        if pad < 0:
                            chord_line += " " + chord
                            lyric_line += " " * (len(chord_line) - len(lyric_line))
                        else:
                            chord_line += (" " * pad) + chord
                        i = end + 1
                    else:
                        lyric_line += line[i]
                        i += 1
                else:
                    lyric_line += line[i]
                    i += 1
            formatted.extend([chord_line, lyric_line])
        else:
            formatted.append(line)
    return "\n".join(formatted)
