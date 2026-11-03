
import pygame
import random
import math
import sys
import array

# ==========================================
# INITIALIZATION
# ==========================================

pygame.init()

FPS = 60

# Create fullscreen display first
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

# Get the actual fullscreen dimensions
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Balloon Pop: Rainbow Challenge")
clock = pygame.time.Clock()

# ==========================================
# SOUND SYSTEM
# ==========================================

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
    SOUND_ENABLED = True
except pygame.error:
    SOUND_ENABLED = False


def create_sound(start_freq, end_freq, duration, volume=0.4):
    if not SOUND_ENABLED:
        return None

    sample_rate = 22050
    total_samples = int(sample_rate * duration)
    samples = array.array("h")

    for i in range(total_samples):
        t = i / total_samples
        frequency = start_freq + (end_freq - start_freq) * t
        envelope = (1 - t) ** 2
        value = math.sin(2 * math.pi * frequency * i / sample_rate)
        samples.append(int(32767 * volume * envelope * value))

    return pygame.mixer.Sound(buffer=samples.tobytes())


sounds = {}

if SOUND_ENABLED:
    sounds["pop"] = create_sound(850, 250, 0.12, 0.4)
    sounds["bonus"] = create_sound(500, 1400, 0.35, 0.4)
    sounds["bomb"] = create_sound(180, 45, 0.5, 0.6)
    sounds["gameover"] = create_sound(500, 100, 0.8, 0.4)
    sounds["start"] = create_sound(400, 900, 0.2, 0.3)


def play_sound(name):
    if SOUND_ENABLED and sounds.get(name):
        sounds[name].play()


# ==========================================
# COLOURS
# ==========================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (20, 15, 40)

MAGENTA = (230, 20, 130)
PURPLE = (145, 55, 220)
DARK_BLUE = (20, 45, 120)
YELLOW = (255, 220, 40)

BALLOON_COLORS = [MAGENTA, PURPLE, DARK_BLUE, WHITE, YELLOW]

BG_TOP = (12, 15, 45)
BG_BOTTOM = (55, 25, 85)

# ==========================================
# FONTS
# ==========================================

UI_SCALE = min(WIDTH / 900, HEIGHT / 650)

title_font = pygame.font.SysFont(
    "comicsansms", max(32, int(54 * UI_SCALE)), bold=True
)
large_font = pygame.font.SysFont(
    "arial", max(26, int(42 * UI_SCALE)), bold=True
)
medium_font = pygame.font.SysFont(
    "arial", max(18, int(27 * UI_SCALE)), bold=True
)
small_font = pygame.font.SysFont(
    "arial", max(14, int(20 * UI_SCALE))
)

# ==========================================
# GAME SETTINGS
# ==========================================

GAME_DURATION = 60
STARTING_LIVES = 5

# ==========================================
# BACKGROUND
# ==========================================

