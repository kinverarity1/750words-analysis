from collections import defaultdict
import os

MOBY_ROOT = 'Moby'
HYPH_FN = os.path.join(MOBY_ROOT, 'mhyph', 'mhyph.txt')
POS_FN = os.path.join(MOBY_ROOT, 'mpos', 'mobyposi.i')
FREQ_FN = os.path.join(MOBY_ROOT, 'mwords', '10001fr.equ')

postypes = {'N': 'noun',
            'p': 'plural',
            'h': 'noun phrase',
            'V': 'verb (participle)',
            't': 'verb (transitive)',
            'i': 'verb (intransitive)',
            'A': 'adjective',
            'v': 'adverb',
            'C': 'conjunction',
            'P': 'preposition',
            '!': 'interjection',
            'r': 'pronoun',
            'D': 'definite article',
            'I': 'indefinite article',
            'o': 'nominative'}
pos_parse_func = lambda codes: [postypes[char] for char in codes]
POS_DELIM = chr(215)
LINE_BREAK = chr(13)


def load_hyphenation(hyphfn=HYPH_FN, kind='syllables'):
    '''Return a dictionary of words with hyphenation info.

    Args:
        - *hyphfn*: filename to mhyph.txt
        - *type*: 'syllable_count' or 'syllables'

    '''
    hyphen_char = chr(165)
    i = 0
    hdict = {}
    with open(hyphfn, mode='r') as f:
        print 'Loading hyphenation data from %s' % hyphfn
        n = 187175
        while i <= n:
            word = f.readline()[:-1]
            parts = word.split(hyphen_char)
            word = word.replace(hyphen_char, '')
            if kind == 'syllable_count':
                hdict[word] = len(parts)
            elif kind == 'syllables':
                hdict[word] = parts
            i += 1
    return hdict


class map_suffixes(dict):
    '''Replacement mapping class which tries suffixes on any words that
    aren't in the keys.'''
    def __init__(self, *args, **kwargs):
        self.debug = debug
        del kwargs['debug']
        dict.__init__(self, *args, **kwargs)
    
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError as original_exception:
            
            # Plural nouns ending in -s. This should be fairly solid.
            if key.endswith('s'):
                try:
                    root_poses = self[key[:-1]]
                except KeyError:
                    raise original_exception
                else:
                    if 'noun' in root_poses:
                        if self.debug:
                            print '%s -> %s [noun]' % (key, key[:-1])
                        return ['plural']
                    else:
                        raise original_exception
            
            # The following looks for -ed, -ing, -ly, and -ic. I have
            # no idea whether this is valid.
            
            for suffix in ('ed', 'ing', 'ly', 'ic'):
                root = key[:-1 * len(suffix)]
                if key.endswith(suffix) and root in self:
                    if self.debug:
                        print '%s -> %s' % (key, root)
                    return self.__getitem__(root)
        raise KeyError(key)


def load_partsofspeech(posfn=POS_FN, guess_suffixes=False, debug=False):
    '''Return dictionary of words, values are a list of
    the parts of speech.'''
    print 'Loading parts-of-speech data from %s' % posfn
    with open(posfn, mode='r') as f:
        poslist = (posfield.split(POS_DELIM) for posfield in
                   f.read().split(LINE_BREAK) if POS_DELIM in posfield)
    if guess_suffixes:
        posdict = map_suffixes(debug=debug)
    else:
        posdict = {}
    for i, content in enumerate(poslist):
        try:
            word, poscodes = content
            posdict[word] = pos_parse_func(poscodes)
        except KeyError:
            print 'line %d' % i, word, '|', poscodes#, sys.exc_info()
    return posdict


def get_by_freq(freqfn=FREQ_FN):
    with open(freqfn, mode='r') as f:
        flist = [fl.strip('\n').strip() for fl in f.readlines()[1:]]
    return flist


syllables = load_hyphenation()
pos = load_partsofspeech()
freq = get_by_freq()