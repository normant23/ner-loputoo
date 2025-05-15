#
#   Sõnestuse järelparandused Tartu Linnavolikogu protokollide töötlemiseks. 
#
#   Kasutab (Asutava Kogu Protokollide märgendamise) järelparandusi:
#   
#   * Initsiaaliga nimed (a la 'A. H. Tammsaare') liidetakse üheks sõneks, välja arvatud 
#     juhul, kui 1) initsiaal langeb kokku Rooma numbriga 'I', 'V' või 'X';
#                2) initsiaal langeb kokku tiitliga (Dr, Lb, Ln, Lw jne);
#   
#   * Ei liida üheks sõneks:
#        * punkti ja/või komaga eraldatud numbreid, kui alamosade vahel ei 
#          ole tühikuid (nt '67 123 , 456');
#        * Rooma numbritega kuud sisaldavaid kuupäevi ("dd. rooma_mm yyyy");
#        * kaldkriipsudega kuupäevi (formaat: "dd/mm/yy")
#        * lühendeid stiilis <suurtäht> + <numbrid>, nt: 'E 251';
#   
#   * Normaliseerib sõnad: teisendab kõikjal 'w' -> 'v' (nt 'tänawune jüripäew' -> 
#     'tänavune jüripäev');
#
#
#   Nõuded:
#   * python           3.9+
#   * estnltk          1.7.3+
#

import regex as re

from estnltk import Layer

from estnltk.taggers import TokenSplitter

from estnltk.taggers.standard.text_segmentation.patterns import MACROS
from estnltk.taggers.standard.text_segmentation.compound_token_tagger import ALL_1ST_LEVEL_PATTERNS
from estnltk.taggers.standard.text_segmentation.compound_token_tagger import CompoundTokenTagger

