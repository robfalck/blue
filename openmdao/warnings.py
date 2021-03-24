"""
A module for OpenMDAO-specific warnings and associated functions.
"""

import inspect
import sys
import io
import warnings


__all__ = ['issue_warning', 'reset_warnings', 'OpenMDAOWarning',
           'SetupWarning', 'DistributedComponentWarning', 'CaseRecorderWarning',
           'CacheWarning', 'PromotionWarning', 'UnusedOptionWarning', 'DerivativesWarning',
           'MPIWarning', 'UnitsWarning', 'SolverWarning', 'DriverWarning', 'OMDeprecationWarning']

_valid_actions = ['warn', 'error', 'raise', 'ignore', 'once', 'always', 'module', 'default']


class OpenMDAOWarning(UserWarning):
    """
    Base class for all OpenMDAO warnings.
    """

    name = 'warn_openmdao'
    filter = 'always'


class SetupWarning(OpenMDAOWarning):
    """
    Warning class for warnings that occur during setup.
    """

    name = 'warn_setup'
    filter = 'always'


#
# Subclasses of SetupWarning
#

class PromotionWarning(SetupWarning):
    """
    Warning dealing with the promotion of an input or output.
    """

    name = 'warn_promotion'
    filter = 'always'


class UnitsWarning(SetupWarning):
    """
    Warning which is issued when unitless variable is connected to a variable with units.
    """

    name = 'warn_units'
    filter = 'always'


class DerivativesWarning(SetupWarning):
    """
    Warning issued when the approximated partials or coloring cannot be evaluated as expected.
    """

    name = 'warn_derivatives'
    filter = 'always'


class MPIWarning(SetupWarning):
    """
    Warning dealing with the availability of MPI.
    """

    name = 'warn_mpi'
    filter = 'always'


class DistributedComponentWarning(SetupWarning):
    """
    Warning specific to a distributed component.
    """

    name = 'warn_distributed_component'
    filter = 'always'

#
# End SetupWarning subclasses
#


class SolverWarning(OpenMDAOWarning):
    """
    Warning base class for solver-related warnings.
    """

    name = 'warn_solver'
    filter = 'always'


class DriverWarning(OpenMDAOWarning):
    """
    Warning which is issued during the execution of a driver.
    """

    name = 'warn_driver'
    filter = 'always'


class UnusedOptionWarning(OpenMDAOWarning):
    """
    Warning dealing with an unnecessary option or argument being provided.
    """

    name = 'warn_unused_option'
    filter = 'always'


class CaseRecorderWarning(OpenMDAOWarning):
    """
    Warning pertaining to case recording and reading.
    """

    name = 'warn_case_recorder'
    filter = 'always'


class CacheWarning(OpenMDAOWarning):
    """
    Warning which is issued when the a cache is invalid and needs to be rebuilt.
    """

    name = 'warn_cache'
    filter = 'always'


class OMDeprecationWarning(OpenMDAOWarning):
    """
    An OpenMDAO-specific deprecation warning that is noisy by default, unlike the Python one.
    """

    name = 'warn_deprecation'
    filter = 'always'


_warnings = [_class for _, _class in
             inspect.getmembers(sys.modules[__name__], inspect.isclass)
             if issubclass(_class, Warning)]

#
# def get_warning_defaults():
#     """
#     Return a dictionary of the default action of each warning type.
#
#     Returns
#     -------
#     dict
#         A dictionary mapping a warning name with its default filter aciton.
#     """
#     defaults = {c.name: c.action for _, c in
#                 inspect.getmembers(sys.modules[__name__], inspect.isclass)
#                 if issubclass(c, Warning) and not c.name.startswith('_')}
#     return defaults


