#!/usr/bin/env python
import os
import re

for root, dirs, files in os.walk('_posts'):
    for file in files:
        if file.endswith('.md'):
            for line in open(os.path.join(root, file)).read().splitlines():
                m = re.match(r'^tags\s*:\s*\[(.+)\]\s*$', line)
                if m:
                    for tag in re.findall(r'\w+', m.group(1)):
                        try:
                            open('_tags/%s.md' % tag, 'x').write('---\nname: %s\n---\n' % tag)
                            print('create:', tag)
                        except:
                            print('skip:', tag)

