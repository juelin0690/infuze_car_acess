from __future__ import annotations

import numpy as np
import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector

from .agents import HouseholdAgent, HouseholdProfile


class CarAccessModel(Model):
    def __init__(
        self,
        seed: int = 42,
        num_agents: int = 500,
        shared_cars: int = 25,
        access_price: float = 0.6,
        booking_fail_prob: float = 0.10,
        booking_friction: float = 0.30,
        prob_drop_ownership: float = 0.50,
        steps: int = 100,
    ):
        super().__init__(seed=seed)  
        np.random.seed(seed)

        self.num_agents = num_agents
        self.shared_cars = shared_cars
        self.access_price = access_price
        self.booking_fail_prob = booking_fail_prob
        self.booking_friction = booking_friction
        self.prob_drop_ownership = prob_drop_ownership
        self.steps_target = steps

        self.available_cars = shared_cars

        # 关键：保存强引用
        self.households: list[HouseholdAgent] = []
        for _ in range(num_agents):
            profile = self._sample_profile()
            a = HouseholdAgent(self, profile)
            self.households.append(a)

        self.datacollector = DataCollector(
            model_reporters={
                "adoption_rate": lambda m: m.current_adoption_rate(),
                "ownership_rate": lambda m: m.current_ownership_rate(),
                "failed_booking_rate": lambda m: m.current_failed_booking_rate(),
                "shared_cars": lambda m: m.shared_cars,
                "price": lambda m: m.access_price,
                "fail_prob": lambda m: m.booking_fail_prob,
                "friction": lambda m: m.booking_friction,
            }
        )

        self.datacollector.collect(self)

    def _sample_profile(self) -> HouseholdProfile:
        rng = self.random
        group = rng.choices(["commuter", "caregiver", "budget"], weights=[0.4, 0.3, 0.3])[0]
        if group == "commuter":
            return HouseholdProfile(group, 1.2, 0.8, 0.2, 0.5, 0.4)
        if group == "caregiver":
            return HouseholdProfile(group, 1.0, 0.4, 0.9, 0.6, 0.5)
        return HouseholdProfile(group, 0.8, 0.3, 0.3, 0.9, 0.6)

    def current_adoption_rate(self) -> float:
        adopted = sum(1 for a in self.households if a.adopt_access)
        return adopted / max(1, self.num_agents)

    def current_ownership_rate(self) -> float:
        own = sum(1 for a in self.households if a.own_car)
        return own / max(1, self.num_agents)

    def current_failed_booking_rate(self) -> float:
        fails = sum(a.failed_bookings for a in self.households)
        succ = sum(a.success_bookings for a in self.households)
        return fails / max(1, fails + succ)

    def try_book_shared_car(self) -> bool:
        if self.available_cars <= 0:
            return False
        if self.random.random() < self.booking_fail_prob:
            return False
        self.available_cars -= 1
        return True

    def step(self):
        self.available_cars = self.shared_cars
        # Mesa 3：用 AgentSet 来激活（替代 RandomActivation） :contentReference[oaicite:4]{index=4}
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)

    def run_model(self) -> pd.DataFrame:
        for _ in range(self.steps_target):
            self.step()
        return self.datacollector.get_model_vars_dataframe()

print("hello world")