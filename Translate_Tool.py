from deep_translator import GoogleTranslator

def translate_portuguese_to_english(text):
    translator = GoogleTranslator(source='pt', target='en')
    translation = translator.translate(text)
    return translation


# 使用示例
portuguese_text = "Lavabo bem bonito e igual a descrição, veio com uma mancha bem pequena, mas nada que seja um problema, recomendo."
english_text = translate_portuguese_to_english(portuguese_text)
print(f"葡萄牙語: {portuguese_text}")
print(f"英語: {english_text}")