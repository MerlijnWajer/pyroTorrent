# Place all your globals here

# ``Base'' URL for your HTTP website
BASE_URL = '/torrent'
# HTTP URL for the static files
STATIC_URL = '/static/torrent'


# # Exemplary SCGI setup using unix socket
# rtorrent_config = {
#     'scgi' : {
#         'unix-socket' : '/tmp/rtorrent.sock'
#     }
# }
#
# # Exemplary SCGI setup using scgi over network
# rtorrent_config = {
#     'scgi' : {
#         'host' : '192.168.1.70',
#         'port' : 80
#     }
# }

# Exemplary HTTP setup using remote XMLRPC server. (SCGI is handled by the HTTPD
# in this case)
rtorrent_config = {
    'http' : {
        'host' : '192.168.1.70',
        'port' : 80,
        'url'  : '/RPC2',
    }
}

# TODO: Remove from config.
session_options = {
    'session.cookie_expires' : True
}
