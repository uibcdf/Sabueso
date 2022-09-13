
class NotImplementedMethodError(NotImplementedError):
    """Exception raised when a method has not been fully implemented yet.

    This exception is raised when a method has been already defined but its code was not fully
    implemented yet. Maybe the method was just included in a developing version to be coded in the
    future. Or maybe the method works already for certain values of the input arguments, but not
    for others yet.

    Note
    ----
    This exception does not require input arguments.

    Raises
    ------
    NotImplementedMethodError
        A message is printed out with the name of the method raising the exception, the link to
        the API documentation, and the link to the issues board of Sabueso's GitHub repository.

    Examples
    --------
    >>> from sabueso._private_tools.exceptions import NotImplementedMethodError
    >>> def method_name(a, b=True):
    ...    raise NotImplementedMethodError
    ...    pass

    .. admonition:: See Also
       :class: attention

        :ref:`Developer Guide \> Exceptions \> NotImplementedMethodError <developer:exceptions:NotImplementedMethodError>`

    """

    def __init__(self):

        from sabueso import __github_issues_web__
        from inspect import stack

        all_stack_frames = stack()
        caller_stack_frame = all_stack_frames[1]
        caller_name = caller_stack_frame[3]

        api_doc = ''

        message = (
                f"The \"{caller_name}\" method has not been implemented yet in the way you are using it. "
                f"Check {api_doc} for more information. "
                f"If you still want to suggest its implementation, open a new issue in {__github_issues_web__}"
                )

        super().__init__(message)


class NotImplementedClassError(NotImplementedError):
    """Exception raised when a class has not been fully implemented yet.

    This exception is raised when a class has being already defined but its code was not fully
    implemented yet. Maybe the class was just included in a developing version to be coded in the
    future. Or maybe the class can be instantated already for certain values of the input
    arguments, but not for others yet.

    Note
    ----
    This exception does not require input arguments.

    Raises
    ------
    NotImplementedClassError
        A message is printed out with the name of the class raising the exception, the link to
        the API documentation, and the link to the issues board of Sabueso's GitHub repository.

    Examples
    --------
    >>> from sabueso._private_tools.exceptions import NotImplementedClassError
    >>> class ClassName():
    ...    def __init__(self):
    ...       raise NotImplementedClassError
    ...       pass

    .. admonition:: See Also
       :class: attention

        :ref:`Developer Guide \> Exceptions \> NotImplementedClassError <developer:exceptions:NotImplementedClassError>`

    """

    def __init__(self):

        from sabueso import __github_issues_web__
        from inspect import stack

        all_stack_frames = stack()
        caller_stack_frame = all_stack_frames[1]
        caller_name = caller_stack_frame[3]

        api_doc = ''

        message = (
                f"The \"{caller_name}\" class has not been implemented yet in the way you are using it. "
                f"Check {api_doc} for more information. "
                f"If you still want to suggest its implementation, open a new issue in {__github_issues_web__}."
                )

        super().__init__(message)


class NotImplementedFormError(NotImplementedError):
    """Exception raised when a method or a class does not support a specific item's form yet.

    This exception is raised when a method or a class should be able to work with an item's form,
    but it has not been implemented yet. For instance, a method gets the number of atoms of a
    molecular system, but the current version works over a pdb file but not yet over a mol file. In
    this case this exception should be rised when the input argument is a mol file.

    Parameters
    ----------
    form : str
        The item's form not supported yet by the class or method raising the exception.

    Raises
    ------
    NotImplementedFormError
        A message is printed out with the name of the not supported form, the name of the class or
        the method raising the exception, the link to the API documentation, and the link to the
        issues board of Sabueso's GitHub repository.

    Examples
    --------
    >>> from sabueso._private_tools.exceptions import NotImplementedFormError
    >>> from sabueso import get_form
    >>> def method_name(item):
    ...    input_form = get_form(item)
    ...    if input_form not in ['file:pdb', 'string:pdb_id', 'string:pdb_text']:
    ...       raise NotImplementedFormError(input_form)
    ...    pass

    .. admonition:: See Also
       :class: attention

        :ref:`Developer Guide \> Exceptions \> NotImplementedFormError <developer:exceptions:NotImplementedFormError>`

    """

    def __init__(self, form):

        from sabueso import __github_issues_web__
        from inspect import stack

        all_stack_frames = stack()
        caller_stack_frame = all_stack_frames[1]
        caller_name = caller_stack_frame[3]

        api_doc = ''

        message = (
                f"The \"{form}\" form has not been implemeted yet in \"{caller_name}\". "
                f"Check {api_doc} for more information. "
                f"Write a new issue in {__github_issues_web__} asking for its implementation."
                )

        super().__init__(message)


