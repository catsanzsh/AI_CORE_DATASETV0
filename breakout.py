import pygame, sys, random, math, array

# --- Atari POKEY–style Sound Engine ---
class PokeySoundEngine:
    def __init__(self, clock_rate=1790000, sample_rate=44100):
        self.clock = clock_rate
        self.rate  = sample_rate
        self.AUDF  = [0]*4      # frequency dividers
        self.AUDC  = [0]*4      # volume & noise control
        self.lfsr  = 0x1FFFF    # 17‑bit LFSR state
        self.phase = [0.0]*4
        self.out   = [0.0]*4

    def write_freq(self, ch, value):
        self.AUDF[ch] = value

    def write_ctrl(self, ch, value):
        self.AUDC[ch] = value

    def _lfsr_step(self):
        bit = self.lfsr & 1
        self.lfsr >>= 1
        if bit:
            self.lfsr ^= 0x12000
        return bit

    def step(self):
        mix = 0.0
        for ch in range(4):
            div = self.AUDF[ch] + 1
            period = self.clock / div
            self.phase[ch] += period / self.rate
            if self.phase[ch] >= 1.0:
                self.phase[ch] -= 1.0
                self.out[ch] = 1.0
            else:
                self.out[ch] = -1.0
            if self.AUDC[ch] & 0xE0:  # noise mode
                bit = self._lfsr_step()
                self.out[ch] = 1.0 if bit else -1.0
            vol = (self.AUDC[ch] & 0x0F) / 15.0
            mix += self.out[ch] * vol
        return mix / 4.0

    def generate_sound(self, duration):
        n = int(self.rate * duration)
        buf = array.array('h', [0]*n)
        for i in range(n):
            sample = self.step()
            buf[i] = int(sample * 32767 * 0.5)
        return pygame.mixer.Sound(buffer=buf)

# --- Game Settings ---
WIDTH, HEIGHT = 600, 400
FPS = 60
LIVES = 3
BRICK_ROWS, BRICK_COLS = 8, 10
BRICK_W, BRICK_H, PADDING = 60, 20, 5
PADDLE_W, PADDLE_H = 80, 10
BALL_R = 8
BG = (0, 0, 0)
BRICK_COLORS = [
    (255, 255, 50), (255, 255, 50),
    (50, 255, 50),  (50, 255, 50),
    (255, 150, 50), (255, 150, 50),
    (255,  50, 50), (255,  50, 50)
]

# --- Initialize Pygame & Sound ---
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Atari Breakout Clone")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

pokey = PokeySoundEngine()

def play_bounce():
    pokey.write_freq(0, 50)
    pokey.write_ctrl(0, 0x0F)
    pokey.generate_sound(0.05).play()

def play_paddle():
    pokey.write_freq(0, 40)
    pokey.write_ctrl(0, 0x0F)
    pokey.generate_sound(0.07).play()

def play_brick(row):
    pokey.write_freq(0, 30 + row*5)
    pokey.write_ctrl(0, 0x0F)
    pokey.generate_sound(0.1).play()

def play_end():
    for div in (20, 30, 40):
        pokey.write_freq(0, div)
        pokey.write_ctrl(0, 0x0F)
        pokey.generate_sound(0.3).play()

# --- Build Bricks ---
bricks = []
for r in range(BRICK_ROWS):
    for c in range(BRICK_COLS):
        x = c*(BRICK_W+PADDING) + (WIDTH - (BRICK_COLS*(BRICK_W+PADDING)-PADDING))//2
        y = r*(BRICK_H+PADDING) + 40
        rect = pygame.Rect(x, y, BRICK_W, BRICK_H)
        color = BRICK_COLORS[r]
        bricks.append([rect, color, r])

# --- Game Objects ---
paddle = pygame.Rect((WIDTH-PADDLE_W)//2, HEIGHT-30, PADDLE_W, PADDLE_H)
ball_x, ball_y = WIDTH//2, HEIGHT//2
angle = math.radians(random.choice([45,135,225,315]))
ball_vx = 5 * math.cos(angle)
ball_vy = 5 * math.sin(angle)
lives, score = LIVES, 0

# --- Main Loop ---
running = True
while running:
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # Move paddle
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle.x = max(0, paddle.x - 7)
    if keys[pygame.K_RIGHT]:
        paddle.x = min(WIDTH-PADDLE_W, paddle.x + 7)

    # Move ball
    ball_x += ball_vx
    ball_y += ball_vy

    # Wall collisions
    if ball_x - BALL_R <= 0 or ball_x + BALL_R >= WIDTH:
        ball_vx *= -1
        play_bounce()
    if ball_y - BALL_R <= 0:
        ball_vy *= -1
        play_bounce()

    # Paddle collision
    if paddle.collidepoint(ball_x, ball_y + BALL_R):
        ball_vy *= -1
        play_paddle()

    # Brick collisions
    for b in bricks:
        rect, color, row = b
        if rect.collidepoint(ball_x, ball_y):
            ball_vy *= -1
            score += 10
            play_brick(row)
            bricks.remove(b)
            break

    # Out of bounds
    if ball_y - BALL_R > HEIGHT:
        lives -= 1
        if lives == 0:
            play_end()
            running = False
        else:
            ball_x, ball_y = WIDTH//2, HEIGHT//2

    # Draw
    screen.fill(BG)
    for rect, color, _ in bricks:
        pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (255,255,255), paddle)
    pygame.draw.circle(screen, (255,255,255), (int(ball_x), int(ball_y)), BALL_R)
    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10, 10))
    screen.blit(font.render(f"Lives: {lives}", True, (255,255,255)), (WIDTH-80, 10))
    pygame.display.flip()

    if not bricks:
        play_end()
        break

# --- End Screen ---
screen.fill(BG)
msg = "YOU WIN!" if lives > 0 else "GAME OVER"
text = font.render(msg, True, (255,255,255))
screen.blit(text, ((WIDTH-text.get_width())//2, HEIGHT//2))
pygame.display.flip()
pygame.time.wait(2000)
pygame.quit()
sys.exit()
