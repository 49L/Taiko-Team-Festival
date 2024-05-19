# Taiko Team Festival
 Program used to balance teams in the Taiko Team Festival.

TTF has a system where players are divided into A, B, C and D seeds based on qualifier results. Teams are formed of a single member of each seed.
The algorithm used here forms teams and tries to swap players around to minimize a metric which represents how unbalanced a team is.
The metric we have chosen has two parts :
- How close the sum of all map seedings of all players are to the expected value (how good a team is overall)
- How close the sum of map seedings of all players are to the expected value on each map (how well-rounded the team is)
A few more adjustments are made to ensure playability. Please read the code for more information on how it is actually implemented.