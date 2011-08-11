import re

TARGET_REGEX = '[A-Za-z]+' # Limit this
TORRENT_REGEX = '[0-9,A-Z]{40}'

wt.add_rule(re.compile('^%s/target/(%s)/torrent/(%s)/?$' % \
    (BASE_URL, TARGET_REGEX, TORRENT_REGEX)),
    torrent_info_page, ['target', 'torrent_hash'])

wt.add_rule(re.compile('^%s/target/(%s)/torrent/(%s)/action/([A-z]+)?$' % \
    (BASE_URL, TARGET_REGEX, TORRENT_REGEX)),
    torrent_action, ['target', 'torrent_hash', 'action'])

wt.add_rule(re.compile('^%s/target/(%s)/add_torrent/?$' % (BASE_URL, TARGET_REGEX)),
        add_torrent_page, ['target'])

wt.add_rule(re.compile('^%s/view/([A-z]+)$' % BASE_URL), main_view_page,
        ['view'])

# This should be the last rule.
wt.add_rule(re.compile('^%s/?$' % BASE_URL), main_page, [])
