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
      
