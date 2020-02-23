import logging
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import Union

import flask
import flask_restful
import marshmallow as msh
import webargs

from keyosk import __about__
from keyosk import constants
from keyosk import exceptions


ResponseBody = Optional[Union[Dict[str, Any], List[Dict[str, Any]], List[str]]]


STATIC_HEADERS = {"x-keyosk-version": __about__.__version__}


class ResponseTuple(NamedTuple):
    """Namedtuple representing the format of a flask-restful response tuple

    :param body: Response body; must be comprised only of JSON-friendly primative types
    :param code: HTTP response code
    :param headers: Dictionary of headers
    """

    body: ResponseBody
    code: int
    headers: Dict[str, str]


class PaginationData(NamedTuple):
    """Tuple of data returned from the pagination function
    :param data: Resulting paginated data to return in the response body
    :param headers: Pagination headers to be included in the response headers
    .. note:: The ``headers`` attribute **should not** include the default headers
    """

    data: Sequence[Any]
    headers: Dict[str, str]


class KeyoskParser(webargs.flaskparser.FlaskParser):

    DEFAULT_VALIDATION_STATUS = 400

    def handle_error(self, error: Type[Exception], *args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.error(error)
        raise error


def make_pagination(matches: Sequence[Any], request=flask.request) -> PaginationData:
    """Paginate a sequence of result data

    Parse the pagination parameters out of the request body and filter the list of
    matches accordinglly

    :param matches: Sequence of results to paginate
    :returns: Pagination data tuple with processed results, pagination parameters, and
              the headers to return to the client
    """

    pagination_parameters = {
        constants.HEADER_REQUEST_PAGE_OFFSET: webargs.fields.Integer(
            location="headers", missing=0, validate=webargs.validate.Range(min=0)
        ),
        constants.HEADER_REQUEST_PAGE_LIMIT: webargs.fields.Integer(
            location="headers", missing=0, validate=webargs.validate.Range(min=0)
        ),
    }

    try:
        args = KeyoskParser().parse(pagination_parameters, request)
    except webargs.ValidationError as err:
        raise exceptions.InvalidPaginationParameterError(
            "Invalid values specified for result pagination",
            data={key: "; ".join(value) for key, value in err.messages.items()},
        ) from err

    try:
        processed = matches[args[constants.HEADER_REQUEST_PAGE_OFFSET] :]
    except IndexError:
        raise exceptions.IndexOutOfRangeError(
            f"Offset of '{args[constants.HEADER_REQUEST_PAGE_OFFSET]}' outside of resource range '0-{len(matches)}'",
            data={
                constants.HEADER_RESPONSE_PAGE_TOTAL: len(matches),
                constants.HEADER_RESPONSE_PAGE_LIMIT: args[
                    constants.HEADER_REQUEST_PAGE_LIMIT
                ],
                constants.HEADER_RESPONSE_PAGE_OFFSET: args[
                    constants.HEADER_REQUEST_PAGE_OFFSET
                ],
            },
        ) from None

    try:
        processed = (
            processed[: args[constants.HEADER_REQUEST_PAGE_LIMIT]]
            if args[constants.HEADER_REQUEST_PAGE_LIMIT]
            else processed
        )
    except IndexError:
        # If an index error happens here, then it means that ``limit`` is greater than the remaining
        # length of the list, after offset is applied. In this case we want to simply return
        # whatever is left in the list, so we ignore the error and move on
        pass

    return PaginationData(
        data=processed,
        headers={
            constants.HEADER_RESPONSE_PAGE_TOTAL: str(len(matches)),
            constants.HEADER_RESPONSE_PAGE_OFFSET: str(
                args[constants.HEADER_REQUEST_PAGE_OFFSET]
            ),
            constants.HEADER_RESPONSE_PAGE_LIMIT: str(
                args[constants.HEADER_REQUEST_PAGE_LIMIT]
            ),
        },
    )


class KeyoskResource(flask_restful.Resource):
    """Extension of the default :class:`flask_restful.Resource` class

    Add a couple of useful things to the default resource class:

    * Adds the :meth:`options` method to respond to HTTP OPTION requests
    * Type hints the :attr:`ROUTES` and :attr:`ARGS` attributes for usage in subclasses

    .. warning:: This class is a stub and should not be directly attached to an application

    :attribute ROUTES: Tuple of route paths that this resource should handle; can be unpacked into
                       ``flask_restful.Api().add_route()``
    :attribute ARGS: Dictionary mapping methods to their arguments for parsing
    """

    ROUTES: Tuple[str]

    ARGS: Dict[str, Union[msh.Schema, Dict[str, webargs.fields.Field]]]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    # pylint: disable=unused-argument,no-self-use
    def options(self, *args, **kwargs) -> ResponseTuple:
        """Give the supported HTTP verbs and request paramaeters for the resource"""

        verbs = ",".join([verb.upper() for verb in flask.request.url_rule.method])

        return ResponseTuple(
            body=None, code=204, headers={**{"Allowed": verbs}, **STATIC_HEADERS,},
        )

    def respond(self, data: ResponseBody, code: int = 200):
        """Create a response tuple from the current context
        Helper function for generating defaults, parsing common data, and formatting the response.
        :param data: Response data to return from the request
        :param code: Response code to return; defaults to ``200: Ok``
        :param request: Request object to use for the request context; defaults to the current flask
                        request context
        :returns: Response tuple ready to be returned out of a resource method
        .. note:: This function will handle pagination and header assembly internally. The response data
                  passed to the ``data`` parameter should be unpaginated.
        """

        if isinstance(data, list):
            pagination = make_pagination(data, flask.request)
            body = pagination.data
        else:
            pagination = None
            body = data

        headers = {**STATIC_HEADERS, **(pagination.headers if pagination else {})}

        return ResponseTuple(
            body=body if code != 204 else None, code=code, headers=headers
        )

    def _head(self, response: ResponseTuple) -> ResponseTuple:
        return ResponseTuple(body=None, code=response.code, headers=response.headers)
