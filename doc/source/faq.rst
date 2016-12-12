Frequently Asked Questions
==========================

.. contents::
    :local:

Where start the Swagger documentation in my function doc?
---------------------------------------------------------

:samp:`aiohttp-swagger` try to find the string :samp:`---`. When it find this string pattern, the next text until the end of function are considered Swagger doc.

Can I Combine the Swagger documentation with my usually Sphinx doc?
-------------------------------------------------------------------

Sure! Your Sphinx doc must be first of the :samp:`---` limiter.

.. code-block:: python

    async def ping(request):
        """
        This is my usually Sphinx doc

        >>> import json
        >>> ping(None)

        :param request: Context injected by aiohttp framework
        :type request: RequestHandler

        ---
        description: This end-point allow to test that service is up.
        tags:
        - Health check
        produces:
        - text/plain
        responses:
            "200":
                description: successful operation. Return "pong" text
            "405":
                description: invalid HTTP Method
        """

How can I group a list of End-Point?
------------------------------------

End-Point will be grouped by their title. The end-point with the same title will be grouped automatically:

.. image:: _static/swagger_title.jpg

How can I change the Title of a group of End-Points?
----------------------------------------------------
Swagger has a tag that uses to build the titles. The tag name is :samp:`tags`. The format is:

.. code-block:: yaml

    tags:  # <-- TAG USEF FOR THE TITLE
    - Health check
    description: This end-point allow to test that service is up.
    produces:
    - text/plain
    responses:
        "200":
            description: successful operation. Return "pong" text
        "405":
            description: invalid HTTP Method

What happens if I use YAML file and function documentation for build Swagger doc at the same time?
--------------------------------------------------------------------------------------------------

If two method are provided, :samp:`aiohttp-swagger` will use the YAML over the function doc.
