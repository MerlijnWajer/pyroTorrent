CONNECTION_SCGI, CONNECTION_HTTP = range(2)

class RTorrentConfigException(Exception):
    pass

def parse_config_part(config_dict, name):
    if 'scgi' in config_dict and 'http' in config_dict:
        raise RTorrentConfigException('Ambigious configuration for: %s\n'
                'You cannot have both a \'scgi\' line and a \'http\' key.' \
                % name)

    if 'scgi' in config_dict:
        if 'unix-socket' in config_dict['scgi']:
            # TODO: Check path
            return \
            {
                'type' : CONNECTION_SCGI,
                'fd' : 'scgi://%s' % config_dict['scgi']['unix-socket'],
                'name' : name
            }
        elif 'host' in config_dict['scgi'] and \
             'port' in config_dict['scgi']:
            return \
            {
                'type' : CONNECTION_SCGI,
                'fd' : 'scgi://%s:%d' % (config_dict['scgi']['host'], \
                                         config_dict['scgi']['port']),
                'name' : name
            }
        else:
            raise RTorrentConfigException('Config lacks specific scgi'
                'information. Needs host and port or unix-socket.')

    elif 'http' in config_dict:
        return \
        {
            'type' : CONNECTION_HTTP,
            'host' : config_dict['http']['host'],
            'port' : config_dict['http']['port'],
            'url' :  config_dict['http']['url'],
            'name' : name
        }
    else:
        raise RTorrentConfigException('Config lacks scgi of http information')