def make_adapted_cp_tagger(**kwargs):
    '''Creates an adapted CompoundTokenTagger that:
       1) exludes roman numerals from names with initials;
       2) does not join date-like token sequences as numbers;'''
    # 1) Exclude roman numerals I, V, X from initials from names starting with initials
    redefined_pat_1 = \
        { 'comment': '*) Names starting with 2 initials (exlude titles (Dr., Ln., Lv. etc) and roman numerals I, V, X from initials);',
          'pattern_type': 'name_with_initial',
          'example': 'A. H. Tammsaare',
          '_regex_pattern_': re.compile(r'''
                            (?!(Dr\.|Lb\.|Lh\.|Lm\.|Ln\.|Lv\.|Lw\.|Pr\.))     # exclude titles
                            ([ABCDEFGHJKLMNOPQRSTUWYZŠŽÕÄÖÜ][{LOWERCASE}]?)   # first initial
                            \s?\.\s?-?                                        # period (and hypen potentially)
                            ([ABCDEFGHJKLMNOPQRSTUWYZŠŽÕÄÖÜ][{LOWERCASE}]?)   # second initial
                            \s?\.\s?                                          # period
                            ((\.[{UPPERCASE}]\.)?[{UPPERCASE}][{LOWERCASE}]+) # last name
                            '''.format(**MACROS), re.X),
         '_group_': 0,
         '_priority_': (4, 1),
         'normalized': lambda m: re.sub('\1.\2. \3', '', m.group(0)),
         }

    redefined_pat_2 = \
       { 'comment': '*) Names starting with one initial (exlude roman numerals I, V, X from initials);',
         'pattern_type': 'name_with_initial',
         'example': 'A. Hein',
         '_regex_pattern_': re.compile(r'''
                            ([ABCDEFGHJKLMNOPQRSTUWYZŠŽÕÄÖÜ])   # first initial
                            \s?\.\s?                            # period
                            ([{UPPERCASE}][{LOWERCASE}]+        # last name
                            (?:-[{UPPERCASE}][{LOWERCASE}]+)?)  # include names with -
                            '''.format(**MACROS), re.X),
         '_group_': 0,
         '_priority_': (4, 2),
         'normalized': lambda m: re.sub('\1. \2', '', m.group(0)),
       }
    # 2) do not join date-like token sequences as numbers (correction for timex tagger)
    redefined_number_pat_1 = \
        { 'comment': '*) A generic pattern for detecting long numbers (1 group) (corrected for timex tagger).',
          'example': '12,456',
          'pattern_type': 'numeric',
          '_group_': 0,
          '_priority_': (2, 1, 5),
          '_regex_pattern_': re.compile(r'''                             
                             \d+           # 1 group of numbers
                             (,\d+|\ *\.)  # + comma-separated numbers or period-ending
                             ''', re.X),
          'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))" }

    redefined_number_pat_2 = \
       { 'comment': '*) A generic pattern for detecting long numbers (2 groups, point-separated, followed by comma-separated numbers) (corrected for timex tagger).',
          'example': '67.123,456',
          'pattern_type': 'numeric',
          '_group_': 0,
          '_priority_': (2, 1, 3, 1),
          '_regex_pattern_': re.compile(r'''
                             \d+\.+\d+   # 2 groups of numbers
                             (,\d+)      # + comma-separated numbers
                             ''', re.X),
          'normalized': r"lambda m: re.sub(r'[\s\.]' ,'' , m.group(0))" }
    # Update patterns
    new_1st_level_patterns = []
    for pat in ALL_1ST_LEVEL_PATTERNS:
        if pat['comment'] == '*) Abbreviations of type <uppercase letter> + <numbers>;':
            # Skip this pattern
            continue 
        if pat['comment'] == '*) Date patterns that contain month as a Roman numeral: "dd. roman_mm yyyy";':
            # Skip this pattern (keep 'dd', 'roman_mm', 'yyyy' as separate tokens)
            continue 
        if pat['comment'] == '*) Date patterns in the commonly used form "dd/mm/yy";':
            # Skip this pattern (keep 'dd', 'mm', 'yy' as separate tokens)
            continue 
        if pat['comment'] == '*) Names starting with 2 initials;':
            # Replace this pattern
            new_1st_level_patterns.append( redefined_pat_1 )
        elif pat['comment'] == '*) Names starting with one initial;':
            # Replace this pattern
            new_1st_level_patterns.append( redefined_pat_2 )
        elif pat['comment'] == '*) A generic pattern for detecting long numbers (1 group).':
            new_1st_level_patterns.append( redefined_number_pat_1 )
        elif pat['comment'] == '*) A generic pattern for detecting long numbers (2 groups, point-separated, followed by comma-separated numbers).':
            new_1st_level_patterns.append( redefined_number_pat_2 )
        else:
            new_1st_level_patterns.append( pat )
    assert len(new_1st_level_patterns)+3 == len(ALL_1ST_LEVEL_PATTERNS)
    if kwargs is not None:
        assert 'patterns_1' not in kwargs.keys(), "(!) Cannot overwrite 'patterns_1' in adapted CompoundTokenTagger."
    return CompoundTokenTagger( patterns_1=new_1st_level_patterns, do_not_join_on_strings = ('\n\n', '\n'), **kwargs )

adapted_cp_tokens_tagger = make_adapted_cp_tagger(input_tokens_layer='tokens',
                                                  output_layer='compound_tokens')

def preprocess_words( input_text ):
    '''Pre-processes given Text object: adds word segmentation layers.
       Normalizes words (w -> v).
    '''
    input_text.tag_layer('tokens')
    token_splitter = TokenSplitter(patterns=[re.compile(r'(?P<end>esitatakse)Linnavolikogule'), re.compile(r'(?P<end>Tamme)linnaosamaa')])
    token_splitter.retag( input_text )
    token_splitter2 = TokenSplitter(patterns=[re.compile(r'(?P<end>linnaosa)maa')])
    token_splitter2.retag( input_text )
    adapted_cp_tokens_tagger.tag( input_text )
    input_text.tag_layer('words')
    for word_span in input_text['words']:
        word_text = word_span.text
        if 'w' in word_text.lower():
            word_span.clear_annotations()
            word_norm = word_text.replace('w', 'v')
            word_norm = word_norm.replace('W', 'V')
            word_span.add_annotation( normalized_form=word_norm )
    return input_text


def _get_preprocessed_words( input_str ):
    '''Applies preprocess_words() on given input_str and returns obtained words layer tokenization.'''
    from estnltk import Text
    text_obj = Text(input_str)
    text_obj = preprocess_words( text_obj )
    return [w.text for w in text_obj['words']]


# Validate tokenization: positions and titles (Ln/Pr/Lv/Ln/Lb/Dr) should be separated from the rest of the names
assert _get_preprocessed_words('Ln.W.Tamman, Pr. E.Tomson, Lv.J.Aavik , Ln.W.Tamman , Lb.J.Viik ja Dr.K.Pfaffi') == \
       ['Ln', '.', 'W.Tamman', ',', 'Pr.', 'E.Tomson', ',', 'Lv', '.', 'J.Aavik', ',', 'Ln', '.', 'W.Tamman', ',', \
        'Lb', '.', 'J.Viik', 'ja', 'Dr.', 'K.Pfaffi']