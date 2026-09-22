"""Falling Sand Simulation — assignment 2.
"""

from __future__ import annotations

from enum import IntEnum

import numpy as np
import pygame


class Material(IntEnum):


    EMPTY = 0
    SAND = 1
    WATER = 2

    # BONUS: TODO Later
    # WALL = 3   (immovable — never update it)
    # FIRE = 4   (lives a few ticks, then becomes EMPTY)
    # SMOKE = 5  (rises instead of falling, then fades)



PALETTE = {
    Material.EMPTY: (0, 0, 0),
    Material.SAND: (194, 178, 128),
    Material.WATER: (52, 120, 235),
}


_COLORS = np.array([PALETTE[m] for m in Material], dtype=np.uint8)


_rng = np.random.default_rng()


class SandSim:
    """Holds the grid and does the physics + rendering.

    The grid is ``self._types``, a 2D NumPy array of shape (HEIGHT, WIDTH)
    where grid[y, x] is the material at row ``y`` (0 = top) and column
    ``x`` (0 = left).
    """

    def __init__(self, width: int, height: int, cell_size: int = 4, fps: int = 60) -> None:
        self.cell_size = cell_size
        self.fps = fps
        self.brush = Material.SAND
        self.brush_radius = 2
        self.resize_cells(width, height)

    # ------------------------------------------------------------------ #
    # Grid lifecycle
    # ------------------------------------------------------------------ #
    def resize_cells(self, width: int, height: int) -> None:
        """Replace the grid with a fresh empty one of the given size."""
        self.width = int(width)
        self.height = int(height)
        # NumPy fills with zeros = Material.EMPTY. Good.
        self._types = np.zeros((self.height, self.width), dtype=np.uint8)

    def clear(self) -> None:
        """Reset every cell to empty space."""
        self._types[:] = 0

    # ------------------------------------------------------------------ #
    # Painting (mouse input)
    # ------------------------------------------------------------------ #
    def paint_at(self, x: int, y: int) -> None:
        """Place the current brush material in a disc of cells at (x, y).

        ``x``/``y`` are in *grid* coordinates (screen pixels / cell_size).
        """
        r = self.brush_radius
        x0, x1 = max(0, x - r), min(self.width, x + r + 1)
        y0, y1 = max(0, y - r), min(self.height, y + r + 1)
        if x1 <= x0 or y1 <= y0:
            return
        # mgrid gives two grids of y- and x-coordinates over the block;
        # the `disc` mask keeps only cells within a circle of radius r.
        yy, xx = np.mgrid[y0:y1, x0:x1]
        disc = ((xx - x) ** 2 + (yy - y) ** 2) <= r * r
        xs, ys = xx[disc], yy[disc]
        self._types[ys, xs] = int(self.brush)

    # ------------------------------------------------------------------ #
    # Physics
    # ------------------------------------------------------------------ #
    def update(self) -> None:

        old = self._types
        new = old.copy()
        H, W = self.height, self.width

        for y in range(H - 1, -1, -1):
            xs = np.flatnonzero(old[y])
            if xs.size == 0:
                continue
            xs = _rng.permutation(xs)


            for x in xs:
                x = int(x)
                m = old[y, x]
                if m != Material.SAND and m != Material.WATER:
                    continue

                if y + 1 < H:
                    if new[y + 1, x] == Material.EMPTY:
                        new[y + 1, x] = m
                        new[y, x] = Material.EMPTY
                        continue


                    left = x>0 and new[y + 1, x - 1] == Material.EMPTY
                    right = x + 1 < W and new[y + 1, x + 1] == Material.EMPTY
                    if left and right:
                        dx = -1 if _rng.random() < 0.5 else 1
                    elif left:
                        dx = -1
                    elif right:
                        dx = 1
                    else:
                        dx = 0

                    if dx:
                        new[y + 1, x + dx] = m
                        new[y, x] = Material.EMPTY
                        continue

                if m == Material.WATER:
                    left = x>0 and new[y, x - 1] == Material.EMPTY
                    right = x + 1 < W and new[y, x + 1] == Material.EMPTY
                    if left and right:
                        dx = -1 if _rng.random() < 0.5 else 1
                    elif left:
                        dx = -1
                    elif right:
                        dx = 1
                    else:
                        dx = 0

                    if dx:
                        new[y, x + dx] = m
                        new[y, x] = Material.EMPTY

        self._types = new

    # ------------------------------------------------------------------ #
    # Rendering (boilerplate — nothing to do here)
    # ------------------------------------------------------------------ #
    def surface(self) -> pygame.Surface:
        """Snapshot the grid as a pygame.Surface, scaled up by cell_size.

        _COLORS[grid] turns the cell-material grid into a grid of RGB
        pixels in one shot. pygame expects the axes as (WIDTH, HEIGHT),
        numpy stores them as (HEIGHT, WIDTH), so transpose swaps them back.
        """
        rgb = _COLORS[self._types]
        surf = pygame.surfarray.make_surface(
            np.ascontiguousarray(np.transpose(rgb, (1, 0, 2)))
        )
        if self.cell_size > 1:
            surf = pygame.transform.scale(
                surf, (self.width * self.cell_size, self.height * self.cell_size)
            )
        return surf


def main() -> None:
    """Setup + event loop. Boilerplate — nothing to do here."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Falling Sand — 1 sand, 2 water, 0 erase, [ ] brush, C clear")
    clock = pygame.time.Clock()

    sim = SandSim(800 // 4, 600 // 4)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    running = False
                elif k == pygame.K_1:
                    sim.brush = Material.SAND
                elif k == pygame.K_2:
                    sim.brush = Material.WATER
                elif k in (pygame.K_0, pygame.K_e):
                    sim.brush = Material.EMPTY
                elif k == pygame.K_LEFTBRACKET:
                    sim.brush_radius = max(1, sim.brush_radius - 1)
                elif k == pygame.K_RIGHTBRACKET:
                    sim.brush_radius = min(40, sim.brush_radius + 1)
                elif k == pygame.K_c:
                    sim.clear()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                sim.resize_cells(event.size[0] // sim.cell_size, event.size[1] // sim.cell_size)

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            sim.paint_at(mx // sim.cell_size, my // sim.cell_size)

        sim.update()
        screen.blit(sim.surface(), (0, 0))

        pygame.display.flip()
        clock.tick(sim.fps)

    pygame.quit()


if __name__ == "__main__":
    main()