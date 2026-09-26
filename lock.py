import json
import time
import hashlib
import secrets
import base64
from sympy import randprime
from cryptography.fernet import Fernet

def generate_puzzle(unlock_seconds: int, squarings_per_second: float):
    """Create a time-lock puzzle that takes ~unlock_seconds of sequential
    computation to solve, using two secret primes only we know."""

    # Generate two large primes (kept secret — this is our "cheat" shortcut)
    p = randprime(2**255, 2**256)
    q = randprime(2**255, 2**256)
    n = p * q # type: ignore
    phi = (p - 1) * (q - 1) # type: ignore

    t = int(unlock_seconds * squarings_per_second)  # number of sequential squarings required

    a = secrets.randbelow(n - 2) + 2  # type: ignore # random base value, publicly known

    # THE SHORTCUT: because we know phi, we can jump straight to the answer
    # instead of doing t actual squarings. This is the whole trick.
    e = pow(2, t, phi)
    puzzle_key_material = pow(a, e, n) # type: ignore

    # Turn that big number into a usable Fernet key via hashing
    derived_key = hashlib.sha256(str(puzzle_key_material).encode()).digest()
    fernet_key = base64.urlsafe_b64encode(derived_key)

    return {
        "n": n,
        "a": a,
        "t": t,
    }, fernet_key


def lock_file(filepath: str, unlock_seconds: int, squarings_per_second: float):
    puzzle_public, fernet_key = generate_puzzle(unlock_seconds, squarings_per_second)

    fernet = Fernet(fernet_key)

    with open(filepath, "rb") as f:
        data = f.read()

    encrypted = fernet.encrypt(data)

    output = {
        "puzzle": puzzle_public,   # n, a, t are all PUBLIC — safe to share, no secrets here
        "created_at": time.time(),
        "unlock_seconds": unlock_seconds,
        "ciphertext": base64.urlsafe_b64encode(encrypted).decode(),
    }

    output_path = filepath + ".timelocked"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Locked: {filepath} -> {output_path}")
    print(f"Puzzle requires {puzzle_public['t']:,} sequential squarings to solve")
    print(f"Estimated unlock time on THIS machine: ~{unlock_seconds} seconds from now")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Lock a file with a time-lock puzzle")
    parser.add_argument("filepath")
    parser.add_argument("--seconds", type=int, required=True, help="Approx. seconds before it can be unlocked")
    parser.add_argument("--rate", type=float, required=True, help="Squarings/sec from calibrate.py")
    args = parser.parse_args()

    lock_file(args.filepath, args.seconds, args.rate)