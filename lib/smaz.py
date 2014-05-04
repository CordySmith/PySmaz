#!/usr/bin/env python
# coding=utf-8
"""
PySmaz a Python port of the SMAZ short string text compression library.
Python port by Max Smith
Smaz by Salvatore Sanfilippo

BSD license per original C implementation at https://github.com/antirez/smaz

Except for text samples which are in the public domain and from:
 The ACT Corpus
 --------------
  http://compression.ca/act/act-files.html
  Jeff Gilchrist

 The Canterbury Corpus
 ---------------------
  http://corpus.canterbury.ac.nz/
  Maintained by: Dr. Tim Bell, Matt Powell, Joffre Horlor, Ross Arnold

 NUS SMS Corpus
 --------------
  http://wing.comp.nus.edu.sg:8080/SMSCorpus/overview.jsp
  Tao Chen and Min-Yen Kan (2012). Creating a Live, Public Short Message Service Corpus: The NUS SMS Corpus.
  Language Resources and Evaluation. Aug 2012. [doi:10.1007/s10579-012-9197-9]

 Leeds Collection of Internet Corpora
 ------------------------------------
  http://corpus.leeds.ac.uk/internet.html
  Serge Sharoff

Usage
-----

from lib.smaz import compress, decompress
compressedData = compress('Hello World!')
decompressedData = decompress(compressedData)

Versions
========
1.0.0 - original release (dict based tree structure)
1.0.1 - throughput improvements approx 10%

A Few Notes on the Python Port
------------------------------

PySmaz is Python 2.x, 3.x and PyPy compatible. I've tested with the latest versions, if you do find an issue with an
earlier version, please let me know, and I'll address it.

The original C implementation used a table approach, along with some hashing to select the right entry. My first attempt
 used the original C-style approach and barely hit 170k/sec on CPython and a i7.

The trie based approach gets closer to one megabyte per second on the same setup. The difference is performance is
largely due to the inner loop not always checking 7 characters per character - i.e. O(7n) vs O(n). I've tried to balance
readability with performance, hopefully it's clear what's going on.

Decompression performance is limited by the single byte approach, and reaches 4.0 megabytes per second. To squeeze
more performance it might be worth considering a multi-byte table for decoding.

After eliminating the O(n^2) string appends, PyPy performance is very impressive.

How should you use it ?

SMAZ works best on small ASCII English strings up to about 100 bytes. Beyond that length it is outperformed by entropy
coders (bz2,zlib). Its throughput on small strings is approximately equal to bz2 and zlib, due to the high fixed cost
per call to the codec.

   STRINGS 1 to 8 bytes
   --------------------
                     SMAZ(CPython)  SMAZ(PyPy)         bz2          zlib
   Comp   throughput  0.5 mb/s       4.0 mb/s     0.2 mb/s     0.43 mb/s
   Decomp throughput  1.4 mb/s      14.0 mb/s     0.5 mb/s      2.6 mb/s

On larger strings the relative advantages drop away, and the entropy coders are a better bet. Interestingly SMAZ isn't
too far off bz2... but zlib crushes it.

   5 MEGABYTE STRING
   -----------------
                     SMAZ(CPython)  SMAZ(PyPy)         bz2          zlib
   Comp   throughput  0.9 mb/s       2.0 mb/s     2.0 mb/s      74.0 mb/s
   Decomp throughput  4.0 mb/s      19.5 mb/s    30.3 mb/s     454.6 mb/s

Compression varies but a reduction to 60% of the original size is pretty typical. Here are some results from some common
text compression corpuses, the text messages and the urls individually encoded are pretty strong. Everything else is
dire.

   COMPRESSION RESULTS
   -------------------
                      Original    SMAZ (b'track)       bz2        zlib  SMAZ-classic SMAZ-classic pathological
   NUS SMS Messages    2666533          1851173    4106666     2667754       1876762                   1864025
   alice29.txt          148481            91958      43102       53408         92405
   asyoulik.txt         125179            83762      39569       48778         84707
   cp.html               24603            19210       7624        7940         19413
   fields.c              11150             9511       3039        3115         10281
   grammar.lsp            3721             3284       1283        1222          3547
   lcet10.txt           419235           252085     107648      142604        254131
   plrabn12.txt         471162           283407     145545      193162        283515
   ACT corpus (concat) 4802130          3349766    1096139     1556366       3450138
   Leeds URL corpus    4629439          3454264    7246436     5011830       3528446                   3527606

If you have a use-case where you need to keep an enormous amount of small (separate) strings that isn't going to be
limited by PySmaz's throughput, then congratulations !

The unit tests explore PySmaz's performance against a series of common compressible strings. You'll notice it does very
well against bz2 and zlib on English text, URLs and paths. In the Moby Dick sample SMAZ is best out to 54 characters
(see unit test) and is often number one on larger samples out to hundreds of bytes. The first paragraph of Moby Dick as
an example, SMAZ leads until 914 bytes of text have passed !

On non-English strings (numbers, symbols, nonsense) it still does better with everything under 10 bytes (see unit test)
And ignoring big wins for zlib like repeating sub-strings, out to 20 bytes it is dominant. This is mostly thanks to the
pathological case detection and backtracking in the compress routine.

Backtracking buys modest improvements to larger strings (1%) and deals with pathological sub-strings, again - you are
better off using zlib for strings longer than 100 bytes in most cases.

BACKGROUND
----------

From the original description:

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

    To compare this with other libraries, think that like zlib will usually not be able to compress text shorter than
    100 bytes.

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
    Small was written by Salvatore Sanfilippo and is released under the BSD license. See __License__ section for more
    information
"""

