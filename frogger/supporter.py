from frogger_new import *
from copy import deepcopy

class Supporter:
    def __init__(self,game):
        self.game=game

    def _load_images(self):
        self.game.images["frog"] = {}
        fImage = os.path.join(self.game._data_dir, "frog.png")
        self.game.images["frog"]["stationary"] = pygame.image.load(fImage).convert_alpha()

        backPath = os.path.join(self.game._data_dir, "background.png")
        self.game.images["background"] = pygame.image.load(backPath).convert_alpha()

        self.game.images["homes"] = {}
        homeImage = os.path.join(self.game._data_dir, "blank-home.png")
        self.game.images["homes"]["blank"] = pygame.image.load(homeImage).convert()
        homeWithFrog = os.path.join(self.game._data_dir, "frog-home.png")
        self.game.images["homes"]["frog"] =  pygame.image.load(homeWithFrog).convert()
        home=os.path.join(self.game._data_dir, "crocodile-home.png")
        self.game.images["homes"]["croc"] = pygame.image.load(home).convert()
        home=os.path.join(self.game._data_dir, "fly-home.png")
        self.game.images["homes"]["fly"] = pygame.image.load(home).convert()

        self.game.images["cars"] = {}
        car1 = os.path.join(self.game._data_dir, "car-1.png")
        self.game.images["cars"]["car1"] = pygame.image.load(car1).convert()
        car2 = os.path.join(self.game._data_dir, "car-2.png")
        self.game.images["cars"]["car2"] = pygame.image.load(car2).convert()
        car3 = os.path.join(self.game._data_dir, "car-3.png")
        self.game.images["cars"]["car3"] = pygame.image.load(car3).convert()
        car4 = os.path.join(self.game._data_dir, "car-4.png")
        self.game.images["cars"]["car4"] = pygame.image.load(car4).convert()
        car5 = os.path.join(self.game._data_dir, "car-5.png")
        self.game.images["cars"]["car5"] = pygame.image.load(car5).convert()

        self.game.images["turtles"] = {1:{},2:{}}
        turtle1 = os.path.join(self.game._data_dir, "turtle-1A.png")
        self.game.images["turtles"][1]["A"] = pygame.image.load(turtle1).convert()
        turtle1 = os.path.join(self.game._data_dir, "turtle-1B.png")
        self.game.images["turtles"][1]["B"] = pygame.image.load(turtle1).convert()
        turtle1 = os.path.join(self.game._data_dir, "turtle-1C.png")
        self.game.images["turtles"][1]["C"] = pygame.image.load(turtle1).convert()
        turtle1 = os.path.join(self.game._data_dir, "turtle-1D.png")
        self.game.images["turtles"][1]["D"] = pygame.image.load(turtle1).convert()
        turtle1 = os.path.join(self.game._data_dir, "turtle-1E.png")
        self.game.images["turtles"][1]["E"] = pygame.image.load(turtle1).convert()
        turtle2 = os.path.join(self.game._data_dir, "turtle-2A.png")
        self.game.images["turtles"][2]["A"] = pygame.image.load(turtle2).convert()
        turtle2 = os.path.join(self.game._data_dir, "turtle-2B.png")
        self.game.images["turtles"][2]["B"] = pygame.image.load(turtle2).convert()
        turtle2 = os.path.join(self.game._data_dir, "turtle-2C.png")
        self.game.images["turtles"][2]["C"] = pygame.image.load(turtle2).convert()
        turtle2 = os.path.join(self.game._data_dir, "turtle-2D.png")
        self.game.images["turtles"][2]["D"] = pygame.image.load(turtle2).convert()
        turtle2 = os.path.join(self.game._data_dir, "turtle-2E.png")
        self.game.images["turtles"][2]["E"] = pygame.image.load(turtle2).convert()

        self.game.images["logs"] = {}
        log1 = os.path.join(self.game._data_dir, "log-1.png")
        self.game.images["logs"]["1"] = pygame.image.load(log1).convert()
        log2 = os.path.join(self.game._data_dir, "log-2.png")
        self.game.images["logs"]["2"] = pygame.image.load(log2).convert()
        log3 = os.path.join(self.game._data_dir, "log-3.png")
        self.game.images["logs"]["3"] = pygame.image.load(log3).convert()

    def init_homes(self):
        self.game.homes=[None]*5
        self.game.homeRects=[None]*5
        (x,y) = (kHomeInitX, kHomeInitY)
        for i in range(5):
            self.game.homes[i] = Home((x,y),self.game.images["homes"])
            self.game.homeRects[i] = self.game.homes[i].get_rect()
            x+=kHomeDX

    def init_river(self):
        self.game.river_group=pygame.sprite.Group()
        x=0.0
        y=kPlayYRiver[0]
        for i in range(4):
            river=Turtle((x,y), (-0.035,0.0), self.game.images["turtles"][1]["A"],self.game.images["turtles"][1],i==0)
            self.game.river_group.add(river)
            x+=128.0

        x=20.0
        y=kPlayYRiver[1]
        for i in range(3):
            river=Log((x,y), (0.035,0.0), self.game.images["logs"]["1"])
            self.game.river_group.add(river)
            x+=192.0

        x=40.0
        y=kPlayYRiver[2]
        for i in range(2):
            river=Log((x,y), (0.065,0.0), self.game.images["logs"]["3"])
            self.game.river_group.add(river)
            x+=256.0

        x=60.0
        y=kPlayYRiver[3]
        for i in range(4):
            river=Turtle((x,y), (-0.034,0.0), self.game.images["turtles"][2]["A"],self.game.images["turtles"][2],i==3)
            self.game.river_group.add(river)
            x+=112.0

        x=80.0
        y=kPlayYRiver[4]
        for i in range(3):
            river=Log((x,y), (0.035,0.0), self.game.images["logs"]["2"])
            self.game.river_group.add(river)
            x+=176.0

    def init_cars(self):
        self.game.cars=[]

        x=0.0
        y=kPlayYCar[0]
        for i in range(2):
            car = Car((x,y), (-0.0150,0.0), self.game.images["cars"]["car1"])
            self.game.cars.append(car)
            x+=144.0

        x=20.0
        y=kPlayYCar[1]
        for i in range(3):
            car = Car((x,y), (0.011,0.0), self.game.images["cars"]["car2"])
            self.game.cars.append(car)
            x+=128.0

        x=40.0
        y=kPlayYCar[2]
        for i in range(3):
            car = Car((x,y), (-0.016,0.0), self.game.images["cars"]["car3"])
            self.game.cars.append(car)
            x+=128.0

        x=60.0
        y=kPlayYCar[3]
        for i in range(1):
            car = Car((x,y), (0.010,0.0), self.game.images["cars"]["car4"])
            self.game.cars.append(car)
            x+=128.0

        x=80.0
        y=kPlayYCar[4]
        for i in range(2):
            car = Car((x,y), (-0.035,0.0), self.game.images["cars"]["car5"])
            self.game.cars.append(car)
            x+=176.0

    def carRects(self):
        carRects=[]
        for car in self.game.cars:
            carRects.append(car.get_rect())
        return carRects

    def riverRects(self):
        riverRects=[]
        for river in self.game.river_group.sprites():
            riverRects.append(river.get_rect())
        return riverRects

    def set_rewards(self):
        self.game.rewards = {'home':kHomeScore,'win':kWinLevel,'midway':kMidPoint,'downmid':kDownMid,'death':kDeathPenalty}

    def homeRects(self):
        # game already has home rects, but this will take out any rects that have a frog
        # or that have a croc in them
        homeR=deepcopy(self.game.homeRects)
        toRm=[]
        for i in range(len(self.game.homes)):
            if self.game.homes[i].frogged or self.game.homes[i].croced:
                # frogged home or croced home, prepare to take out of homeR
                toRm.append(i)

        # toRm holds all the indices that need to be removed from homeR
        for i in range(len(toRm)-1,-1,-1):
            homeR.pop(toRm[i])
       
        return homeR
                
            
