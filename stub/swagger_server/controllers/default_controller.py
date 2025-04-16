import connexion
import six

from swagger_server.models.efficiency import Efficiency  # noqa: E501
from swagger_server.models.latest import Latest  # noqa: E501
from swagger_server.models.log_item import LogItem  # noqa: E501
from swagger_server import util


def controller_get_latest(user_id):  # noqa: E501
    """Returns the user&#x27;s latest sleep data recorded.

     # noqa: E501

    :param user_id: 
    :type user_id: int

    :rtype: Latest
    """
    return 'do some magic!'


def controller_get_user_efficiency(user_id):  # noqa: E501
    """Returns predicted sleep efficiency of the specified user.

     # noqa: E501

    :param user_id: 
    :type user_id: int

    :rtype: Efficiency
    """
    return 'do some magic!'


def controller_get_user_log(user_id):  # noqa: E501
    """Returns a list of user&#x27;s sleep logs in the database.

     # noqa: E501

    :param user_id: 
    :type user_id: int

    :rtype: List[LogItem]
    """
    return 'do some magic!'
