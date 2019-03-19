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

for _, line in df.iterrows():
    print(line.RF, line.COGESTOR, line.DRE)
    phone = line.TELEFONE
    mob, ph = phone.split('_')
    sub_manager = SubManagerProfile(name=line.COGESTOR,
                                    email=line.EMAIL,
                                    functional_register=line.RF,
                                    phone=ph,
                                    mobile_phone=mob)
    sub_manager.save()

    alternate_manager = AlternateProfile(name=line.SUPLENTE,
                                         email=line.EMAIL2,
                                         functional_register=line.RF,
                                         phone=line.TELEFONE2)
    alternate_manager.save()

    dre = RegionalDirectorProfile(abbreviation=line.DRE,
                                  description='My Wonderful Description',
                                  alternate=alternate_manager,
                                  sub_manager=sub_manager)
    dre.save()
