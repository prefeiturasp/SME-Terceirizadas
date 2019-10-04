import environ
import pandas as pd

from sme_terceirizadas.user_profiles.models import NutritionistProfile, RegionalDirectorProfile

env = environ.Env()
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
    names = line.NOME.split(' ')
    first = names[0]
    last = ' '.join(p for p in names[1:])
    n = NutritionistProfile(first_name=first.strip(),
                            last_name=last.strip(),
                            password=env('DEFAULT_PASSWORD'),
                            username=first + last[:3],  # primeiro nome + 3 letras
                            functional_register=line.RF,
                            regional_director=dre)
    n.save()