__author__ = "Salvatore Sanfilippo and Max Smith"
__copyright__ = "Copyright 2006-2014 Max Smith, Salvatore Sanfilippo"
__credits__ = ["Max Smith", "Salvatore Sanfilippo"]
__license__ = """
BSD License
Copyright (c) 2006-2009, Salvatore Sanfilippo
Copyright (c) 2014, Max Smith
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the
      following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
      following disclaimer in the documentation and/or other materials provided with the distribution.
    * Neither the name of Smaz nor the names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
__version__ = "1.0.1"
__maintainer__ = "Max Smith"
__email__ = None  # Sorry, I get far too much spam as it is. Track me down at http://www.notonbluray.com

BACKTRACK_LIMIT = 254  # No point backtracking more than 255 characters


def make_trie(decode_table):
    """ Create a trie representing the encoding strategy implied by the passed table.
        For each string in the table, assign it an encoded value, walk through the string
        creating a node for each character at a position (if none already exists), and when
        we reach the end of the string populate that node with the assigned encoded value.

    :param decode_table: list
    """
    empty_node = list(None for _ in range(0, 256))
    root_node = list(empty_node)
    if not decode_table:
        raise ValueError('Empty data passed to make_tree')
    elif len(decode_table) > 254:
        raise ValueError('Too long list in make tree: %d' % len(decode_table))
    else:
        for enc_byte, sstr in enumerate(decode_table):
            node_ptr = root_node
            for str_pos, ch in enumerate(sstr):
                if node_ptr[ord(ch)]:  # If a child node exists for character
                    terminal_byte, children = node_ptr[ord(ch)]
                    if len(sstr) == str_pos + 1:  # At the end ?
                        if not terminal_byte:
                            node_ptr[ord(ch)] = [chr(enc_byte), children]
                            break
                        else:
                            raise ValueError('Unexpected terminal: duplicates in data (%s) (%s) (%s)' %
                                             (sstr, ch, node_ptr))
                    node_ptr = children
                else:  # Create the child node
                    if len(sstr) == str_pos + 1:  # At the end ?
                        node_ptr[ord(ch)] = [chr(enc_byte), list(empty_node)]
                    else:
                        node_ptr[ord(ch)] = [None, list(empty_node)]
                        _, node_ptr = node_ptr[ord(ch)]
    # Now we've built the trie, we can optimize it a bit by replacing empty terminal nodes early with None
    stack = list(root_node)
    while stack:
        node_ptr = stack.pop()
        if node_ptr:
            _, children = node_ptr
            if children == empty_node:
                node_ptr[1] = None  # Replace empty entries with None
            else:
                stack.extend(children)
    return root_node


def make_tree(decode_table):
    """ Create a tree representing the encoding strategy implied by the passed table.
        For each string in the table, assign it an encoded value, walk through the string
        creating a node for each character at a position (if none already exists), and when
        we reach the end of the string populate that node with the assigned encoded value.

    :param decode_table: list
    """
    root_node = {}
    if not decode_table:
        raise ValueError('Empty data passed to make_tree')
    elif len(decode_table) > 254:
        raise ValueError('Too long list in make tree: %d' % len(decode_table))
    else:
        for enc_byte, sstr in enumerate(decode_table):
            node_ptr = root_node
            for str_pos, ch in enumerate(sstr):
                if node_ptr.get(ch):  # If a child node exists for character
                    terminal_byte, children = node_ptr.get(ch)
                    if len(sstr) == str_pos + 1:  # At the end ?
                        if not terminal_byte:
                            node_ptr[ch] = (chr(enc_byte), children)
                            break
                        else:
                            raise ValueError('Unexpected terminal: duplicates in data (%s) (%s) (%s)' %
                                             (sstr, ch, node_ptr))
                    node_ptr = children
                else:  # Create the child node
                    if len(sstr) == str_pos + 1:  # At the end ?
                        node_ptr[ch] = (chr(enc_byte), {})
                    else:
                        node_ptr[ch] = (None, {})
                        _, node_ptr = node_ptr[ch]
    return root_node

# Can be up to 253 entries in this table.
DECODE = [" ", "the", "e", "t", "a", "of", "o", "and", "i", "n", "s", "e ", "r", " th",
          " t", "in", "he", "th", "h", "he ", "to", "\r\n", "l", "s ", "d", " a", "an",
          "er", "c", " o", "d ", "on", " of", "re", "of ", "t ", ", ", "is", "u", "at",
          "   ", "n ", "or", "which", "f", "m", "as", "it", "that", "\n", "was", "en",
          "  ", " w", "es", " an", " i", "\r", "f ", "g", "p", "nd", " s", "nd ", "ed ",
          "w", "ed", "http://", "for", "te", "ing", "y ", "The", " c", "ti", "r ", "his",
          "st", " in", "ar", "nt", ",", " to", "y", "ng", " h", "with", "le", "al", "to ",
          "b", "ou", "be", "were", " b", "se", "o ", "ent", "ha", "ng ", "their", "\"",
          "hi", "from", " f", "in ", "de", "ion", "me", "v", ".", "ve", "all", "re ",
          "ri", "ro", "is ", "co", "f t", "are", "ea", ". ", "her", " m", "er ", " p",
          "es ", "by", "they", "di", "ra", "ic", "not", "s, ", "d t", "at ", "ce", "la",
          "h ", "ne", "as ", "tio", "on ", "n t", "io", "we", " a ", "om", ", a", "s o",
          "ur", "li", "ll", "ch", "had", "this", "e t", "g ", "e\r\n", " wh", "ere",
          " co", "e o", "a ", "us", " d", "ss", "\n\r\n", "\r\n\r", "=\"", " be", " e",
          "s a", "ma", "one", "t t", "or ", "but", "el", "so", "l ", "e s", "s,", "no",
          "ter", " wa", "iv", "ho", "e a", " r", "hat", "s t", "ns", "ch ", "wh", "tr",
          "ut", "/", "have", "ly ", "ta", " ha", " on", "tha", "-", " l", "ati", "en ",
          "pe", " re", "there", "ass", "si", " fo", "wa", "ec", "our", "who", "its", "z",
          "fo", "rs", ">", "ot", "un", "<", "im", "th ", "nc", "ate", "><", "ver", "ad",
          " we", "ly", "ee", " n", "id", " cl", "ac", "il", "</", "rt", " wi", "div",
          "e, ", " it", "whi", " ma", "ge", "x", "e c", "men", ".com"]

# Can be regenerated with the below line
SMAZ_TREE = make_trie(DECODE)


def _check_ascii(sstr):
    """ Return True iff the passed string contains only ascii chars """
    return all(ord(ch) < 128 for ch in sstr)


def _encapsulate(input_str):
    """ There are some pathological cases, where it may be better to just encapsulate the string in 255 code chunks
    """
    if not input_str:
        return input_str
    else:
        output = []
        for chunk in (input_str[i:i+255] for i in range(0, len(input_str), 255)):
            if 1 == len(chunk):
                output.append(chr(254) + chunk)
            else:
                output.append(chr(255) + chr(len(chunk) - 1))
                output.append(chunk)
        return "".join(output)


def _encapsulate_list(input_list):
    """ There are some pathological cases, where it may be better to just encapsulate the string in 255 code chunks
    """
    if not input_list:
        return input_list
    else:
        output = []
        for chunk in (input_list[i:i+255] for i in range(0, len(input_list), 255)):
            if 1 == len(chunk):
                output.append(chr(254))
                output.extend(chunk)
            else:
                output.extend((chr(255), chr(len(chunk) - 1)))
                output.extend(chunk)
        return output


def _worst_size(str_len):
    """ Given a string length, what's the worst size that we should grow to """
    if str_len == 0:
        return 0
    elif str_len == 1:
        return 2
    elif str_len % 255 in (0, 1):
        return (str_len / 255) * 2 + str_len + (str_len % 255)
    else:
        return ((str_len / 255) + 1) * 2 + str_len


