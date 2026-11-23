"""Encryptor: monoalphabetic, polyalphabetic (Vigenère), Playfair and Polybius (8x8) ciphers."""
import string

GRID = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ."
MODES = ("monoalphabetic", "vigenere", "playfair", "polybius")


# ---------- Monoalphabetic (one fixed substitution alphabet, scrambled by a keyword) ----------
def _mono_alphabet(key):
    k = []
    for c in (key or "").upper():
        if "A" <= c <= "Z" and c not in k:
            k.append(c)
    if not k:
        raise ValueError("Enter a keyword (letters) for the monoalphabetic cipher")
    # keyword first, then the rest of the alphabet reversed (so a short key never gives the identity mapping)
    rest = [c for c in reversed(string.ascii_uppercase) if c not in k]
    return "".join(k + rest)


def monoalphabetic(text, key, decrypt=False):
    plain, cipher = string.ascii_uppercase, _mono_alphabet(key)
    src, dst = (cipher, plain) if decrypt else (plain, cipher)
    return text.translate(str.maketrans(src + src.lower(), dst + dst.lower()))


# ---------- Polyalphabetic: Vigenère (letters only, case preserved) ----------
def vigenere(text, key, decrypt=False):
    k = [ord(c) - 65 for c in (key or "").upper() if "A" <= c <= "Z"]
    if not k:
        raise ValueError("Enter a keyword (letters) for the polyalphabetic cipher")
    sign, j, out = (-1 if decrypt else 1), 0, []
    for ch in text:
        if ch.isascii() and ch.isalpha():
            base = 65 if ch.isupper() else 97
            out.append(chr((ord(ch) - base + sign * k[j % len(k)]) % 26 + base))
            j += 1
        else:
            out.append(ch)
    return "".join(out)


# ---------- Playfair (5x5 grid, I/J merged, letters only) ----------
def _square(key):
    if not any("A" <= c <= "Z" for c in (key or "").upper()):
        raise ValueError("Enter a keyword (letters) for the Playfair cipher")
    seen = []
    for c in key.upper().replace("J", "I") + "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if "A" <= c <= "Z" and c not in seen:
            seen.append(c)
    return "".join(seen)


def _letters(text):
    return [c for c in text.upper().replace("J", "I") if "A" <= c <= "Z"]


def _playfair(pairs, key, step):
    sq, out = _square(key), []
    for a, b in pairs:
        ra, ca = divmod(sq.index(a), 5)
        rb, cb = divmod(sq.index(b), 5)
        if ra == rb:                      # same row: shift along the row
            ca, cb = (ca + step) % 5, (cb + step) % 5
        elif ca == cb:                    # same column: shift along the column
            ra, rb = (ra + step) % 5, (rb + step) % 5
        else:                             # rectangle: swap columns
            ca, cb = cb, ca
        out.append(sq[ra * 5 + ca] + sq[rb * 5 + cb])
    return "".join(out)


def playfair_encrypt(text, key):
    letters, pairs, i = _letters(text), [], 0
    if not letters:
        raise ValueError("Playfair needs at least one letter in the text")
    while i < len(letters):
        a = letters[i]
        b = letters[i + 1] if i + 1 < len(letters) else "X"
        if a == b:
            b, i = "X", i + 1             # split double letters with X
        else:
            i += 2
        pairs.append((a, b))
    return _playfair(pairs, key, 1)


def playfair_decrypt(data, key):
    letters = _letters(data)
    if not letters or len(letters) % 2:
        raise ValueError("Not valid Playfair text (needs an even number of letters)")
    return _playfair(list(zip(letters[::2], letters[1::2])), key, -1)


# ---------- Polybius (8x8 grid, optional keyword scrambles the grid) ----------
def _grid(key=""):
    seen, out = set(), []
    for c in (key or "") + GRID:
        if c in GRID and c not in seen:
            seen.add(c)
            out.append(c)
    return "".join(out)


def polybius_encrypt(text, key=""):
    g, out = _grid(key), []
    for ch in text:
        i = g.find(ch)
        # characters outside the grid are escaped as ~hex~ so any text works
        out.append(f"~{ord(ch):x}~" if i < 0 else f"{i // 8 + 1}{i % 8 + 1}")
    return "".join(out)


def polybius_decrypt(data, key=""):
    g, out, i = _grid(key), [], 0
    try:
        while i < len(data):
            if data[i] == "~":
                j = data.index("~", i + 1)
                out.append(chr(int(data[i + 1:j], 16)))
                i = j + 1
            else:
                r, c = int(data[i]) - 1, int(data[i + 1]) - 1
                if not (0 <= r < 8 and 0 <= c < 8):
                    raise ValueError
                out.append(g[r * 8 + c])
                i += 2
    except (ValueError, IndexError, OverflowError):
        raise ValueError("Not valid Polybius text (expects pairs of digits 1-8)")
    return "".join(out)


# ---------- Public API used by app.py ----------
def convert(mode, text, key, decrypt=False):
    if mode == "monoalphabetic":
        return monoalphabetic(text, key, decrypt)
    if mode == "vigenere":
        return vigenere(text, key, decrypt)
    if mode == "playfair":
        return playfair_decrypt(text, key) if decrypt else playfair_encrypt(text, key)
    if mode == "polybius":
        return polybius_decrypt(text, key) if decrypt else polybius_encrypt(text, key)
    raise ValueError("Unknown cipher")


def key_table(mode, key):
    """Data the page draws under the converter, or None when there is nothing to show."""
    try:
        if mode == "monoalphabetic":
            return {"kind": "mono", "plain": string.ascii_uppercase, "cipher": _mono_alphabet(key)}
        if mode == "playfair":
            return {"kind": "grid", "cols": 5, "cells": list(_square(key))}
        if mode == "polybius":
            return {"kind": "grid", "cols": 8, "cells": list(_grid(key))}
    except ValueError:
        pass
    return None