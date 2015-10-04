from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
try:
    import argparse
except ImportError:
    argparse = None
import datetime
import glob
import os
import pprint
import re
import sys
import time
import urlparse
import webbrowser

try:
    import markdown2
except ImportError:
    print('WARNING: please install markdown2 for improved performance!')
    markdown2 = None


MONTHS = dict(zip(['NOTHING', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
                   'sep', 'oct', 'nov', 'dec'], range(13)))
HEAD = '''
<html>
<head>
<style>
body{
    margin: 1em 0em 1em 14em;
    font-family: Arial, Helvetica, sans-serif;
    color: #222;
    line-height: 1;
    max-width: 960px;
    padding: 5px;
}
h1, h2, h3, h4 {
    color: #008800;
    font-weight: 800;
    font-family: Lucida Grande, Trebuchet MS, sans-serif;
}
h1, h2, h3, h4, h5, p {
    margin-bottom: 1em;
    padding: 0;
}
h1 {
    font-size: 28px;
}
h2 {
    font-size: 22px;
    margin: 20px 0 6px;
}
h3 {
    font-size: 21px;
}
h4 {
    font-size: 18px;
}
h5 {
    font-size: 16px;
}
a {
    color: #0099aa;
    margin: 0;
    padding: 0;
    vertical-align: baseline;
}
a:hover {
    text-decoration: none;
    color: #ff6600;
}
a:visited {
    color: #006688;
}
ul, ol {
    padding: 0;
    margin: 0;
}
li {
    line-height: 1.4em;
    margin-left: 44px;
}
li ul, li ul {
    margin-left: 24px;
}
p, ul, ol {
    font-size: 1em;
    line-height: 1.4em;
    max-width: 50em;
}
pre {
    padding: 0px 24px;
    max-width: 800px;
    white-space: pre-wrap;
}
code {
    font-family: Consolas, Monaco, Andale Mono, monospace;
    line-height: 1.5;
    font-size: 13px;
}
aside {
    display: block;
    float: right;
    width: 390px;
}
blockquote {
    border-left:.5em solid #eee;
    padding: 0 2em;
    margin-left:0;
    max-width: 476px;
}
blockquote  cite {
    font-size:14px;
    line-height: 1.4em;
    color:#bfbfbf;
}
blockquote cite:before {
    content: '\2014 \00A0';
}

blockquote p {  
    color: #666;
    max-width: 460px;
}
hr {
    width: 540px;
    text-align: left;
    margin: 0 auto 0 0;
    color: #999;
}

button,
input,
select,
textarea {
  font-size: 100%;
  margin: 0;
  vertical-align: baseline;
  *vertical-align: middle;
}
button, input {
  line-height: normal;
  *overflow: visible;
}
button::-moz-focus-inner, input::-moz-focus-inner {
  border: 0;
  padding: 0;
}
button,
input[type="button"],
input[type="reset"],
input[type="submit"] {
  cursor: pointer;
  -webkit-appearance: button;
}
input[type=checkbox], input[type=radio] {
  cursor: pointer;
}
/* override default chrome & firefox settings */
input:not([type="image"]), textarea {
  -webkit-box-sizing: content-box;
  -moz-box-sizing: content-box;
  box-sizing: content-box;
}

input[type="search"] {
  -webkit-appearance: textfield;
  -webkit-box-sizing: content-box;
  -moz-box-sizing: content-box;
  box-sizing: content-box;
}
input[type="search"]::-webkit-search-decoration {
  -webkit-appearance: none;
}
label,
input,
select,
textarea {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 13px;
  font-weight: normal;
  line-height: normal;
  margin-bottom: 18px;
}
input[type=checkbox], input[type=radio] {
  cursor: pointer;
  margin-bottom: 0;
}
input[type=text],
input[type=password],
textarea,
select {
  display: inline-block;
  width: 210px;
  padding: 4px;
  font-size: 13px;
  font-weight: normal;
  line-height: 1.4em;
  height: 18px;
  color: #808080;
  border: 1px solid #ccc;
  -webkit-border-radius: 3px;
  -moz-border-radius: 3px;
  border-radius: 3px;
}
select, input[type=file] {
  height: 27px;
  line-height: 27px;
}
textarea {
  height: auto;
}

/* grey out placeholders */
:-moz-placeholder {
  color: #bfbfbf;
}
::-webkit-input-placeholder {
  color: #bfbfbf;
}

input[type=text],
input[type=password],
select,
textarea {
  -webkit-transition: border linear 0.2s, box-shadow linear 0.2s;
  -moz-transition: border linear 0.2s, box-shadow linear 0.2s;
  transition: border linear 0.2s, box-shadow linear 0.2s;
  -webkit-box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
  -moz-box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}
input[type=text]:focus, input[type=password]:focus, textarea:focus {
  outline: none;
  border-color: rgba(82, 168, 236, 0.8);
  -webkit-box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1), 0 0 8px rgba(82, 168, 236, 0.6);
  -moz-box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1), 0 0 8px rgba(82, 168, 236, 0.6);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1), 0 0 8px rgba(82, 168, 236, 0.6);
}

/* buttons */
button {
  display: inline-block;
  padding: 4px 14px;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 13px;
  line-height: 18px;
  -webkit-border-radius: 4px;
  -moz-border-radius: 4px;
  border-radius: 4px;
  -webkit-box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 1px 2px rgba(0, 0, 0, 0.05);
  -moz-box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 1px 2px rgba(0, 0, 0, 0.05);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 1px 2px rgba(0, 0, 0, 0.05);
  background-color: #0064cd;
  background-repeat: repeat-x;
  background-image: -khtml-gradient(linear, left top, left bottom, from(#049cdb), to(#0064cd));
  background-image: -moz-linear-gradient(top, #049cdb, #0064cd);
  background-image: -ms-linear-gradient(top, #049cdb, #0064cd);
  background-image: -webkit-gradient(linear, left top, left bottom, color-stop(0%, #049cdb), color-stop(100%, #0064cd));
  background-image: -webkit-linear-gradient(top, #049cdb, #0064cd);
  background-image: -o-linear-gradient(top, #049cdb, #0064cd);
  background-image: linear-gradient(top, #049cdb, #0064cd);
  color: #fff;
  text-shadow: 0 -1px 0 rgba(0, 0, 0, 0.25);
  border: 1px solid #004b9a;
  border-bottom-color: #003f81;
  -webkit-transition: 0.1s linear all;
  -moz-transition: 0.1s linear all;
  transition: 0.1s linear all;
  border-color: #0064cd #0064cd #003f81;
  border-color: rgba(0, 0, 0, 0.1) rgba(0, 0, 0, 0.1) rgba(0, 0, 0, 0.25);
}
button:hover {
  color: #fff;
  background-position: 0 -15px;
  text-decoration: none;
}
button:active {
  -webkit-box-shadow: inset 0 3px 7px rgba(0, 0, 0, 0.15), 0 1px 2px rgba(0, 0, 0, 0.05);
  -moz-box-shadow: inset 0 3px 7px rgba(0, 0, 0, 0.15), 0 1px 2px rgba(0, 0, 0, 0.05);
  box-shadow: inset 0 3px 7px rgba(0, 0, 0, 0.15), 0 1px 2px rgba(0, 0, 0, 0.05);
}
button::-moz-focus-inner {
  padding: 0;
  border: 0;
}

/* CSS stylesheet is based on Kevin Burke's Markdown.css project (http://kevinburke.bitbucket.org/markdowncss) */


#floating_sidebar {
  position: fixed;
  overflow: scroll;
  left: 0;
  top: 20px; /* change to adjust height from the top of the page */
  height: 100%;
  padding-right: 1em;
  width: 12em;
}


#floating_sidebar ul, #floating_sidebar li {
  margin-left: 5px;
  line-height: 1.5em;
}

#metadata_table
{
    width: auto;
    margin: 2em;
    text-align: left;
    border-collapse: collapse;
}

#metadata_table td
{
    padding: 0.5em;
    white-space: nowrap;
}
#metadata_table .odd
{
    background: #e8edff; 
}
</style>
</head>
<body>
'''


class TextServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        path = self.path
        qs = {'view': 'entries'}
        if '?' in path:
            path, tmp = path.split('?', 1)
            qs = urlparse.parse_qs(tmp)
        func = self.server.get_html
        args = ()
        kwargs = {}
        if 'metadata' in qs.get('view', ()):
            func = self.server.get_metadata_list
        if 'metadata' in qs.keys():
            keys = qs.get('metadata')
            func = self.server.get_metadata
            kwargs['keys'] = keys
        self.wfile.write(func(*args, **kwargs))
        return


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
    month = int(MONTHS[name[17:20]])
    year = int(name[21:25])
    return '%d-%02.0f' % (year, month)
    

def find_export_files(path):
    '''Find export files, discard smaller duplicates, sort by date,
    and return list of filenames.'''
    now = datetime.datetime.today()
    fns = sorted(glob.glob(os.path.join(path, '750 Words-export-*')), key=get_yeardate)
    if not len(fns):
        return []
    months_inv = dict([v, k] for k, v in MONTHS.items())
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


def main():
    if argparse is None:
        print('WARNING: install argparse (or Python 2.7+) for easier usage')
        port = 8984
        path = os.path.expanduser('~/Downloads')
        if '--help' in sys.argv:
            print('Usage: view750 [path [port]]\n'
                  ' - path: folder containing 750 Words export files [default %s]\n'
                  ' - port: port to start HTTP server on [default %s]' % (path, port))
            sys.exit(0)
        else:
            if len(sys.argv) > 1:
                path = sys.argv[1]
                if len(sys.argv) > 2:
                    port = int(sys.argv[2])
    else:
        parser = get_cmdline_parser()
        args = parser.parse_args(sys.argv[1:])
        port = int(args.port)
        path = args.path

    class Call(object):
        def __init__(self, func, *args, **kwargs):
            self.func = func
            self.args = args
            self.kwargs = kwargs

        def __call__(self, *args, **kwargs):
            a = args + self.args
            k = dict(**self.kwargs)
            k.update(kwargs)
            return self.func(*a, **k)

    try:
        server = HTTPServer(('', port), TextServer)
        server.get_html = Call(get_html, path=path)
        server.get_metadata_list = Call(get_metadata_list, path=path)
        server.get_metadata = Call(get_metadata, path=path)
        webbrowser.open('http://localhost:%d/' % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print('Ctrl+C received, shutting down server')
        server.socket.close()


def get_cmdline_parser():
    home = os.path.expanduser('~')
    parser = argparse.ArgumentParser('View all 750 Words entries on a single page.')
    parser.add_argument('-P', '--path', default=os.path.join(home, 'Downloads'),
                        help='Folder containing 750 Words export files')
    parser.add_argument('-p', '--port', default='8984',
                        help='Port to start server on')
    return parser


def get_md_entries(path='.'):
    raw_text = ''
    for fn in find_export_files(path):
        with open(fn, mode='r') as f:
            raw_text += f.read()
    cleaned_md, entries = parse_markdown(raw_text)
    return raw_text, cleaned_md, entries


def get_entries_frame(path='.', frame_type='entries'):
    raw_text, cleaned_md, entries = get_md_entries(path=path)
    html = str(HEAD)
    html += '<div id="floating_sidebar">\n<ul>\n'
    if frame_type == 'entries':
        html += '\t<li><u><a href="/?view=entries">Entries</a></u> | <a href="/?view=metadata">Metadata</a></li><li></li>\n\n'
        for entry in entries:
            html += '\t<li><a href="%s">%s</a></li>\n' % (
                        '/?view=entries#%s' % entry['date'].strftime('%Y-%m-%d'),
                        entry['date'].strftime('%a %d %b %Y'))
        html += '<li></li><li></li></ul></div>'
    elif frame_type == 'metadata':
        html += '\t<li><a href="/?view=entries">Entries</a> | <u><a href="/?view=metadata">Metadata</a></u></li><li></li>\n\n'
        metadata = get_metadatas(entries)
        keys = sorted(metadata.keys())
        for key in keys:
            instances = sorted(metadata[key], key=lambda L: L[0])
            html += '\t<li><a href="%s">%s</a></li>' % ('/?view=metadata&metadata=' + key, key)
        html += '<li></li><li></li></ul></div>'
    return html, raw_text, cleaned_md, entries


def get_html(path='.'):
    html, raw_text, cleaned_md, entries = get_entries_frame(path=path, frame_type='entries')
    html += '<h1>Entries</h1>\n\n'
    if markdown2 is None:
        class FakeMarkdownParser(object):
            def convert(self, text):
                return text.replace('\n', '\n<br />')
        markdowner = FakeMarkdownParser()
    else:
        markdowner = markdown2.Markdown()
    html += markdowner.convert(cleaned_md).encode('utf-8')
    html += '\n</body></html>\n'
    return html


def get_metadata_list(path='.'):
    html, raw_text, cleaned_md, entries = get_entries_frame(path=path, frame_type='metadata')
    html += '<h1>Metadata</h1>\n\n<ul>'
    metadata = get_metadatas(entries)
    keys = sorted(metadata.keys())
    for key in keys:
        instances = sorted(metadata[key], key=lambda L: L[0])
        html += '\t<li><a href="%s">%s</a></li>' % ('/?view=metadata&metadata=' + key, key)
    html += '\n\n</ul>\n\n</body></html>\n'
    return html


def get_metadatas(entries):
    metadata = {}
    for entry in entries:
        for key, mdinstances in entry['metadata'].items():
            for value, number in mdinstances:
                if key in metadata:
                    metadata[key].append([entry['date'], entry['mins'], entry['words'], value, number])
                else:
                    metadata[key] = [[entry['date'], entry['mins'], entry['words'], value, number]]
    return metadata


def insert_gchart(html, dates, values, key):
    gchart = r'''<script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
        google.load('visualization', '1.0', {'packages':['corechart']});
        google.setOnLoadCallback(drawChart);
        function drawChart() {
            var data = new google.visualization.DataTable();
            data.addColumn('date', 'Date');
            data.addColumn('number', 'Value');
            DATA
            var chart = new google.visualization.BarChart(document.getElementById('chart_%s'));
            chart.draw(data, {legend: {position: 'none'},
                              chartArea: {left: 100}
                              });
        }
    </script>''' % key
    Dates = ['new Date("%s")' % date.strftime('%Y-%m-%d 00:00:00') for date in dates]
    # gchart = gchart.replace('DATA', pprint.pformat([list(i) for i in zip(Dates, values)]).replace("'", ""))
    data = ''
    for i in range(len(Dates)):
        data += 'data.addRow([%s, %s]);\n            ' % (Dates[i], values[i])
    gchart = gchart.replace('DATA', data)
    return html.replace('<head>', '<head>\n\n' + gchart + '\n\n')


def test_metadata_numeric(values):
    once = False
    twice = False
    x = []
    y = []
    for i, (date, mins, words, value, number) in enumerate(values):
        if not number is None:
            if once:
                twice = True
            else:
                once = True
            x.append(date)
            y.append(number)
    return twice, x, y


def get_metadata(keys=(), path='.'):
    html, raw_text, cleaned_md, entries = get_entries_frame(path=path, frame_type='metadata')
    metadata = get_metadatas(entries)
    for key in keys:
        html += '<h2>' + key + '</h2>\n\n'
        flag, x, y = test_metadata_numeric(metadata[key])
        if flag:
            height = len(y) * 40
            min_height = 160
            if height < min_height:
                height = min_height
            html += '<div id="chart_%s" style="width:500; height:%d"></div>\n\n' % (key, height)
            html = insert_gchart(html, x, y, key)
        html += '<table id="metadata_table"><tbody>\n'
        prev_date = None
        for i, (date, mins, words, value, number) in enumerate(sorted(metadata[key], key=lambda i: i[0])[::-1]):
            html += '<tr'
            if not i % 2:
                html += ' class="odd">\n'
            else:
                html += '>\n'
            if date == prev_date:
                date_str = ''
            else:
                date_str = date.strftime('%A %B %d, %Y')
            html += '\t<td>%s</td>\n' % (date_str)
            html += '\t<td>%s</td>\n' % (value)
            html += '</tr>\n'
            prev_date = date
        html += '</tbody></table>'
    html += '\n\n</body></html>\n'
    return html


def get_entries(path=r'U:\Downloads'):
    md = ''
    for fn in find_export_files(path):
        with open(fn, mode='r') as f:
            md += f.read()
    md2, entries = parse_markdown(md)
    return entries

if __name__ == '__main__':
    main()

