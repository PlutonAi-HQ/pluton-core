def generate_referral_code():
    import random
    import string

    chars = "".join(c for c in string.ascii_letters + string.digits if c not in "01OIL")
    return "".join(random.choices(chars, k=16))


if __name__ == "__main__":
    for _ in range(100):
        print(generate_referral_code())
