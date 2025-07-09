#!/usr/bin/env python3
# ================================================================
#  QUICK VISUAL POSITIONAL ACCURACY TEST
#  Hitung selisih dua pasang koordinat (aplikasi vs referensi)
#  dengan pendekatan equirectangular (flat-Earth) ≈ <0,2 % galat
# ================================================================

import math
import pandas as pd
import numpy as np

# ---------- 1) fungsi equirectangular / flat-Earth distance ----------
def flat_distance(lat1: float, lon1: float,
                  lat2: float, lon2: float) -> float:
    """
    Perkiraan jarak permukaan bumi (meter) menggunakan rumus equirectangular.
    Akurasi cukup untuk |lat| < 5° (sekitar ekuator) dengan galat < 0,2 %.
    """
    # Δlatitude dalam meter
    dlat_m = (lat2 - lat1) * 111_320                     # 1° lat ≈ 111 320 m
    # Δlongitude disesuaikan kosinus garis lintang rata-rata pasangan
    lat_mean_rad = math.radians((lat1 + lat2) / 2.0)
    dlon_m = (lon2 - lon1) * 111_320 * math.cos(lat_mean_rad)
    # Jarak Euclidean (Pythagoras)
    return math.hypot(dlat_m, dlon_m)

# ---------- 2) muat data & hitung error ----------
# Pastikan kolom CSV: lat_app, lon_app, lat_ref, lon_ref
INPUT_CSV  = "pengujian lokasi TA.csv"   
OUTPUT_CSV = "pairs_with_error.csv"

df = pd.read_csv(INPUT_CSV)

# hitung error per baris
df["error_m"] = df.apply(
    lambda r: flat_distance(r.lat_app, r.lon_app, r.lat_ref, r.lon_ref),
    axis=1
)

# ---------- 3) statistik ringkas ----------
metrics = {
    "N"            : len(df),
    "Mean_err_m"   : df.error_m.mean(),
    "Median_err_m" : df.error_m.median(),
    "RMSE_m"       : math.sqrt((df.error_m ** 2).mean()),
    "CE95_m"       : np.percentile(df.error_m, 95),   # Circular Error 95 %
    "Max_err_m"    : df.error_m.max(),
}
print("\nRingkasan galat (meter):")
print(pd.Series(metrics).round(3))

# ---------- 4) klasifikasi lulus/gagal ----------
THRESHOLD = 10        # meter; ubah sesuai kebutuhan riset
df["is_pass"] = df.error_m <= THRESHOLD
pass_rate = df["is_pass"].mean() * 100

print(
    f"\nPass rate (≤{THRESHOLD} m): {pass_rate:.1f}%  "
    f"({df['is_pass'].sum()}/{len(df)})"
)

# ---------- 5) simpan hasil ----------
df.to_csv(OUTPUT_CSV, index=False)
print(f"\n>> Hasil lengkap tersimpan ke: {OUTPUT_CSV}")
