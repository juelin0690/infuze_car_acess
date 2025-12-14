from __future__ import annotations
from dataclasses import dataclass
import random
from mesa import Agent


@dataclass
class HouseholdProfile:
    """Simple heterogeneity container."""
    group: str              # "commuter" | "caregiver" | "budget"
    income: float           # proxy
    commute_need: float     # 0-1
    caregiving_need: float  # 0-1
    price_sensitivity: float  # 0-1
    social_susceptibility: float  # 0-1


class HouseholdAgent(Agent):
    """
    Decision: own-car vs access-car (shared).
    Track adoption, failed bookings, and utility.
    """
    def __init__(self, model, profile: HouseholdProfile):
        super().__init__(model)
        self.profile = profile

        self.adopt_access = False
        self.own_car = True  # start from ownership-heavy world
        self.failed_bookings = 0
        self.success_bookings = 0

    def _base_trips_this_step(self) -> int:
        """Generate a small number of trips per step based on needs."""
        base = 1
        # commuters travel more often; caregivers more complex but here we proxy via extra trips
        base += 1 if self.profile.commute_need > 0.6 else 0
        base += 1 if self.profile.caregiving_need > 0.6 else 0
        return base

    def _access_utility(self, local_adoption_rate: float) -> float:
        """
        Stylized utility of using access (shared) instead of owning.
        Higher is better.
        """
        price = self.model.access_price
        reliability = 1.0 - self.model.booking_fail_prob  # simple proxy
        friction = self.model.booking_friction            # larger = worse
        supply_factor = self.model.shared_cars / max(1, self.model.num_agents)

        # Social influence: adoption rises if neighbors adopt (here: global proxy)
        social = self.profile.social_susceptibility * (local_adoption_rate - 0.2)

        # Needs: caregivers dislike friction/reliability issues more
        need_penalty = (0.8 * self.profile.caregiving_need) * (1.0 - reliability) + 0.5 * friction

        # Price sensitivity
        price_penalty = self.profile.price_sensitivity * price

        # Benefit from not owning: fixed benefit baseline
        benefit = 1.5 + 2.0 * supply_factor + social

        return benefit - price_penalty - need_penalty

    def step(self):
        # local adoption proxy (you can replace with spatial neighborhood later)
        adoption_rate = self.model.current_adoption_rate()

        # Decide whether to adopt access-car this step
        u = self._access_utility(adoption_rate)

        # Convert utility to probability (simple logistic-ish)
        p_adopt = 1 / (1 + (2.71828 ** (-u)))
        if (not self.adopt_access) and (random.random() < p_adopt):
            self.adopt_access = True
            # Once adopted, some may sell/stop relying on own car
            if random.random() < self.model.prob_drop_ownership:
                self.own_car = False

        # Simulate trips and bookings if adopted and not owning
        trips = self._base_trips_this_step()
        if self.adopt_access and (not self.own_car):
            for _ in range(trips):
                ok = self.model.try_book_shared_car()
                if ok:
                    self.success_bookings += 1
                else:
                    self.failed_bookings += 1
