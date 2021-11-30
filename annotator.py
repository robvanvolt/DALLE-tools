import io
import os
import time
import json
import webdataset as wds
import matplotlib.pyplot as plt
from PIL import Image

print()
print('###################################################')
print('####   Welcome to the WebDataset annotator!    ####')
print('#### https://github.com/robvanvolt/DALLE-tools ####')
print('###################################################')
print()
print('Short introduction to the WebDataset annotator:')
print('Press <space> to switch to the next page, <c> to change the annotation category or')
print('click on the image to add it to the current cateogry and save it in annotations.json')
print()

print('Specify the image key in your dataset (default: img).')
webdataset_imagekey = input()
webdataset_imagekey = 'img' if webdataset_imagekey == '' else webdataset_imagekey

print('Specify the possible, comma separated annotation categories (default: watermark,nsfw).')
possible_annotations = input()
possible_annotations = 'watermark,nsfw' if possible_annotations == '' else possible_annotations
possible_annotations = possible_annotations.split(',')

def save_dict(mydict):
    for annotation in possible_annotations:
        mydict[annotation] = sorted(list(mydict[annotation]))
    with open('annotations.json', 'w') as f:
        json.dump(mydict, f, indent=4)

try:
    with open('annotations.json') as f:
        annotations = json.loads(f.read())
    for annotation in possible_annotations:
        if annotation in annotations:
            annotations[annotation] = set(annotations[annotation])
        else:
            annotations[annotation] = set()
except Exception as e:
    print(e)
    print('Creating new file for annotations (annotations.json).')
    annotations = {
        'current_batch': 0,
        'dataset_size': {}
    }
    for annotation in possible_annotations:
        annotations[annotation] = set()
    save_dict(annotations)

print('Specify the path to the .tar(.gz) file you want to annotate (default is the first dataset in annotations.json, if it exists).')
webdataset_filepath = input()
if webdataset_filepath == '' and len(annotations['dataset_size']) > 0:
    webdataset_filepath = list(annotations['dataset_size'].keys())[0]
assert os.path.isfile(webdataset_filepath), 'The specified file ({}) is not a valid .tar(.gz) file.'.format(webdataset_filepath)

figure_width = 14
figure_height = 8
vertical_row_number = 4
horizontal_row_number = 8

current_key = possible_annotations[0]
bs = vertical_row_number * horizontal_row_number
start = time.time()

dataset = wds.WebDataset(webdataset_filepath, handler=wds.ignore_and_continue).to_tuple(webdataset_imagekey, "__key__")
dl = wds.WebLoader(dataset, batch_size=bs)

def return_next_key(current_key):
    current_index = possible_annotations.index(current_key)
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

for i, d in enumerate(dl):
    if i >= annotations['current_batch']:
        f, axarr = plt.subplots(
            vertical_row_number, horizontal_row_number, figsize=(figure_width, figure_height)) 

        c = 0
        for ii in range(vertical_row_number):
            for jj in range(horizontal_row_number):
                axarr[ii, jj].imshow(Image.open(io.BytesIO(d[0][c])))
                axarr[ii, jj].set_xticklabels([])
                axarr[ii, jj].set_yticklabels([])
                axarr[ii, jj].axis('off')
                if d[1][c] in annotations[current_key]:
                    axarr[ii, jj].axis('on')
                    axarr[ii, jj].patch.set_edgecolor('red')  
                    axarr[ii, jj].patch.set_linewidth('5')
                    axarr[ii, jj].tick_params(
                        which='both',
                        bottom=False,
                        left=False,
                        right=False,
                        top=False,
                        labelbottom=False)
                    f.canvas.draw()
                c += 1

        def onclick(event):
            for inner_i, ax in enumerate(axarr.flatten()):
                if ax == event.inaxes:
                    if d[1][inner_i] in annotations[current_key]:
                        annotations[current_key].remove(d[1][inner_i])
                        ax.axis('off')
                        ax.patch.set_edgecolor('red')  
                        ax.patch.set_linewidth('0')
                        f.canvas.draw()
                    else:
                        ax.axis('on')
                        ax.patch.set_edgecolor('red')  
                        ax.patch.set_linewidth('5')
                        ax.tick_params(
                            which='both',
                            bottom=False,
                            left=False,
                            right=False,
                            top=False,
                            labelbottom=False)
                        f.canvas.draw()
                        if type(annotations[current_key]) != 'set':
                            annotations[current_key] = set(annotations[current_key])
                        annotations[current_key].add(d[1][inner_i])
                    save_dict(annotations)
        
        def on_press(event):
            if event.key == ' ':
                plt.close()
            if event.key == 'c':
                global current_key
                current_key = return_next_key(current_key)
                annotations_length = len(annotations[current_key])
                seen = (i+1)*bs
                annotations_length_percent = 100*annotations_length/seen
                c = 0
                for ii in range(vertical_row_number):
                    for jj in range(horizontal_row_number):
                        axarr[ii, jj].imshow(Image.open(io.BytesIO(d[0][c])))
                        axarr[ii, jj].set_xticklabels([])
                        axarr[ii, jj].set_yticklabels([])
                        axarr[ii, jj].axis('off')
                        if d[1][c] in annotations[current_key]:
                            axarr[ii, jj].axis('on')
                            axarr[ii, jj].patch.set_edgecolor('red')  
                            axarr[ii, jj].patch.set_linewidth('5')
                            axarr[ii, jj].tick_params(
                                which='both',
                                bottom=False,
                                left=False,
                                right=False,
                                top=False,
                                labelbottom=False)
                            f.canvas.draw()
                        c += 1
                plt.suptitle('Annotator v1.0 - Page {} - Image {} out of {} ({:.2f}%) - {} {:.2f}% - Remaining {}'.format(i, i*bs, total, 100*i*bs/total, current_key, annotations_length_percent, time.strftime("%H:%M:%S", time.gmtime(remaining_time))))
                f.canvas.draw()

        f.canvas.mpl_connect('button_press_event', onclick)
        f.canvas.mpl_connect('key_press_event', on_press)

        if i-substract != 0:
            remaining_time = (time.time()-start)/(i-substract) * (total - i*bs)/bs
        else:
            remaining_time = 0

        annotations_length = len(annotations[current_key])
        seen = (i+1)*bs
        annotations_length_percent = 100*annotations_length/seen

        plt.suptitle('Annotator v1.0 - Page {} - Image {} out of {} ({:.2f}%) - {} {:.2f}% - Remaining {}'.format(i, i*bs, total, 100*i*bs/total, current_key, annotations_length_percent, time.strftime("%H:%M:%S", time.gmtime(remaining_time))))
        plt.tight_layout()
        plt.show()

        annotations['current_batch'] += 1
        save_dict(annotations)
    else:
        substract += 1