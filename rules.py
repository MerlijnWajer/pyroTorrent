import re

wt.add_rule(re.compile('^%s/torrent/([0-9,A-Z]{40})/?$' % BASE_URL),
        torrent_info_page, ['torrent_hash'])

wt.add_rule(re.compile('^%s/torrent/([0-9,A-Z]{40})/action/([A-z]+)?$' % BASE_URL),
        torrent_action, ['torrent_hash', 'action'])

wt.add_rule(re.compile('^%s/add_torrent/?$' % BASE_URL),
        add_torrent_page, [])

# This should be the last rule.
wt.add_rule(re.compile('^%s/?$' % BASE_URL), main_page, [])
