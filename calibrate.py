import time

def benchmark_squarings(n_bits=2048, duration_seconds=3):
    """Measure how many modular squarings this machine can do per second."""
    n = (1 << n_bits) - 1  # a large-ish modulus for benchmarking purposes
    x = 12345678901234567890

    count = 0
    start = time.time()
    while time.time() - start < duration_seconds:
        x = pow(x, 2, n)
        count += 1

    rate = count / duration_seconds
    print(f"This machine performs approximately {rate:,.0f} squarings/second (at {n_bits}-bit modulus)")
    return rate

if __name__ == "__main__":
    benchmark_squarings()