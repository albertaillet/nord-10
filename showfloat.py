#!/usr/bin/env python3
# Script to show the internal representation of a 32-bit float
import struct

E, M = 8, 23  # Exponent and fraction bit lengths
M_DIV = 1 << M  # 2^23
BIAS = (1 << (E - 1)) - 1 # 127
E_MAX = (1 << E) - 1  # 255


def show_float32(x: float):
    print(f"value: {x!r}")
    u = int.from_bytes(struct.pack('>f', x), 'big')
    s = (u >> (E + M)) & 1
    e = (u >> M) & E_MAX
    m = u & (M_DIV - 1)
    if e == 0 and m == 0:
        kind = "zero"
        exp = 0
        mantissa = 0.0
    elif e == 0:
        kind = "subnormal"
        exp = 1 - BIAS  # -126
        mantissa = m  # no implicit leading 1
    elif e == E_MAX:
        kind = "infinity" if m == 0 else "NaN"
        exp = None
        mantissa = None
    else:
        kind = "normal"
        exp = e - BIAS
        # mantissa = m + M_DIV  # implicit leading 1
        mantissa = (m | M_DIV) # implicit leading 1

    print(f"bits : {s=:b} {e=:0{E}b} {m=:0{M}b} ({u=:032b})")
    print(f"numb : {s=:d} {e=:<{E}d} {m=:<{M}d} ({u=:d})")
    print(f"kind : {kind}")
    if kind in ("normal", "subnormal", "zero"):
        recon = ((-1)**s) * (2**exp) * mantissa / M_DIV
        assert abs(recon - x) < 2e-7, f"{recon=} does not match original {x=}"
        print(f"recon ≈ {recon}")
        u_recon = int.from_bytes(struct.pack('>f', recon), 'big')
        assert u_recon == u, f"Bits differ: {u_recon=:08x} vs {u=:08x}"
    print()

# Examples
show_float32(0.0)
show_float32(-0.0)
show_float32(2**-149)  # Smallest positive subnormal
show_float32(-2**-149)  # Smallest negative subnormal
show_float32(0.15625)
show_float32(1.0)
show_float32(1.2)
show_float32(2.0)
show_float32(64.0)
show_float32(-15.3)
show_float32(float("inf"))
show_float32(-float("inf"))