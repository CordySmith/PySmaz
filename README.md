======
PySmaz
======

PySmaz is a Python port of the SMAZ short string text compression library.
Smaz by Salvatore Sanfilippo
Python port by Max Smith

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

Usage
=====

from lib.smaz import compress, decompress
compressedData = compress('Hello World!')
decompressedData = decompress(compressedData)

Versions
========
1.0.0 - original release (dict based tree structure)
1.0.1 - throughput improvements approx 10%

A Few Notes on the Python Port
==============================

PySmaz is Python 2.x, 3.x and PyPy compatible. I've tested with the latest versions, if you do find an issue with an earlier version, please let me know, and I'll address it.

The original C implementation used a table approach, along with some hashing to select the right entry. My first attempt used the original C-style approach and barely hit 170k/sec on CPython and a i7.

The trie based approach gets closer to one megabyte per second on the same setup. The difference is performance is largely due to the inner loop not always checking 7 characters per character - i.e. O(7n) vs O(n). I've tried to balance readability with performance, hopefully it's clear what's going on.

Decompression performance is limited by the single byte approach, and reaches 4.0 megabytes per second. To squeeze more performance it might be worth considering a multi-byte table for decoding.

After eliminating the O(n^2) string appends, PyPy performance is very impressive.

How should you use it ?

SMAZ works best on small ASCII English strings up to about 100 bytes. Beyond that length it is outperformed by entropy coders (bz2,zlib).

SMAZ Throughput on small strings is approximately equal to bz2 and zlib, due to the high setup cost per call to the entropy coders.

   STRINGS 1 to 8 BYTES
   --------------------
                     SMAZ(CPython)  SMAZ(PyPy)         bz2          zlib
   Comp   throughput  0.5 mb/s       4.0 mb/s     0.2 mb/s     0.43 mb/s
   Decomp throughput  1.4 mb/s      14.0 mb/s     0.5 mb/s      2.6 mb/s

On larger strings the relative advantages drop away, and the entropy coders are a better bet. Interestingly SMAZ isn't too far off bz2... but zlib crushes it.

   5 MEGABYTE STRINGS
   ------------------
                     SMAZ(CPython)  SMAZ(PyPy)         bz2          zlib
   Comp   throughput  0.9 mb/s       2.0 mb/s     2.0 mb/s     74.0 mb/s
   Decomp throughput  4.0 mb/s      19.5 mb/s    30.3 mb/s    454.6 mb/s

Compression varies but a reduction to 60% of the original size is pretty typical. Here are some results from some common text compression corpuses, the text messages and the urls individually encoded are pretty strong. Everything else is dire.

   COMPRESSION RESULTS
   -------------------
                      Original   SMAZ*      bz2    zlib SMAZc **  SMAZcp ***
   NUS SMS Messages    2666533 1851173  4106666 2667754  1876762     1864025
   alice29.txt          148481   91958    43102   53408    92405
   asyoulik.txt         125179   83762    39569   48778    84707
   cp.html               24603   19210     7624    7940    19413
   fields.c              11150    9511     3039    3115    10281
   grammar.lsp            3721    3284     1283    1222     3547
   lcet10.txt           419235  252085   107648  142604   254131
   plrabn12.txt         471162  283407   145545  193162   283515
   ACT corpus (concat) 4802130 3349766  1096139 1556366  3450138
   Leeds URL corpus    4629439 3454264  7246436 5011830  3528446     3527606
   * SMAZ with back-tracking
   ** SMAZ classic (original algorithm)
   *** SMAZ classic with pathological case detection

If you have a use-case where you need to keep an enormous amount of small (separate) strings that isn't going to be limited by PySmaz's throughput, then congratulations !

The unit tests explore PySmaz's performance against a series of common compressible strings. You'll notice it does very well against bz2 and zlib on English text, URLs and paths. In the Moby Dick sample SMAZ is best out to 54 characters (see unit test) and is often number one on larger samples out to hundreds of bytes. The first paragraph of Moby Dick as an example, SMAZ leads until 914 bytes of text have passed !

On non-English strings (numbers, symbols, nonsense) it still does better with everything under 10 bytes (see unit test) And ignoring big wins for zlib like repeating sub-strings, out to 20 bytes it is dominant. This is mostly thanks to the pathological case detection and backtracking in the compress routine.

Backtracking buys modest improvements to larger strings (1%) and deals with pathological sub-strings, again - you are better off using zlib for strings longer than 100 bytes in most cases.

Background
==========

From the original description::

    SMAZ - compression for very small strings
    -----------------------------------------

    Smaz is a simple compression library suitable for compressing very short
    strings. General purpose compression libraries will build the state needed
    for compressing data dynamically, in order to be able to compress every kind
    of data. This is a very good idea, but not for a specific problem: compressing
    small strings will not work.

    Smaz instead is not good for compressing general purpose data, but can compress
    text by 40-50% in the average case (works better with English), and is able to
    perform a bit of compression for HTML and urls as well. The important point is
    that Smaz is able to compress even strings of two or three bytes!

    For example the string "the" is compressed into a single byte.

    To compare this with other libraries, think that like zlib will usually not be
    able to compress text shorter than 100 bytes.

    COMPRESSION EXAMPLES
    --------------------

    'This is a small string' compressed by 50%
    'foobar' compressed by 34%
    'the end' compressed by 58%
    'not-a-g00d-Exampl333' enlarged by 15%
    'Smaz is a simple compression library' compressed by 39%
    'Nothing is more difficult, and therefore more precious, than to be able to decide' compressed by 49%
    'this is an example of what works very well with smaz' compressed by 49%
    '1000 numbers 2000 will 10 20 30 compress very little' compressed by 10%

    In general, lowercase English will work very well. It will suck with a lot
    of numbers inside the strings. Other languages are compressed pretty well too,
    the following is Italian, not very similar to English but still compressible
    by smaz:

    'Nel mezzo del cammin di nostra vita, mi ritrovai in una selva oscura' compressed by 33%
    'Mi illumino di immenso' compressed by 37%
    'L'autore di questa libreria vive in Sicilia' compressed by 28%

    It can compress URLS pretty well:

    'http://google.com' compressed by 59%
    'http://programming.reddit.com' compressed by 52%
    'http://github.com/antirez/smaz/tree/master' compressed by 46%

    CREDITS
    -------
    Small was written by Salvatore Sanfilippo and is released under the BSD license. See LICENSE section for more
    information
