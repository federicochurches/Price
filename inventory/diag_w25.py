import pandas as pd

df_raw = pd.read_excel('dataHoteles_contratos.xlsx', header=1)
df_pp = df_raw[df_raw['TipoHotel'].isin(['solo propio','Propio_con_tercero','sólo propio'])]
print(f"PP total: {len(df_pp)}")
print(f"PP FechaCreacion nula: {df_pp['FechaCreacion'].isna().sum()}")

mask_valida = df_pp['FechaCreacion'].notna()
df2 = df_pp[mask_valida].copy()
df2['fecha_dt'] = pd.to_datetime(df2['FechaCreacion'].str.slice(0,19), errors='coerce')
df2 = df2[df2['fecha_dt'].notna()]
print(f"PP con fecha valida: {len(df2)}")

mask_w25 = (df2['fecha_dt'] >= '2026-06-15') & (df2['fecha_dt'] <= '2026-06-21 23:59:59')
print(f"PP con FechaCreacion en W25 (15-21 jun): {mask_w25.sum()}")
print(df2[mask_w25][['Hotel','TipoHotel','FechaCreacion']].head(10))