class NotWithThisFormError(ValueError):
    """Exception raised when a method or a class can not accept a specific item's form -by no means-.

    This exception is raised when a method or a class should be able to work with an item's form,
    but it has not been implemented yet. For instance, the method used to get the value of the
    dihedral angle defined by four atoms can not work over a GROMACS topology file (.top). In this
    case the method will raise a 'NotWithTisFormError' exception.

    Parameters
    ----------
    form : str
        The item's form not accepted by the method or class raising the exception.

    Raises
    ------
    NotWithThisFormError
        A message is printed out with the name of the not supported form, the name of the class or
        the method raising the exception, the link to the API documentation, and the link to the
        issues board of Sabueso's GitHub repository.

    Examples
    --------
    >>> from sabueso._private_tools.exceptions import NotWithThisFormError
    >>> from sabueso import get_form
    >>> def method_name(item):
    ...    input_form = get_form(item)
    ...    if input_form not in ['file:top', 'file:prmtop']:
    ...       raise NotWithThisFormError(input_form)
    ...    pass

    .. admonition:: See Also
       :class: attention

        :ref:`Developer Guide \> Exceptions \> NotWithThisFormError <developer:exceptions:NotWithThisFormError>`

    """

    def __init__(self, form):

        from sabueso import __github_issues_web__
        from inspect import stack

        all_stack_frames = stack()
        caller_stack_frame = all_stack_frames[1]
        caller_name = caller_stack_frame[3]

        api_doc = ''

        message = (
                f"\"{caller_name}\" does not work with {form} items. "
                f"Check {api_doc} for more information. "
                f"If you still need help, open a new issue in {__github_issues_web__}."
                )

        super().__init__(message)


class WrongFormError(ValueError):
    """Exception raised when the item has not the correct form expected by a method or a class.

    This exception is raised when an item has not the correct form for the method to work or the
    class to be instantiated.

    Parameters
    ----------
    form : str
        The form accepted by the method or the class.

    Raises
    ------
    WrongFormError
        A message is printed out with the name of the right form, the name of the class or
        the method raising the exception, the link to the API documentation, and the link to the
        issues board of Sabueso's GitHub repository.

    Examples
    --------
    >>> from sabueso._private_tools.exceptions import WrongFormError
    >>> from sabueso import get_form
    >>> input_form = get_form('1VII.pdb')
    ... if input_form != 'file:top':
    ...    raise WrongFormError('file:top')

    .. admonition:: See Also
       :class: attention

        :ref:`Developer Guide \> Exceptions \> WrongFormError <developer:exceptions:WrongFormError>`

    """

    def __init__(self, form):

        from sabueso import __github_issues_web__
        from inspect import stack

        all_stack_frames = stack()
        caller_stack_frame = all_stack_frames[1]
        caller_name = caller_stack_frame[3]

        api_doc = ''

        message = (
                f"The input item's form of \"{caller_name}\" should be {form} and is not. "
                f"Check {api_doc} for more information. "
                f"If you still need help, open a new issue in {__github_issues_web__}."
                )

        super().__init__(message)


class UnknownFormError(ValueError):
    """Exception raised when the item's form is unknown and thereby not supported.

    This exception is raised when Sabueso does not recognize the item as a supported form.

    Note
    ----
    This exception does not require input arguments.

    Raises
    ------
    UnknownFormError
        A message is printed out with the name of the class or the method raising the exception,
        the link to the API documentation with the list of supported forms, and the link to the
        issues board of Sabueso's GitHub repository.

    Examples
    --------
    >>> from sabueso._private_tools.exceptions import UnknownFormError
    >>> from sabueso import get_form
    >>> try:
    ...    _ = get_form(item)
    ... except:
    ...    raise UnknownFormError

    .. admonition:: See Also
       :class: attention

        :ref:`Developer Guide \> Exceptions \> UnknownFormError <developer:exceptions:UnknownFormError>`

    """

    def __init__(self):

        from sabueso import __github_issues_web__
        from inspect import stack

        all_stack_frames = stack()
        caller_stack_frame = all_stack_frames[1]
        caller_name = caller_stack_frame[3]

        api_doc = ''

        message = (
                f"The input item in \"{method_name}\" has an unknown form. "
                f"Check {api_doc} for more information. "
                f"If you still need help, open a new issue in {__github_issues_web__}."
                )

        super().__init__(message)