def compress_no_backtracking(input_str):
    """ As ccmpress, but with backtracking and pathological case detection, and ascii checking disabled """
    return compress(input_str, check_ascii=False, backtracking=False, pathological_case_detection=False)


def compress(input_str, check_ascii=True, raise_on_error=True, compression_tree=None, backtracking=True,
             pathological_case_detection=True, backtrack_limit=BACKTRACK_LIMIT):
    """ Compress the passed string using the SMAZ algorithm. Returns the encoded string. Performance is a O(N), but the
        constant will vary depending on the relationship between the compression tree and input_str, in particular the
        average depth explored/average characters per encoded symbol.


    :param input_str The ASCII str to be compressed
    :param check_ascii Check the input_str is ASCII before we encode it (default True)
    :param raise_on_error Throw a value type exception (default True)
    :param compression_tree: A tree represented as a dict of ascii char to tuple( encoded_byte, dict( ... ) ), that
                             describes how to compress content. By default uses built in SMAZ tree. See also make_tree
    :param backtracking: Enable checking for poor performance of the standard algorithm, some performance impact
                             True = better compression (1% on average), False = Higher throughput
    :param pathological_case_detection: A lighter version of backtracking to catch output growth beyond the
                             simple worst case handling of encapsulation. You probably want this enabled.
    :param backtrack_limit: How many characters to look backwards for backtracking, defaults to 255 - setting it higher
                            may achieve slightly higher compression ratios (0.1% on big strings) at the expense of much
                            worse performance, particularly on random data. You probably want this left as default

    :type input_str: str
    :type check_ascii: bool
    :type raise_on_error: bool
    :type compression_tree: dict
    :type backtracking: bool
    :type pathological_case_detection: bool

    :rtype: str
    :return: The compressed input_str
    """
    if not input_str:
        return input_str
    else:
        if check_ascii and not _check_ascii(input_str):
            if raise_on_error:
                raise ValueError('SMAZ can only process ASCII text.')
            else:
                return None

        # Invariants:
        terminal_tree_node = (None, None)
        compression_tree = compression_tree or SMAZ_TREE
        input_str_len = len(input_str)

        # Invariant: All of these arrays assume len(array) = number of bytes in array
        output = []          # Single bytes. Committed, non-back-track-able output
        unmatched = []       # Single bytes. Current pool for encapsulating (i.e. 255/254 + unmatched)
        backtrack_buff = []  # Single bytes. Encoded between last_backtrack_pos and pos (excl enc_buf and unmatched)
        enc_buf = []         # Single bytes. Encoded output for the current run of compression codes

        last_backtrack_pos = pos = 0
        while pos < input_str_len:
            tree_ptr = compression_tree
            enc_byte = None
            j = 0
            while j < input_str_len - pos:  # Search the tree for the longest matching sequence
                byte_val, tree_ptr = tree_ptr[ord(input_str[pos + j])] or terminal_tree_node
                j += 1
                if byte_val is not None:
                    enc_byte = byte_val  # Remember this match, and search for a longer one
                    enc_len = j
                if not tree_ptr:
                    break  # No more matching characters in the tree

            if enc_byte is None:
                unmatched.append(input_str[pos])
                pos += 1  # We didn't match any stems, add the character the unmatched list

                # Backtracking - sometimes it makes sense to go back and not use a length one symbol between two runs of
                # raw text, since the cost of the context switch is 2 bytes. The following code looks backwards and
                # tries to judge if the mode switches left us better or worse off. If worse off, re-encode the text as
                # a raw text run.
                if len(enc_buf) > 0 or input_str_len == pos:
                    # Mode switch ! or end of string
                    merge_len = _worst_size(pos - last_backtrack_pos)
                    unmerge_len = len(backtrack_buff) + len(enc_buf) + _worst_size(len(unmatched))
                    if merge_len > unmerge_len + 2 or pos - last_backtrack_pos > backtrack_limit or not backtracking:
                        # Unmerge: gained at least 3 bytes through encoding, reset the backtrack marker to here
                        output.extend(backtrack_buff)
                        output.extend(enc_buf)
                        backtrack_buff = []
                        last_backtrack_pos = pos - 1
                    elif merge_len < unmerge_len:
                        # Merge: Mode switch doesn't make sense, don't move backtrack marker
                        backtrack_buff = []
                        unmatched = list(input_str[last_backtrack_pos:pos])
                    else:
                        # Gains are two bytes or less - don't move the backtrack marker till we have a clear gain
                        backtrack_buff.extend(enc_buf)
                        if input_str_len == pos:
                            backtrack_buff.extend(_encapsulate_list(unmatched))
                            unmatched = []
                    enc_buf = []
            else:
                # noinspection PyUnboundLocalVariable
                pos += enc_len  # We did match in the tree, advance along, by the number of bytes matched
                enc_buf.append(enc_byte)
                if unmatched:  # Entering an encoding run
                        backtrack_buff.extend(_encapsulate_list(unmatched))
                        unmatched = []

        output.extend(backtrack_buff)
        output.extend(_encapsulate_list(unmatched))
        output.extend(enc_buf)

        # This may look a bit clunky, but it is worth 20% in cPython and O(n^2) -> O(n) in PyPy
        output = "".join(output)

        # Pathological case detection - Did we grow more than we would by encapsulating the string ?
        # There are some cases where backtracking doesn't work correctly, examples:
        # Y OF
        if pathological_case_detection:
            worst = _worst_size(input_str_len)
            if len(output) > worst:
                return _encapsulate(input_str)
        return output


