from sqlalchemy import BigInteger, ForeignKey, MetaData
from sqlalchemy.orm import mapped_column, as_declarative, Mapped

metadata = MetaData()


@as_declarative(metadata=metadata)
class AbstractModel:
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)


class Team(AbstractModel):
    __tablename__ = 'team'
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)


class UserTeam(AbstractModel):
    __tablename__ = 'user_team'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('team.id'), nullable=False)


class TeamPhoto(AbstractModel):
    __tablename__ = 'team_photo'
    team_id: Mapped[int] = mapped_column(ForeignKey('team.id'), nullable=False)
    photo_path: Mapped[str] = mapped_column(unique=True, nullable=True)


class OBS(AbstractModel):
    __tablename__ = 'obs'
    host: Mapped[str] = mapped_column(nullable=False)
    port: Mapped[int] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)


class TeamOBS(AbstractModel):
    __tablename__ = 'team_obs'
    team_id: Mapped[int] = mapped_column(ForeignKey('team.id'), unique=True, nullable=False)
    obs_id: Mapped[int] = mapped_column(ForeignKey('obs.id'), unique=True, nullable=False)


class Template(AbstractModel):
    __tablename__ = 'template'
    name: Mapped[str] = mapped_column(unique=True, nullable=False)


class TeamTemplate(AbstractModel):
    __tablename__ = 'team_template'
    team_id: Mapped[int] = mapped_column(ForeignKey('team.id'), unique=True, nullable=False)
    template_id: Mapped[int] = mapped_column(ForeignKey('template.id'), nullable=False)
