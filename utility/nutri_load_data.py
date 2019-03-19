import pandas as pd

df = pd.read_csv('nutris.csv', sep=',', converters={'RF': str})

for _, line in df.iterrows():
    print(line.RF, line.NOME, line.DRE)
    print('________--')
