def variants(gls):
    """
    Yields all possible variants of the parameter values.

    ``gls`` is a list of tuples (name, vals, i0), where ``name`` is the
    parameter's name, ``vals`` is the list of values this parameter takes and
    the optional ``i0`` is the 1-st index used for file naming purposes.

    The iterator yields idx, Ntot, Plst, where ``idx`` is a tuple of parameter
    value indices, ``Ntot`` is the total number of variants, and ``Plst`` is a
    list of parameter names and correspondent values. This list can be passed
    to ``dict`` constructor to obtain a dictionary defining the scope with the
    current set of parameter values.
    """
    if gls:
        k, vals = gls[0][:2]
        if len(gls[0]) > 2:
            n = gls[0][2]
        else:
            n = 0
        for v in vals:
            for t in variants(gls[1:]):
                yield (n, ) + t[0], ((k, v),) + t[1]
            n += 1
    else:
        yield ((), ())


def params(cla):
    """
    From the command line argument starting with '--' get the parameter name
    and a list of its values.

    ``cla`` -- the command line argument with the preceeding `--` stripped.
    """
    # this is a list of variable values, preceeded with the name
    tokens = cla.split()
    vname = tokens.pop(0)
    # Check if the name contains the 1-st index. General form:
    # vname-I
    # where 'vname' is the name of the variable, and I -- is the
    # index of the first value, used to name the template output.
    if '-' in vname:
        vname, i0 = vname.replace('-', ' ').split()
        i0 = int(i0)
    else:
        i0 = 0
    try:
        vals = map(int, tokens)
    except ValueError:
        try:
            vals = map(float, tokens)
        except ValueError:
            vals = map(None, tokens)
    return (vname, vals, i0)
