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

def convert_from_db_format(db_text):
    if not db_text or str(db_text).lower() == 'nan':
        return ""
    return str(db_text).replace('<BR>', '\n').replace('<slide>', '\n\n').strip()

def extract_root_and_suffix(key_str):
    if not key_str:
        return 'C', ''
    m = re.match(r'^([A-G][#b]?)(.*)$', str(key_str).strip())
    return (m.group(1), m.group(2)) if m else ('C', '')

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
