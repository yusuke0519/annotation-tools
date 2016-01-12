# # -*- coding: utf-8 -*-
""" Manage the expID, userID, and filename

- TODO: Delete sensitive information
- TODO: Remove hard coding
"""

USER_TABLE = [
    # ('user_name', 'userID')
    ('hoshi', 1),
    ('kuniya', 2),
    ('oshida', 3),
    ('ikeda', 4),
    ('sawaki', 5),
    ('satoh', 6),
    ('sakaki', 7),
    ('takami', 8),
    ('goto', 9),
]

EXP_TABLE = [
    # ('exp_name', 'expID')
    ('sophia-route1', 1),
    ('sophia-route2', 2),
    ('sophia-fundamental', 3),
]


def get_userID(user_name):
    """
    Ex.
    >>> get_userID('goto')
    9
    >>> get_userID('kkkk')


    """
    # return None if there is no user named {user_name}
    return dict(USER_TABLE).get(user_name.lower())


def get_username(userID):
    """
    Ex.
    >>> get_username(1)
    'hoshi'
    >>> get_username(-1)

    """
    # return None if there is no user named {user_name}
    _dic = dict(USER_TABLE)
    inverse_dic = {v: k for k, v in _dic.items()}
    return inverse_dic.get(userID)


def get_expID(exp_name):
    """
    Ex.
    >>> get_expID('sophia-route1')
    1
    >>> get_expID('sophia-route2')
    2

    """
    # return None if there is no exp named {exp_name}
    return dict(EXP_TABLE).get(exp_name.lower())


def get_expname(expID):
    """
    Ex.
    >>> get_expname(1)
    'sophia-route1'
    >>> get_expname(-1)
    """
    # return None if there is no user named {user_name}
    _dic = dict(EXP_TABLE)
    inverse_dic = {v: k for k, v in _dic.items()}
    return inverse_dic.get(expID)


def get_filename(expID, userID):
    return "exp{expID}-sub{userID}".format(expID=expID, userID=userID)


def get_IDs_from_path(path):
    return [x for x in path.replace("exp", "").replace("sub", "").split("_")]


def allowed_prefix(prefix):
    prefix = prefix.replace('_label', '')
    flag = True
    IDs = get_IDs_from_path(prefix)
    if len(IDs) != 2:
        return False

    flag = flag and (get_expname(int(IDs[0])))
    print(get_expname(IDs[0]))
    flag = flag and (get_username(int(IDs[1])))

    return flag


if __name__ == '__main__':
    import doctest
    doctest.testmod()
