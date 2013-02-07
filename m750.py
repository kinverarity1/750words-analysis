'''Functions for reading and analysing exported data from 750words.com

Currently the only source of data is a collection of monthly export files
from the website::

    >>> text, entries = read_local_750words(r'C:\Users\Fred\Downloads')

Direct download via HTTPS will be included soon.

Statistics are then calculated from the *entries* list via three classes::

    >>> s750 = stats_750(entries)       # Streaks, etc.
    >>> all = stats(text)               # Text statistics on all your writing
    >>> estats = entrystats(entries)    # Text statistics per entry

Use ``print`` to explore the results of these classes, and take a look at their
docstrings and methods.

'''
from __future__ import division

from collections import defaultdict
import datetime
import glob
import os
import re

try:
    import matplotlib.pyplot as plt
except ImportError:
    print 'Note: plotting functions require matplotlib'


months = dict(zip(['NOTHING', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
                   'aug', 'sep', 'oct', 'nov', 'dec'], range(13)))

# Don't want to measure contractions like etc. vs et cetera, etc.?
substitutions = {"it's": 'it is'}

# Pre-calculate ratios in word frequencies. For example::
#       
#   ratios = [('CapitalBlah', 'Blah', ('bla', 'blah')),
#             ('CapitalBlah2', 'Blah', ('Blah', 'bla', 'blah')),
#             ('CapitalBlah3', 'Blah', ('Blah',)]
#
# causes the calculation of the following statistics:
# 
#       >>> s = stats('Blah blah blah blah')
#       >>> s.CapitalBlah_ratio
#       0.333
#       >>> s.CapitalBlah2_ratio
#       0.25
#       >>> s.CapitalBlah3_ratio
#       1
#
ratios = [('The', 'The', ('The', 'the')),
          ('I', 'I', ('I', 'i')),
          ('OK', 'OK', ('OK', 'ok', 'okay', 'Okay', 'okies'))]



def read_local_750words(path):
    '''Read 750 words entries from local download files.

    Returns: *clean_md, entries*
        - *clean_md*: cleaned Markdown file of all entries.
        - *entries*: a list of dictionaries for each entry

    '''
    rawtext = ''
    for fn in find_export_files(path):
        with open(fn, mode='r') as f:
            rawtext += f.read()
    return parse_markdown(rawtext)



class stats_750(dict):
    '''Performance in the context of the 750 words website.

    Args:
        - *entries*: a list of dictionaries for each entry (see other functions)

    Attributes: 
        - Lists of values for each entry:
            - *dates*: datetime objects
            - *nwords*: number of words per entry
            - *successes*: bool: whether you made 750 words
            - *consecs*: bool: did you write the day before?
        - *streaks*: a list of (*days*, *first_day*, *last_day*) for each
          streak, where *first_day* and *last_day* are datetime objects

    Methods:
        - *plot_entry_lengths*
        - *plot_history*

    '''
    def __init__(self, entries, verbose=0):
        self.__dict__ = self
        self.entries = entries
        self.dates = [e['date'] for e in entries]
        self.nwords = [count_words(e['text']) for e in entries]
        self.successes = [True if n > 750 else False for n in self.nwords]
        
        streaks = []
        consecs = []
        streak = 0
        start = self.dates[0]
        for i, reached_750 in enumerate(self.successes):
            consecutive = 0
            if i > 0:
                consecutive = 1
                if self.dates[i] - self.dates[i - 1] != datetime.timedelta(hours=24):
                    consecutive = 0
            consecs.append(consecutive)
            
            # you can't have a streak if this entry's date does not follow on from the previous date
            if not consecutive:
                if streak > 0:
                    streaks.append([streak, start, self.dates[i - 1]])
                streak = 0
            
            # if you reached 750 words and aren't on a streak, you have started one
            if reached_750 and streak == 0:
                start = self.dates[i]
            
            # no streak yet, and you reached 750 words
            if not streak and reached_750:
                streak += 1
                continue
                
            # there is a streak, and you reached 750 words, and you didn't skip a day
            if streak and reached_750 and consecutive:
                streak += 1
                continue
                
            # there is a streak, and you failed to reach 750 OR you skipped a day
            if streak and (not reached_750 or not consecutive):
                streaks.append([streak, start, self.dates[i - 1]])
                streak = 0
                continue
        
        # you are on a streak as of the last day
        if streak > 0:
            streaks.append([streak, start, self.dates[-1]])
            
        self.streaks = streaks
        self.consecs = consecs
        
    def plot_entry_lengths(self, **kwargs):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError('Plotting requires matplotlib')
        kws = dict(bins=9, histtype='step', hatch='\\', )
        kws.update(kwargs)
        ax = plt.figure().add_subplot(111)
        n, bins, patches = ax.hist(self.nwords, **kws)
        ax.axvline(750, color='r', )
        ax.set_ylim(0, 10)
        ax.set_xlim(min(self.nwords), max(self.nwords))
        ax.set_ylabel('No. entries')
        ax.set_xlabel('No. words')
       
    def plot_history(self, datefmt='%b\'%y', **kwargs):
        try:
            import matplotlib.pyplot as plt
            from matplotlib.dates import DateFormatter
        except ImportError:
            raise ImportError('Plotting requires matplotlib')
        kws = dict(marker='o', mfc='c', mec='b', ms=7, )
        kws.update(kwargs)
        ax = plt.figure(figsize=(13, 4)).add_subplot(111)
        ax.plot_date(self.dates, self.nwords, **kws)
        ax.xaxis.set_major_formatter(DateFormatter(datefmt))
        labs = plt.setp(ax.get_xticklabels(), rotation=0, ha='left')
        
    def __str__(self):
        st = []
        s = []
        s.append('Number of entries: %d' % len(self.entries))
        for ndays, start, end in sorted(self.streaks, reverse=True, ):
            st.append('%d (%s' % (ndays, start.strftime('%d/%m/%y')))
            if end - start >= datetime.timedelta(hours=24):
                st[-1] += ' - %s)' % end.strftime('%d/%m/%y')
            else:
                st[-1] += ')'
            st[-1] = re.sub('(?P<prefix>[^0-9])0', r'\g<prefix>', st[-1]) # Convert 05/06/12 to 5/6/12
        s.append('Streaks > 1 day: ' + ', '.join((sti for sti in st if int(sti.split()[0]) > 1)))
        return '\n'.join(s)



