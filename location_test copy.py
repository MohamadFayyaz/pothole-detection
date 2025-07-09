#!/usr/bin/env python3
# ================================================================
#  QUICK VISUAL POSITIONAL ACCURACY TEST
#  — Mengukur seberapa jauh perbedaan posisi (GPS) antara:
#    • Koordinat yang dilaporkan aplikasi  (lat_app, lon_app)
#    • Koordinat referensi/ground-truth   (lat_ref, lon_ref)
#  — Metode: jarak equirectangular (flat-Earth) ≈ galat <0,2 % di lintang <5°
# ================================================================

# ------------------------------------------------
# 0) Import pustaka yang diperlukan
# ------------------------------------------------
import math          # fungsi matematika dasar (cos, radians, sqrt, dsb.)
import pandas as pd  # pengolahan data tabular (CSV → DataFrame)
import numpy as np   # fungsi numerik tambahan (percentile)

# ------------------------------------------------
# 1) Definisi fungsi penghitung jarak equirectangular
# ------------------------------------------------
def flat_distance(lat1: float, lon1: float,
                  lat2: float, lon2: float) -> float:
    """
    Mengembalikan jarak permukaan bumi (meter) antara dua titik
    menggunakan pendekatan equirectangular.

    Kelebihan:
      • Rumus sederhana (hanya +,-,*,cos,√) → cepat dihitung vectorised.
      • Cukup akurat untuk lintang kecil (|lat| ≲ 5°), galat < 0,2 %.
    """
    # Konversi selisih lintang (Δlat) dari derajat ke meter
    dlat_m = (lat2 - lat1) * 111_320          # 1° lintang ~ 111.320 m

    # Konversi selisih bujur (Δlon) → meter
    # Faktor kosinus(lat_mean) karena jarak 1° bujur mengecil di dekat kutub
    lat_mean_rad = math.radians((lat1 + lat2) / 2.0)
    dlon_m = (lon2 - lon1) * 111_320 * math.cos(lat_mean_rad)

    # Jarak datar (Pythagoras di bidang 2-D)
    return math.hypot(dlat_m, dlon_m)

# ------------------------------------------------
# 2) Muat data CSV dan hitung error tiap pasang titik
# ------------------------------------------------
INPUT_CSV  = "pengujian lokasi TA.csv"   # nama file masukan
OUTPUT_CSV = "pairs_with_error.csv"      # nama file keluaran

# Baca CSV menjadi DataFrame; pastikan kolom sesuai:
# lat_app, lon_app, lat_ref, lon_ref
df = pd.read_csv(INPUT_CSV)

# Tambah kolom 'error_m' berisi jarak aplikasi-referensi (meter)
df["error_m"] = df.apply(
    lambda r: flat_distance(r.lat_app, r.lon_app, r.lat_ref, r.lon_ref),
    axis=1
)

# ------------------------------------------------
# 3) Hitung statistik ringkas galat (error)
# ------------------------------------------------
metrics = {
    "N"            : len(df),                           # jumlah pasangan titik
    "Mean_err_m"   : df.error_m.mean(),                 # rata-rata galat
    "Median_err_m" : df.error_m.median(),               # median galat
    "RMSE_m"       : math.sqrt((df.error_m ** 2).mean()),# root mean square error
    "CE95_m"       : np.percentile(df.error_m, 95),     # radius yg mencakup 95 % data
    "Max_err_m"    : df.error_m.max(),                  # galat terburuk
}

print("\nRingkasan galat (meter):")
print(pd.Series(metrics).round(3))  # tampilkan 3 digit desimal agar rapi

# ------------------------------------------------
# 4) Klasifikasi pass/fail berdasarkan ambang tertentu
# ------------------------------------------------
THRESHOLD = 10        # meter – ubah sesuai kebutuhan evaluasi
df["is_pass"] = df.error_m <= THRESHOLD        # True jika error ≤ threshold
pass_rate = df["is_pass"].mean() * 100         # % data yg lolos

# Cetak ringkasan kelulusan
print(
    f"\nPass rate (≤{THRESHOLD} m): {pass_rate:.1f}%  "
    f"({df['is_pass'].sum()}/{len(df)})"
)

# ------------------------------------------------
# 5) Simpan DataFrame hasil (lengkap: error + status pass) ke CSV
# ------------------------------------------------
df.to_csv(OUTPUT_CSV, index=False)
print(f"\n>> Hasil lengkap disimpan ke: {OUTPUT_CSV}")
