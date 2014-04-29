#!/usr/bin/env python
# coding=utf-8
"""
Unit tests for the Python port of SMAZ
Copyright (c) 2014 Max Smith except for portions of Moby Dick which are in the public domain
Public domain
"""

from unittest import TestCase
import bz2
import zlib
import datetime
import itertools
import random

from lib.smaz import compress, decompress, _encapsulate, DECODE, _check_ascii, make_tree, SMAZ_TREE, _worst_size, \
    _encapsulate_list, compress_no_backtracking, compress_classic


__author__ = "Max Smith"

try:
    # noinspection PyShadowingBuiltins
    xrange = range  # Fix for python 3 compatibility.
except NameError:
    pass

RUN_HEAVY_TESTS = True  # False = 2 to 3 seconds, True = 2 to 3 minutes

MOBYDICK_CHAPTER1 = """
Call me Ishmael. Some years ago--never mind how long precisely--having
little or no money in my purse, and nothing particular to interest me on
shore, I thought I would sail about a little and see the watery part of
the world. It is a way I have of driving off the spleen and regulating
the circulation. Whenever I find myself growing grim about the mouth;
whenever it is a damp, drizzly November in my soul; whenever I find
myself involuntarily pausing before coffin warehouses, and bringing up
the rear of every funeral I meet; and especially whenever my hypos get
such an upper hand of me, that it requires a strong moral principle to
prevent me from deliberately stepping into the street, and methodically
knocking people's hats off--then, I account it high time to get to sea
as soon as I can. This is my substitute for pistol and ball. With a
philosophical flourish Cato throws himself upon his sword; I quietly
take to the ship. There is nothing surprising in this. If they but knew
it, almost all men in their degree, some time or other, cherish very
nearly the same feelings towards the ocean with me.

There now is your insular city of the Manhattoes, belted round by
wharves as Indian isles by coral reefs--commerce surrounds it with
her surf. Right and left, the streets take you waterward. Its extreme
downtown is the battery, where that noble mole is washed by waves, and
cooled by breezes, which a few hours previous were out of sight of land.
Look at the crowds of water-gazers there.

Circumambulate the city of a dreamy Sabbath afternoon. Go from Corlears
Hook to Coenties Slip, and from thence, by Whitehall, northward. What
do you see?--Posted like silent sentinels all around the town, stand
thousands upon thousands of mortal men fixed in ocean reveries. Some
leaning against the spiles; some seated upon the pier-heads; some
looking over the bulwarks of ships from China; some high aloft in the
rigging, as if striving to get a still better seaward peep. But these
are all landsmen; of week days pent up in lath and plaster--tied to
counters, nailed to benches, clinched to desks. How then is this? Are
the green fields gone? What do they here?

But look! here come more crowds, pacing straight for the water, and
seemingly bound for a dive. Strange! Nothing will content them but the
extremest limit of the land; loitering under the shady lee of yonder
warehouses will not suffice. No. They must get just as nigh the water
as they possibly can without falling in. And there they stand--miles of
them--leagues. Inlanders all, they come from lanes and alleys, streets
and avenues--north, east, south, and west. Yet here they all unite.
Tell me, does the magnetic virtue of the needles of the compasses of all
those ships attract them thither?

Once more. Say you are in the country; in some high land of lakes. Take
almost any path you please, and ten to one it carries you down in a
dale, and leaves you there by a pool in the stream. There is magic
in it. Let the most absent-minded of men be plunged in his deepest
reveries--stand that man on his legs, set his feet a-going, and he will
infallibly lead you to water, if water there be in all that region.
Should you ever be athirst in the great American desert, try this
experiment, if your caravan happen to be supplied with a metaphysical
professor. Yes, as every one knows, meditation and water are wedded for
ever.

But here is an artist. He desires to paint you the dreamiest, shadiest,
quietest, most enchanting bit of romantic landscape in all the valley of
the Saco. What is the chief element he employs? There stand his trees,
each with a hollow trunk, as if a hermit and a crucifix were within; and
here sleeps his meadow, and there sleep his cattle; and up from yonder
cottage goes a sleepy smoke. Deep into distant woodlands winds a
mazy way, reaching to overlapping spurs of mountains bathed in their
hill-side blue. But though the picture lies thus tranced, and though
this pine-tree shakes down its sighs like leaves upon this shepherd's
head, yet all were vain, unless the shepherd's eye were fixed upon the
magic stream before him. Go visit the Prairies in June, when for scores
on scores of miles you wade knee-deep among Tiger-lilies--what is the
one charm wanting?--Water--there is not a drop of water there! Were
Niagara but a cataract of sand, would you travel your thousand miles to
see it? Why did the poor poet of Tennessee, upon suddenly receiving two
handfuls of silver, deliberate whether to buy him a coat, which he sadly
needed, or invest his money in a pedestrian trip to Rockaway Beach? Why
is almost every robust healthy boy with a robust healthy soul in him, at
some time or other crazy to go to sea? Why upon your first voyage as a
passenger, did you yourself feel such a mystical vibration, when first
told that you and your ship were now out of sight of land? Why did the
old Persians hold the sea holy? Why did the Greeks give it a separate
deity, and own brother of Jove? Surely all this is not without meaning.
And still deeper the meaning of that story of Narcissus, who because
he could not grasp the tormenting, mild image he saw in the fountain,
plunged into it and was drowned. But that same image, we ourselves see
in all rivers and oceans. It is the image of the ungraspable phantom of
life; and this is the key to it all.

Now, when I say that I am in the habit of going to sea whenever I begin
to grow hazy about the eyes, and begin to be over conscious of my lungs,
I do not mean to have it inferred that I ever go to sea as a passenger.
For to go as a passenger you must needs have a purse, and a purse is
but a rag unless you have something in it. Besides, passengers get
sea-sick--grow quarrelsome--don't sleep of nights--do not enjoy
themselves much, as a general thing;--no, I never go as a passenger;
nor, though I am something of a salt, do I ever go to sea as a
Commodore, or a Captain, or a Cook. I abandon the glory and distinction
of such offices to those who like them. For my part, I abominate all
honourable respectable toils, trials, and tribulations of every kind
whatsoever. It is quite as much as I can do to take care of myself,
without taking care of ships, barques, brigs, schooners, and what not.
And as for going as cook,--though I confess there is considerable glory
in that, a cook being a sort of officer on ship-board--yet, somehow,
I never fancied broiling fowls;--though once broiled, judiciously
buttered, and judgmatically salted and peppered, there is no one who
will speak more respectfully, not to say reverentially, of a broiled
fowl than I will. It is out of the idolatrous dotings of the old
Egyptians upon broiled ibis and roasted river horse, that you see the
mummies of those creatures in their huge bake-houses the pyramids.

No, when I go to sea, I go as a simple sailor, right before the mast,
plumb down into the forecastle, aloft there to the royal mast-head.
True, they rather order me about some, and make me jump from spar to
spar, like a grasshopper in a May meadow. And at first, this sort
of thing is unpleasant enough. It touches one's sense of honour,
particularly if you come of an old established family in the land, the
Van Rensselaers, or Randolphs, or Hardicanutes. And more than all,
if just previous to putting your hand into the tar-pot, you have been
lording it as a country schoolmaster, making the tallest boys stand
in awe of you. The transition is a keen one, I assure you, from a
schoolmaster to a sailor, and requires a strong decoction of Seneca and
the Stoics to enable you to grin and bear it. But even this wears off in
time.

What of it, if some old hunks of a sea-captain orders me to get a broom
and sweep down the decks? What does that indignity amount to, weighed,
I mean, in the scales of the New Testament? Do you think the archangel
Gabriel thinks anything the less of me, because I promptly and
respectfully obey that old hunks in that particular instance? Who ain't
a slave? Tell me that. Well, then, however the old sea-captains may
order me about--however they may thump and punch me about, I have the
satisfaction of knowing that it is all right; that everybody else is
one way or other served in much the same way--either in a physical
or metaphysical point of view, that is; and so the universal thump is
passed round, and all hands should rub each other's shoulder-blades, and
be content.

Again, I always go to sea as a sailor, because they make a point of
paying me for my trouble, whereas they never pay passengers a single
penny that I ever heard of. On the contrary, passengers themselves must
pay. And there is all the difference in the world between paying
and being paid. The act of paying is perhaps the most uncomfortable
infliction that the two orchard thieves entailed upon us. But BEING
PAID,--what will compare with it? The urbane activity with which a man
receives money is really marvellous, considering that we so earnestly
believe money to be the root of all earthly ills, and that on no account
can a monied man enter heaven. Ah! how cheerfully we consign ourselves
to perdition!

Finally, I always go to sea as a sailor, because of the wholesome
exercise and pure air of the fore-castle deck. For as in this world,
head winds are far more prevalent than winds from astern (that is,
if you never violate the Pythagorean maxim), so for the most part the
Commodore on the quarter-deck gets his atmosphere at second hand from
the sailors on the forecastle. He thinks he breathes it first; but not
so. In much the same way do the commonalty lead their leaders in many
other things, at the same time that the leaders little suspect it.
But wherefore it was that after having repeatedly smelt the sea as a
merchant sailor, I should now take it into my head to go on a whaling
voyage; this the invisible police officer of the Fates, who has the
constant surveillance of me, and secretly dogs me, and influences me
in some unaccountable way--he can better answer than any one else. And,
doubtless, my going on this whaling voyage, formed part of the grand
programme of Providence that was drawn up a long time ago. It came in as
a sort of brief interlude and solo between more extensive performances.
I take it that this part of the bill must have run something like this:


"GRAND CONTESTED ELECTION FOR THE PRESIDENCY OF THE UNITED STATES.

"WHALING VOYAGE BY ONE ISHMAEL.

"BLOODY BATTLE IN AFFGHANISTAN."


Though I cannot tell why it was exactly that those stage managers, the
Fates, put me down for this shabby part of a whaling voyage, when others
were set down for magnificent parts in high tragedies, and short and
easy parts in genteel comedies, and jolly parts in farces--though
I cannot tell why this was exactly; yet, now that I recall all the
circumstances, I think I can see a little into the springs and motives
which being cunningly presented to me under various disguises, induced
me to set about performing the part I did, besides cajoling me into the
delusion that it was a choice resulting from my own unbiased freewill
and discriminating judgment.

Chief among these motives was the overwhelming idea of the great
whale himself. Such a portentous and mysterious monster roused all my
curiosity. Then the wild and distant seas where he rolled his island
bulk; the undeliverable, nameless perils of the whale; these, with all
the attending marvels of a thousand Patagonian sights and sounds, helped
to sway me to my wish. With other men, perhaps, such things would not
have been inducements; but as for me, I am tormented with an everlasting
itch for things remote. I love to sail forbidden seas, and land on
barbarous coasts. Not ignoring what is good, I am quick to perceive a
horror, and could still be social with it--would they let me--since it
is but well to be on friendly terms with all the inmates of the place
one lodges in.

By reason of these things, then, the whaling voyage was welcome; the
great flood-gates of the wonder-world swung open, and in the wild
conceits that swayed me to my purpose, two and two there floated into
my inmost soul, endless processions of the whale, and, mid most of them
all, one grand hooded phantom, like a snow hill in the air.
"""