# def register_warning(*args):
#     """
#     Register th new warning class within the OpenMDAO warning ecosystem.
#
#     Parameters
#     ----------
#     *args : class
#         One or more classes derived from Warning.  Each must have class "name" and "filter"
#         attributes that provide the name and default filter action of the warning.
#     """
#     for c in args:
#         if not issubclass(c, Warning):
#             raise TypeError(f'Only subclasses of Warning may be registered using '
#                             f'register_warning. {c} is not a subclass of Warning.')
#
#         if not hasattr(c, 'name') or not isinstance(c.name, str):
#             raise AttributeError(f'class {c} is required to have a class attribute "name" of '
#                                  f'type str.')
#
#         if not hasattr(c, 'filter') or not isinstance(c.name, str):
#             raise AttributeError(f'class {c} is required to have a class attribute "filter" of '
#                                  f'type str.')
#
#         if c.name in _warnings:
#             raise ValueError(f'Class name {c.name} is already registered.')
#
#         if c.filter not in _valid_actions:
#             raise ValueError(f'Class {c} has an invalid filter setting: {c.filter}. Valid values '
#                              f'for filter are {_valid_actions}')
#
#         _warnings[c.name] = c
#         kwg = {c.name: c.filter}
#         filter_warnings(kwg)


def reset_warnings():
    """
    Apply the default warning filter actions for the OpenMDAO-specific warnings.

    This is necessary when testing the filters, because Python resets the default filters
    before running each test.
    """
    for w_class in _warnings:
        warnings.filterwarnings(w_class.filter, category=w_class)


# def filter_warnings(reset_to_defaults=False, **kwargs):
#     """
#     Apply the warning filters as given by warning_options.
#
#     This is necessary when testing the filters, because Python resets the default filters
#     before running each test.
#     """
#     if reset_to_defaults:
#         for w_name, w_class in _warnings.items():
#             warnings.filterwarnings(w_class.filter, category=w_class)
#
#     for w_name, action in kwargs.items():
#         _action = 'error' if action == 'raise' else action
#         if w_name not in _warnings:
#             valid = [key for key in _warnings.keys() if not key.startswith('_')]
#             msg = f"The warning '{w_name}' is not a valid OpenMDAO warning. \n" \
#                   f"Valid values are {valid}."
#             raise ValueError("\n".join(textwrap.wrap(msg, width=80)))
#         if action not in _valid_actions:
#             msg = f"The action '{action}' for warning '{w_name}' is not a valid action. \n" \
#                   f"Must be one of {_valid_actions}.  See Python warning documentation for " \
#                   f"more details."
#             raise ValueError(msg)


def _warn_simple_format(message, category, filename, lineno, file=None, line=None):
    return f'{filename}:{lineno}: {category.__name__}:{message}\n'


def issue_warning(msg, prefix='', stacklevel=2, category=OpenMDAOWarning):
    """
    Display a warning with the desired stack level and optional prefix.

    Parameters
    ----------
    msg : str
        The warning message.
    prefix : str
        An optional prefix to be prepended to the warning message (usually the system path).
    stacklevel : int
        Number of levels up the stack to identify as the warning location.
    category : class
        The class of warning to be issued.

    Examples
    --------
    om.issue_warning('some warning message', prefix=self.pathname, category=om.SetupWarning)

    """
    old_format = warnings.formatwarning
    warnings.formatwarning = _warn_simple_format
    _msg = f'{prefix}: {msg}' if prefix else f'{msg}'
    try:
        warnings.warn(_msg, category=category, stacklevel=stacklevel)
    finally:
        warnings.formatwarning = old_format


def _make_table(superclass=OpenMDAOWarning):
    """
    Generate a markdown table of the warning options.

    Returns
    -------
    str
        A string representation of a markdown table of the warning options.
    """
    s = io.StringIO()
    max_name_len = max([len(_class.__name__) for _class in _warnings])
    max_desc_len = max([len(' '.join(c.__doc__.split())) for c in _warnings])

    name_header = "Option Name"
    desc_header = "Description"
    print(f'| {name_header:<{max_name_len}} | {desc_header:<{max_desc_len}} |', file=s)
    print(f'| {max_name_len*"-"} | {max_desc_len*"-"} |', file=s)

    for _class in _warnings:
        if isinstance(_class, superclass) or issubclass(_class, superclass):
            desc = ' '.join(_class.__doc__.split())
            print(f'| {_class.__name__:<{max_name_len}} | {desc:<{max_desc_len}} |', file=s)
    return s.getvalue()


# When we import OpenMDAO and load this module, set the default filters on these warnings.
reset_warnings()


if __name__ == '__main__':
    issue_warning('foo', prefix='my.comp', category=OpenMDAOWarning)

    print(_make_table(SetupWarning))