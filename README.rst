Functions for reading and analysing your content on 750words.com

Read data in
------------

To read data from your downloads folder (``DEFAULT_PATH`` set in this file)::

    >>> text, entries = read_local_750words()

Or to download directly from https://www.750words.com::

    >>> text, entries = download_750words()

if you have PyQt4_/wxPython_ installed a login dialog will appear, otherwise
you can log in via a shell or pass ``email='...'`` and ``password='...'`` 
arguments to the function directly. This function requires the third-party 
Python packages requests_, lxml_, and pyquery_ to be installed, by 
default, only downloads the current month's writing. It also saves the exported 
data to disk to avoid unnecessary load on 750words.com servers. How to do this 
depends on what kind of Python installation you have, and is beyond the scope 
of this README.

See the docstrings of these functions for more information, and please use
``read_local_750words()`` whenever possible.

Statistics
----------

Statistics are calculated from the *entries* list via three classes::

    >>> s750 = stats_750(entries)       # Streaks, etc.
    >>> all = stats(text)               # Text statistics on all your writing
    >>> estats = entrystats(entries)    # Text statistics per entry

Use ``print`` to explore the results of these classes, and take a look at their
docstrings and methods. I'm going to add more stats, obviously, as I get time.

Graphing methods (``plot_...``) require matplotlib_.

The stats on the 750words.com website are -- and will probably continue to be --
far better. I made this framework mainly so I could look at how whatever
measures I can find change over time, something the 750words.com site doesn't
quite do at the moment (Feb 2013).

Copyright © 2000 nietky <nietky2@gmail.com>

This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

.. _PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/download
.. _wxPython: http://wxpython.org/download.php
.. _requests: http://docs.python-requests.org/en/latest/user/install/#install
.. _lxml: http://lxml.de/
.. _pyquery: http://pypi.python.org/pypi/pyquery
.. _matplotlib: http://matplotlib.org/downloads.html
