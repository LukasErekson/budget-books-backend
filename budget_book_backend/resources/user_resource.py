import json
from flask_restful import Resource


class UserResource(Resource):
    """User Resource. For getting user authentication data and making
    changes to the user's account.
    """

    def get(self):
        """Get the current user given the user id. For now, defaults to
        development user with id of 0.
        """

        return (
            json.dumps(
                dict(
                    user_id=0,
                    name="Dev",
                )
            ),
            200,
        )
