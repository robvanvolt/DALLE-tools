import io
import os
import sys
import time
import json
import torch
from itertools import islice
import webdataset as wds
import matplotlib.pyplot as plt
from PIL import Image

if __name__ == '__main__':
    default_annotations_file = 'annotations.json'
    print()
    print('###################################################')
    print('####   Welcome to the WebDataset annotator!    ####')
    print('#### https://github.com/robvanvolt/DALLE-tools ####')
    print('###################################################')
    print()
    print('Short introduction to the WebDataset annotator:')
    print('Press <f>, <j> or <space> to annotate the current image to the respective category')
    print('(f: 1st category, j: second category, space: third category), press <c> to change ')
    print('the shwon annotation category. The annotations json file is saved automatically.')
    print('Press <q> to quit the annotation and <b> to go to the previous image.')
    print()

    event_dict = {'w': 0, ' ': 1, 'p': 2}

    print('What is your (the annotator) name? The name gets appended to the annotations.json filename. (Default: kendrick)')
    annotator = input()
    annotator_name = 'kendrick' if annotator == '' else annotator
    default_annotations_file = default_annotations_file.split('.')[0] + '_' + annotator_name + '.json'

    print('Specify the image key in your dataset (default: img).')
    webdataset_imagekey = input()
    webdataset_imagekey = 'img' if webdataset_imagekey == '' else webdataset_imagekey

    print('Specify the possible, comma separated annotation categories (default: watermark,no_watermark_but_text,no_watermark).')
    possible_annotations = input()
    possible_annotations = 'watermark,no_watermark_but_text,no_watermark' if possible_annotations == '' else possible_annotations
    possible_annotations = possible_annotations.split(',')
    current_key = possible_annotations[0]
    pressed_back = False

    print('Starting page (default 0 or the value in {}).'.format(default_annotations_file))
    starting_page = input()

    def save_dict(mydict):
        for annotation in possible_annotations:
            mydict[annotation] = sorted(list(mydict[annotation]))
        with open(default_annotations_file, 'w') as f:
            json.dump(mydict, f, indent=4)

    try:
        with open(default_annotations_file) as f:
            annotations = json.loads(f.read())
        for annotation in possible_annotations:
            if annotation in annotations:
                annotations[annotation] = set(annotations[annotation])
            else:
                annotations[annotation] = set()
    except Exception as e:
        print(e)
        print('Creating new file for annotations ({}).'.format(default_annotations_file))
        annotations = {
            'current_batch': 0,
            'dataset_size': {}
        }
        for annotation in possible_annotations:
            annotations[annotation] = set()
        save_dict(annotations)

    print('Specify the path to the .tar(.gz) file you want to annotate (default is the first dataset in {}, if it exists).'.format(default_annotations_file))
    webdataset_filepath = input()
    if webdataset_filepath == '' and len(annotations['dataset_size']) > 0:
        webdataset_filepath = list(annotations['dataset_size'].keys())[0]
    assert os.path.isfile(webdataset_filepath), 'The specified file ({}) is not a valid .tar(.gz) file.'.format(webdataset_filepath)

    figure_width = 14
    figure_height = 8

    start = time.time()

    dataset = wds.WebDataset(webdataset_filepath, handler=wds.ignore_and_continue).to_tuple(webdataset_imagekey, "__key__")
    # dl = wds.WebLoader(dataset, batch_size=bs)
    dl = torch.utils.data.DataLoader(dataset, num_workers=1, batch_size=1)

    def return_next_key(ck):
        current_index = possible_annotations.index(ck)
        if current_index + 1 == len(possible_annotations):
            return possible_annotations[0]
        else:
            return possible_annotations[current_index + 1]

    if webdataset_filepath not in annotations['dataset_size']:
        print('Counting dataset length of {}'.format(webdataset_filepath))
        annotations['dataset_size'][webdataset_filepath] = len([1 for _ in dataset])
        total = annotations['dataset_size'][webdataset_filepath]
        print('Finished counting dataset length!')
        save_dict(annotations)
    else:
        total = annotations['dataset_size'][webdataset_filepath]

    substract = 0
    total_pages = int(total)

    last_keypress = ''
    last_id = ''
    last_annotation = ''

    if starting_page != '':
        starting_page = int(starting_page)
        annotations['current_batch'] = starting_page

    i = int(annotations['current_batch'])

    while i < total:
        dl_iter = iter(islice(dl, i, total))
        pressed_back = False
        while pressed_back == False:
            try: 
                d = next(dl_iter)
                i += 1
            except Exception as e:
                print(e)
                break
            else:                    
                f = plt.figure(figsize=(figure_width, figure_height))
                plt.imshow(Image.open(io.BytesIO(d[0][0])))
                plt.axis('off')

                def on_press(event):
                    global current_key

                    if event.key == 'q':
                        sys.exit()

                    if event.key == 'b':
                        global i, annotations, pressed_back
                        i = i - 2
                        annotations['current_batch'] = annotations['current_batch'] - 1
                        pressed_back = True
                        plt.close()

                    if event.key == 'c':
                        current_key = return_next_key(current_key)
                        annotations_length = len(annotations[current_key])
                        seen = i+1
                        annotations_length_percent = 100*annotations_length/seen
                        plt.title('Annotator v1.0 - Page {}/{} - Image {} out of {} ({:.2f}%) - {} {:.2f}% - Remaining {}'.format(
                            i, total_pages, i, total, 100*i/total, current_key, annotations_length_percent, time.strftime("%H:%M:%S", time.gmtime(remaining_time))))
                        f.canvas.draw()

                    global event_dict

                    if event.key in event_dict.keys():
                        assign_to_key = possible_annotations[event_dict[event.key]]
                        if type(annotations[assign_to_key]) != 'set':
                            annotations[assign_to_key] = set(annotations[assign_to_key])
                        for k in possible_annotations:
                            if d[1][0] in annotations[k]:
                                annotations[k].remove(d[1][0])
                        annotations[assign_to_key].add(d[1][0])
                        annotations['current_batch'] += 1
                        plt.close()
                
                f.canvas.mpl_connect('key_press_event', on_press)

                if i-substract != 0:
                    remaining_time = (time.time()-start)/(i-substract) * (total - i)
                else:
                    remaining_time = 0

                annotations_length = len(annotations[current_key])
                seen = i+1
                annotations_length_percent = 100*annotations_length/seen

                plt.title('Annotator v1.0 - Page {}/{} - Image {} out of {} ({:.2f}%) - {} {:.2f}% - Remaining {}'.format(
                    i, total_pages, i, total, 100*i/total, current_key, annotations_length_percent, time.strftime("%H:%M:%S", time.gmtime(remaining_time))))
                plt.tight_layout()
                if hasattr(sys, 'getwindowsversion'):
                    figManager = plt.get_current_fig_manager()
                    figManager.window.showMaximized()
                plt.show()
                save_dict(annotations)