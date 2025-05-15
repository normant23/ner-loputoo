#
#   Lausestaja järelparandused Tartu Linnavolikogu protokollide töötlemiseks. 
#
#   Vaikimisi kasutatav lausestusmudel määrab liiga palju lauselõppe (punktiga
#   lõppevate lühendite järele). Paranduste eesmärk on liita kokku ekslikult 
#   "poolitatud" laused.
#
#   Nõuded:
#   * python           3.9+
#   * estnltk          1.7.3+
#

import regex as re
import warnings

from estnltk import Layer

from estnltk.taggers import SentenceTokenizer
from estnltk.taggers.standard.text_segmentation.sentence_tokenizer import merge_patterns

#==========================================================
#  Kellaajad ja kuupäevad
#==========================================================

kll_fix_1 = \
{ 'comment'  : '{p or e} {period} + {l} {period}', \
  'example'  : '"Järgmisel päewal kell 7 p." + "l."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?kell\s+([0-9/:,. ]+)(min.?)?\s*[pe]\.$', re.DOTALL), \
                 re.compile(r'^[l]\.(.*)$', re.DOTALL)], \
}
kll_fix_2 = \
{ 'comment'  : '{p. l or e. l} {period} + {lowercase letter}', \
  'example'  : '"Järgmisel päewal kell 7 p.l." + "kokku tulla"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?kell\s+([0-9/:,. ]+)(min.?)?\s*[pe]\.\s*[l]\.$', re.DOTALL), \
                 re.compile(r'^([a-zöäüõžš])\s*(.*)?$', re.DOTALL)], \
}
kll_fix_3 = \
{ 'comment'  : '{min} {period} + {p. l or e. l}', \
  'example'  : '"kell 6,20 min." + "p.l."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?kell\s+([0-9/:,. ]+)(min\.)$', re.DOTALL), \
                 re.compile(r'^\s*[pe]\.(.*)?$', re.DOTALL)], \
}

month_pattern_str = \
    r"(jaan|[vw]eeb|märts|apr|mai|juuni|juuli|aug|sept|okt|no[vw]|dets|det\ss)[a-z]*"

kll_fix_4 = \
{ 'comment'  : '{min} {period} + {number}', \
  'example'  : '"25.weebruaril k." + "24 p.l."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?'+month_pattern_str+r'\s*(k\.)$', re.DOTALL), \
                 re.compile(r'^[0-9]+(.*)?$', re.DOTALL)], \
}

kll_fix_5 = \
{ 'comment'  : '{p} {period} + {l.}', \
  'example'  : '"25.weebruaril k.24 p." + "l."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?'+month_pattern_str+r'\s*(k\.)\s*([0-9/:,. ]+)(min.?)?\s*[pe]\.$', re.DOTALL), \
                 re.compile(r'^[l]\.(.*)$', re.DOTALL)], \
}

kll_fix_6 = \
{ 'comment'  : '{k} {period} + {number}', \
  'example'  : '"päewal enne k." + "10 teatas"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?k\.$', re.DOTALL), \
                 re.compile(r'^\s*([0-9]+)(.*)?$', re.DOTALL)], \
}

day_fix_1 = \
{ 'comment'  : 'Fix for very specific broken date references', \
  'example'  : '"laup." + "- 18.ja pühapäewal..."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.*)laup\.\s*$', re.DOTALL), \
                 re.compile(r'^\s*-\s*([0-9]+)\.ja\s*pühapäewal(.*)?$', re.DOTALL)], \
}

month_fix_1 = \
{ 'comment'  : '{number} {month} {period} + {number or lowercase letter}', \
  'example'  : '"25 oktoobr." + "1920 a."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?([0-9]+\s*\.?)\s*'+month_pattern_str+r'\s*(\.)$', re.DOTALL), \
                 re.compile(r'^([0-9]|[a-zöäüõžš])(.*)?$', re.DOTALL) ], \
}

month_fix_2 = \
{ 'comment'  : '{number} {month} {period} + {dash} {number} {month} {period}', \
  'example'  : '"1. okt." + "- 31. dets."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.*)([0-9]+\.?)\s*'+month_pattern_str+r'\s*(\.)$', re.DOTALL), \
                 re.compile(r'^-+\s*([0-9]+\.?)\s*'+month_pattern_str+'(.*)?$', re.DOTALL) ], \
}

