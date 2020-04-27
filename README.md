**blocky** (comparative blockier, superlative blockiest)

    Resembling a block in shape.

        *The oldest video games had crude, blocky graphics.*

# Release 0.02

- [ ] Fix bug with last floor (no block added)
- [ ] Fix `move_camera`: use unit circle coordinates (cos, sin)
- [ ] Refactor selector/grid mode color
- [ ] Refactor symmetry processing
- [x] Refactor intersections management
- [x] Remove code duplication between build and delete

### Toolbar

- [x] build mode
- [x] delete mode
- [ ] area selection mode
- [ ] camera mode
- [ ] edit mode
- [ ] library
- [ ] settings
- [ ] help

### ToDo

- Fix dependency with plotter (all over the place)
- Add property/setter functions (i.e. Block.origin)
- Add an option to decrease opacity on blocks located in other floors
- Add key bindings to rcParams
- The selector are duplicated in the middle when symmetry is on
