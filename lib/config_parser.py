from model.pyro.user import PyroUser

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

def parse_user_part(config_dict, name):
    user = PyroUser()

    user.name = name

    if not config_dict.has_key('targets'):
        raise RTorrentConfigException('User %s has no ``targets'' entry' % name)
    elif type(config_dict['targets']) not in (list,):
        raise RTorrentConfigException('User %s ``targets'' needs to be a list'\
                                         % name)

    user.targets = config_dict['targets']

    if not config_dict.has_key('background-image'):
        user.background_image = None
    elif type(config_dict['background-image']) not in (str,):
        raise RTorrentConfigException('User %s ``background-image'' must be a str'\
                                         % name)

    user.background_image = config_dict['background-image']

    if not config_dict.has_key('password'):
        raise RTorrentConfigException('User %s has no ``password'' entry' % name)
    elif type(config_dict['password']) not in (str,):
        raise RTorrentConfigException('User %s ``password'' must be a str'\
                                         % name)

    user.password = config_dict['password']

    return user