class BadCallError(ValueError):
    """Exception raised when a method, or a class, was not properly called or instantiated.

    This exception is raised when a method or a class was not properly called or instantiated.

    Parameters
    ----------
    argument : str, optional
        The name of the possible wrong input argument.

    Raises
    ------
    BadCallError
        A message is printed out with the name of the class or the method raising the exception,
        the possible wrong argument, the link to the API documentation, and the link to the
        issues board of Sabueso's GitHub repository.

    Examples
    --------
    >>> from sabueso._private_tools.exceptions import BadCallError
    >>> def method_name(item, a=True):
    ...    if type(a) not in [int, float]:
    ...       raise BadCallError('a')
    ...    pass

    .. admonition:: See Also
       :class: attention

        :ref:`Developer Guide \> Exceptions \> BadCallError <developer:exceptions:BadCallError>`

    """

    def __init__(self, argument=None):

        from sabueso import __github_issues_web__
        from inspect import stack

        all_stack_frames = stack()
        caller_stack_frame = all_stack_frames[1]
        caller_name = caller_stack_frame[3]

        api_doc = ''

        message = f"The \"{caller_name}\" method or class was not properly invoked"
        if argument is not None:
            message += f", probably due to the \"{argument}\" input argument"
        message += (
                f". Check {api_doc} for more information. "
                f"If you still need help, open a new issue in {__github_issues_web__}."
                )

        super().__init__(message)

class LibraryNotFoundError(NotImplementedError):
    """Exception raised when a library required by the user is not found.

    Some libraries are not considered as dependencies by Sabueso. These libraries are required if
    the user choose to execute a method with a not default engine. In this case, the user hat to
    install it previousy. It that's not the case, the method will raise this exceptions suggesting
    the manual installation.

    Parameters
    ----------
    argument : str
        The name of the not found library.

    Raises
    ------
    LibraryNotFoundError
        A message is printed out with the name of the class or the method raising the exception,
        the name of the not found library, the link to the API documentation, and the link to the
        issues board of Sabueso's GitHub repository.

    Examples
    --------
    >>> from sabueso._private_tools.exceptions import LibraryNotFoundError
    >>> def method_name(item, engine='MolSysMT'):
    ...    if engine == 'OpenMM':
    ...       try:
    ...          import openmm
    ...       except:
    ...          raise LibraryNotFoundError('OpenMM')
    ...    pass

    .. admonition:: See Also
       :class: attention

        :ref:`Developer Guide \> Exceptions \> LibraryNotFoundError <developer:exceptions:LibraryNotFoundError>`

    """

    def __init__(self, library):

        from sabueso import __github_issues_web__
        from inspect import stack

        all_stack_frames = stack()
        caller_stack_frame = all_stack_frames[1]
        caller_name = caller_stack_frame[3]

        api_doc = ''

        message = (
                f"The python library {library} was not found. "
                f"Although {library} is not considered a dependency, it needs "
                f"to be installed to execute the {caller_name} method the way you require. "
                f"If you still need help, open a new issue in {__github_issues_web__}."
                )

        super().__init__(message)

class DatabaseNotAccessibleError(NotImplementedError):
    """Exception raised when an online database can not be reached.

    This exception is raised when an noline database can not be reached for whatever reason.

    Parameters
    ----------
    argument : str
        The name of the online database not reachable.

    Raises
    ------
    DatabaseNotAccessibleError
        A message is printed out with the name of the class or the method raising the exception,
        the name of the not accessible database, the link to the API documentation, and the link to the
        issues board of Sabueso's GitHub repository.

    Examples
    --------
    >>> from sabueso._private_tools.exceptions import DatabaseNotAccessibleError
    >>> import requests
    >>> r = requests.get('https://www.ebi.ac.uk/chembl/api/data', stream=True, timeout=5)
    >>> if not r.status_code == requests.codes.ok.
    ...     raise DababaseNotAccessibleError('ChEMBL')

    .. admonition:: See Also
       :class: attention

        :ref:`Developer Guide \> Exceptions \> DatabaseNotAccessibleError <developer:exceptions:DatabaseNotAccessibleError>`

    """

    def __init__(self, database):

        from sabueso import __github_issues_web__

        message = (
                f"The online database {database} cannot be reached. "
                f"Check your internet connection and the availability of {database}"
                f"If you still need help, open a new issue in {__github_issues_web__}."
                )

        super().__init__(message)

