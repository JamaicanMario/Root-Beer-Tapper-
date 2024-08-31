import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BAR_HEIGHT = 100
NUM_BARS = 5
MUG_MAX_FILL = 50
MUG_REQUIRED_FILL = 49  # Set the required fill level
MUG_SPEED = 7
CUSTOMER_SPEED = 0.5  # Constant speed for customers
LIVES = 3
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GRAY = (169, 169, 169)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Root Beer Tapper")

# Game classes
class Bartender:
    def __init__(self):
        self.image = pygame.image.load("bartender.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (130, 130))  # Adjust this size as necessary
        self.rect = self.image.get_rect(topleft=(50, 0))
        self.current_bar = 0
        self.target_bar = 0
        self.is_moving = False
        self.filling = False
        self.mug_fill = 0

    def move(self, direction):
        if not self.is_moving:  # Only move if not already moving
            if direction == "up" and self.current_bar > 0:
                self.target_bar = self.current_bar - 1
                self.is_moving = True
            elif direction == "down" and self.current_bar < NUM_BARS - 1:
                self.target_bar = self.current_bar + 1
                self.is_moving = True

    def update(self):
        # Move smoothly to the target bar
        target_y = self.target_bar * BAR_HEIGHT + (BAR_HEIGHT // 2) - 25
        if self.rect.y < target_y:
            self.rect.y += 5
            if self.rect.y >= target_y:
                self.rect.y = target_y
                self.current_bar = self.target_bar
                self.is_moving = False
        elif self.rect.y > target_y:
            self.rect.y -= 5
            if self.rect.y <= target_y:
                self.rect.y = target_y
                self.current_bar = self.target_bar
                self.is_moving = False

        # Filling the mug
        if self.filling:
            if self.mug_fill < MUG_MAX_FILL:
                self.mug_fill += 1

    def start_filling(self):
        self.filling = True

    def stop_filling(self):
        self.filling = False
        if self.mug_fill >= MUG_REQUIRED_FILL:  # Only send if filled to the required level
            mug = Mug(self.current_bar, self.mug_fill)
            self.mug_fill = 0  # Reset mug fill after sending
            return mug
        else:
            self.mug_fill = 0  # Reset if not filled enough
            return None

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        # Draw the filling mug indicator
        if self.filling or self.mug_fill > 0:
            fill_rect = pygame.Rect(self.rect.right + 10, self.rect.centery - 10, self.mug_fill, 20)
            pygame.draw.rect(surface, BROWN, fill_rect)



class Customer:
    def __init__(self, bar):
        # Set the initial position based on the bar (lane) the customer spawns in
        self.rect = pygame.Rect(SCREEN_WIDTH - 60, bar * BAR_HEIGHT + (BAR_HEIGHT // 2) - 25, 50, 50)
        self.speed = CUSTOMER_SPEED

    def update(self):
        # Move the customer towards the bartender by reducing the x position
        self.rect.x -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)


class Mug:
    def __init__(self, bar, fill_amount):
        self.rect = pygame.Rect(100, bar * BAR_HEIGHT + (BAR_HEIGHT // 2) - 15, fill_amount, 30)
        self.speed = MUG_SPEED

    def update(self):
        self.rect.x += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, BROWN, self.rect)


# Game logic
def main():
    clock = pygame.time.Clock()
    bartender = Bartender()
    customers = []
    mugs = []
    score = 0
    lives = LIVES
    lanes_occupied = [False] * NUM_BARS  # Track if a lane is occupied by a customer
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            bartender.move("up")
        if keys[pygame.K_DOWN]:
            bartender.move("down")

        if keys[pygame.K_SPACE]:
            bartender.start_filling()
        else:
            if bartender.filling:
                new_mug = bartender.stop_filling()
                if new_mug:
                    mugs.append(new_mug)

        bartender.update()

        screen.fill(WHITE)

        # Draw bar tables
        for i in range(NUM_BARS):
            pygame.draw.rect(screen, BLACK, (0, i * BAR_HEIGHT, SCREEN_WIDTH, 5))

        bartender.draw(screen)

        # Update and draw customers
        for customer in customers:
            customer.update()
            customer.draw(screen)

        # Update and draw mugs
        for mug in mugs:
            mug.update()
            mug.draw(screen)

        # Handle collision between mugs and customers
        for mug in mugs[:]:
            for customer in customers[:]:
                if mug.rect.colliderect(customer.rect):
                    mugs.remove(mug)
                    customers.remove(customer)
                    lanes_occupied[customer.rect.y // BAR_HEIGHT] = False  # Free up the lane
                    score += 10
                    break  # Stop checking other customers since this mug is removed

        # Check for game over conditions
        for customer in customers[:]:
            if customer.rect.left <= 0:
                customers.remove(customer)
                lanes_occupied[customer.rect.y // BAR_HEIGHT] = False  # Free up the lane
                lives -= 1
                if lives <= 0:
                    running = False

        for mug in mugs[:]:
            if mug.rect.right >= SCREEN_WIDTH:
                if mug in mugs:  # Ensure mug is still in list before removing
                    mugs.remove(mug)
                lives -= 1
                if lives <= 0:
                    running = False

        # Randomly add customers
        if random.random() < 0.02:
            bar_index = random.randint(0, NUM_BARS - 1)
            if not lanes_occupied[bar_index]:  # Only spawn if the lane is free
                customers.append(Customer(bar_index))
                lanes_occupied[bar_index] = True  # Mark the lane as occupied

        # Draw score and lives
        score_text = pygame.font.Font(None, 36).render(f"Score: {score}", True, BLACK)
        lives_text = pygame.font.Font(None, 36).render(f"Lives: {lives}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
