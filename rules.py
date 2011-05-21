import re

wt.add_rule(re.compile('^%s/torrent/([0-9,A-Z]{32})/?' % BASE_URL),
        torrent_info_page, ['torrent_hash'])

# This should be the last rule.
wt.add_rule(re.compile('^%s/?$' % BASE_URL), main_page, [])