sa_fix_1 = \
{ 'comment'  : '{month} {"s"} {period} + {"a"} {period}', \
  'example'  : '"27. august.s." + "a."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.*)'+month_pattern_str+r'\s*(\.)?\s*s(\.)$', re.DOTALL), \
                 re.compile(r'^(a\.)\s*', re.DOTALL) ], \
}

#==========================================================
#  Lühendid:  j.n.e
#==========================================================

jne_fix_1 = \
{ 'comment'  : '{j} {period} + {n} {period} (+ {e} {period})', \
  'example'  : '"j." + "n." (+ "e.")', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?\s+j\.$', re.DOTALL), \
                 re.compile(r'^n\.(.*)$', re.DOTALL)], \
}

jne_fix_2 = \
{ 'comment'  : '{j} {period} {n} {period} + {e} {period}', \
  'example'  : '"j. n." + "e."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?\s+j\.\s*n\.$', re.DOTALL), \
                 re.compile(r'^e\.(.*)$', re.DOTALL)], \
}

jne_fix_3 = \
{ 'comment'  : '{j} {period} {n} {period} {e} {period} + {lowercase letter}', \
  'example'  : '"j. n. e." + "iga toru pealt."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?\s+j\.\s*n\.\s*e\.$', re.DOTALL), \
                 re.compile(r'^\s*([a-zöäüõžš])(.*)$', re.DOTALL)], \
}

#==========================================================
#  Lühendid:  uulits, tänav, kvartal
#==========================================================

uul_fix_1 = \
{ 'comment'  : '{uul} {period} + {Nr} {period}', \
  'example'  : '"Tolstoi uul." + "Nr.4,"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?([Uu]ul|tän|t)\.$', re.DOTALL), \
                 re.compile(r'^\s*Nr\.(.*)$', re.DOTALL)], \
}

uul_fix_2 = \
{ 'comment'  : '{uul} {period} + {number}', \
  'example'  : '"Võru uul.nr." + "59"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?([Uu]ul|tän|t)\.$', re.DOTALL), \
                 re.compile(r'^\s*([0-9]+)(.*)?$', re.DOTALL)], \
}

kvartal_fix_1 = \
{ 'comment'  : '{kvart} {period} + {roman_number}', \
  'example'  : '"kvart." + "V asuva krundi"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?(kvart|kv)\.$', re.DOTALL), \
                 re.compile(r'^\s*([IVXL]+)(.*)?$', re.DOTALL)], \
}

#=====================================================================
#  Lühendid:  isikute tiitlid või ametinimetused, sh linnavolinik
#=====================================================================

lwn_fix_1 = \
{ 'comment'  : '{lwn} {period} + {uppercase letter}', \
  'example'  : '"3) Lnw." + "Saint-Hilaire ettepanek"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(^|(.+)?\s+)[Ll](n[wv]?d?|[wv]d?)\.$', re.DOTALL), \
                 re.compile(r'^[A-ZÖÄÜÕŠŽ](.*)$', re.DOTALL)], \
}

TITLE_fix_1 = \
{ 'comment'  : '{TITLE} {period} + {uppercase letter}', \
  'example'  : '"walmistatud arh." + " Arno Matteuse poolt"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(^|(.+)?\s+)([Aa]rh|[Aa]d[vw]|[Aa]set|[Aa]suk|[Dd]r|[Ee]nd|[Hh]r|[Ii]ns|[Kk]apt|[Ll]in[wv]|[Ll]tn|[Ll][wv]ol|[Ll][wv]|[Pp]r|[Pp]rl|[Pp]rof|[Pp]rov|[Ss]urn|[WVwv]ol|[WVwv]an\s*\.[Aa]d[vw])\.$', re.DOTALL), \
                 re.compile(r'^\s*[A-ZÖÄÜÕŠŽ](.*)$', re.DOTALL)], \
}

