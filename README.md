##Require
* python packages: chardet, BeautifulSoup, NLTK, numpy, sckit-learn, scipy
* python version: 2.7+

It would be easier to install all packages with [conda](http://conda.pydata.org)


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
```bash
./preprocess.py --dir=/tmp/data --sep=reuters --label=topics,places --tag=body --stoplist=/tmp/stoplist --MIN=95 --output=/tmp/out.pickle
```
type ./preprocess.py --help to see more.

####Output
When pass --ouput=file as argument, result dataset will be saved in *ouput*, and feature vector will be saved in
*output.feature*.

###train_test.py
run train_test.py --help to see more details.

####Run K-Nearest-Neighbors
```bash
train_test.py --file=full.pickle --label=topics --percent=80 --method=knn --args=10
```

####Run Naive Bayes
```bash
train_test.py --file=full.pickle --label=topics --percent=90 --method=naive_bayes
```

###cluster_test.py
This script takes .vec yielded by preprocess.py as input *file*, and cluster it with specified *method*. The output includes the entropy score and variance of the clustering.

####Run DBSCAN
The DBSCAN method requires three parameters *--args=eps,min_samples,metric*. The eps speficifies the maximum distance between two points that can be thought in the same neighborhood; the min_samples indicats the minimum number of point a core point should have; the metric tells us how to calculate the distance between points.
```bash
python cluster_test.py --file=./all.pickle.vec --method=dbscan --args=25,20,manhattan
```

####Run Agglomerative Clustering
The Agglomerative Clustering requires two parameters *--args=ncluster,linkage*. The ncluster specifies the number of clusters this method trying to identify; The linkage indicates the method to calculate distance between two set of points (or samples). 
```bash
python cluster_test.py --file=./all.pickle.vec --method=aggc --args=2,average
```

###eval_metric.py
This script will first calculate the Jaccard Similarity, then run the given method that approximates the exact similarity. At last, it presents the mean squared error and relative mean error of the method.

####MinHash
The sole argument specifies the number of hash functions (permutation) to use.
```bash
python eval_metric.py --file=full.pickle --method=minhash --args=128
```

##Cross Validation Test
####Apriori
```bash
conda run "python cv_apriori.py --file=./full.pickle --label=topics --percent=80 --method=apriori --args1=0.02,0.05,0.08 --args2=0.2,0.3,0.4" 
```

####Apriori with Clustering
```bash
conda run "python cv_apriori.py --file=./full.pickle --label=topics --percent=80 --method=capriori --args1=0.02,0.05,0.08 --args2=0.2,0.3,0.4" 
```
