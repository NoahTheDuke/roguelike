# roguelike
Using the BearLibTerminal library, which is pretty excellent so far.

# Design Ideas
Suburban wasteland, possibly post-apocalypse. Takes place in a massive [Fused Grid][0] system. A square will be 4 feet, so a single quandrant will be 325 x 325 squares. That's really big, but we'll see. Procedural quadrants, then filled in with houses and shops and all that jazz, based on Richard Stephens' [Periodic Table of City Planning Elements][2].

[0]: https://en.wikipedia.org/wiki/Fused_grid
[2]: http://www.stephensplanning.com/media.html

To keep the scope small while I figure out the code, let's make it one quadrant to start. 40 - 60 houses, small road connections, 2 - 3 parks, and nothing else. If that works, I'll build it up, but not one second before.

House generation:

* One story: Living room, kitchen, bedroom, bathroom. Garage, if I'm feeling crazy!
* Template base size, marked "dark" with 0s. Carve out the living room, pick a wall and carve out the next room, incrementing the "room counter".
* Props? Chairs, desks, bookcases, beds, clothing? Close enough.
* Don't place it in the main world immediately. Find the bounds and only render those. No seeing in, no seeing out. KISS

Street sizes:

* Local streets are 5 squares wide (20 feet).
* Minor connectors are 10 squares wide (40 feet).
* Major connectors are 13 squares wide (52 feet).
* Freeways are 15-20 squares wide (60-80 feet).

# Development Ideas
Color scheme will be inspired by [Paul Tol's notes][1]. I really like how these colors look, and that they're color-blind friendly.

[1]: https://personal.sron.nl/~pault/
