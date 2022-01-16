import pandas as pd
import unidecode


def unidecode_columns(df):
    col_name = {}

    for i in df.columns:
        col_name[i] = unidecode.unidecode(i).replace(' ','_').lower()

    df.rename(columns=col_name, inplace=True)


def clean_text(x):
    return str(x).replace('=','').replace('"','')

def clean_cols(df):
    for col in df.select_dtypes(['object']).columns:
        df[col] = df[col].map(lambda x: clean_text(x))

df = pd.read_csv('school.csv')

unidecode_columns(df)
clean_cols(df)

for col in df.columns:
    if df[col].nunique() < 100:
        #print(f'{col}, unique :' ,df[col].nunique())
        df[col] = df[col].astype('category')

df['gmina_typ_cat'] = df.gmina.map(lambda x: x.split('(')[1].replace(')',''))

df['gmina_nazwa_cat'] = df.gmina.map(lambda x: x.split('(')[0].replace(')',''))

df['gmina_typ_cat'] = df['gmina_typ_cat'].astype('category')

df['gmina_nazwa_cat'] = df['gmina_nazwa_cat'].astype('category')

# convert the 'Date' column to datetime format
df['data_likwidacji']= pd.to_datetime(df['data_likwidacji'])

df['data_zalozenia']= pd.to_datetime(df['data_zalozenia'], errors = 'coerce')

df['data_rozpoczecia_dzialalnosci']= pd.to_datetime(df['data_rozpoczecia_dzialalnosci'], errors = 'coerce')
