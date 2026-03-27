import pandas as pd
import time
import unicodedata
from tkinter import filedialog

encodings = ["utf-8", "cp1252", "latin1"]
na_values = ['nan', '?', 'null', '0']

# HOMENS, EXPURGUEM TUDO E TODOS QUE SÃO Á À Ê Õ!!
def purge_unicode(text):
    if pd.isna(text):
        return text
    return ''.join(c for c in unicodedata.normalize('NFKD', str(text)) if not unicodedata.combining(c))

if __name__ == "__main__":
    print("Iniciando mesclagem e tratamento de dados CSV.")
    print("Por favor, selecione os arquivos correspondentes.\n1° Ordem: 'ipvs_esp-raw'\n2° Ordem: 'codigos_ibge_sp'\n")
    start_time = time.perf_counter()
    try:
        # Primeiro arquivo CSV devem ser nossos dados pra limparmos
        csv_df = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("Excel CSV file", "*.csv")])

        # Esse aqui é feito pra guardar o codigos_ibge_sp pra comparação e substituição dos códigos do CSV acima
        # Como todo CSV que usamos possuem como primeiro campo 'cod_ibge', fazemos as substituições
        csv_codes = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("Excel CSV file", "*.csv")])

    except Exception as e:
        raise

    if csv_df:
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(csv_df, encoding=enc, sep=";", na_values=na_values)
                break
            except Exception:
                continue

        if df is None:
            raise ValueError("ERRO NO CSV DE DADOS: Não foi possível ler o arquivo com os encodings testados.")

        df.dropna(inplace=True)

        if csv_codes:
            c_df = None
            colunas = ['cod_ibge', 'municipio']

            for enc in encodings:
                try:
                    c_df = pd.read_csv(csv_codes, encoding=enc, sep=";", na_values=na_values)
                    break
                except Exception:
                    continue
        
            if c_df is None:
                raise ValueError("ERRO NO CSV DE CÓDIGOS: Não foi possível ler o arquivo com os encodings testados.")
        
            c_df.dropna(inplace=True)
            c_df = c_df[[c for c in colunas if c in c_df.columns]]

            # Aqui só tratamos o cod_ibge pois ele é a única categoria que vamos comparar com outro DB, por isso ambos precisam ficar no mesmo formato.
            cd_map = c_df.set_index('cod_ibge')['municipio']
            df['cod_ibge'] = df['cod_ibge'].map(cd_map)
            df['cod_ibge'] = df['cod_ibge'].astype(str).apply(purge_unicode).str.upper()

            colunas_int = ['n_pessoas', 'n_domicilios', 'n_setores']
            df[colunas_int] = df[colunas_int].astype('Int64')

            # Nome padrão, só renomear o arquivo assim que criar o novo csv
            df.to_csv("dados_mesclados.csv", index=False, sep=";")
        else:
            # Se não houver um csv de mapeamento de código, consideramos como se fosse apenas um tratamento simples de dado, em tese esse seria o nosso 'inst_hospitalares_sp'
            df['municipio'] = df['municipio'].astype(str)
            df['municipio'] = df['municipio'].str.replace(r'\d+', '', regex=True).str.strip()
            df['quantidade'] = df['quantidade'].astype('Int64')

            # Nome padrão, só renomear o arquivo assim que criar o novo csv
            df.to_csv("dados_limpos.csv", index=False, sep=";")

    end_time = time.perf_counter()
    elapsed = end_time - start_time
    input(f"Finalizada mesclagem e tratamento de dados de CSV.\nDemorado {int(elapsed)} milisegundos.")