specific_name_fix_1 = \
{ 'comment'  : 'Specific first name abbreviation (Ed|Fr|Kr|Aug|Joh|Chr|Aleks) followed by a family name', \
  'example'  : '"Linnapea abi Ed." + "Juhanson teatab"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(^|(.+)?\s+)(Ed|Fr|Kr|Aug|Joh|Chr|Aleks)\.$', re.DOTALL), \
                 re.compile(r'^\s*[A-ZÖÄÜÕŠŽ](.*)$', re.DOTALL)], \
}

specific_name_fix_2 = \
{ 'comment'  : 'Specific name that tends to get wrongly split: M.Kurs-Olesk', \
  'example'  : '"Ln.M." + "Kurs-Olesk"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(^|.+)(M)\.$', re.DOTALL), \
                 re.compile(r'^\s*(Krus[ea]?|Kursk?)-?Olesk(.*)$', re.DOTALL)], \
}

specific_name_fix_3 = \
{ 'comment'  : 'Specific name that tends to get wrongly split: A. Le-Coq (infrequent)', \
  'example'  : '"A." + "Le-Coq\'i palwe"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(^|.+)(A)\.$', re.DOTALL), \
                 re.compile(r'^\s*Le-Coq(.*)$', re.DOTALL)], \
}

son_daughter_fix = \
{ 'comment'  : '{titlecase_word} {"p" or "tr"} {period} + {titlecase_word}', \
  'example'  : '"Eduard Mardi p." + "Kenkmannile"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.*)[A-ZÖÄÜÕŠŽ][a-zöäüõžš\-]+\s+(p|tr)\.$', re.DOTALL), \
                 re.compile(r'^\s*[A-ZÖÄÜÕŠŽ][a-zöäüõžš](.*)$', re.DOTALL)], \
}

ex_fix_1 = \
{ 'comment'  : '{End} {period} + {some letter}', \
  'example'  : '"End." + " linnanõunikule J. Roo-le"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(^\s*)([Ee]nd)\.$', re.DOTALL), \
                 re.compile(r'^\s*[A-ZÖÄÜÕŠŽa-zöäüõšž](.*)$', re.DOTALL)], \
}

#==========================================================
#  Rahasummad
#==========================================================

rbl_fix = \
{ 'comment'  : '{rbl} {period} + {lowercase letter}', \
  'example'  : '"linna poolt 2000 rbl." + " abiraha määrata"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?\srbl\s*\.$', re.DOTALL), \
                 re.compile(r'^([a-zöäüõžš])\s*(.*)?$', re.DOTALL)], \
}

summa_fix_1 = \
{ 'comment'  : '{m} {period} + {lowercase letter or number}', \
  'example'  : '"summa 37.211 m." + "92 p."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?([0-9]+([,.][0-9]+)+|[0-9]+)\s*(m|[Mm]k|[Kk]r)\.$', re.DOTALL), \
                 re.compile(r'^\s*([0-9a-zöäüõžš])(.*)$', re.DOTALL)], \
}

summa_fix_2 = \
{ 'comment'  : '{mk} {period} + {number}', \
  'example'  : '"Rahaline seis: saada Mk." + "758.521.82,"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?\s(m|[Mm]k|[Kk]r)\.$', re.DOTALL), \
                 re.compile(r'^\s*([0-9]+([,.][0-9]+)+|[0-9]+)(.*)$', re.DOTALL)], \
}

summa_fix_3 = \
{ 'comment'  : '{p} {period} + {lowercase letter}', \
  'example'  : '"summa 37.211 m.92 p." + "maksis linnapäälik"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?([0-9]+)\s*(p|s)\.$', re.DOTALL), \
                 re.compile(r'^\s*([a-zöäüõžš])(.*)$', re.DOTALL)], \
}

#==========================================================
#  Muud ühikud
#==========================================================

yhik_fix_1 = \
{ 'comment'  : '{NK} {period} + {lowercase letter}', \
  'example'  : '"Üle 50 NK." + "lampide tarwitamise "', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?[0-9]+\s*(NK|V)\.$', re.DOTALL), \
                 re.compile(r'^\s*([a-zöäüõžš])(.*)$', re.DOTALL)], \
}

#==========================================================
#  Lühendid:  erakondade/rühmade nimetused
#==========================================================

party_abbr_fix_1 = \
{ 'comment'  : '{sots} {period} + {dash...}', \
  'example'  : '"lnw.L.Johanson sots." + "-\ndem. rühma nimel"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)(sots)\.$', re.DOTALL), \
                 re.compile(r'^-?\s*(dem|re[wv]|req|tööl|rühma|min|minist|demokr)\s*[\.\-](.*)$', re.DOTALL)], \
}