def compress_classic(input_str, pathological_case_detection=True):
    """ A trie version of the original SMAZ compressor, should give identical output to C version.
        Faster on typical material, but can be tripped up by pathological cases.
        :type input_str: str
        :type pathological_case_detection: bool

        :param input_str The string to be compressed
        :param pathological_case_detection Look for growth beyond the worst case of encapsulation and encapsulate
               default is True, you probably want this enabled.

        :rtype: str
        :return: The compressed input_str
        """
    if not input_str:
        return input_str
    else:
        # Invariants:
        terminal_tree_node = (None, None)
        input_str_len = len(input_str)

        # Invariant: All of these arrays assume len(array) = number of bytes in array
        output = []     # Single bytes. Committed, non-back-track-able output
        unmatched = []  # Single bytes. Current pool for encapsulating (i.e. 255/254 + unmatched)

        pos = 0
        while pos < input_str_len:
            tree_ptr = SMAZ_TREE
            enc_byte = None
            j = 0
            while j < input_str_len - pos:  # Search the tree for the longest matching sequence
                byte_val, tree_ptr = tree_ptr[ord(input_str[pos + j])] or terminal_tree_node
                j += 1
                if byte_val is not None:
                    enc_byte = byte_val  # Remember this match, and search for a longer one
                    enc_len = j
                if not tree_ptr:
                    break  # No more matching characters in the tree

            if enc_byte is None:
                unmatched.append(input_str[pos])
                pos += 1  # We didn't match any stems, add the character the unmatched list
            else:
                # noinspection PyUnboundLocalVariable
                pos += enc_len  # We did match in the tree, advance along, by the number of bytes matched
                if unmatched:  # Entering an encoding run
                    output.extend(_encapsulate_list(unmatched))
                    unmatched = []
                output.append(enc_byte)
        if unmatched:
            output.extend(_encapsulate_list(unmatched))

        if pathological_case_detection and len(output) > _worst_size(input_str_len):
            return _encapsulate(input_str)
        else:
            return "".join(output)


