import simplejson as json
import urllib
import urllib2

url = 'http://localhost/torrent/api'
values = [
        {
            'target' : 'sheevareborn',
            'type' : 'torrentrequester',
            'view' : '',
            'attributes' : [
                ('get_name', []),
                ('get_download_rate', []),
                ('get_upload_rate', []),
                ('is_complete', []),
                ('get_size_bytes', []),
                ('get_download_total', []),
                ('get_hash', [])
            ]
        },
        {
            'target' : 'sheevareborn',
            'type' : 'rtorrent',
            'attributes' : [
                ('set_upload_throttle', [20480]),
                ('get_upload_throttle', [])
            ]
        },
        {
            'target' : 'sheevareborn',
            'type' : 'rtorrent',
            'attributes' : [
                ('set_upload_throttle', [20480*2]),
                ('get_upload_throttle', [])
            ]
        },

        {
            'target' : 'sheevareborn',
            'type' : 'torrent',
            'hash' : '8EB5801B88D34D50A6E7594B6678A2CF6224766E',
            'attributes' : (
                ('get_hash', []),
                ('get_name', []),
                ('is_complete', [])
            )
        }
    ]

data = urllib.urlencode({'request' : json.dumps(values)})
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
the_page = response.read()
print the_page


