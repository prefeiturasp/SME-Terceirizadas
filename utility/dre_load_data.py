import pandas as pd

from sme_pratoaberto_terceirizadas.user_profiles.models import (RegionalDirectorProfile, AlternateProfile,
                                                                SubManagerProfile)

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
    print(line)
    sub = SubManagerProfile.objects.filter(functional_register=line.RF).first()
    if not line.RF:
        return None
    mob, ph = line.TELEFONE.split('_')
    if not sub:
        sub = SubManagerProfile(name=line.COGESTOR,
                                email=line.EMAIL,
                                functional_register=line.RF,
                                phone=ph,
                                mobile_phone=mob)
        sub.save()
    return sub


def get_or_create_alternate(line):
    sub = AlternateProfile.objects.filter(functional_register=line.RF2).first()
    if not line.RF2:
        print(line)
        return None
    if not sub:
        sub = AlternateProfile(name=line.SUPLENTE,
                               email=line.EMAIL2,
                               functional_register=line.RF2,
                               phone=line.TELEFONE2)
        sub.save()
    return sub


for _, line in df.iterrows():
    phone = line.TELEFONE
    sub_manager = get_or_create_submanager(line)
    alternate_manager = get_or_create_alternate(line)

    dre = RegionalDirectorProfile(abbreviation=line.DRE,
                                  description='My Wonderful Description',
                                  alternate=alternate_manager,
                                  sub_manager=sub_manager)
    dre.save()
