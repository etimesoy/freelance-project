def discount_code_generator(seed=None):
    import uuid

    if (not seed) or (type(seed) != str) or (len(seed) < 10):
        seed = str(uuid.uuid4())[:10]

    code = "Exental-"
    for character in seed:
        value = str(ord(character))
        code += value

    return code[:18]
