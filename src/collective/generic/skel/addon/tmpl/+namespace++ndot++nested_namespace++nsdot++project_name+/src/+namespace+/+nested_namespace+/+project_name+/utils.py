#!/usr/bin/env python
# -*- coding: utf-8 -*-

import chardet

def magicstring(string):
    """Convert any string to UTF-8 ENCODED one"""
    seek = False
    if isinstance(string, unicode):
        try:
            string = string.encode('utf-8')
        except:
            seek = True
    if seek:
        try:
            detectedenc = chardet.detect(string).get('encoding')
        except Exception, e:
            detectedenc = None
        if detectedenc:
            sdetectedenc = detectedenc.lower()
        else:
            sdetectedenc = ''
        if sdetectedenc.startswith('iso-8859'):
            detectedenc = 'ISO-8859-15'

        found_encodings = [
            'ISO-8859-15', 'TIS-620', 'EUC-KR',
            'EUC-JP', 'SHIFT_JIS', 'GB2312', 'utf-8', 'ascii',
        ]
        if sdetectedenc not in ('utf-8', 'ascii'):
            try:
                if not isinstance(string, unicode):
                    string = string.decode(detectedenc)
                string = string.encode(detectedenc)
            except:
                for idx, i in enumerate(found_encodings):
                    try:
                        if not isinstance(string, unicode) and detectedenc:
                            string = string.decode(detectedenc)
                        string = string.encode(i)
                        break
                    except:
                        if idx == (len(found_encodings) - 1):
                            raise
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    string = string.decode('utf-8').encode('utf-8')
    return string

 
