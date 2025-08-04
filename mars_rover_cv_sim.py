import cv2
import pygame  # type: ignore
import mediapipe as mp  # type: ignore
import random
import os

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Rover Star Collector")
clock = pygame.time.Clock()

rover = pygame.image.load(r"C:\Users\dell\OneDrive\Dokumen\computer_vision\proj11\vover.png")
rover = pygame.transform.scale(rover, (60, 60))
bg = pygame.image.load(r"C:\Users\dell\OneDrive\Dokumen\computer_vision\proj11\mars.jpeg")
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
star_img = pygame.image.load(r"C:\Users\dell\OneDrive\Dokumen\computer_vision\proj11\star.webp")
star_img = pygame.transform.scale(star_img, (40, 40))

x, y = WIDTH // 2, HEIGHT // 2
speed = 5
direction = "STOP"
previous_direction = "STOP"
stars = []
MAX_STARS_ON_SCREEN = 5
score = 0
font = pygame.font.SysFont(None, 36)
start_time = pygame.time.get_ticks()
game_duration = 60000  


def add_star():
    while True:
        star_x = random.randint(50, WIDTH - 90)
        star_y = random.randint(50, HEIGHT - 90)
        new_star = pygame.Rect(star_x, star_y, 40, 40)
        if not any(s.colliderect(new_star) for s in stars):
            stars.append(new_star)
            break

for _ in range(MAX_STARS_ON_SCREEN):
    add_star()

cap = cv2.VideoCapture(0)
prev_index_finger = None
movement_threshold = 0.02  # Sensitivity

emoji_map = {
    "UP": "👆",
    "DOWN": "👇",
    "LEFT": "👈",
    "RIGHT": "👉",
    "STOP": "🖐"
}

running = True
while running:
    screen.blit(bg, (0, 0))
    for star in stars:
        screen.blit(star_img, (star.x, star.y))

    elapsed = pygame.time.get_ticks() - start_time
    time_left = max(0, game_duration - elapsed)
    time_text = font.render(f"Time Left: {time_left // 1000}s", True, (255, 100, 100))
    screen.blit(time_text, (10, 90))

    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gesture_detected = False

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger = hand_landmarks.landmark[8]

            if prev_index_finger:
                dx = index_finger.x - prev_index_finger.x
                dy = index_finger.y - prev_index_finger.y

                if abs(dx) > abs(dy):
                    if dx > movement_threshold:
                        direction = "RIGHT"
                    elif dx < -movement_threshold:
                        direction = "LEFT"
                else:
                    if dy > movement_threshold:
                        direction = "DOWN"
                    elif dy < -movement_threshold:
                        direction = "UP"

            prev_index_finger = index_finger
            gesture_detected = True

            h, w, _ = frame.shape
            x_tip, y_tip = int(index_finger.x * w), int(index_finger.y * h)
            cv2.circle(frame, (x_tip, y_tip), 10, (0, 255, 0), -1)  

    if not gesture_detected:
        direction = "STOP"
        prev_index_finger = None

    if direction == "UP":
        y -= speed
    elif direction == "LEFT":
        x -= speed
    elif direction == "RIGHT":
        x += speed
    elif direction == "DOWN":
        y += speed

    x = max(0, min(WIDTH - 60, x))
    y = max(0, min(HEIGHT - 60, y))
    rover_rect = pygame.Rect(x, y, 60, 60)

    for star in stars[:]:
        if rover_rect.colliderect(star):
            stars.remove(star)
            score += 1
            add_star()

            if score % 10 == 0:
                speed += 1
                MAX_STARS_ON_SCREEN += 1

    while len(stars) < MAX_STARS_ON_SCREEN:
        add_star()

    screen.blit(rover, (x, y))
    score_text = font.render(f"Stars Collected: {score}", True, (255, 255, 0))
    screen.blit(score_text, (10, 50))
    gesture_text = font.render(f"Gesture: {direction} {emoji_map.get(direction, '')}", True, (255, 255, 255))
    screen.blit(gesture_text, (10, 10))

    frame_small = cv2.resize(frame, (160, 120))
    frame_small = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(cv2.transpose(frame_small))
    screen.blit(frame_surface, (WIDTH - 170, HEIGHT - 130))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(30)

    if time_left <= 0:
        running = False


screen.fill((0, 0, 0))
final_text = font.render(f"Game Over! Final Score: {score}", True, (255, 255, 255))
screen.blit(final_text, (WIDTH // 2 - 150, HEIGHT // 2))
pygame.display.flip()
pygame.time.wait(4000)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
