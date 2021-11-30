import webdataset as wds
import os

print('Specify the tar file you want to align.')
tar_filepath = input() # 'watermark_ds_v1.tar.gz'
assert os.path.isfile(tar_filepath), 'The specified file ({}) is not a valid .tar(.gz) file.'.format(tar_filepath)

print('Specify the keys you want to keep in the aligend .tar(.gz) file (e.g., jpg,txt for jpg and txt).')
cols = input()
cols_set = set(cols.split(','))

ds = wds.WebDataset(tar_filepath)
values = {}

for col in cols_set:
    values[col] = {}

for i, row in enumerate(ds):
    remaining_keys = set(row.keys()).intersection(cols_set)

    for key in remaining_keys:
        values[key][row['__key__']] = row[key]

    if i % 10000 == 0:
        print('Processed {} rows.'.format(i), end='\r')

for col in cols_set:
    print('Processed {} values for {}'.format(len(values[col].keys()), col))

sink = wds.TarWriter(tar_filepath + '_aligned', encoder=False)

sink.write

for i, key in enumerate(values[list(cols_set)[0]].keys()):
    sample = {
        "__key__": key,
    }
    for col in cols_set:
        sample[col] = values[col][key]
    sink.write(sample)
    if i % 10000 == 0:
        print('Saved {} aligned rows.'.format(i))
sink.close()
