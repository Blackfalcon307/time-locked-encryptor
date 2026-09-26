import json
import hashlib
import base64
import time
import argparse
from cryptography.fernet import Fernet

def solve_puzzle(n: int, a: int, t: int):
    """The slow path — no shortcut available here, must do t real squarings."""
    print(f"Solving puzzle: {t:,} sequential squarings required...")
    start = time.time()

    result = a
    for i in range(t):
        result = pow(result, 2, n)
        if i % max(t // 20, 1) == 0:  # progress update every ~5%
            elapsed = time.time() - start
            print(f"  Progress: {i:,}/{t:,} squarings ({elapsed:.1f}s elapsed)", end="\r")

    elapsed = time.time() - start
    print(f"\nPuzzle solved in {elapsed:.2f} seconds")
    return result


def unlock_file(locked_path: str):
    with open(locked_path, "r") as f:
        data = json.load(f)

    puzzle = data["puzzle"]
    n, a, t = puzzle["n"], puzzle["a"], puzzle["t"]

    puzzle_key_material = solve_puzzle(n, a, t)

    derived_key = hashlib.sha256(str(puzzle_key_material).encode()).digest()
    fernet_key = base64.urlsafe_b64encode(derived_key)
    fernet = Fernet(fernet_key)

    ciphertext = base64.urlsafe_b64decode(data["ciphertext"])
    plaintext = fernet.decrypt(ciphertext)

    output_path = locked_path.replace(".timelocked", "")
    with open(output_path, "wb") as f:
        f.write(plaintext)

    print(f"Unlocked: {locked_path} -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Attempt to unlock a time-locked file")
    parser.add_argument("filepath")
    args = parser.parse_args()

    unlock_file(args.filepath)