# Time-Locked File Encryptor

A file encryption tool where files genuinely cannot be decrypted before a
target amount of time has passed — enforced by a cryptographic time-lock
puzzle (Rivest, Shamir, Wagner, 1996), not a date check that could be
bypassed by editing the code.

## How it works

Unlike a naive implementation that checks `datetime.now()` against a stored
unlock date (trivially bypassed by anyone with the source code), this uses
a **time-lock puzzle**: the encryption key is derived from repeated modular
squaring, `x -> x^2 mod n`, applied sequentially `t` times.

- The person locking the file knows two secret prime factors of `n`, which
  lets them compute the final squared value instantly via Euler's theorem
  — this is the "shortcut" only the locker has.
- Anyone trying to unlock the file does NOT know those primes, so they must
  perform all `t` squarings one after another for real. Squaring cannot be
  parallelized (each step depends on the last), so no amount of extra CPU
  cores, GPUs, or cloud compute lets someone skip ahead.
- `t` is calibrated to the target machine's actual squaring speed
  (`calibrate.py`), converting a desired wait time into a required squaring count.

## Usage

    python calibrate.py
    python lock.py myfile.txt --seconds 3600 --rate <measured_rate>
    python unlock.py myfile.txt.timelocked

## Limitation (stated honestly)

The unlock time is only as accurate as the machine performing the
calculation — a faster machine finishes slightly sooner than the target,
a slower one slightly later. This is an inherent property of time-lock
puzzles, not a bug in this implementation.

## Why this matters

Most "time-locked" tools online are just a date check in the code, which
provides zero real security — anyone can patch it out. This project
implements the actual cryptographic construction that makes the delay
mathematically enforced.