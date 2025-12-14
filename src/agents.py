from __future__ import annotations
from dataclasses import dataclass
import math
from mesa import Agent


@dataclass
class HouseholdProfile:
    group: str
    income: float
    commute_need: float
    caregiving_need: float
    price_sensitivity: float
    social_susceptibility: float


class HouseholdAgent(Agent):
    def __init__(self, model, profile: HouseholdProfile):
        super().__init__(model)
        self.profile = profile
        self.adopt_access = False
        self.own_car = True
        self.failed_bookings = 0
        self.success_bookings = 0

    def _base_trips_this_step(self) -> int:
        base = 1
        base += 1 if self.profile.commute_need > 0.6 else 0
        base += 1 if self.profile.caregiving_need > 0.6 else 0
        return base

    def _access_utility(self, local_adoption_rate: float) -> float:
        price = self.model.access_price
        reliability = 1.0 - self.model.booking_fail_prob
        friction = self.model.booking_friction
        supply_factor = self.model.shared_cars / max(1, self.model.num_agents)

        social = self.profile.social_susceptibility * (local_adoption_rate - 0.2)
        need_penalty = (0.8 * self.profile.caregiving_need) * (1.0 - reliability) + 0.5 * friction
        price_penalty = self.profile.price_sensitivity * price
        benefit = 1.5 + 2.0 * supply_factor + social
        return benefit - price_penalty - need_penalty

    def step(self):
        adoption_rate = self.model.current_adoption_rate()
        u = self._access_utility(adoption_rate)

        p_adopt = 1 / (1 + math.exp(-u))
        rng = self.model.random

        if (not self.adopt_access) and (rng.random() < p_adopt):
            self.adopt_access = True
            if rng.random() < self.model.prob_drop_ownership:
                self.own_car = False

        trips = self._base_trips_this_step()
        if self.adopt_access and (not self.own_car):
            for _ in range(trips):
                if self.model.try_book_shared_car():
                    self.success_bookings += 1
                else:
                    self.failed_bookings += 1
print("world")
