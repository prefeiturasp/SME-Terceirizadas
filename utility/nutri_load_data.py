import pandas as pd

from sme_pratoaberto_terceirizadas.user_profiles.models import NutritionistProfile, RegionalDirectorProfile

df = pd.read_csv('nutris.csv', sep=',', converters={'RF': str})
df['DRE'] = df['DRE'].str.strip()
df['NOME'] = df['NOME'].str.strip()
df['RF'] = df['RF'].str.strip()


def get_or_create_dre(abbreviation):
    reg = RegionalDirectorProfile.objects.filter(abbreviation=abbreviation).first()
    if not reg:
        reg = RegionalDirectorProfile(abbreviation=abbreviation)
        reg.save()
    return reg


for _, line in df.iterrows():
    print(line.RF, line.NOME, line.DRE.replace(' ', '').replace('.', ''))
    dre = get_or_create_dre(abbreviation=line.DRE.replace(' ', '').replace('.', ''))
    print(dre)
    print('________')
    n = NutritionistProfile(name=line.NOME,
                            functional_register=line.RF,
                            regional_director=dre)
    n.save()
