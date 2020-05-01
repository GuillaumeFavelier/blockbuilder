### blockbuilder

<details open>

<summary><b>Milestone 0.03</b></summary>

</details>

<details>

<summary><b>Milestone 0.02</b></summary>

- [x] Refactor `load_toolbar` (the function is big and full of duplicated code)
- [x] Refactor symmetry processing
- [x] Fix `move_camera`: use unit circle coordinates (cos, sin)
- [x] Fix bug with last floor (no block added)
- [x] Refactor intersections management
- [x] Remove code duplication between build and delete

</details>

#### ToDo

- Add key bindings to rcParams
- The selector are duplicated in the middle when symmetry is on
- Fix dependency with plotter (all over the place)
- Add property/setter functions (i.e. Block.origin)
- ReDo/UnDo action buttons
- Show only the current floor (with subgrid/subsample)
- Paint mode (default painting color to build mode)
- Add suppport for library (reuse previously built blockset)
- Add basic help
- Add a way to configure the app settings
- Add an area selection toggle (square selection or free selection)
- Add a way to change the geometry of a block (deletion of block vertices)
- Add a way to control the camera with the mouse right-click
- Add directory `changes` and use one changelog for each release
