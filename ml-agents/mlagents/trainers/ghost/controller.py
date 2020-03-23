from typing import Deque, Dict
from collections import deque
from mlagents.trainers.ghost.trainer import GhostTrainer


class GhostController(object):
    """
    GhostController contains a queue of team ids. GhostTrainers subscribe to the GhostController and query
    it to get the current learning team.  The GhostController cycles through team ids every 'swap_interval'
    which corresponds to the number of trainer steps between changing learning teams.
    """

    def __init__(self, swap_interval: int, maxlen: int = 10):
        """
        Create a GhostController.
        :param swap_interval: Number of trainer steps between changing learning teams.
        :param maxlen: Maximum number of GhostTrainers allowed in this GhostController
        """

        self._swap_interval = swap_interval
        # Tracks last swap step for  each learning team because trainer
        # steps of all GhostTrainers do not increment together
        self._last_swap: Dict[int, int] = {}
        self._queue: Deque[int] = deque(maxlen=maxlen)
        self._learning_team: int = -1
        # Dict from team id to GhostTrainer
        self._ghost_trainers: Dict[int, GhostTrainer] = {}

    def subscribe_team_id(self, team_id: int, trainer: GhostTrainer) -> None:
        """
        Given a team_id and trainer, add to queue and trainers if not already.
        The GhostTrainer is used later by the controller to get ELO ratings of agents.
        :param team_id: The team_id of an agent managed by this GhostTrainer
        :param trainer: A GhostTrainer that manages this team_id.
        """
        if team_id not in self._ghost_trainers:
            self._ghost_trainers[team_id] = trainer
            self._last_swap[team_id] = 0
            if self._learning_team < 0:
                self._learning_team = team_id
            else:
                self._queue.append(team_id)

    def get_learning_team(self, step: int) -> int:
        """
        Returns the current learning team. If 'swap_interval' steps have elapsed, the current
        learning team is added to the end of the queue and then updated with the next in line.
        :param step: Current step of the trainer.
        :return: The learning team id
        """
        if step >= self._swap_interval + self._last_swap[self._learning_team]:
            self._last_swap[self._learning_team] = step
            self._queue.append(self._learning_team)
            self._learning_team = self._queue.popleft()
        return self._learning_team

    # Adapted from https://github.com/Unity-Technologies/ml-agents/pull/1975 and
    # https://metinmediamath.wordpress.com/2013/11/27/how-to-calculate-the-elo-rating-including-example/
    # ELO calculation
    # TODO : Generalize this to more than two teams
    def compute_elo_rating_changes(self, rating: float, result: float) -> float:
        """
        Calculates ELO. Given the rating of the learning team and result.  The GhostController
        queries the other GhostTrainers for the ELO of their agent that is currently being deployed.
        Note, this could be the current agent or a past snapshot.
        :param rating: Rating of the learning team.
        :param result: Win, loss, or draw from the perspective of the learning team.
        :return: The change in ELO.
        """
        opponent_rating: float = 0.0
        for team_id, trainer in self._ghost_trainers.items():
            if team_id != self._learning_team:
                opponent_rating = trainer.get_opponent_elo()
        r1 = pow(10, rating / 400)
        r2 = pow(10, opponent_rating / 400)

        summed = r1 + r2
        e1 = r1 / summed

        change = result - e1
        for team_id, trainer in self._ghost_trainers.items():
            if team_id != self._learning_team:
                trainer.change_opponent_elo(change)

        return change