**blocky** (comparative blockier, superlative blockiest)

    Resembling a block in shape.

        *The oldest video games had crude, blocky graphics.*

# Release 0.02

- [x] Refactor `load_toolbar` (the function is big and full of duplicated code)
- [x] Refactor symmetry processing
- [x] Fix `move_camera`: use unit circle coordinates (cos, sin)
- [x] Fix bug with last floor (no block added)
- [x] Refactor intersections management
- [x] Remove code duplication between build and delete

### Toolbar

- [x] build mode
- [x] delete mode
- [ ] area selection toggle (square selection or free selection)
- [ ] camera mode
- [ ] edit mode
- [ ] library
- [ ] settings
- [ ] help

### ToDo

- Add key bindings to rcParams
- The selector are duplicated in the middle when symmetry is on
- Fix dependency with plotter (all over the place)
- Add property/setter functions (i.e. Block.origin)
- Add an option to decrease opacity on blocks located in other floors
- ReDo/UnDo action buttons
- Show only the current floor (with subgrid/subsample)
- Paint mode (default painting color to build mode)