class stats(dict):
    '''Calculate text statistics. Subclass of dict.

    Args:
        - *text*: string
        - *clean_func*: function to pass *text* through first. Set to None
          to use *text* directly.

    Methods:
        - *ratio*

    '''
    def __init__(self, text, clean_func='auto'):
        self.__dict__ = self
        self._attrs = ['text', 'words', 'word_lengths', 'success', 'freqdict',
                       'wordfreqpairs']
        if clean_func is None:
            clean_func = lambda x: x
        elif clean_func == 'auto':
            clean_func = clean_for_stats
        text = clean_func(text)

        self.text = text
        self.words = count_words(text)
        self.word_lengths = [len(w) for w in text.split() if '://' not in w] # remove hyperlinks
        self.success = True if self.words >= 750 else False
        self.freqdict = freqdict(text)
        self.wordfreqpairs = wordfreqpairs(self.freqdict)

        for label, word, words in ratios:
            try:
                assert re.match('[A-Za-z_]', label[0]) is not None
            except AssertionError, IndexError:
                print 'Skipping the invalid label "%s"' % label
                continue
            label += '_ratio'
            self[label] = self.ratio(word, words)
            self._attrs.append(label)

    def ratio(self, word, words):
        '''Return ratio of frequencies: *word* / *words*.'''
        denominator = sum((self.freqdict[w] for w in words))
        if denominator == 0:
            return None
        else:
            return self.freqdict[word] / denominator
       
    def __str__(self):
        if len(self.text) < 40:
            hint = self.text
        else:
            hint = self.text[:40]
        s = '\n'.join(('Words: %d' % self.words,
                       'Text: "%s"...' % hint,
                       'Most common words: ' + ', '.join(
                           ('%s (%d)' % (word, freq) for word, freq in self.wordfreqpairs[:5]))
                       + ', ...'
                       ))
        return s



class entrystats(list):
    '''Calculate statistics of a collection of entries. Subclasses list,
    so each item is the statistics for each entry.

    Args:
        - *entries*: list of dictionaries for each entry.

    Methods:
        - *plot_word_lengths*

    '''
    def __init__(self, entries, clean_func='auto'):
        if clean_func is None:
            clean_func = lambda x: x
        elif clean_func == 'auto':
            clean_func = clean_for_stats
        list.__init__(self, [stats(clean_func(e['text'])) for e in entries])
    
    def __getattr__(self, key):
        if key in self[0]._attrs:
            return [s[key] for s in self]
    
    def plot_word_lengths(self):
        try:
            import numpy as np
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError('Plotting requires matplotlib and numpy')
        ax = plt.figure().add_subplot(111)
        ax.plot([np.median(s.word_lengths) for s in self], label='median', marker='o', mfc='none', mec='k', ls='', )
        ax.plot([np.mean(s.word_lengths) for s in self], label='mean', color='r', )
        ax.fill_between(range(len(self)), 
                        [np.min(s.word_lengths) for s in self],
                        [np.max(s.word_lengths) for s in self], 
                        label='max', alpha=0.05, color='g', )
        ax.set_ylabel('Word length')
        ax.set_xlabel('Entry #')
        leg = ax.legend(loc='best', )
        leg.get_frame().set_alpha(0.5)
        
    def __str__(self):
        s = []
        s.append('Number of entries: %d' % len(self))
        return '\n'.join(s)



def strip_pair(line):
    return ':'.join(line.split(':')[1:]).strip()


def str2dt(ymd, fmt='%Y-%m-%d'):
    return datetime.datetime.strptime(ymd, fmt)