def decompress(input_str, raise_on_error=True, check_ascii=False, decompress_table=None):
    """ Returns decoded text from the input_str using the SMAZ algorithm by default
        :type input_str: str
        :type raise_on_error: bool
        :type check_ascii: bool
        :type decompress_table: list

        :param raise_on_error Throw an exception on any kind of decode error, if false, return None on error
        :param check_ascii Check that all output is ASCII. Will raise or return None depending on raise_on_error
        :param decompress_table Alternative 253 entry decode table, by default uses SMAZ

        :rtype: str
        :return: The decompressed input_str
    """
    if not input_str:
        return input_str
    else:
        decompress_table = decompress_table or DECODE
        input_str_len = len(input_str)
        output = []
        pos = 0
        try:
            while pos < input_str_len:
                ch = ord(input_str[pos])
                pos += 1
                if ch < 254:
                    # Code table entry
                    output.append(decompress_table[ch])
                else:
                    next_byte = input_str[pos]
                    pos += 1
                    if 254 == ch:
                        # Verbatim byte
                        output.append(next_byte)
                    else:  # 255 == ch:
                        # Verbatim string
                        end_pos = pos + ord(next_byte) + 1
                        if end_pos > input_str_len:
                            raise ValueError('Invalid input to decompress - buffer overflow')
                        output.append(input_str[pos:end_pos])
                        pos = end_pos
            # This may look a bit clunky, but it is worth 20% in cPython and O(n^2)->O(n) in PyPy
            output = "".join(output)
            if check_ascii and not _check_ascii(output):
                raise ValueError('Invalid input to decompress - non-ascii byte payload')
        except (IndexError, ValueError) as e:
            if raise_on_error:
                raise ValueError(str(e))
            else:
                return None
        return output
