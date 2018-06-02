#!/usr/bin/env python3

import fontforge as ff
from sys import argv
import sys

font=None

def usage():
    print('USAGE: CreateLigLookup.py ligname')

def ligname_tuple(ligname):
    if ligname.endswith('.liga'):
        parts = ligname.split('.')[0].split('_')
        return (ligname, parts, ''.join([chr(ff.unicodeFromName(c)) for c in parts]))
    else:
        chars = ligname
        parts = [ff.nameFromUnicode(ord(c)) for c in chars]
        ligname = '_'.join(parts) + '.liga'
        return (ligname, parts, chars)

def createSingleSubLookup(name):
    if name in font.gsub_lookups:
        print('Using existing Single Substitution lookup table "%s"' % name)
        for ls in font.getLookupSubtables(name):
            font.removeLookupSubtable(ls)
    else:
        print('Creating Single Substitution lookup "%s"' % name)
        font.addLookup(name, 'gsub_single', 0, ())
    font.addLookupSubtable(name, name)

def contAltName(chars):
    return '\'%s\' Contextual Alternates' % chars

def createSingleSubs(ligname, parts, chars):
    usedalready=[]
    lookups=[]
    baselname = '%s Single Substitution' % ligname
    for i in range(len(chars)):
        if parts[i] in usedalready:
            nth = '1st' if i == 0 else '2nd' if i == 1 else '%drd' % (i-1)
            lname = '%s (%s)' % (baselname, nth)
            createSingleSubLookup(lname)
        else:
            lname = baselname
            if i == 0:
                createSingleSubLookup(lname)
        glyph = font[parts[i]]
        ligat = ligname if i == len(parts)-1 else 'LIG%d' % (i+1) if i > 0 else 'LIG'
        glyph.addPosSub(lname, ligat)
        usedalready.append(parts[i])
        lookups.append(lname)
    return lookups

def createContAlts(ligname, parts, chars, lookups):
    ligas = ['LIG'] + ['LIG%d' % (i+1) for i in range(1,len(parts)-1)] + [ligname]
    lname = contAltName(chars) 
    if (lname in font.gsub_lookups):
        # font.removeLookup(lname)
        print('Using existing Contextual Chained Substitution lookup talbe "%s"' % lname)
        for ls in font.getLookupSubtables(lname):
            font.removeLookupSubtable(ls)
    else:
        print('Creating Contextual Chained Substitution lookup "%s"' % lname)
        font.addLookup(lname, 'gsub_contextchain', (), 
                (('calt', (('DFLT', ('dflt',)),
                           ('arab', ('dflt',)),
                           ('armn', ('dflt',)),
                           ('cyrl', ('SRB ', 'dflt')),
                           ('geor', ('dflt',)),
                           ('grek', ('dflt',)),
                           ('lao ', ('dflt',)),
                           ('latn', ('CAT ', 'ESP ', 'GAL ', 'ISM ', 'KSM ', 'LSM ', 'MOL ', 'NSM ', 'ROM ', 'SKS ', 'SSM ', 'dflt')),
                           ('math', ('dflt',)),
                           ('thai', ('dflt',)))),))
    for i in range(len(chars)):
        lsname = '%s %d' % (lname, len(chars) - i)
        print('    creating subtable "%s"' % lsname)
        rule = '%s | %s @<%s> | %s' % (' '.join(ligas[:i]), 
                                       parts[i], 
                                       lookups[i], 
                                       ' '.join(parts[i+1:]))
        font.addContextualSubtable(lname, lsname, 'glyph', rule)

def createLigaLookup(ligname, parts=None, chars=None):
    global font
    ligname, newparts, newchars = ligname_tuple(ligname)

    if parts == None:
        parts = newparts
    if chars == None:
        chars = newchars

    lookups = createSingleSubs(ligname, parts, chars)
    createContAlts(ligname, parts, chars, lookups)
    font.save()

def main(argv):
    global font
    if len(argv) < 2:
        usage()
        sys.exit(1)
    if font:
        font.close()
    if argv[1].endswith('.sfd'):
        font = ff.open(argv[1])
        ligas = argv[2:]
    else:
        font = ff.open("Inconsoliga-Regular.sfd")
        ligas = argv[1:]
    for lig in ligas:
        createLigaLookup(lig)

if __name__ == '__main__':
    main(argv)