def draw_background():
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = tuple(
            int(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t)
            for i in range(3)
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

    for i in range(45):
        x = (i * 137) % WIDTH
        y = (i * 83) % HEIGHT

        brightness = 130 + int(
            100 * abs(math.sin(pygame.time.get_ticks() / 800 + i))
        )

        pygame.draw.circle(
            screen, (brightness, brightness, brightness), (x, y), 1
        )


# ==========================================
# CLOUD CLASS
# ==========================================

class Cloud:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = y
        self.speed = random.uniform(0.25, 0.65)
        self.scale = random.uniform(0.7, 1.3)

    def update(self):
        self.x += self.speed
        if self.x > WIDTH + 100:
            self.x = -150

    def draw(self):
        x = int(self.x)
        y = int(self.y)
        color = (220, 215, 245)

        pygame.draw.circle(
            screen, color, (x, y), int(22 * self.scale)
        )
        pygame.draw.circle(
            screen, color,
            (x + int(25 * self.scale), y - int(12 * self.scale)),
            int(28 * self.scale)
        )
        pygame.draw.circle(
            screen, color,
            (x + int(52 * self.scale), y),
            int(22 * self.scale)
        )
        pygame.draw.ellipse(
            screen, color,
            (
                x - int(5 * self.scale), y,
                int(65 * self.scale), int(25 * self.scale)
            )
        )


clouds = [
    Cloud(int(WIDTH * 0.09), int(HEIGHT * 0.18)),
    Cloud(int(WIDTH * 0.39), int(HEIGHT * 0.13)),
    Cloud(int(WIDTH * 0.72), int(HEIGHT * 0.25)),
    Cloud(int(WIDTH * 0.88), int(HEIGHT * 0.46)),
    Cloud(int(WIDTH * 0.20), int(HEIGHT * 0.62))
]


def draw_clouds():
    for cloud in clouds:
        cloud.update()
        cloud.draw()


# ==========================================
# BALLOON CLASS
# ==========================================

class Balloon:
    def __init__(self):
        self.radius = random.randint(24, 35)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = HEIGHT + self.radius
        self.speed = random.uniform(2.0, 3.5)

        self.wobble = random.uniform(0, 6.28)
        self.wobble_speed = random.uniform(0.04, 0.08)
        self.color = random.choice(BALLOON_COLORS)

        chance = random.random()

        if chance < 0.10:
            self.kind = "bonus"
        elif chance < 0.22:
            self.kind = "bomb"
        else:
            self.kind = "normal"

    def update(self, difficulty):
        self.y -= self.speed + difficulty
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * 0.8

    def draw(self):
        x = int(self.x)
        y = int(self.y)

        if self.kind == "bomb":
            color = (35, 35, 45)
        elif self.kind == "bonus":
            color = YELLOW
        else:
            color = self.color

        pygame.draw.ellipse(
            screen, color,
            (
                x - self.radius, y - self.radius,
                self.radius * 2, int(self.radius * 2.3)
            )
        )

        pygame.draw.ellipse(
            screen, WHITE,
            (
                x - self.radius, y - self.radius,
                self.radius * 2, int(self.radius * 2.3)
            ), 2
        )

        pygame.draw.ellipse(
            screen, WHITE,
            (
                x - self.radius // 2, y - self.radius // 2,
                8, 16
            )
        )

        pygame.draw.polygon(
            screen, color,
            [
                (x - 5, y + self.radius * 2),
                (x + 5, y + self.radius * 2),
                (x, y + self.radius * 2 + 9)
            ]
        )

        pygame.draw.line(
            screen, WHITE,
            (x, y + self.radius * 2 + 9),
            (x + 3, y + self.radius * 2 + 27),
            1
        )

        if self.kind == "bonus":
            star = medium_font.render("★", True, WHITE)
            screen.blit(star, star.get_rect(center=(x, y)))

        if self.kind == "bomb":
            bomb_text = medium_font.render("!", True, WHITE)
            screen.blit(bomb_text, bomb_text.get_rect(center=(x, y)))

    def clicked(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y

        return dx * dx + dy * dy <= self.radius * self.radius * 1.5


# ==========================================
# PARTICLE CLASS
# ==========================================

class Particle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 35
        self.radius = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(
                screen, self.color,
                (int(self.x), int(self.y)),
                max(1, self.radius)
            )


# ==========================================
# MAIN GAME CLASS
# ==========================================

class BalloonPopGame:
    def __init__(self):
        self.state = "menu"
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.lives = STARTING_LIVES
        self.time_left = GAME_DURATION

        self.start_ticks = pygame.time.get_ticks()
        self.pause_time = 0

        self.balloons = []
        self.particles = []

        self.spawn_timer = 0
        self.spawn_interval = 850
        self.difficulty = 0
        self.bonus_end_time = 0

    # ======================================
    # DRAW TEXT
    # ======================================

    def draw_text(self, text, font, color, x, y):
        image = font.render(text, True, color)
        rect = image.get_rect(center=(x, y))
        screen.blit(image, rect)

    # ======================================
    # BUTTON
    # ======================================

    def draw_button(self, text, x, y, width, height):
        rect = pygame.Rect(x, y, width, height)

        pygame.draw.rect(
            screen, (120, 50, 190), rect, border_radius=15
        )
        pygame.draw.rect(
            screen, WHITE, rect, 2, border_radius=15
        )

        self.draw_text(
            text, medium_font, WHITE,
            x + width // 2, y + height // 2
        )

        return rect

    # ======================================
    # MENU SCREEN
    # ======================================

    def draw_menu(self):
        draw_background()
        draw_clouds()

        self.draw_text(
            "BALLOON POP", title_font, MAGENTA,
            WIDTH // 2, int(HEIGHT * 0.23)
        )

        self.draw_text(
            "RAINBOW CHALLENGE", large_font, YELLOW,
            WIDTH // 2, int(HEIGHT * 0.33)
        )

        self.draw_text(
            "Pop balloons and get the highest score!",
            medium_font, WHITE,
            WIDTH // 2, int(HEIGHT * 0.46)
        )

        self.draw_text(
            "Normal: +10     Bonus: +25",
            small_font, WHITE,
            WIDTH // 2, int(HEIGHT * 0.55)
        )

        self.draw_text(
            "Missing balloons does not cost lives!",
            small_font, (180, 255, 180),
            WIDTH // 2, int(HEIGHT * 0.60)
        )

        button_width = int(220 * UI_SCALE)
        button_height = int(60 * UI_SCALE)

        self.start_button = self.draw_button(
            "START GAME",
            WIDTH // 2 - button_width // 2,
            int(HEIGHT * 0.69),
            button_width,
            button_height
        )

        self.draw_text(
            "Click balloons | P: Pause | ESC: Quit",
            small_font, WHITE,
            WIDTH // 2, int(HEIGHT * 0.86)
        )

    # ======================================
    # HUD
    # ======================================

    def draw_hud(self):
        pygame.draw.rect(
            screen, (15, 12, 35), (0, 0, WIDTH, 65)
        )

        self.draw_text(
            f"Score: {self.score}", medium_font, YELLOW,
            int(WIDTH * 0.13), 32
        )

        self.draw_text(
            f"Lives: {self.lives}", medium_font, WHITE,
            int(WIDTH * 0.39), 32
        )

        self.draw_text(
            f"Time: {self.time_left}", medium_font, MAGENTA,
            int(WIDTH * 0.65), 32
        )

        if pygame.time.get_ticks() < self.bonus_end_time:
            self.draw_text(
                "DOUBLE SCORE!", medium_font, YELLOW,
                int(WIDTH * 0.87), 32
            )

    # ======================================
    # GAME SCREEN
    # ======================================

    def draw_game(self):
        draw_background()
        draw_clouds()

        for balloon in self.balloons:
            balloon.draw()

        for particle in self.particles:
            particle.draw()

        self.draw_hud()

    # ======================================
    # PAUSE SCREEN
    # ======================================

    def draw_pause(self):
        self.draw_game()

        overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        self.draw_text(
            "GAME PAUSED", title_font, YELLOW,
            WIDTH // 2, HEIGHT // 2 - 40
        )

        self.draw_text(
            "Press P to Continue", medium_font, WHITE,
            WIDTH // 2, HEIGHT // 2 + 30
        )

    # ======================================
    # GAME OVER SCREEN
    # ======================================

    def draw_gameover(self):
        draw_background()
        draw_clouds()

        self.draw_text(
            "GAME OVER!", title_font, MAGENTA,
            WIDTH // 2, int(HEIGHT * 0.30)
        )

        self.draw_text(
            f"Your Score: {self.score}", large_font, YELLOW,
            WIDTH // 2, int(HEIGHT * 0.43)
        )

        self.draw_text(
            "Press R to Restart", medium_font, WHITE,
            WIDTH // 2, int(HEIGHT * 0.57)
        )

        self.draw_text(
            "Press ESC to Quit", small_font, WHITE,
            WIDTH // 2, int(HEIGHT * 0.66)
        )

    # ======================================
    # UPDATE GAME
    # ======================================

    def update(self, dt):
        elapsed = (
            pygame.time.get_ticks() - self.start_ticks
        ) / 1000

        self.time_left = max(
            0, GAME_DURATION - int(elapsed)
        )

        if self.time_left <= 0:
            self.state = "gameover"
            play_sound("gameover")
            return

        elapsed = GAME_DURATION - self.time_left

        self.difficulty = min(2.5, elapsed / 25)
        self.spawn_interval = max(
            300, 850 - int(elapsed * 7)
        )

        self.spawn_timer += dt

        if self.spawn_timer >= self.spawn_interval:
            self.balloons.append(Balloon())
            self.spawn_timer = 0

        # Missed balloons disappear without losing lives.
        for balloon in self.balloons[:]:
            balloon.update(self.difficulty)

            if balloon.y + balloon.radius * 2.3 < 0:
                self.balloons.remove(balloon)

        for particle in self.particles[:]:
            particle.update()

            if particle.life <= 0:
                self.particles.remove(particle)

    # ======================================
    # HANDLE BALLOON CLICK
    # ======================================

    def handle_click(self, mouse_pos):
        for balloon in self.balloons[:]:
            if balloon.clicked(mouse_pos):
                self.balloons.remove(balloon)

                if balloon.kind == "bomb":
                    self.lives -= 1
                    play_sound("bomb")

                    self.create_particles(
                        balloon.x, balloon.y, (100, 100, 110)
                    )

                    if self.lives <= 0:
                        self.state = "gameover"
                        play_sound("gameover")

                elif balloon.kind == "bonus":
                    self.score += 25
                    self.bonus_end_time = (
                        pygame.time.get_ticks() + 5000
                    )

                    play_sound("bonus")
                    self.create_particles(
                        balloon.x, balloon.y, YELLOW
                    )

                else:
                    if pygame.time.get_ticks() < self.bonus_end_time:
                        self.score += 20
                    else:
                        self.score += 10

                    play_sound("pop")
                    self.create_particles(
                        balloon.x, balloon.y, balloon.color
                    )

                break

    # ======================================
    # CREATE PARTICLES
    # ======================================

    def create_particles(self, x, y, color):
        for _ in range(18):
            self.particles.append(Particle(x, y, color))

    # ======================================
    # MAIN GAME LOOP
    # ======================================

    def run(self):
        running = True

        while running:
            dt = clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # KEYBOARD EVENTS
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_p:

                        if self.state == "playing":
                            self.state = "paused"
                            self.pause_time = pygame.time.get_ticks()

                        elif self.state == "paused":
                            paused_duration = (
                                pygame.time.get_ticks() - self.pause_time
                            )

                            self.start_ticks += paused_duration

                            if self.bonus_end_time > 0:
                                self.bonus_end_time += paused_duration

                            self.state = "playing"

                    elif event.key == pygame.K_r:
                        if self.state == "gameover":
                            self.reset_game()
                            self.state = "playing"
                            play_sound("start")

                # MOUSE EVENTS
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:

                        if self.state == "menu":
                            if self.start_button.collidepoint(event.pos):
                                self.reset_game()
                                self.state = "playing"
                                play_sound("start")

                        elif self.state == "playing":
                            self.handle_click(event.pos)

            # DRAW GAME STATES
            if self.state == "menu":
                self.draw_menu()

            elif self.state == "playing":
                self.update(dt)

                if self.state == "playing":
                    self.draw_game()

            elif self.state == "paused":
                self.draw_pause()

            elif self.state == "gameover":
                self.draw_gameover()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


# ==========================================
# START THE GAME
# ==========================================

if __name__ == "__main__":
    game = BalloonPopGame()
    game.run()
