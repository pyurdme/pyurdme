#!/usr/bin/env python
import os

mappings = {
    '="_static/' : '="static/',
    '="_sources/' : '="sources/',
    '="_modules/' : '="modules/',
}

print mappings

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for filename in files:
    if filename == os.path.basename(__file__): continue
    print filename
    with open(filename, "r+") as f:
        data = f.read()
        for k,v in mappings.iteritems():
            print "\t{0} --> {1}".format(k,v)
            data = data.replace(k,v)
        f.seek(0)
        f.write(data)
        f.truncate()

