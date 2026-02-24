import utils

text_1 = """Para 1

Para 2

Para 3"""

text_2 = """**Reasoning**
This is reasoning.

Para 1 (Answer)"""

text_3 = """This is a short answer."""

print(f"--- Text 1 (3 paras) ---\nOriginal:\n{text_1}\n\nStripped:\n{utils.strip_reasoning(text_1)}")
print(f"\n--- Text 2 (Pseudo-Reasoning) ---\nOriginal:\n{text_2}\n\nStripped:\n{utils.strip_reasoning(text_2)}")
print(f"\n--- Text 3 (Short) ---\nOriginal:\n{text_3}\n\nStripped:\n{utils.strip_reasoning(text_3)}")
