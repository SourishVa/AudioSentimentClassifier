Update the file paths in sentiment_classifier.py
Open sentiment_classifier.py and update these two lines near the top to match your computer:
python
DATA_DIR = Path(r"C:\Users\YourUsername\AudioSentimentClassifier\SubSetAudioWAV")
OUT_DIR  = Path(r"C:\Users\YourUsername\AudioSentimentClassifier\outputs")

Or use a different path up to the user.
Then run the code by typing
python sentiment_classifier.py
With the full dataset (~5,986 files) this will take around 1-2 hours. Results and plots will be saved to the `outputs/` folder.
