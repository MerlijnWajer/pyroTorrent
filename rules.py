import re

TARGET_REGEX = '[0-9A-Za-z_-]+' # Limit this
TORRENT_REGEX = '[0-9,A-Z]{40}'

wt.add_rule(re.compile('^%s/target/(%s)/torrent/(%s)/?$' % \
    (BASE_URL, TARGET_REGEX, TORRENT_REGEX)),
    torrent_info_page, ['target', 'torrent_hash'])

wt.add_rule(re.compile('^%s/target/(%s)/torrent/(%s).torrent$' % \
    (BASE_URL, TARGET_REGEX, TORRENT_REGEX)),
    torrent_file, ['target', 'torrent_hash'])

wt.add_rule(re.compile('^%s/target/(%s)/add_torrent/?$' % (BASE_URL, TARGET_REGEX)),
        add_torrent_page, ['target'])

wt.add_rule(re.compile('^%s/view/([A-z]+)$' % BASE_URL), main_view_page,
        ['view'])

wt.add_rule(re.compile('^%s/(.*)$' % STATIC_URL), static_serve,
        ['static_file'])

wt.add_rule(re.compile('^%s/style.css$' % BASE_URL), style_serve, [])

wt.add_rule(re.compile('^%s/login' % BASE_URL), handle_login, [])

wt.add_rule(re.compile('^%s/logout' % BASE_URL), handle_logout, [])

if ENABLE_API:
    wt.add_rule(re.compile('^%s/api' % BASE_URL), handle_api, [])

# This should be the last rule.
wt.add_rule(re.compile('^%s/?$' % BASE_URL), main_page, [])