def parse_markdown(raw_md, header_prefix='## '):
    '''Parse raw markdown from 750 words export files.

    Returns: *clean_md, entries*
        - *clean_md*: string of all entries in cleaner markdown (minus the metadata)
        - *entries*: list of dictionaries, one per entry with keys:
            - 'date': datetime object
            - 'words': int
            - 'mins': int
            - 'metadata': dictionary; each value is a list, even if it has only one value
            - 'text': string
    
    '''
    lines = raw_md.splitlines()
    newlines = []
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('------ ENTRY ------'):
            mins = int(strip_pair(lines[i + 2]))
            if mins:
                entry_dict = {
                        'date': str2dt(strip_pair(lines[i + 1])),
                        'words': int(strip_pair(lines[i + 2])),
                        'mins': int(strip_pair(lines[i + 3])),
                        'metadata': {},
                        'entry_lines': []}
                newlines += [
                        '<a id="%s">' % entry_dict['date'].strftime('%Y-%m-%d'),
                        header_prefix + entry_dict['date'].strftime('%A %B %d, %Y'),
                        '</a>'
                        '<i>Entry: {words} words, {mins} mins</i>'.format(**entry_dict)]
                entries.append(entry_dict)
            i += 4
        if entries:
            flag, key, value, number = parse_line_metadata(lines[i])
            if flag:
                emdict = entries[-1]['metadata']
                if key in emdict:
                    emdict[key].append([value, number])
                else:
                    emdict[key] = [[value, number]]
            entries[-1]['entry_lines'].append(lines[i])
        newlines.append(lines[i])
        i += 1
    for entry in entries:
        entry['text'] = '\n'.join(entry['entry_lines'])
        del entry['entry_lines']
    clean_md = '\n'.join(newlines)
    return clean_md, entries


def parse_line_metadata(line):
    '''Parse metadata from a line.

    Returns: *flag, key, value, number*
        - *flag*: bool for if this is a metadata tag or not
        - *key*: string, uppercase, metadata key
        - *value*: string (always), the metadata value
        - *number*: float or None, (attempt to derive a number from the start of *value*

    '''
    r = re.compile(r'[A-Z]*:')
    flag = False
    key = None
    value = None
    number = None
    if r.match(line):
        flag = True
        value = ':'.join(line.split(':')[1:]).strip()
        key = line.split(':')[0]
        try:
            number = float(value.split()[0])
        except:
            pass
    if not key:
        flag = False
        key = None
        value = None
        number = None
    return flag, key, value, number


def get_yeardate(fn):
    name = os.path.basename(fn)
    month = int(months[name[17:20]])
    year = int(name[21:25])
    return '%d-%02.0f' % (year, month)


def find_export_files(path):
    '''Find export files, discard smaller duplicates, sort by date,
    and return list of filenames.'''
    now = datetime.datetime.today()
    fns = sorted(glob.glob(os.path.join(path, '750 Words-export-*')), key=get_yeardate)
    if not len(fns):
        return []
    months_inv = dict([v, k] for k, v in months.items())
    ym0 = get_yeardate(fns[0])
    year, month = map(int, get_yeardate(fns[0]).split('-'))
    fns1 = []
    while year <= now.year:
        if month > 12:
            month = 1
        if year == now.year:
            condition = month <= now.month
        else:
            condition = True
        while condition and month <= 12:
            search = '750 Words-export-%s-%02.0f*' % (months_inv[month], year)
            mfns = glob.glob(os.path.join(path, search))
            max_size = -1
            max_fn = None
            for mfn in mfns:
                if os.path.getsize(mfn) > max_size:
                    max_size = os.path.getsize(mfn)
                    max_fn = mfn
            if max_fn:
                fns1.append(max_fn)
            month += 1
        year += 1
    return sorted(fns1, key=get_yeardate)


def count_words(text):
    '''Return number of word forms (split by whitespace).'''
    return len(text.split())


def remove_punctuation(
        txt, replace=((r'''~`!@#$%^&*()_-+=[]\{}|;:",./<>?''', ' '),
                      ('\n\r', ''))
        ):
    '''Remove punctuation from text.'''
    for repls, new in replace:
        for repl in repls:
            txt = txt.replace(repl, new)
    return txt



def apply_substitutions(txt, substs=substitutions):
    '''Make substitutions for common contractions, like "it's".'''
    for old, new in substs.items():
        txt = txt.replace(old, new)
    return txt


def clean_for_stats(text):
    '''Wrapper function to clean text for stats calculation.'''
    return apply_substitutions(remove_punctuation(text))


def freqdict(txt):
    '''Calculation word form frequency in *txt*.

    Returns a dictionary.

    '''
    wdict = defaultdict(int)
    for word in txt.split():
        wdict[word] += 1
    return wdict


def wordfreqpairs(wfdict):
    '''Turns frequency dict into an ordered list of (word, freq) tuples.'''
    return sorted(wfdict.iteritems(), key=lambda x: x[1], reverse=True)