MOBYDICK_PARAGRAPH1 = MOBYDICK_CHAPTER1[0:1111]

FIVE_MEGABYTES_OF_MOBY_DICK = MOBYDICK_CHAPTER1 * 429

TEST_DATA_LIST = (
    "This is a small string",
    "foobar",
    "the end",
    "not-a-g00d-Exampl333",
    "Smaz is a simple compression library",
    "Nothing is more difficult, and therefore more precious, than to be able to decide",
    "this is an example of what works very well with smaz",
    "1000 numbers 2000 will 10 20 30 compress very little",
    "and now a few italian sentences:",
    "Nel mezzo del cammin di nostra vita, mi ritrovai in una selva oscura",
    "Mi illumino di immenso",
    "L'autore di questa libreria vive in Sicilia",
    "try it against urls",
    "http://google.com",
    "http://programming.reddit.com",
    "http://github.com/antirez/smaz/tree/master",
    "/media/hdb1/music/Alben/The Bla",
    '\n',
    None,
    '',
    '1',
    '12',
    '123',
    '1234',
    '12345',
    '123456',
    '1234567',
    '12345678',
    '123456789',
    '1234567890',
    '12345678901',
    '123456789012',
    '1234567890123',
    '12345678901234',
    '123456789012345',
    '1234567890123456',
    '12345678901234567',
    '123456789012345678',
    '1234567890123456789',
    '12345678901234567891',
    '123456789012345678912',
    '1234567890123456789123',
    '12345678901234567891234',
    '123456789012345678912345',
    '1234567890123456789123456',
    '12345678901234567891234567',
    '123456789012345678912345670',
    '1' * 1000,
    '1' * 256,
    '1' * 255,
    '1' * 257,
    'a',
    'aa',
    'the',
    'which',
    'thewhich',
    'the which',
    'the which ',
    'abc',
    '111',
    '1111111',
    '111111111',
    '1111111111',
    't@',  # Pathological cases
    't@t@',
    't@t@t@',
    't@t@t@t@',
    't@t@t@t@t@',
    't@t@t@t@t@t@t@',
    't@' * 127,
    't@' * 128,
    't@' * 129,
    't@' * 141,
    't@' * 1026,
)


