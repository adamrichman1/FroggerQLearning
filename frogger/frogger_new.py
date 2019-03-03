import pygame
from pygame.constants import K_w,K_a,K_s,K_d,K_F15
import ple
from ple.games import base
from constants import *
import os, sys, time
from sys import stderr as err
from frog_sprites import *
from supporter import *

class Backdrop:
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, image_background):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        self.background_image = image_background
        self.x = 0
        self.y = 0
        self.leftOffset = None
        self.rightOffset = None
        self.rect = self.background_image.get_rect()
        self.rect.left = self.x + kXOffset
        self.rect.top = self.y

    def draw_background(self, screen):
        screen.fill((0,0,0))
        screen.blit(self.background_image, (self.rect.left,self.rect.top))

    def draw_outerEdge(self, screen):
        if self.leftOffset == None and self.rightOffset == None:
            self.leftOffset = screen.subsurface(pygame.Rect(0,0,kXOffset,self.SCREEN_HEIGHT))
            self.rightOffset = screen.subsurface(pygame.Rect(kXOffset+kPlayWidth,0,self.SCREEN_WIDTH-(kXOffset+kPlayWidth),self.SCREEN_HEIGHT))
        self.leftOffset.fill((0,0,0))
        self.rightOffset.fill((0,0,0))

class Frogger(base.PyGameWrapper):
    def __init__(self, width=kScreenWidth, height=kScreenHeight):
        actions = {
            "up": K_w,
            "right": K_d,
            "down": K_s,
            "left": K_a
        }

        fps = 30
        base.PyGameWrapper.__init__(self, width, height, actions=actions)

        self.images={}
        pygame.display.set_mode((1,1),pygame.NOFRAME)

        self.support = Supporter(self)
        
        self._dir_ = os.path.dirname(os.path.abspath(__file__))
        self._data_dir = os.path.join(self._dir_, "data/")
        self.support._load_images()

        self.support.set_rewards()

        self.backdrop = None
        self.frog = None

    def init(self):
        self.backdrop = Backdrop(self.width,self.height,self.images["background"])

        # frog init
        self.frog = Frog(kPlayFrog, self.images["frog"]["stationary"])

        # place homes
        self.support.init_homes()
        self.numFrogsHomed=0

        self.support.init_cars()
        self.support.init_river()

        self.bonusCroc=BonusRandom(kCrocodileBonusRate,kCrocodileBonusDelay)
        self.bonusFly=BonusRandom(kFlyBonusRate,kFlyBonusDelay)

        self.reachedMidway = False

        self.score = 0.0
        self.lives = 1
        self.game_tick = 0

    def getScore(self):
        return self.score

    def getGameState(self):
        homeStatus=[None]*len(self.homes)
        for i in range(len(self.homes)):
            if self.homes[i].frogged == True: homeStatus[i] = float(0.66) # fly is worth more
            elif self.homes[i].flied == True: homeStatus[i] = float(1)
            elif self.homes[i].croced == True: homeStatus[i] = float(0.33) # let's frog know what's here
            else: homeStatus[i] = 0

        state = {
            'frog_x': self.frog.get_pos()[0],
            'frog_y': self.frog.get_pos()[1],
            'rect_w': self.frog.get_rect().width,
            'rect_h': self.frog.get_rect().height,
            'cars': self.support.carRects(),
            'rivers': self.support.riverRects(),
            'homes': homeStatus,
            'homeR': self.support.homeRects()
        }

        return state

    def _handle_player_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == self.actions["up"]:
                    self.frog.set_move((0.0,-1.0))
                if key == self.actions["right"]:
                    self.frog.set_move((1.0,0.0))
                if key == self.actions["down"]:
                    self.frog.set_move((0.0,1.0))
                if key == self.actions["left"]:
                    self.frog.set_move((-1.0,0.0))

    def game_over(self):
        if self.numFrogsHomed == 5:
            # game over because we won
            return True
        return self.lives <= 0

    def step(self, dt):
        self.game_tick += 1
        #dt = dt / 1000.0

        self._handle_player_events()

        # all sprites do their update
        for home in self.homes: home.update(dt)
        for car in self.cars: car.update(dt)
        self.river_group.update(dt)
        self.frog.update(dt)

        # check for collisions with the homes first
        if self.frog._y < kPlayYHomeLimit:
            collideInd = self.frog.get_rect().collidelist(self.homeRects)
            if collideInd != -1 and self.homes[collideInd].frogged == False and self.homes[collideInd].croced == False:
                # hit an open home, kill frog and init a new one
                if self.homes[collideInd].flied == True:
                    # fly bonus --> give reward here
                    print 'fly bonus!'
                self.homes[collideInd].homeFrog()
                self.score += self.rewards['home']
                self.numFrogsHomed += 1
                if self.numFrogsHomed == 5: self.score += self.rewards['win']
                self.frog.kill()
                self.frog = Frog(kPlayFrog, self.images["frog"]["stationary"])
                self.reachedMidway = False
            else:
                self.lives -= 1
                self.score += self.rewards['death']
        elif self.frog._y < kPlayYRiverLimit:
            # in the river zone
            h=pygame.sprite.spritecollide(self.frog,self.river_group,False)
            if len(h) == 0:
                # fell in the river
                self.lives -= 1
                self.score += self.rewards['death']
            else:
                # if haven't been given the midway reward, give it now
                if self.reachedMidway == False:
                    self.score += self.rewards['midway']
                    self.reachedMidway = True
                # attach to h[0] (first check that we aren't hopping laterally)
                if self.frog.attached and h[0] != self.frog.attachedObj and h[0].get_rect()[1] == self.frog.attachedObj.get_rect()[1]:
                    # tried to move laterally between attached objects, can't do that, kill
                    self.lives -= 1
                    self.score += self.rewards['death']
                else:
                    self.frog.attachTo(h[0])

                # check if frog has gone off screen while attached to object, kill
                if self.frog.attachDisappeared():
                    self.lives -= 1
                    self.score += self.rewards['death']

                # check for diving turtle
                if isinstance(self.frog.attachedObj, Turtle) and self.frog.attachedObj.disappeared == True:
                    # if frog is attached to a disappeared Turtle, kill
                    self.lives -= 1
                    self.score += self.rewards['death']
        else:
            # in the road zone, check for collisions with cars
            # if we have been given the midway reward and went back to the road, need to penalize
            if self.reachedMidway == True:
                self.score += self.rewards['downmid']
                self.reachedMidway = False
            collideInd = self.frog.get_rect().collidelist(self.support.carRects())
            if collideInd != -1:
                # collided with a car, kill the frog
                self.lives -= 1
                self.score += self.rewards['death']

        
        # determine if homes should get a croc/fly placed
        if self.bonusCroc.get_chance(self.clock.get_time()): self.homes[int(5*random.random())].setCroc()
        if self.bonusFly.get_chance(self.clock.get_time()): self.homes[int(5*random.random())].setFly()

        self.backdrop.draw_background(self.screen)
        for home in self.homes: home.draw(self.screen)
        for car in self.cars: car.draw(self.screen)
        self.river_group.draw(self.screen)
        self.frog.draw(self.screen)
        self.backdrop.draw_outerEdge(self.screen)
        pygame.display.update()
