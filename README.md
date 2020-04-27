**blocky** (comparative blockier, superlative blockiest)

    Resembling a block in shape.

        *The oldest video games had crude, blocky graphics.*

### Experimental branch

The build mode rely on a set of vtkPoints sent to a glyph
filter that computes the output blocks. One actor for all
the blocks. Adding blocks is really fast. Removing is
challenging (not done yet):

* Detecting the intersection with a particular block of the
set of blocks is not trivial
* Removing a point from the list of points requires data
copy


### Toolbar

- [x] build mode
- [x] delete mode
- [ ] area selection mode
- [ ] camera mode
- [ ] edit mode
- [ ] library
- [ ] settings
- [ ] help

### PRIORITY

- Refactor intersections management, code duplication between build and delete
- Fix dependency with plotter (all over the place)

### ToDo

- Add property/setter functions (i.e. Block.origin)
- Refactor selector/grid mode color
- Add support for symmetry

### Bug

- Fix bug with last floor (no block added)
- Fix `move_camera`: use unit circle coordinates (cos, sin)
