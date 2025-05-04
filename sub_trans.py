from traceback import print_tb

import pandas as pd
import pysrt
import time
import os
import shutil

from googletrans import Translator
from sqlalchemy import create_engine, exc
from tqdm import tqdm

from sql_tools import cprint, read_sql




def find_files_and_copy(source_path: str, extension: str, destination_path: str = None):
    found_files = []
    copied_count = 0

    if destination_path:
        os.makedirs(destination_path, exist_ok=True)

    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.endswith(extension):
                source_file = os.path.join(root, file)
                if destination_path:
                    destination_file = os.path.join(destination_path, file)

                full_path = os.path.join(root, file)
                found_files.append(full_path)

                if destination_path:
                    try:
                        shutil.copy2(source_file, destination_file)
                        copied_count += 1
                        print(f'"{file}" copied.')
                    except Exception as e:
                        print(f'Error "{str(e)}" rises in coping "{file}"')

    if destination_path and copied_count:
        print(f'"{copied_count}" files copied in "{destination_path}" path')

    return found_files


# trans = Translator()
# translated = trans.translate('I love.', dest='fa', src='en')
# print(translated.text)


class TranslateCash:
    def __init__(self):
        self.engine = self.create_engine()
        self.table = 'sub_translate'

    @staticmethod
    def create_engine():
        return create_engine('sqlite:///files/db/sub_trans_cash.db', echo=False)

    def read_cash(self):
        try:
            sql = f'SELECT * FROM {self.table}'
            file = pd.read_sql_query(sql=sql, con=self.engine)
            cash_dict = dict(zip(file['OrigText'], file['TransText']))
            return cash_dict
        except exc.OperationalError:
            return {}

    def write_cash(self, cash_dict: dict):
        file = pd.DataFrame(data={'OrigText': cash_dict.keys(), 'TransText': cash_dict.values()} )
        cprint('writing hash...', 'y')
        file.to_sql(name=self.table, con=self.engine, if_exists='replace', index=False)


class SubtitleTranslator:
    def __init__(self):
        self.translator = Translator()
        self.cash_manager = TranslateCash()
        self.cash_dict = self.cash_manager.read_cash()

    def translate_text(self, text):
        if text in self.cash_dict:
            cprint('found in hash', 'p')
            return self.cash_dict[text]
        try:
            translated = self.translator.translate(text, src='en', dest='fa').text
            print(f'"{text}" translated to:\n"{translated}"')
            self.cash_dict[text] = translated
            time.sleep(0.5)
            return translated
        except Exception as e:
            print(f'Error: {e}\nraises when translating {text}')
            return text

    def translate_file(self, input_file, output_file):
        subs = pysrt.open(input_file)

        i = 1
        for sub in tqdm(subs):
            if i % 200 == 0:
                self.cash_manager.write_cash(cash_dict=self.cash_dict)
            sub.text = self.translate_text(sub.text)
            i += 1

        self.cash_manager.write_cash(cash_dict=self.cash_dict)
        subs.save(output_file, encoding='utf-8')
        cprint(f'Translation of "{input_file}" done!', 'g')


# translator = SubtitleTranslator()
# translator.translate_file('files/all saints_season 01/All.Saints.S01E01 - Body & Soul.en.srt',
#                           'files/all saints _ season 01 _ fa/All.Saints.S01E01 - Body & Soul.fa.srt')


en_path = 'files/all saints_season 01'
en_files = os.listdir(en_path)

fa_path = 'files/all saints _ season 01 _ fa'
fa_files = os.listdir(fa_path)

translator = SubtitleTranslator()

for file in en_files:
    if file.endswith('.srt'):
        cprint(f'Translating "{file}" to farsi', 'c')

        en_add = f'{en_path}/{file}'

        sub_name = file.split('.en.srt')[0]
        fa_add = f'{fa_path}/{sub_name}.fa.srt'

        if f'{sub_name}.fa.srt' in fa_files:
            cprint('This file already translated.', 'y')
        else:
            cprint(f'Farsi subtitle address: "{fa_add}"', 'p')
            translator.translate_file(input_file=en_add,
                                  output_file=fa_add)




"""Merge databases"""
# df = read_sql(database='files/db/sub_trans_cash', table='sub_translate')
# print(df.info())

# _df = read_sql(database='sub_trans_cash', table='sub_translate')
# print(_df.info())
#
# df = pd.concat([df, _df])
# df.drop_duplicates(inplace=True)
# print(df.info())
#
# database = 'files/db/sub_trans_cash'
# engine = create_engine('sqlite:///{}.db'.format(database), echo=False)
#
# df.to_sql('sub_translate', con=engine, if_exists='replace', index=False)



