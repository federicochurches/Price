import pandas as pd

df = pd.read_excel('dataHoteles_contratos.xlsx', skiprows=[0])
print("Columnas:")
print(list(df.columns)[:15])
print()
print(f"Filas: {len(df)}")
print()
print("Primeras 2:")
print(df[['IdHotel', 'FechaCreacion', 'Hotel', 'EsTercerov2']].head(2))
