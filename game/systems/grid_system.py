import pygame

class GridSystem:
    def __init__(self, width=10, height=8, cell_size=60):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.offset_x = 100
        self.offset_y = 80
    
    def get_grid_position(self, screen_pos):
        x, y = screen_pos
        grid_x = (x - self.offset_x) // self.cell_size
        grid_y = (y - self.offset_y) // self.cell_size
        return (int(grid_x), int(grid_y))
    
    def get_screen_position(self, grid_pos):
        grid_x, grid_y = grid_pos
        screen_x = grid_x * self.cell_size + self.offset_x
        screen_y = grid_y * self.cell_size + self.offset_y
        return (screen_x, screen_y)
    
    def is_valid_position(self, grid_pos):
        x, y = grid_pos
        return 0 <= x < self.width and 0 <= y < self.height
    
    def draw(self, screen):
        for x in range(self.width):
            for y in range(self.height):
                rect = pygame.Rect(
                    x * self.cell_size + self.offset_x,
                    y * self.cell_size + self.offset_y,
                    self.cell_size, self.cell_size
                )
                pygame.draw.rect(screen, (50, 50, 80), rect, 1)