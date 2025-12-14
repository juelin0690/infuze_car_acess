# infuze_car_acess(Mesa) — from ownership to on-demand access

## Research question
How do availability, booking friction, and social influence affect the transition from car ownership to car access?

## Why this matters (INFUZE context)
Short paragraph linking to: reducing car dependence while maintaining mobility, equity across groups, real-world trials.

## Model overview
- Agents: heterogeneous households (commuter / caregiver / budget)
- Decision: adopt access-car; possibly drop ownership
- System constraints: limited shared cars per step; booking failures
- Social influence: adoption increases with observed adoption rate (placeholder for spatial network)

## Key assumptions
List 5–8 assumptions + parameter ranges.

## Experiments
Scenario grid:
- shared_cars: 10 / 25 / 50
- booking_friction: 0.2 / 0.4 / 0.6
Report metrics:
- adoption_rate, ownership_rate, failed_booking_rate
- (optional) group-level equity metrics

## Results (what to expect)
- More supply -> higher adoption
- More friction -> lower adoption
- Equity: caregivers more sensitive to reliability/friction

## Reproducibility
```bash
pip install -r requirements.txt
python -m src.run
python -m src.experiments
