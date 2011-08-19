# Pulled somewhere from the net. Used in jinja.
def wiz_normalise(a):
    a = float(a)
    if a >= 1099511627776:
        terabytes = a / 1099511627776
        size = '%.2fT' % terabytes
    elif a >= 1073741824:
        gigabytes = a / 1073741824
        size = '%.2fG' % gigabytes
    elif a >= 1048576:
        megabytes = a / 1048576
        size = '%.2fM' % megabytes
    elif a >= 1024:
        kilobytes = a / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % a
    return size