party_abbr_fix_2 = \
{ 'comment'  : 'Fix for specific broken party name references', \
  'example'  : '"rahwaer." + "- maj.-pöllu. rühmade nimel"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.*)(rahwaer)\.$', re.DOTALL), \
                 re.compile(r'^-?\s*(majand|maj)\s*[\.\-](.*)$', re.DOTALL)], \
}

#==========================================================
#  Lühendid:  firmade/organisatsioonide nimetused
#==========================================================

company_abbr_fix_1 = \
{ 'comment'  : 'Fix for company / shareholders group abbreviation', \
  'example'  : '"A.s." + "A.Le Coq\'i palve"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(^|(.+)?-|(.+)?\s+)[Aa][/.]s\.$', re.DOTALL), \
                 re.compile(r'^"?[A-ZÖÄÜÕŠŽ](.*)$', re.DOTALL)], \
}

company_abbr_fix_2 = \
{ 'comment'  : 'Fix for Company / shareholders group abbreviation', \
  'example'  : '"U/ü." + "M. A. Kamenovsky ja Pojad"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(^|(.+)?\s+)[OoUu][/.][ÜüUu]\.$', re.DOTALL), \
                 re.compile(r'^"?[A-ZÖÄÜÕŠŽ](.*)$', re.DOTALL)], \
}


#==========================================================
#  Lühendid:  päevakorrapunktid
#==========================================================

agenda_point_roman_fix_1 = \
{ 'comment'  : '{"pp"} {period} + {roman_number}', \
  'example'  : '"päevakorra pp." + "V, VI ja VII otsustamiseks"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(^|(.+)?\s+)(pp)\.$', re.DOTALL), \
                 re.compile(r'^\s*([IVXL]+)(.*)?$', re.DOTALL)], \
}


#==========================================================
#  Jäme parandus: kui punktile järgneb väiketäht, 
#  liida kokku
#==========================================================

ROUGH_FIX = \
{ 'comment'  : '{lowercase} {period} + {lowercase letter}', \
  'example'  : '"kell 10 hom." + "algab."', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?\s(([a-zöäüõžš\-]+)?[a-zöäüõžš]+\-?)\.$', re.DOTALL), \
                 re.compile(r'^\s*([a-zöäüõžš])(.*)$', re.DOTALL)], \
}

ROUGH_FIX_2 = \
{ 'comment'  : '{lowercase} {period} {lowercase} {period} + {lowercase letter}', \
  'example'  : '"II jaosk.riikl." + "kinniswarade hindamisekomisjon"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.+)?\s([a-zöäüõžš\-]+)\.([a-zöäüõžš]+\-?)\.$', re.DOTALL), \
                 re.compile(r'^\s*([a-zöäüõžš])(.*)$', re.DOTALL)], \
}

#==========================================================
#  Järgmine "lause" algab sulgude- ja väiketähega
#==========================================================

