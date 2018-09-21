# pySmaz

pySmaz is a Python port of the [SMAZ](https://github.com/antirez/smaz) short
string text compression algorithm by Salvatore Sanfilippo.

SMAZ works best on small ASCII English strings up to about 100 bytes. Beyond
that length it is outperformed by entropy coders (bz2, zlib).  This makes SMAZ
ideal for applications like English names and most URLs.

SMAZ throughput on small strings is approximately equal to bz2 and zlib, due to
the high setup cost per call to the entropy coders.

SMAZ by Salvatore Sanfilippo, Python port by Max Smith.

## Installation

```
pip install pySmaz
```

## Usage

```python
from smaz import compress, decompress


print compress("Hello, world!")
print compress("https://github.com/antirez/smaz")
print decompress(compress("Salvatore"))
```

## Versions

* 1.0.0 - original release (dict based tree structure)
* 1.0.1 - throughput improvements approx 10%

## Background

For additional background, check out the original C implementation by Salvatore
Sanfilippo [here](https://github.com/antirez/smaz).

## Compatibility and Performance

pySmaz is Python 2.x, PyPy (and mostly Python 3.x) compatible. I've tested with
the latest versions, if you do find an issue with an earlier version, please
let me know, and I'll address it.

The original C implementation used a table approach, along with some hashing to
select the right entry. My first attempt used the original C-style approach and
barely hit 170k/sec on CPython and a i7.

The tree based approach gets closer to one megabyte per second on the same
setup. The difference is performance is largely due to the inner loop not
always checking 7 characters per character - i.e. O(7n) vs O(n). I've tried to
balance readability with performance, hopefully it's clear what's going on.

Decompression performance is limited by the single byte approach, and reaches
4.0 megabytes per second. To squeeze more performance it might be worth
considering a multi-byte table for decoding.

After eliminating the O(n^2) string appends, PyPy performance is very
impressive.

## How should you use it ?

SMAZ works best on small ASCII English strings up to about 100 bytes. Beyond
that length it is outperformed by entropy coders (bz2, zlib).

SMAZ Throughput on small strings is approximately equal to bz2 and zlib, due
to the high setup cost per call to the entropy coders.

### Strings 1-8 Bytes

|                   | SMAZ(CPython) | SMAZ(PyPy) | bz2      | zlib      |
| ----------------- | ------------- | ---------- | -------- | --------- |
| Comp throughput   | 0.5 mb/s      | 4.0 mb/s   | 0.2 mb/s | 0.43 mb/s |
| Decomp throughput | 1.4 mb/s      | 14.0 mb/s  | 0.5 mb/s | 2.6 mb/s  |

On larger strings the relative advantages drop away, and the entropy coders
are a better bet. Interestingly SMAZ isn't too far off bz2... but zlib crushes
it.

### Strings 5 Megabytes

|                   | SMAZ(CPython) | SMAZ(PyPy) | bz2       | zlib       |
| ----------------- | ------------- | ---------- | --------- | ---------- |
| Comp throughput   | 0.9 mb/s      | 2.0 mb/s   | 2.0 mb/s  | 74.0 mb/s  |
| Decomp throughput | 4.0 mb/s      | 19.5 mb/s  | 30.3 mb/s | 454.6 mb/s |

Compression varies but a reduction to 60% of the original size is pretty
typical. Here are some results from some common text compression corpuses, the
text messages and the urls individually encoded are pretty strong. Everything
else is dire.

```
COMPRESSION RESULTS
-------------------
                    Original  SMAZ*     bz2      zlib     SMAZc **  SMAZcp ***
NUS SMS Messages    2666533   1851173   4106666  2667754  1876762   1864025
alice29.txt          148481     91958     43102    53408    92405
asyoulik.txt         125179     83762     39569    48778    84707
cp.html               24603     19210      7624     7940    19413
fields.c              11150      9511      3039     3115    10281
grammar.lsp            3721      3284      1283     1222     3547
lcet10.txt           419235    252085    107648   142604   254131
plrabn12.txt         471162    283407    145545   193162   283515
ACT corpus (concat) 4802130   3349766   1096139  1556366  3450138
Leeds URL corpus    4629439   3454264   7246436  5011830  3528446   3527606

* SMAZ with back-tracking
** SMAZ classic (original algorithm)
*** SMAZ classic with pathological case detection
```

If you have a use-case where you need to keep an enormous amount of small
(separate) strings that isn't going to be limited by pySmaz's throughput, then
congratulations!

The unit tests explore pySmaz's performance against a series of common
compressible strings. You'll notice it does very well against bz2 and zlib on
English text, URLs and paths. In the Moby Dick sample SMAZ is best out to 54
characters (see unit test) and is often number one on larger samples out to
hundreds of bytes. The first paragraph of Moby Dick as an example, SMAZ leads
until 914 bytes of text have passed!

On non-English strings (numbers, symbols, nonsense) it still does better with
everything under 10 bytes (see unit test) And ignoring big wins for zlib like
repeating sub-strings, out to 20 bytes it is dominant. This is mostly thanks
to the pathological case detection and backtracking in the compress routine.

Backtracking buys modest improvements to larger strings (1%) and deals with
pathological sub-strings, again - you are better off using zlib for strings
longer than 100 bytes in most cases.

Notes on Python 3.x compatbility: Basically the split between bytes and
strings is problematic for this codebase (in particular the unit tests !)
I'll try and get it fixed-up over the next few months.

## Licenses

BSD license per original C implementation at https://github.com/antirez/smaz
Except for text samples which are in the public domain and from:

* The ACT Corpus
  http://compression.ca/act/act-files.html
  Jeff Gilchrist

* The Canterbury Corpus
  http://corpus.canterbury.ac.nz/
  Maintained by: Dr. Tim Bell, Matt Powell, Joffre Horlor, Ross Arnold

* NUS SMS Corpus
  http://wing.comp.nus.edu.sg:8080/SMSCorpus/overview.jsp
  Tao Chen and Min-Yen Kan (2012). Creating a Live, Public Short Message Service Corpus: The NUS SMS Corpus.
  Language Resources and Evaluation. Aug 2012. [doi:10.1007/s10579-012-9197-9]

* Leeds Collection of Internet Corpora
  http://corpus.leeds.ac.uk/internet.html
  Serge Sharoff
