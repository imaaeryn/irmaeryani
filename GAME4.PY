import pygame
import sys
import time
import os
from bird import Bird
from cloud import Cloud

pygame.init()
pygame.mixer.init()

pygame.display.set_caption("Lillyimaa Sky Bird")

icon = pygame.image.load("assets/gmbar/bird1.png")
pygame.display.set_icon(icon)

bg_music = pygame.mixer.Sound("assets/audio/background_music.mp3")
flap_sound = pygame.mixer.Sound("assets/audio/swoosh.wav")
game_over_sound = pygame.mixer.Sound("assets/audio/die.wav")
point_sound = pygame.mixer.Sound("assets/audio/score.wav")

bg_music.play(-1)

class Button:
    def __init__(self, x, y, width, height, text, font, base_color, hover_color):
        #inisialisasi tombol menu
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.color = base_color
        self.text_surf = font.render(text, True, (0, 0, 0))
        self.text_rect = self.text_surf.get_rect(center=(x + width // 2, y + height // 2))

    def draw(self, surface):
        surface.blit(self.text_surf, self.text_rect)

    def is_hovered(self):
        #untuk menempatkan atau mengecek apakah mouse berada di dalam menu
        mouse_pos = pygame.mouse.get_pos()
        return self.text_rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered():
                return True
        return False

    def update(self):
        if self.is_hovered():
            self.text_surf = self.font.render(self.text, True, self.hover_color)
        else:
            self.text_surf = self.font.render(self.text, True, self.base_color)

class Game:
    def __init__(self):
         # inisialisasi layar game
        self.width = 500
        self.height = 560
        self.scale_factor = 2
        self.win = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.move_speed = 260
        self.font = pygame.font.Font(None, 36)
        self.bird = Bird(self.scale_factor)

        self.score = 0
        self.high_score = self.loadHighScore()
        self.is_enter_pressed = False
        self.clouds = []
        self.cloud_generate_counter = 30
        self.setUpBgAndGround()

        self.state = "main_menu"
        self.setupButtons()

        self.last_time = time.time()

        self.gameLoop()

    def loadHighScore(self):
        #untk memuat score tertinggi
        if os.path.exists("high_score.txt"):
            with open("high_score.txt", "r") as file:
                return int(file.read())
        return 0

    def saveHighScore(self):
        #menyimpan score
        with open("high_score.txt", "w") as file:
            file.write(str(self.high_score))

    def setupButtons(self):
        # tml menu yang ada di game
        font = pygame.font.SysFont(None, 50)
        self.start_button = Button(self.width // 2 - 100 , self.height // 2 - 90, 200, 60, "Start", font, (0, 0, 0), (62, 254, 255))
        self.quit_button = Button(self.width // 2 - 100, self.height // 2 + 30, 200, 60, "Exit", font, (25, 154, 221), (62, 254, 255))
        self.restart_button = Button(self.width // 2 - 200, self.height // 2 + 60, 150, 60, "Play again", font, (255, 0, 0), (62, 254, 255))
        self.exit_button = Button(self.width // 2 + 50, self.height // 2 + 60, 150, 60, "Exit", font, (25, 154, 221), (62, 254, 255))

    def gameLoop(self):
        while True:
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    self.resizeWindow(event.w, event.h)

                if self.state == "main_menu":
                    if self.start_button.is_clicked(event):
                        self.state = "playing"
                        self.is_enter_pressed = True
                        self.bird.update_on = True
                    elif self.quit_button.is_clicked(event):
                        pygame.quit()
                        sys.exit()
                elif self.state == "game_over":
                    if self.restart_button.is_clicked(event):
                        self.resetGame()
                        self.state = "playing"
                        self.is_enter_pressed = True
                    elif self.exit_button.is_clicked(event):
                        pygame.quit()
                        sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == "playing":
                        self.bird.flap(dt)
                        flap_sound.play()

            if self.state == "playing":
                self.updateEverything(dt)
                self.checkCollisions()

            self.drawEverything()
            pygame.display.update()
            self.clock.tick(60)

    def checkScore(self):
        # mengupdate skor jika burung melewati awan
        for cloud in self.clouds:
            if not cloud.passed and cloud.rect.right < self.bird.rect.left:
                cloud.passed = True
                self.score += 1
                point_sound.play()

    def resizeWindow(self, width, height):
        # menyesuaikan ukuran jendela resizable
        self.width = width
        self.height = height
        self.win = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.setUpBgAndGround()
        self.setupButtons()

    def checkCollisions(self):
        bird_rect = self.bird.rect

        for cloud in self.clouds:
            if cloud.rect.colliderect(bird_rect.inflate(-30, -30)):
                self.gameOver()
                return

        if bird_rect.bottom >= self.ground1_rect.top:
            self.gameOver()

    def resetGame(self):
        # untk game agar kembali ke awal
        self.bird = Bird(self.scale_factor)
        self.clouds = []
        self.cloud_generate_counter = 30
        self.is_enter_pressed = False
        self.score = 0
        self.last_time = time.time()

    def gameOver(self):
        # mengatur kondsi gameover
        self.state = "game_over"
        self.is_enter_pressed = False
        if self.score > self.high_score:
            self.high_score = self.score
            self.saveHighScore()
        game_over_sound.play()

    def updateEverything(self, dt):
        #mengupdate semua elemen dalam game
        if self.is_enter_pressed:
            # memindahkan posisi ground1 dan ground2 ke kirim berdasarkan kecepatan
            self.ground1_rect.x -= int(self.move_speed * dt)
            self.ground2_rect.x -= int(self.move_speed * dt)

            if self.ground1_rect.right < 0:
                self.ground1_rect.x = self.ground2_rect.right
            if self.ground2_rect.right < 0:
                self.ground2_rect.x = self.ground1_rect.right

              # untk membuat awan baru
            if self.cloud_generate_counter > 70:
                new_cloud = Cloud(self.width, self.height, self.scale_factor, self.move_speed)
                new_cloud.rect.x = self.width + 20
                self.clouds.append(new_cloud)
                self.cloud_generate_counter = 0

            self.cloud_generate_counter += 1

            for cloud in self.clouds:
                cloud.update(dt)

               # menghapus awan jika sudah keluar layar
            if len(self.clouds) != 0:
                if self.clouds[0].rect.right < 0:
                    self.clouds.pop(0)

            self.checkScore()

        self.bird.update(dt)


    def drawEverything(self):
        # menggambar semua elemen
        self.win.blit(self.bg_img, (0, 0))
        for cloud in self.clouds:
            cloud.drawCloud(self.win)
        self.win.blit(self.ground1_img, self.ground1_rect)
        self.win.blit(self.ground2_img, self.ground2_rect)
        self.win.blit(self.bird.image, self.bird.rect)

        if self.state == "main_menu":
            self.drawMainMenu()
        elif self.state == "game_over":
            self.drawGameOverMenu()
        elif self.state == "playing":
            self.drawScore()

    def drawMainMenu(self):
        self.start_button.update()
        self.start_button.draw(self.win)
        self.quit_button.update()
        self.quit_button.draw(self.win)

    def drawGameOverMenu(self):
        font = pygame.font.SysFont(None, 55)

        game_over_text = font.render("Game Over", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 70))
        self.win.blit(game_over_text, game_over_rect.topleft)

        score_text = font.render(f'Score: {self.score}', True, (25, 154, 221))
        score_rect = score_text.get_rect(center=(self.width // 2, game_over_rect.bottom + 30))
        self.win.blit(score_text, score_rect.topleft)

        high_score_surf = self.font.render(f'High Score: {self.high_score}', True, (25, 154, 221))
        high_score_rect = high_score_surf.get_rect(center=(self.width // 2, score_rect.bottom + 30))
        self.win.blit(high_score_surf, high_score_rect.topleft)

        self.restart_button.update()
        self.restart_button.draw(self.win)
        self.exit_button.update()
        self.exit_button.draw(self.win)

    def drawScore(self):
        score_surf = self.font.render(f'Score: {self.score}', True, (25, 154, 221))
        score_rect = score_surf.get_rect(center=(self.width // 2, 30))
        self.win.blit(score_surf, score_rect)

    def setUpBgAndGround(self):
        bg_img_original = pygame.image.load("assets/gmbar/bacgroun2.png").convert()
        self.bg_img = pygame.transform.scale(bg_img_original, (self.width, self.height))

        ground_img_original = pygame.image.load("assets/gmbar/ground.png").convert()
        ground_height = int(ground_img_original.get_height() * self.scale_factor)
        ground_width = int(self.width * 2)
        self.ground1_img = pygame.transform.scale(ground_img_original, (ground_width, ground_height))
        self.ground2_img = pygame.transform.scale(ground_img_original, (ground_width, ground_height))

        self.ground1_rect = self.ground1_img.get_rect()
        self.ground2_rect = self.ground2_img.get_rect()

        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.ground1_rect.y = self.height - ground_height
        self.ground2_rect.y = self.height - ground_height

game = Game()
