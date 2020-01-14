from sqlalchemy.sql.expression import func

import application.db_models as models


def get_teams():
    """
    Return a list of teams, ordered by the last application
    submission time of a member of the team
    """
    q = models.Team.query\
        .join(models.User)\
        .join(models.Application, models.Application.user_id == models.User.id)\
        .group_by(models.User.team_id)\
        .order_by(func.max(models.Application.submitted_time).asc())
    return q
