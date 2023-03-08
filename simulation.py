import pygame
import random
import NN
import math
import numpy as np
import time








white = (255,255,255)
black = (0,0,0)
red = (255, 0, 0)


class Food:
    def __init__(self, x, y, color):
        self.status="alive"
        self.x = x
        self.y = y
        self.color = color
        
    def draw(self, screen, x_offset, y_offset):
        pygame.draw.circle(screen, self.color, (self.x-x_offset, self.y-y_offset), 5)


class Unit:
    id_counter=0
    action_size=5
    state_size=45
    
    def __init__(self, x, y, color):
        self.status="alive"
        self.network=NN.NN(Unit.action_size,Unit.state_size)
        self.x = x
        self.y = y
        self.color = color
        self.health = 100
        self.food = 100
        self.strength = 10
        self.alliances = []
        self.enemies = []
        self.id=Unit.id_counter
        Unit.id_counter +=1
        self.action_buffer=[]
        self.state_buffer=[]
        self.disc_out_buffer=[]
        self.disc_in_buffer=[]

    def getFood(self):
        return self.food

    def draw(self, screen, x_offset, y_offset):
        pygame.draw.circle(screen, self.color, (self.x - x_offset, self.y - y_offset), 10)
    

    def move(self, env, units, foods):



        env=np.expand_dims(env, axis=0)
        action_probs = self.network.generator(env)

        action_probs = np.array(action_probs)
        action_probs /= action_probs.sum()
        action= np.random.choice(np.arange(Unit.action_size),p=action_probs[0])
        disc_in = np.concatenate((env, action_probs), axis=1)
        disc_out= self.network.discriminator(disc_in)
        self.disc_out_buffer.append(disc_out)
        self.disc_in_buffer.append(disc_in)


        if action == 0:
            self.x += 1
        elif action == 1:
            self.x += -1
        elif action == 2:
            self.y += 1
        elif action == 3:
            self.y += -1                        
        elif action == 4:
            self.eat_food(foods)    




    
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
                enemy.status="dead"
                return True
        return False

    def eat_food(self,foods):
        for f in foods:
                if math.sqrt((f.x-self.x)**2+(f.y-self.y)**2)<50 and f.status == "alive":
                    f.status="dead"
                    self.food+=5
                    return True
        return False               


    
    def check_env(self,units,foods):
        env = np.zeros(40)
        for u in units:
            if(u.id!=self.id):
                if math.sqrt((u.x-self.x)**2+(u.y-self.y)**2)<50:
                    env = np.concatenate([env, np.array([u.x/3000, u.y/3000, u.health/100, u.strength/100])])

        for f in foods:
            if math.sqrt((f.x-self.x)**2+(f.y-self.y)**2)<50 and f.status=="alive":
                env = np.concatenate([env, np.array([f.x/3000, f.y/3000, 0, 0])])

        env = np.concatenate([env[:40], np.array([self.x/3000, self.y/3000, self.health/100, self.food/200, self.strength/100])])

        return env




class ScrollableScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x_offset = 0
        self.y_offset = 0
        self.units = []
        self.food = []

        for i in range(25):
            x = random.randint(0, width)
            y = random.randint(0, height)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.units.append(Unit(x, y, color))

        for i in range(500):
            x = random.randint(0, width)
            y = random.randint(0, height)
            color = (0, 255, 0)
            self.food.append(Food(x, y, color))

    def reset_game(self):
        for unit in self.units:
            unit.x= random.randint(0, self.width)
            unit.y= random.randint(0, self.height)
            unit.health=100
            unit.food=100
            unit.strength=10
            unit.status="alive"
            unit.action_buffer=[]
            unit.state_buffer=[]
            unit.disc_out_buffer=[]
            unit.disc_in_buffer=[]            

        for f in self.food:
            unit.f= random.randint(0, self.width)
            unit.f= random.randint(0, self.height)            
            f.status="alive"

    def draw(self, screen, my_font):
        screen.fill(black)

        mousex, mousey = pygame.mouse.get_pos()
        nearest=self.units[0]
        for unit in self.units:
            unit.draw(screen, self.x_offset, self.y_offset)
            nearest= unit if (unit.x-self.x_offset-mousex)**2+(unit.y-self.y_offset-mousey)**2<=(nearest.x-self.x_offset-mousex)**2+(nearest.y-self.y_offset-mousey)**2 else nearest

        for f in self.food:
            if f.status=="alive":
                f.draw(screen, self.x_offset, self.y_offset)


        pygame.draw.circle(screen, (255,0,0), (nearest.x-self.x_offset, nearest.y-self.y_offset), 50,2)

        text_surface = my_font.render("Health: "+str(nearest.health)+" Food: "+str(nearest.food)+" id: "+str(nearest.id)+" strength: "+str(nearest.strength), False, (255, 255, 255))
        screen.blit(text_surface, (0,0))



        pygame.draw.rect(screen,white,(0-self.x_offset,0-self.y_offset,3000,3000),4)



    def move(self, dx, dy):
        self.x_offset += dx
        self.y_offset += dy



class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        #self.screen = pygame.display.set_mode((1280, 768))
        #self.clock = pygame.time.Clock()
        self.scrollable_screen = ScrollableScreen(width, height)
        self.running = True
        Game.tour=0

    def run(self):
        epoch=0
        while self.running:
            """
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

            """
            self.round()
            if Game.tour >= 250:
                print("tur 250")
                sortedElements = sorted(self.scrollable_screen.units, key = Unit.getFood)
                epoch+=1
                for u in sortedElements[0:int(250/33)]:
                    u.network.train_network(sortedElements[-int(250/33):250],sortedElements[0:int(250/33)],u,epoch)
                Game.tour=0
                self.scrollable_screen.reset_game()

            #pygame.display.update()
            #self.clock.tick(60)

    def round(self):
        #pygame.font.init()
        #my_font = pygame.font.SysFont('Comic Sans MS', 30)            
        #self.scrollable_screen.draw(self.screen,my_font)

        for unit in self.scrollable_screen.units:
            env=unit.check_env(self.scrollable_screen.units,self.scrollable_screen.food)

            unit.state_buffer.append(env)


            unit.move(env,self.scrollable_screen.units,self.scrollable_screen.food)

        
        sortedElements = sorted(self.scrollable_screen.units, key = Unit.getFood)
        #print(max(unit.food for unit in self.scrollable_screen.units))
        Game.tour+=1


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
        #pygame.init()
        #pygame.key.set_repeat(10,10)

        self.game = Game(3000, 3000)
        self.game.run()
        #pygame.quit()

if __name__ == "__main__":
    Main()