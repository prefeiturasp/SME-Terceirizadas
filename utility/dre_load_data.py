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


def get_or_create_manager(line, instance):
    if isinstance(instance, SubManagerProfile):  # sub manager
        sub = instance.objects.filter(functional_register=line.RF).first()
        if not line.RF:
            print(line)
            return None
        mob, ph = line.TELEFONE.split('_')
        if not sub:
            sub = instance(name=line.COGESTOR,
                           email=line.EMAIL,
                           functional_register=line.RF,
                           phone=ph,
                           mobile_phone=mob)
            sub.save()
    else:  # alternate
        sub = instance.objects.filter(functional_register=line.RF2).first()
        if not line.RF2:
            return None
        if not sub:
            sub = instance(name=line.SUPLENTE,
                           email=line.EMAIL2,
                           functional_register=line.RF2,
                           phone=line.TELEFONE2)
            sub.save()
    return sub


for _, line in df.iterrows():
    # print(line)
    phone = line.TELEFONE

    sub_manager = get_or_create_manager(line, SubManagerProfile)
    alternate_manager = get_or_create_manager(line, AlternateProfile)

    dre = RegionalDirectorProfile(abbreviation=line.DRE,
                                  description='My Wonderful Description',
                                  alternate=alternate_manager,
                                  sub_manager=sub_manager)
    dre.save()