def heavytest(test_func):
    '''Tag tests that take too long to run for quick regression'''
    def heavytest_deco(self):
        if RUN_HEAVY_TESTS:
            test_func(self)
        else:
            print('Skipping @heavytest %s' % test_func.__name__)
    return heavytest_deco

class TestSmaz(TestCase):
    def timedelta_to_float(self, td):
        """ Return a floating point value in seconds for the timedelta """
        return float(td.seconds) + float(td.microseconds) / 1000000.

    def cycle(self, input_str, quiet=False, compress_tree=None, decompress_table=None, show_input_and_output=True,
              strict=True):
        """ Exercise a complete co -> dec cycle """
        compressed_text = compress(input_str, compression_tree=compress_tree, backtracking=False,
                                   check_ascii=strict)
        backtracked_compressed_text = compress(input_str, compression_tree=compress_tree, backtracking=True,
                                               check_ascii=strict)
        decompressed_text = decompress(compressed_text, decompress_table=decompress_table)
        backtracked_decompressed_text = decompress(backtracked_compressed_text, decompress_table=decompress_table)
        classic_compresssed_text = compress_classic(input_str)
        classic_decompressed_test = decompress(classic_compresssed_text)

        if not quiet and input_str:
            print('---------------------------------------------------------------------')
            if show_input_and_output:
                print(decompressed_text)
                print(compressed_text)
            if backtracked_compressed_text != compressed_text:
                if show_input_and_output:
                    print('--back tracked:--')
                    print(backtracked_compressed_text)
            ratio = 1.0 / (float(len(input_str)) / float(len(compressed_text)))
            b_ratio = 1.0 / (float(len(input_str)) / float(len(backtracked_compressed_text)))
            c_ratio = 1.0 / (float(len(input_str)) / float(len(classic_compresssed_text)))
            bz2c = bz2.compress(input_str)
            zlibc = zlib.compress(input_str, 9)
            bz2ratio = 1.0 / (float(len(input_str)) / float(len(bz2c)))
            zlibratio = 1.0 / (float(len(input_str)) / float(len(zlibc)))
            if backtracked_compressed_text != compressed_text:
                print('backtracked compression ratio 1:%f (%.2f%%) from %d bytes to %d bytes' %
                      (b_ratio, b_ratio * 100., len(input_str), len(backtracked_compressed_text)))
                self.assertTrue(len(compressed_text) >= len(backtracked_compressed_text),
                                'Back-tracking (%d) should always be better than not-backtracking (%d)'
                                % (len(input_str), len(backtracked_compressed_text)))
            print('compression ratio 1:%f (%.2f%%) from %d bytes to %d bytes' %
                  (ratio, ratio * 100., len(input_str), len(compressed_text)))
            print(' vs ')
            print('  zlib ratio 1:%f (%.2f%%) to %d bytes' %
                  (zlibratio, zlibratio * 100., len(zlibc)))
            print('  bz2 ratio 1:%f (%.2f%%) to %d bytes' %
                  (bz2ratio, bz2ratio * 100., len(bz2c)))
            print('  smaz classic 1:%f (%.2f%%) to %d bytes' %
                  (c_ratio, c_ratio * 100., len(classic_compresssed_text)))

        self.assertEqual(input_str, decompressed_text)
        self.assertEqual(input_str, backtracked_decompressed_text)
        self.assertEqual(input_str, classic_decompressed_test)

    def test_backtracking(self):
        """ These are torture tests for the back tracking logic, in particular off by one type errors """
        self.cycle('1000 numbers 2000 will 10 20 30 compress very little')
        self.cycle('1000 numbers 2000 will 102030 compress very little')
        self.cycle('GRAND CONTESTED ELECTION FOR THE PRESIDENCY OF THE UNITED STATES.')
        self.cycle('t@')
        self.cycle(('@' * 200 + ' ') * 10)
        self.cycle(('@' * 200 + '  ') * 10)
        self.cycle(('@' * 200 + '   ') * 10)
        self.cycle(('@' * 200 + '   @') * 10)
        self.cycle((('@' * 200 + '   ') * 10) + ' @')
        self.cycle((('@' * 200 + '   ') * 10) + ' @ @')
        self.cycle((('@' * 200 + '   ') * 10) + ' @ @ @')
        self.cycle('not-a-g00d-Exampl333')
        self.cycle("p<7l")
        self.cycle(" !p")
        self.cycle('7nqd')
        self.cycle('#e]4z')
        self.cycle(" *A'Rt")


    def test_worstsize(self):
        testcases = ['@' * i for i in xrange(0, 5000)]
        for test in testcases:
            self.assertEqual(len(_encapsulate(test)), _worst_size(len(test)))
            self.assertEqual(test, decompress(_encapsulate(test)))  # Sanity checks
            self.assertEqual(test, decompress("".join(_encapsulate_list(list(test)))))

    def test_compress(self):
        """ A series of basic tests, asserting that the string isn't a mess """
        methods = (
            (None, None),  # i.e. SMAZ
        )

        for tree, table in methods:
            for test in TEST_DATA_LIST:
                self.cycle(test, compress_tree=tree, decompress_table=table)

    def test_encapsulate(self):
        """ Test the encapsulation method """
        for test in TEST_DATA_LIST:
            self.assertEqual(test, decompress(_encapsulate(test)))
            if test:
                self.assertEqual(test, decompress("".join(_encapsulate_list(list(test)))))

    def test_expected_compression_results(self):
        """ This test asserts some expected behavior in terms out compressed output, if you change the compression
            algorithm (or decoding table) this will change. """
        self.assertEqual(len(compress('thethethe')), 3)
        self.assertEqual(len(compress('thewhich')), 2)
        self.assertEqual(len(compress('123thewhich123')), 12)
        self.assertEqual(len(compress('not-a-g00d-Exampl333')), 20)

    def test_mobydick(self):
        """ Test the first paragraph, and the full first chapter. """
        self.cycle(MOBYDICK_PARAGRAPH1)
        self.cycle(MOBYDICK_CHAPTER1)

    @heavytest
    def test_scaling(self):
        """ Test (but don't assert) that SMAZ scales linearly with string length - i.e. O(N) """
        print('factor should remain roughly constant if performance is O(N)')
        for i in (1, 5, 10, 20, 50, 100, 250, 500, 1000, 2500, 10000, 100000):
            runs = 1
            if i < 10000:
                runs = 100
                if i < 500:
                    runs = 1000

            tick = datetime.datetime.now()
            cdata = [compress(FIVE_MEGABYTES_OF_MOBY_DICK[0:i]) for _ in xrange(runs)]
            tock = datetime.datetime.now()
            tdf = self.timedelta_to_float(tock - tick)
            print('%i, %f, factor: %.10f - %d' % (i, tdf, tdf / (float(i) * float(runs)), len(cdata)))

    def test_onlycompressable(self):
        self.cycle("".join(DECODE))  # All the perfectly compressible words

    @heavytest
    def test_randomtext(self):
        """ Test a large block of random text (1mb), then walk through it testing sub-strings of
        length 1 to 64 characters. Basically fuzzing the compression algo, found a couple of interesting
        bugs here around backtracking here."""
        ascii_chars = [chr(i) for i in xrange(127)]
        offset_range = 1024
        mega = 2 ** 20
        randomtext = "".join(random.choice(ascii_chars) for _ in xrange(mega + offset_range))

        try:
            ## Test a megabyte of random text
            test_string = randomtext
            self.cycle(randomtext, quiet=True)

            for i in xrange(64):
                for j in xrange(offset_range):
                    test_string = randomtext[j:j + i]
                    self.cycle(test_string, quiet=True)
        except ValueError as e:
            print('Broken string:%s' % test_string)
            print('Error: %s' % str(e))
            raise

    def test_ascii(self):
        """ By default, we check we are only processing ascii data"""
        self.assertRaises(ValueError, compress, chr(129))
        for i in xrange(127):
            compress(chr(i))  # Doesn't raise - valid data

    @heavytest
    def test_random_invalid_input(self):
        """ Test we don't go off the rails with a large random input """
        allbytes = [chr(i) for i in xrange(255)]
        randominput = "".join(random.choice(allbytes) for _ in xrange(10000))  # 10kb of random bytes
        for i in xrange(2048):
            decompress(randominput[i:i + 4096], raise_on_error=False)  # Walk through the 4k of the range

    def test_specific_bad_data(self):
        """ A few implict error/edge cases in the SMAZ algorithm """
        buffer_overflow = chr(255) + chr(255)  # Buffer overflow - expects 254 bytes, gets 0
        multibyte_non_ascii = chr(255) + chr(1) + chr(200) + chr(200)  # Non ascii multi-byte payload
        singlebyte_non_ascii = chr(254) + chr(129)  # Non ascii single-byte payload

        self.assertFalse(_check_ascii(multibyte_non_ascii))
        self.assertEqual(decompress(buffer_overflow, raise_on_error=False), None)
        self.assertRaises(ValueError, decompress, buffer_overflow, raise_on_error=True)
        self.assertEqual(decompress(multibyte_non_ascii), (chr(200) + chr(200)))  # Returns non-ascii data
        self.assertRaises(ValueError, decompress, multibyte_non_ascii, raise_on_error=True, check_ascii=True)
        self.assertEqual(decompress(multibyte_non_ascii, raise_on_error=False, check_ascii=True), None)
        self.assertEqual(decompress(singlebyte_non_ascii), chr(129))  # Returns non-ascii data
        self.assertRaises(ValueError, decompress, singlebyte_non_ascii, raise_on_error=True, check_ascii=True)
        self.assertEqual(decompress(singlebyte_non_ascii, raise_on_error=False, check_ascii=True), None)

    def test_ascii_check(self):
        """ Test the ascii check """
        self.assertTrue(_check_ascii('1230ABCZADSADW'))
        self.assertFalse(_check_ascii(chr(129) + chr(129)))
        self.assertEquals(None, compress(chr(129), raise_on_error=False))

    def test_make_tree(self):
        """ Test the tree building function. A bit weak """
        self.assertEqual(make_tree(DECODE), SMAZ_TREE)  # A bit weak
        self.assertRaises(ValueError, make_tree, None)
        self.assertRaises(ValueError, make_tree, [])
        self.assertRaises(ValueError, make_tree, ['b', 'b'])
        self.assertRaises(ValueError, make_tree, ['%d' % i for i in xrange(257)])

    def test_quick_string_check(self):
        """ A quick performant sanity check of strings """
        self.performance_string(MOBYDICK_CHAPTER1, 200, 1, 100, 2)

    @heavytest
    def test_very_very_small_strings(self):
        """ Test strings varying in length from 1 to 10 chars from MOBY DICK. All safely inside L1 cache"""
        self.performance_string(MOBYDICK_CHAPTER1, 20000, 1, 10, 1)

    @heavytest
    def test_very_small_strings(self):
        """ Test strings varying in length from 3 to 20 chars from MOBY DICK. All safely inside L1 cache"""
        self.performance_string(MOBYDICK_CHAPTER1, 10000, 3, 20, 1)

    @heavytest
    def test_small_strings(self):
        """ Test strings varying in length from 20 to 100 chars from MOBY DICK. All safely inside L1 cache"""
        self.performance_string(MOBYDICK_CHAPTER1, 900, 20, 100, 3)

    @heavytest
    def test_medium_strings(self):
        """ Test strings of length 100k from MOBY DICK. Blows L1 cache """
        self.performance_string(FIVE_MEGABYTES_OF_MOBY_DICK, 100, 100000, 100010, 1000)

    @heavytest
    def test_very_large_string(self):
        """ This should safely break any cosy L1 and L2 cache dependencies"""
        self.performance_string(FIVE_MEGABYTES_OF_MOBY_DICK, 1, len(FIVE_MEGABYTES_OF_MOBY_DICK),
                                len(FIVE_MEGABYTES_OF_MOBY_DICK) + 1, 2)

    def performance_string(self, sourcetext, maxdepth, minsize, maxsize, step):
        """ Measure the codec performance on a range of strings from sourcetext, testing at maxdepth places from a
            minimum string size of minsize to a maximum size of maxsize in steps of step.
        """
        test_data = [sourcetext[startpos:startpos + offset] for startpos in xrange(0, maxdepth) for offset in
                     xrange(minsize, maxsize, step)]
        total_len = float(sum(len(x) for x in test_data)) / (2.0 ** 20)
        print(
            '-------------------------- Strings of size: %d to %d --------------------------' % (minsize, maxsize - 1))
        print('Total data size: %f megabytes in %d strings' % (total_len, len(test_data)))
        methods = ((bz2.compress, bz2.decompress, 'bz2'),
                   (zlib.compress, zlib.decompress, 'zlib'),
                   (compress, decompress, 'smaz'),
                   (compress_classic, decompress, 'smaz-classic'),
                   (compress_no_backtracking, decompress, 'smaz-no-backtracking'))
        for c_func, d_func, name in methods:
            tick = datetime.datetime.now()
            c_data = [c_func(data) for data in test_data]
            mid_tock = datetime.datetime.now()
            d_data = [d_func(data) for data in c_data]
            end_tick = datetime.datetime.now()

            dc_time = self.timedelta_to_float(end_tick - mid_tock)
            c_time = self.timedelta_to_float(mid_tock - tick)
            for input, output in zip(test_data, d_data):
                self.assertEqual(input, output)

            c_throughput = total_len / c_time
            dc_throughput = total_len / dc_time
            print('------------------------------- %s ---------------------------------' % name)
            print('Compression time = %f, throughput = %f megabytes/sec' % (c_time, c_throughput))
            print('Decompression time = %f, throughput = %f megabytes/sec' % (dc_time, dc_throughput))
            print('Size uncompressed = %d vs %d' % (sum(len(x) for x in test_data), sum(len(x) for x in c_data)))

    def assert_smaz_optimal(self, comb, display=False):
        """ Assert that SMAZ is optimal for a given string, setting display shows the output """
        if display:
            print(comb)
        smaz_comp = bz2_comp = zlib_comp = 0
        try:
            bz2_comp = bz2.compress(comb)
            zlib_comp = zlib.compress(comb, 9)
            smaz_comp = compress(comb)
            self.assertTrue(len(bz2_comp) >= len(smaz_comp))
            self.assertTrue(len(zlib_comp) >= len(smaz_comp))
        except AssertionError:
            raise AssertionError(
                'Found String (%d) where SMAZ not >=. SMAZ len: %d bz2 len: %d zlib len: %d string: %s' %
                (len(comb), len(smaz_comp), len(bz2_comp), len(zlib_comp), comb))

    def prove_optimal_for_string_length(self, n, display=False):
        """ This test will prove (through sheer brute force) that smaz is better than zlib or bz2 for strings of less
            than length n.

            To do this we will make a couple of assumptions - testing 2^(n*7) different strings isn't really going
            to be possible in a unit test.

            We will assume there are only two options, a character we've already seen, and a new character. This brings
            the number of tests down to a much more manageable level.

            We also need to explore the combination of code-book value and non-code-book values. But where we match a
            single SMAZ code-book value in a short string, the odds of zlib or bz2 beating SMAZ are basically none,
            the more limited entropy strings are where they have the advantage, and this is fully exercised. """

        print('Testing length %d' % n)
        count = 0
        all_combinations = itertools.combinations_with_replacement((chr(i + 48) for i in xrange(n)), n)
        for ccomb in all_combinations:
            count += 1
            comb = "".join(ccomb)
            self.assert_smaz_optimal(comb)

        extra_testcases = [
            '@' * n,
            't@' * (n / 2),
            chr(0) * n,
            ' ' * n,
        ]
        for i in xrange(253):
            extra_testcases.append(('' + DECODE[i] + '@') * (n / 2))  # Blend of code-book, and non-code-book values
            extra_testcases.append(('@' + DECODE[i]) * (n / 2))

        for i in xrange(127):
            extra_testcases.append(chr(i) * n)

        for testcase in extra_testcases:
            count += 1
            self.assert_smaz_optimal(testcase, display=display)

        print('Tested %d combinations, SMAZ is optimal for length %d' % (count, n))

    @heavytest
    def test_prove_optimal(self):
        """ Prove that SMAZ is optimal (vs bz2 and zlib) for very small strings """
        for i in xrange(1, 10):
            self.prove_optimal_for_string_length(i)

    def find_shortest_substring_in_where_smaz_is_not_best(self, testtext, startat=0, vary_startingpos=True,
                                                          display_string=True):
        """ Find the first shortest substring in chapter one of mobydick where SMAZ is not the best compressor (or
            equal best).
        """
        textstringlen = len(testtext)
        llen = 0
        try:
            for llen in xrange(startat, textstringlen):
                starting_range = xrange(0, textstringlen - llen) if vary_startingpos else (0,)
                for startpos in starting_range:
                    teststring = testtext[startpos:startpos + llen]
                    self.assert_smaz_optimal(teststring)
            self.assertTrue(False)  # Should never reach here unless something has gone very wrong
        except AssertionError as e:
            if display_string:
                print('Shortest string that SMAZ is sub-optimal for %d' % llen)
            print(str(e))

    @heavytest
    def test_find_shortest_substring_in_mobydick_where_smaz_breaks(self):
        if RUN_HEAVY_TESTS:
            print('Checking first chapter of Moby Dick')
            self.find_shortest_substring_in_where_smaz_is_not_best(MOBYDICK_CHAPTER1)
            print('Checking first paragraph of Moby Dick')
            self.find_shortest_substring_in_where_smaz_is_not_best(MOBYDICK_PARAGRAPH1, startat=700,
                                                                   vary_startingpos=False)


    def test_the_canterbury_corpus(self):
        """ Exercise the ascii bits of the Canterbury Corpus - the lisp file is interesting. """
        test_files = ('alice29.txt', 'asyoulik.txt', 'cp.html', 'fields.c', 'grammar.lsp', 'lcet10.txt', 'plrabn12.txt')
        for test_file in test_files:
            with open('data/%s' % test_file,'r') as f:
                test_text = f.read()
                print('-------Starting Canterbury Corpus file: %s ----------------' % test_file)
                self.cycle(test_text, show_input_and_output=False, strict=False)
                self.find_shortest_substring_in_where_smaz_is_not_best(test_text, startat=30,
                                                                           vary_startingpos=False, display_string=False)
                print('-------Finished %s ----------------------------------------' % test_file)

    def test_the_act_corpus_text(self):
        """ from http://compression.ca/act/act-text.html by Jeff Gilchrist
            SMAZ doesn't really do very well here against entropy encoders (it would come last in the table).
            But it's the best for the first 484 bytes (vs zlib and bz2)"""

        test_files = ('1musk10.txt', 'anne11.txt', 'world95.txt')
        test_data = []
        print('-------Starting ACT test--------------')

        for test_file in test_files:
            with open('data/%s' % test_file,'r') as f:
                test_data.append(f.read())
        test_text = "".join(test_data)

        self.cycle(test_text, show_input_and_output=False, strict=False)
        self.find_shortest_substring_in_where_smaz_is_not_best(test_text, startat=30,
                                                               vary_startingpos=False, display_string=False)

    def test_the_national_university_of_singapore_sms_corpus(self):
        """ from http://wing.comp.nus.edu.sg:8080/SMSCorpus/overview.jsp
            slightly messed around with to remove anonymous <TOKENS> (John, 1234 put in their place)
            also remove a few Chinese messages that crept in. About 40k text messages. Mostly in English.
            Note: we are checking individual messages. bz2 and zlib would easily win if we ran against the entire file
        """
        self.corpus_line_by_line('data/sms_corpus-NUS.txt')

    def test_the_leeds_internet_corpus_english_urls(self):
        """ from http://corpus.leeds.ac.uk/internet.html, 40k urls """
        self.corpus_line_by_line('data/final-url-en.txt')

    def corpus_line_by_line(self, filename):
        """ Process a .txt corpus file line by line
        """
        with open(filename,'r') as f:
            lines = f.read()
        test_data = lines.split('\n')
        c_data = []
        bz_data = []
        zlib_data = []
        c_cl_data = []
        c_cl_path_data = []
        for test in test_data:
            c_data.append(compress(test))
            bz_data.append(bz2.compress(test))
            zlib_data.append(zlib.compress(test))
            c_cl_data.append(compress_classic(test,pathological_case_detection=False))
            c_cl_path_data.append(compress_classic(test,pathological_case_detection=True))

        print('Total data size %d bytes' % sum(len(x) for x in test_data))
        print(' Smaz size %d bytes' % sum(len(x) for x in c_data))
        print(' bz2 size %d bytes' % sum(len(x) for x in bz_data))
        print(' zlib size %d bytes' % sum(len(x) for x in zlib_data))
        print(' Smaz classic size %d bytes' % sum(len(x) for x in c_cl_data))
        print(' Smaz classic with pathological case detection size %d bytes' % sum(len(x) for x in c_cl_path_data))


