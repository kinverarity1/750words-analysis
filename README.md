# 750words-analysis

![](https://img.shields.io/badge/status-beta-yellow.svg)

An assortment of Python code to look at what you've written on 750words.com.

## Download your writing

The 750 Words export files can be grabbed automatically if you have the Python
packages requests, lxml, and pyquery installed, using this script:

    $ python download_750words.py --help
    
## Statistics

Text analysis code is in ``m750.py``.

```python
>>> from m750 import *
>>> text, entries = read_local_750words() # or text, entries = download_750words()
```

Statistics are calculated from the *entries* list via three classes::

```python
>>> s750 = stats_750(entries)       # Streaks, etc.
>>> all = stats(text)               # Text statistics on all your writing
>>> estats = entrystats(entries)    # Text statistics per entry
```

Use ``print`` to explore the results of these classes, and take a look at their
docstrings and methods. The graphing methods require matplotlib.

![example](https://raw.github.com/kinverarity1/750words-analysis/master/wordcloud.png)

*An example of a word cloud plotted using pytagcloud*

You can also see some example IPython Notebooks:

- [Analyse 750 Words content.ipynb](http://nbviewer.ipython.org/github/kinverarity1/750words-analysis/blob/master/Analyse%20750%20Words%20content.ipynb)
- [word clouds via pytagcloud.ipynb](http://nbviewer.ipython.org/github/kinverarity1/750words-analysis/blob/master/word%20clouds%20via%20pytagcloud.ipynb)
- [convert to daily markdown files.ipynb](http://nbviewer.ipython.org/github/kinverarity1/750words-analysis/blob/master/convert%20to%20daily%20markdown%20files.ipynb)
- [how to do stop words list.ipynb](http://nbviewer.ipython.org/github/kinverarity1/750words-analysis/blob/master/how%20to%20do%20stop%20words%20list.ipynb)
- [Moby](http://nbviewer.ipython.org/github/kinverarity1/750words-analysis/blob/master/Moby.ipynb)  

The stats on the 750words.com website are -- and will probably continue to be --
far better. I made this framework mainly so I could look at how whatever
measures I can find change over time, something the 750words.com site doesn't
quite do at the moment (Feb 2013).

I've included hyphenation and parts-of-speech dictionaries from the 
[Moby Project](http://icon.shef.ac.uk/Moby/)
and some functions to load these in moby.py. The stats classes will use this
data if you use ``use_moby=True``. They're not included in the repository but
you can download [this 26 MB file](http://www.dcs.shef.ac.uk/research/ilash/Moby/moby.tar.Z)
 and unzip it into a "Moby" folder here.

## Viewing your writing and metadata

There is also a script which shows your entries and metadata on a single page
through a local HTTP server. Just run:

    $ python view750.py
    
![example](https://raw.github.com/kinverarity1/750words-analysis/master/example_entries.png)

*Your entries*

![example](https://raw.github.com/kinverarity1/750words-analysis/master/example_metadata_graph.png)

*Your metadata*
