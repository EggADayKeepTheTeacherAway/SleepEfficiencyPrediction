import connexion
import six

from swagger_server.models.efficiency import Efficiency  # noqa: E501
from swagger_server.models.latest import Latest  # noqa: E501
from swagger_server.models.log_item import LogItem  # noqa: E501
from swagger_server import util


def controller_get_latest(username):  # noqa: E501
    """Returns the user&#x27;s latest sleep data recorded.

     # noqa: E501

    :param username: 
    :type username: str

    :rtype: Latest
    """
    return 'do some magic!'


def controller_get_user_efficiency(username):  # noqa: E501
    """Returns predicted sleep efficiency of the specified user.

     # noqa: E501

    :param username: 
    :type username: str

    :rtype: Efficiency
    """
    return 'do some magic!'


def controller_get_user_log(username):  # noqa: E501
    """Returns a list of user&#x27;s sleep logs in the database.

     # noqa: E501

    :param username: 
    :type username: str

    :rtype: List[LogItem]
    """
    return 'do some magic!'
