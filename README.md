##Require
python packages: chardet, BeautifulSoup, NLTK


### Install Packages
```bash
sudo apt-get install python-chardet python-bs python-nltk
```


##Tools

###preprocess.py
The preprocess.py takes one xml file (or a directory) with the following format:

```html
<REUTERS TOPICS="YES" LEWISSPLIT="TRAIN" CGISPLIT="TRAINING-SET" OLDID="5544" NEWID="1">
<TOPICS><D>cocoa</D></TOPICS>
<PLACES><D>el-salvador</D><D>usa</D><D>uruguay</D></PLACES>
...
<TEXT><BODY>
Content
</BODY></TEXT>
</REUTERS>
<REUTERS ...>
</REUTERS>
...
```

It parses the file into a list of dictionaries, where each dictionary corresponds to a <REUTERS>
tag (set **sep** parameter reuters). One such dictionary will contain several labels (**label** parameter)
and a feature set extracted form *Content* (set **tag** parameter body). 

The features here are n-grams in the *Content* and their corresponding numbers of occurrences. To select the features properly, we first use stop wrods (**stoplist** parameter) to exclude any n-gram that contains at least one stop word.
When n-grams are extracted, we also convert them into **lower cases** and **stem** them. 
So variants of one n-gram will not be treated as different n-grams. 
Furthermore, we collects the number of occurrences of all n-grams in the given file 
(or all files in the given directory). A high pass filter is then applied to remove n-gram
feature that rarely appears. It filters out low frequent n-grams that 
contribute to **MIN** (parameter) portion of the total number of n-gram occurrences.
Note that unigram, bigram, ... are filtered separately to preserve longer n-gram features.


####Usage
type ./preprocess.py --help to see more.

####Output
When pass --ouput=file as argument, result dataset will be saved in *ouput*, and feature vector will be saved in
*output.feature*.