parenthesis_fix_1 = \
{ 'comment'  : 'Fix accidental sentence break before parenthesis', \
  'example'  : '"Anne uul.nr.26 as." + "(kinnistu nr.145)elumaja"', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.*)([a-zöäüõžš]+\-?)\.$', re.DOTALL), \
                 re.compile(r'^\s*\(\s*[a-zöäüõžš]+(.*)$', re.DOTALL)], \
}

#==========================================================
#  Spetsiifilised parandused
#  ( väga madala saagisega mustrid )
#==========================================================

tax_ref_fix_1 = \
{ 'comment'  : 'Fix for specific broken tax reference', \
  'example'  : '"... jooksul (w." + "Lõbustusmaksu muutm.sead.§ 3', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.*)\(w\.$', re.DOTALL), \
                 re.compile(r'^\s*Lõbustusmaksu(.*)$', re.DOTALL)], \
}

tax_ref_fix_2 = \
{ 'comment'  : 'Fix for specific broken tax reference', \
  'example'  : '"... R.T.nr.99-1926." + "/) otsustas: ...', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.*)R\.T\.nr\.99-1926\.$', re.DOTALL), \
                 re.compile(r'^\/\)\s*otsustas:(.*)$', re.DOTALL)], \
}

law_ref_fix_1 = \
{ 'comment'  : 'Fix for specific broken law reference', \
  'example'  : '"... § 36." + "Balti eriseadus III § 228).', \
  'fix_type' : 'abbrev_common', \
  'regexes'  : [ re.compile(r'(.*)§ 36\.$', re.DOTALL), \
                 re.compile(r'^\s*Balti\s*eriseadus(.*)$', re.DOTALL)], \
}


# Lisa uued parandused 
merge_patterns.append( kll_fix_1 )
merge_patterns.append( kll_fix_2 )
merge_patterns.append( kll_fix_3 )
merge_patterns.append( kll_fix_4 )
merge_patterns.append( kll_fix_5 )
merge_patterns.append( kll_fix_6 )
merge_patterns.append( day_fix_1 )
merge_patterns.append( month_fix_1 )
merge_patterns.append( month_fix_2 )
merge_patterns.append( sa_fix_1 )
merge_patterns.append( jne_fix_1 )
merge_patterns.append( jne_fix_2 )
merge_patterns.append( jne_fix_3 )
merge_patterns.append( lwn_fix_1 )
merge_patterns.append( uul_fix_1 )
merge_patterns.append( uul_fix_2 )
merge_patterns.append( kvartal_fix_1 )
merge_patterns.append( rbl_fix )
merge_patterns.append( summa_fix_1 )
merge_patterns.append( summa_fix_2 )
merge_patterns.append( summa_fix_3 )
merge_patterns.append( yhik_fix_1 )
merge_patterns.append( ROUGH_FIX )
merge_patterns.append( ROUGH_FIX_2 )
merge_patterns.append( parenthesis_fix_1 )
merge_patterns.append( TITLE_fix_1 )
merge_patterns.append( specific_name_fix_1 )
merge_patterns.append( specific_name_fix_2 )
merge_patterns.append( specific_name_fix_3 )
merge_patterns.append( son_daughter_fix )
merge_patterns.append( ex_fix_1 )
merge_patterns.append( party_abbr_fix_1 )
merge_patterns.append( party_abbr_fix_2 )
merge_patterns.append( company_abbr_fix_1 )
merge_patterns.append( company_abbr_fix_2 )
merge_patterns.append( agenda_point_roman_fix_1 )
merge_patterns.append( tax_ref_fix_1 )
merge_patterns.append( tax_ref_fix_2 )
merge_patterns.append( law_ref_fix_1 )

# Loo parandatud lausestaja
sentence_tokenizer = SentenceTokenizer(patterns = merge_patterns)


# =======================================================================
#   Ekslikult sulgude sisse lisatud lauselõppude parandamine
# =======================================================================

_parentheses_content = re.compile(r'(\([^()]+?\))')

def postfix_sentence_breaks_inside_parentheses( text: 'Text', sentences_layer:str='sentences', doc_name:str=None, debug_out:bool=False, validate:bool=True ):
    '''
    Ekslikult sulgude sisse lisatud lauselõppude parandamine.
    Põhineb osaliselt vastavate vigade tuvastamise heuristikul:
    https://github.com/estnltk/estnltk/blob/main/estnltk/estnltk/taggers/standard/text_segmentation/annotation_validation.py
    
    Kasutame lihtsat heuristikut: kui sulgudevaheline sisu on lühem kui 100 sümbolit, võib suure 
    tõenäosusega sulgude sees olevad lausekatkestused kustutada ja laused kokku liita.
    
    Näited parandatud lauselõppudest:

    *) "Tartu I Gümnaasiumi (Poegl."
       "gümnaas."
       ") hoone juurde- ja\nümberehitustööde jatkamiseks"
       ==>  
       "Tartu I Gümnaasiumi (Poegl. gümnaas.) hoone juurde- ja\nümberehitustööde jatkamiseks"  

    *) "otsus 20. juunist 1932 (prot."
       "p."
       "XII) selles\nosas,"
       ==>  
       "otsus 20. juunist 1932 (prot. p. XII) selles\nosas,", 

    *) "Saksa keskkool - 5-klassiline - 1 haru (dir."
       "K.Zeddelmann) - linna ülal\npidada."
       ==>  
       "Saksa keskkool - 5-klassiline - 1 haru (dir. K.Zeddelmann) - linna ülal\npidada."

    *) "(Lwol."
       "'ots."
       "15.000,- P.1."
       "Ujula ehitamiseks."
       "28/I.29."
       ")"
       ==>  
       "(Lwol.'ots.15.000,- P.1.Ujula ehitamiseks.28/I.29.)"

    *) "Maks laewade ja parkade seisu eest (Sisemin."
       "poolt 8. weebr.\n1900 a. Nr. 816 kinnit. määruste pöhjal) - laewadelt 100 m. ööpäewa\nkohta"
       ==>  
       "Maks laewade ja parkade seisu eest (Sisemin. poolt 8. weebr.\n1900 a. Nr. 816 kinnit. määruste pöhjal) ..."

    '''
    assert sentences_layer in text.layers
    # Check that none of the other layers depends on the sentences layer
    for layer in text.layers:
        if text[layer].parent == sentences_layer or text[layer].enveloping == sentences_layer:
            raise Exception(f'(!) Unexpected dependency between layers {sentences_layer} and '+\
                            f'{layer}: {sentences_layer} cannot be parent or enveloped layer '+\
                            f'of {layer}.')
    #
    # Check all consecutive pairs of parentheses, find sentence breaks inside such parentheses
    #
    all_joinable_sentences = []
    all_joinable_sentences_index = set()
    for matchobj in _parentheses_content.finditer(text.text):
        start = matchobj.span(1)[0]
        end   = matchobj.span(1)[1]
        # Check length limitation
        if end - start <= 100:
            # Collect sentences that are covered by parentheses
            joinable_sentences = []
            for sid, sentence in enumerate( text[sentences_layer] ):
                if sentence.start <= start and start < sentence.end and \
                   sentence.end < end:
                    # Start
                    joinable_sentences.append( sentence )
                elif start < sentence.start and sentence.end <= end:
                    # Midpoint
                    joinable_sentences.append( sentence )
                elif sentence.start <= end and end <= sentence.end:
                    # End
                    joinable_sentences.append( sentence )
                if sentence.start > end:
                    # No need to look further
                    break
            if len(joinable_sentences) > 1:
                # Check if we can merge consecutive sentences 
                extended = False
                if all_joinable_sentences:
                    last = all_joinable_sentences[-1][-1]
                    if last.start == joinable_sentences[0].start and \
                         last.end == joinable_sentences[0].end:
                        # Simply extend the last list of joinable sentences 
                        joinable_sentences.pop(0)
                        all_joinable_sentences[-1].extend(joinable_sentences)
                        extended = True
                if not extended:
                    # Add as a new list of joinable sentences 
                    all_joinable_sentences.append(joinable_sentences)
                # Update joinable sentences index
                for sent in joinable_sentences:
                    all_joinable_sentences_index.add( (sent.start, sent.end) )
    if validate:
        # Validate that the old sentences layer consumes all words in the text
        enveloped_layer = text[sentences_layer].enveloping
        word_count = 0
        for sid, sent in enumerate(text[sentences_layer]):
            word_count += len(sent)
        if word_count != len(text[enveloped_layer]):
            warnings.warn(f'\n(!) {doc_name}: OLD SENTENCES LAYER: Number of words covered by sentences ({word_count}) '+\
                          f'does not match number of words layer spans ({len(text[enveloped_layer])}).')
    #
    # Rewrite sentences layer: merge joinable sentences into one
    #
    if all_joinable_sentences:
        new_sentences_layer = Layer( name=text[sentences_layer].name,
            attributes=text[sentences_layer].attributes,
            secondary_attributes=text[sentences_layer].secondary_attributes,
            text_object=text[sentences_layer].text_object,
            parent=text[sentences_layer].parent,
            enveloping=text[sentences_layer].enveloping,
            ambiguous=text[sentences_layer].ambiguous,
            default_values=text[sentences_layer].default_values,
            serialisation_module=text[sentences_layer].serialisation_module)
        all_joined_sentences_index = set()
        for sid, sent in enumerate( text[sentences_layer] ):
            if (sent.start, sent.end) in all_joinable_sentences_index:
                if (sent.start, sent.end) not in all_joined_sentences_index:
                    # Find all sentences to be joined
                    for joinable_sentences in all_joinable_sentences:
                        start = joinable_sentences[0].start
                        end   = joinable_sentences[0].end
                        if (start, end) == (sent.start, sent.end):
                            new_base_span = []
                            for sent2 in joinable_sentences:
                                new_base_span.extend( sent2.base_span )
                            new_sentences_layer.add_annotation( base_span=new_base_span )
                            for sent2 in joinable_sentences:
                                all_joined_sentences_index.add( (sent2.start, sent2.end) )
                            if debug_out:
                                print(f'{doc_name}: DEBUG: Joining sentences: '+\
                                      f'{[s.enclosing_text for s in joinable_sentences]!r}.')
                            break
            else:
                new_sentences_layer.add_annotation( base_span=sent.base_span )
        if validate:
            # Validate that the new sentences layer consumes all words in the text
            enveloped_layer = text[sentences_layer].enveloping
            new_word_count = 0
            for sid, sent in enumerate(new_sentences_layer):
                new_word_count += len(sent)
            if new_word_count != len(text[enveloped_layer]):
                warnings.warn(f'\n(!) {doc_name}: NEW SENTENCES LAYER: Number of words covered by sentences ({new_word_count}) '+\
                              f'does not match number of words layer spans ({len(text[enveloped_layer])}).')

        text.pop_layer(sentences_layer)
        text.add_layer( new_sentences_layer )


def _get_preprocessed_sentences( input_str ):
    '''Applies modified sentence tokenization on the given input_str and returns obtained sentence texts (enclosing_texts).
       [for testing and debugging purposes]
    '''
    from estnltk import Text
    from words_tokenization import preprocess_words
    text_obj = Text(input_str)
    text_obj = preprocess_words( text_obj )
    sentence_tokenizer.tag( text_obj )
    postfix_sentence_breaks_inside_parentheses( text_obj, doc_name='', validate=True )
    return [s.enclosing_text for s in text_obj['sentences']]



# Validate sentence tokenization: fix street name abbreviations
assert _get_preprocessed_sentences('Kartuli t. Nr.6/8 asuwate maatüki ja hoonete ostmine linnale.') == \
                                  ['Kartuli t. Nr.6/8 asuwate maatüki ja hoonete ostmine linnale.']

assert _get_preprocessed_sentences('Meltsiweski tän.Nr.30,32 ja 34 asuwate linna majade ja krundi müümise küsimus.') == \
                                  ['Meltsiweski tän.Nr.30,32 ja 34 asuwate linna majade ja krundi müümise küsimus.']

# Validate sentence tokenization: 'end.' (ex./former) abbreviations
assert _get_preprocessed_sentences('End. Gildede waranduste linnale nöutamise küsimus.') == \
                                  ['End. Gildede waranduste linnale nöutamise küsimus.']

assert _get_preprocessed_sentences('End. gildide varadest saadud kapitalide kasustamise küsimus ja nende kapitalide määruste kinnitamine.') == \
                                  ['End. gildide varadest saadud kapitalide kasustamise küsimus ja nende kapitalide määruste kinnitamine.']

# Validate sentence tokenization: 'kvart.' (city block) abbreviations
assert _get_preprocessed_sentences('Tamme linnaosa kvart. V asuva krundi nr.8 tükeldamise küsimus.') == \
                                  ['Tamme linnaosa kvart. V asuva krundi nr.8 tükeldamise küsimus.']

assert _get_preprocessed_sentences('Tamme linnaosa ehituskrundi nr. 14 kvart.XXXV kaheks krundiks jaotamine') == \
                                  ['Tamme linnaosa ehituskrundi nr. 14 kvart.XXXV kaheks krundiks jaotamine']

# Validate sentence tokenization: 'A/s.' / 'U/ü.' (company or organization) abbreviations
assert _get_preprocessed_sentences("A/s. A.Le Coq'i palve loa saamiseks kohaltarvitamise õigusega õllekaupluse avamiseks.") == \
                                  ["A/s. A.Le Coq'i palve loa saamiseks kohaltarvitamise õigusega õllekaupluse avamiseks."]

assert _get_preprocessed_sentences('A.s. "A.Le Coq\'i" palve Tähtvere linnaosas asetseva maatüki müümise kohta.') == \
                                  ['A.s. "A.Le Coq\'i" palve Tähtvere linnaosas asetseva maatüki müümise kohta.']

assert _get_preprocessed_sentences('Ettepanek tööstuskrundi nr. 185 müümise kohta U/ü. "M. A. Kamenovsky ja Pojad".') == \
                                  ['Ettepanek tööstuskrundi nr. 185 müümise kohta U/ü. "M. A. Kamenovsky ja Pojad".']

assert _get_preprocessed_sentences('O/Ü. Ehitus-tehnika kontor "Estorussi" ja linna wahel sölmitud lepingu pikendamise küsimus.') == \
                                  ['O/Ü. Ehitus-tehnika kontor "Estorussi" ja linna wahel sölmitud lepingu pikendamise küsimus.']

# Validate sentence tokenization: agenda point abbreviation followed by roman numerals
assert _get_preprocessed_sentences("Koosoleku juhataja J.Lill teatab, et päevakorra pp. V, VI ja VII otsustamiseks puudub kvoorum.") == \
                                  ["Koosoleku juhataja J.Lill teatab, et päevakorra pp. V, VI ja VII otsustamiseks puudub kvoorum."]

# Validate sentence tokenization: first name abbreviation followed by family name + fix specific names (such as M.Kurs-Olesk)
assert _get_preprocessed_sentences("Joh. Gerni ehituslaenu küsimus, Aug. Univer'i soowiawaldus ja Fr. Kangro palwe") == \
                                  ["Joh. Gerni ehituslaenu küsimus, Aug. Univer'i soowiawaldus ja Fr. Kangro palwe"]

assert _get_preprocessed_sentences("Lwol. M. Kurs-Oleski soowiawaldus ning lwol. M.Kursk-Oleski ettepanek.") == \
                                  ["Lwol. M. Kurs-Oleski soowiawaldus ning lwol. M.Kursk-Oleski ettepanek."]

assert _get_preprocessed_sentences("Alwine Jüri tr. Heeringa soowiawaldus Aleksandri uul.nr.47 asuwa restorani pidamise loa kohta.") == \
                                  ["Alwine Jüri tr. Heeringa soowiawaldus Aleksandri uul.nr.47 asuwa restorani pidamise loa kohta."]

assert _get_preprocessed_sentences("Wolmer Madise p.Heidemann wölgneb linnale hobuse, koera ja sõiduriistade maksu.") == \
                                  ["Wolmer Madise p.Heidemann wölgneb linnale hobuse, koera ja sõiduriistade maksu."]

# Validate sentence tokenization: 's.a.' (this time?) abbreviations
assert _get_preprocessed_sentences('Palve Tartus 24.- 27. august.s. a. korraldava näituse lõbustusmaksust vabastamise kohta.') == \
                                  ['Palve Tartus 24.- 27. august.s. a. korraldava näituse lõbustusmaksust vabastamise kohta.']

# Validate sentence tokenization: avoid "lowercase string {period} lowercase string {period} sentence break lowercase string"
assert _get_preprocessed_sentences('Linna II jaosk.riikl. kinniswarade hindamisekomisjoni liikmete ja asemikkude walimine.') == \
                                  ['Linna II jaosk.riikl. kinniswarade hindamisekomisjoni liikmete ja asemikkude walimine.']

# Validate sentence tokenization: fix accidental sentence break before parenthesis
assert _get_preprocessed_sentences('Linnavolikogu otsusega 20.juunist 1932.a. (prot.p.XII).') == \
                                  ['Linnavolikogu otsusega 20.juunist 1932.a. (prot.p.XII).']

assert _get_preprocessed_sentences('Feodor Arula palve temale müüa otsustatud Anne uul.nr.26 as. (kinnistu nr.145)elumaja ühes krundiga.') == \
                                  ['Feodor Arula palve temale müüa otsustatud Anne uul.nr.26 as. (kinnistu nr.145)elumaja ühes krundiga.']