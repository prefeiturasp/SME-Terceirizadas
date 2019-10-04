import environ
import pandas as pd

from sme_terceirizadas.user_profiles.models import (RegionalDirectorProfile, AlternateProfile,
                                                    SubManagerProfile)

env = environ.Env()

df = pd.read_csv('DRES.csv', sep=',',
                 converters={'RF': str,
                             'RF2': str})
df['DRE'] = df['DRE'].str.strip()
df['COGESTOR'] = df['COGESTOR'].str.strip()
df['EMAIL'] = df['EMAIL'].str.strip()
df['TELEFONE'] = df['TELEFONE'].str.strip()
df['SUPLENTE'] = df['SUPLENTE'].str.strip()
df['RF2'] = df['RF2'].str.strip()
df['EMAIL2'] = df['EMAIL2'].str.strip()
df['TELEFONE2'] = df['TELEFONE2'].str.strip()


def get_or_create_submanager(line):
    sub = SubManagerProfile.objects.filter(functional_register=line.RF).first()
    if not line.RF:
        return None
    mob, ph = line.TELEFONE.split('_')
    if not sub:
        names = line.COGESTOR.split(' ')
        first = names[0]
        last = ' '.join(p for p in names[1:])
        sub = SubManagerProfile(first_name=first.strip(),
                                last_name=last.strip(),
                                username=first + last[:3],  # primeiro nome + 3 letras
                                email=line.EMAIL,
                                password=env('DEFAULT_PASSWORD'),
                                functional_register=line.RF,
                                phone=ph,
                                mobile_phone=mob)
        sub.save()
    return sub


def get_or_create_alternate(line):
    sub = AlternateProfile.objects.filter(functional_register=line.RF2).first()
    if not line.RF2:
        return None
    if not sub:
        names = line.SUPLENTE.split(' ')
        first = names[0]
        last = ' '.join(p for p in names[1:])
        sub = AlternateProfile(first_name=first.strip(),
                               last_name=last.strip(),
                               password=env('DEFAULT_PASSWORD'),
                               username=first + last[:3],  # primeiro nome + 3 letras
                               email=line.EMAIL2,
                               functional_register=line.RF2,
                               phone=line.TELEFONE2)
        sub.save()
    return sub


for _, line in df.iterrows():
    print(line.DRE)
    sub_manager = get_or_create_submanager(line)
    alternate_manager = get_or_create_alternate(line)

    dre = RegionalDirectorProfile(abbreviation=line.DRE.replace(' ', ''),
                                  description='',
                                  alternate=alternate_manager,
                                  sub_manager=sub_manager)
    dre.save()
