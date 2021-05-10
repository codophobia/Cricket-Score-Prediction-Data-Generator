# Cricket-Score-Prediction-Data-Generator

## How to run the code

```bash
git clone https://github.com/codophobia/Cricket-Score-Prediction-Data-Generator.git
virtualenv -p python3 venv # You should have Python3 installed on your system
pip install -r requirements.txt
python script.py
```

Do note that the script will generate prediction data for all the matches(odi,test,t-20, ipl).
If you want dataset for a particular format, you can filter that in csv file.

## How to update the dataset

```bash
# The current directory should be where old data is present
git clone https://git.sr.ht/~srushe/cricsheet-xml # This will download the dataset from https://git.sr.ht/~srushe/cricsheet-xml
rm -r data # Delete the old data. If you want to keep it, rename it using mv command.
cp -r cricsheet-xml/data .
```


