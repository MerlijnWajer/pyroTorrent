#!/usr/bin/env python

# REQUEST_METHOD = GET/POST
# REQUEST_URI = /mai/linkoe
# IP = REMOTE_ADDR

# Handle post data using FieldStorage
import cgi

class WebToolException(Exception):
    """
        Raised on an exception in the WebTool.
    """

class WebTool(object):
    """
        The WebTool class provides me with the required MiddleWare utilities.
        Current functionality:
            -   URL-Based function calling and argument parsing.
    """

    def __init__(self):
        self.rules = {}
        pass

    def add_rule(self, rule, func, varnames):
        """
            Add a new rule. The rule has to be a regex object. (Use re.compile)
            func is called with varnames amount of named arguments.
        """
        if rule in self.rules:
            raise WebToolException('Rule %s already exists' % rule)
        self.rules[rule] = {'func': func, 'vars': varnames}

    def add_rules(self, rules, funcs, varnames):
        for rule, func, vnames in zip(rules, funcs, varnames):
            self.add_rule(rule, func, vnames)

    def apply_rule(self, url, env):
        """
            apply_rule finds an appropriate rule and applies it if found.
        """
        for rule, fv in self.rules.iteritems():
            m = rule.match(url)
            if m:
                l = [x for x in m.groups()]
                if len(l) != len(fv['vars']):
                    raise WebToolException('Matches does not equal variable \
                            amount')
                return fv['func'](env=env, **dict(zip(fv['vars'], l)))
        return None

def read_post_data(env):
#    if env['CONTENT_TYPE'] == 'multipart/form-data' :
    if True:

        # Code taken from:
        # http://stackoverflow.com/questions/530526/accessing-post-data-from-wsgi
        post_env = env.copy()
        post_env['QUERY_STRING'] = ''
        post = cgi.FieldStorage(
            fp=env['wsgi.input'],
            environ=post_env,
            keep_blank_values=True
        )

        #print "Form fields: " + repr(post)
        return post

#    else:
#        splitdata = [x.split('=') for x in postdata.split('&')]
#        try:
#            data = dict(splitdata)
#        except (TypeError, ValueError):
#            data = None
#        return data
