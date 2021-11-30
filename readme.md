# WebDataset tools

WebDataset tools is a github repository with useful tools to categorize, annotate or check the sanity of your datasets.

## Installation

Just clone this repository to your folder and use one of the following commands in the section underneath.

### WebDataset Annotator

```python
python annotator.py
```

Press <space> to switch to the next page, <c> to change the annotation category or click on the image to add it to the current cateogry and save it in annotations.json

![Screenshot](screenshot.png)

### WebDataset aligner

```python
python aligner.py
```

This tool helps to align the shuffled keys, so the WebDataset module can read your datasets correctly.
You just need to specify the keys you want to look for and keep in your new dataset.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)