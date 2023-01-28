import pygame
import random

white = (255,255,255)
black = (0,0,0)
red = (255, 0, 0)


class Food:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        
    def draw(self, screen, x_offset, y_offset):
        pygame.draw.circle(screen, self.color, (self.x-x_offset, self.y-y_offset), 5)


class Unit:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.health = 100
        self.food = 100
        self.strength = 10
        self.alliances = []
        self.enemies = []

    def draw(self, screen, x_offset, y_offset):
        pygame.draw.circle(screen, self.color, (self.x - x_offset, self.y - y_offset), 10)
    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def offer_alliance(self, other):
        if other not in self.enemies:
            if other not in self.alliances:
                if self.food >= 10:
                    self.food -= 10
                    if random.random() < 0.05:
                        self.alliances.append(other)
                        other.alliances.append(self)
                        return True
                return False

    def heal_friend(self, friend):
        if friend in self.alliances:
            if self.food >= 10:
                self.food -= 10
                friend.health += 5
                return True
        return False

    def attack(self, enemy):
        if enemy in self.enemies:
            enemy.health -= self.strength
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                return True
        return False

class ScrollableScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x_offset = 0
        self.y_offset = 0
        self.units = []
        self.food = []

        for i in range(250):
            x = random.randint(0, width)
            y = random.randint(0, height)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.units.append(Unit(x, y, color))

        for i in range(50):
            x = random.randint(0, width)
            y = random.randint(0, height)
            color = (0, 255, 0)
            self.food.append(Food(x, y, color))


    def draw(self, screen, my_font):
        screen.fill(black)

        mousex, mousey = pygame.mouse.get_pos()
        nearest=self.units[0]
        for unit in self.units:
            unit.draw(screen, self.x_offset, self.y_offset)
            nearest= unit if (unit.x-self.x_offset-mousex)**2+(unit.y-self.y_offset-mousey)**2<=(nearest.x-self.x_offset-mousex)**2+(nearest.y-self.y_offset-mousey)**2 else nearest
        for f in self.food:
            f.draw(screen, self.x_offset, self.y_offset)


        pygame.draw.circle(screen, (255,0,0), (nearest.x-self.x_offset, nearest.y-self.y_offset), 50,2)

        text_surface = my_font.render("Health: "+str(nearest.health)+" Food: "+str(nearest.food), False, (255, 255, 255))
        screen.blit(text_surface, (0,0))



        pygame.draw.rect(screen,white,(0-self.x_offset,0-self.y_offset,3000,3000),4)



    def move(self, dx, dy):
        self.x_offset += dx
        self.y_offset += dy



class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.scrollable_screen = ScrollableScreen(width, height)
        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.screen.fill(black)
                        self.scrollable_screen.move(10, 0)
                    if event.key == pygame.K_RIGHT:
                        self.screen.fill(black)                    
                        self.scrollable_screen.move(-10, 0)
                    if event.key == pygame.K_UP:
                        self.screen.fill(black)                    
                        self.scrollable_screen.move(0, 10)
                    if event.key == pygame.K_DOWN:
                        self.screen.fill(black)
                        self.scrollable_screen.move(0, -10)


            self.round()
            pygame.display.update()
            self.clock.tick(60)

    def round(self):
        pygame.font.init()
        my_font = pygame.font.SysFont('Comic Sans MS', 30)            
        self.scrollable_screen.draw(self.screen,my_font)
        for unit in self.scrollable_screen.units:
            probs=[(0,0),(0,1),(1,0),(0,-1),(-1,0)]
            choice = random.choice(probs)
            unit.move(choice[0],choice[1])
            #unit.update()

"""
def main():
    pygame.init()
    pygame.font.init()
    my_font = pygame.font.SysFont('Comic Sans MS', 30)    

    pygame.key.set_repeat(10,10)
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Simulation")
    scrollable_screen = ScrollableScreen(3000, 3000)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    screen.fill(black)
                    scrollable_screen.move(10, 0)
                if event.key == pygame.K_RIGHT:
                    screen.fill(black)                    
                    scrollable_screen.move(-10, 0)
                if event.key == pygame.K_UP:
                    screen.fill(black)                    
                    scrollable_screen.move(0, 10)
                if event.key == pygame.K_DOWN:
                    screen.fill(black)
                    scrollable_screen.move(0, -10)
        scrollable_screen.draw(screen,my_font)
        pygame.display.flip()
        
    pygame.quit()
"""


class Main:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(10,10)

        self.game = Game(3000, 3000)
        self.game.run()
        pygame.quit()

if __name__ == "__main__":
    Main()