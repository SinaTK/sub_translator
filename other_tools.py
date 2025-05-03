def create_dataframe(subs: list):
    file = pd.DataFrame(columns=['start', 'end', 'text'], index=range(1, len(subs)))
    for i, sub in enumerate(subs):
        file.loc[i, 'text'] = sub.text
        file.loc[i, 'start'] = sub.start
        file.loc[i, 'end'] = sub.end

    file = file.astype({'start': str, 'end': str})

    return file

def add_exist_sub_to_dict(en_sub: str, fa_sub: str, db_name:str, table: str):
    print('='* 100)
    print(f'adding to hash, "{en_sub}"...')
    print(f'using {fa_sub} as translator.')
    print('=' * 100)

    en_subs = list(pysrt.open(en_sub))
    fa_subs = list(pysrt.open(fa_sub))

    en_file = create_dataframe(en_subs)
    print(en_file.info())

    fa_file = create_dataframe(fa_subs)
    print(fa_file.info())

    file = en_file.merge(fa_file, on=['start', 'end'], suffixes=('_en', '_fa'), how='left')
    print(file.info())

    file.dropna(subset='text_fa', inplace=True)

    engine = create_engine(f'sqlite:///{db_name}.db', echo=False)
    file.to_sql(table, con=engine, if_exists='append', index=False)


en_path = 'files/all saints_season 01'
fa_path = 'files/fa_all_saints_S01'

fa_sub_list = find_files_and_copy(source_path=fa_path, extension='.srt')
# print(fa_sub_list)

sub_dict = {}

for root, dirs, files in os.walk(en_path):
    for file in files:
        episode = file.split(' - ')[0]
        for fa_file in fa_sub_list:
            fa_episode = fa_file.split(' -')[0].split('/')[-1]
            # print(fa_episode)
            if fa_episode == episode:
                full_path = os.path.join(root, file)
                sub_dict[full_path] = fa_file
                break

database = 'files/db/sub_trans_cash'
table_name = 'translate'

for en_sub, fa_sub in sub_dict.items():
    # print(f'English: "{k}":')
    # print(f'Farsi: "{v}"')
    add_exist_sub_to_dict(en_sub=en_sub, fa_sub=fa_sub, db_name=database, table=table_name)
