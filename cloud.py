import pygame
import random

class Cloud:
    def __init__(self, game_width, game_height, scale_factor, move_speed):
        self.image = pygame.image.load("assets/gmbar/cloud.png").convert_alpha()
        scale_factor = random.uniform(0.2, 0.2)  
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale_factor), int(self.image.get_height() * scale_factor)))
        self.rect = self.image.get_rect()
        self.rect.x = game_width
        self.ground_height = int(game_height * 0.3)  
        self.rect.y = random.randint(20, game_height - self.rect.height - self.ground_height - 30)  

        self.passed = False
        self.move_speed = move_speed
        self.vertical_speed = 10
        self.direction = 1  
        self.zigzag_counter = 0  

    def update(self, dt):
        self.rect.x -= int(self.move_speed * dt)
        self.rect.y += int(self.direction * self.vertical_speed * dt)
        self.zigzag_counter += 1

        if self.zigzag_counter >= 10:
            self.direction *= -1
            self.zigzag_counter = 0

        if self.rect.y < 50:
            self.rect.y = 40
            self.direction = 1
        elif self.rect.y > pygame.display.get_surface().get_height() - self.rect.height - self.ground_height - 60:
            self.rect.y = pygame.display.get_surface().get_height() - self.rect.height - self.ground_height - 60
            self.direction = -1

    def drawCloud(self, surface):
        surface.blit(self.image, self.rect)
