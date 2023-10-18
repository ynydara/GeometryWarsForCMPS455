#I want a ashtroid game that is similar to that one xbox game geometry wars
#shapes follow the player
# player has 3 lives
# each shape when defeated gives points
# circle //red

# squares // purple?

# [squares] when hit bigger ashtroid, it splits into 4 smaller ones and if smaller one, it deletes




# -*- coding: utf-8 -*-


import pygame as p
import random
import math
import pygame.mixer as mixer

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BLUE = (0,0,255)

background_image = p.image.load("hyrule.jpg")


colorPalette = [WHITE, GREEN, RED, ORANGE, YELLOW, CYAN, MAGENTA]
nColors = len(colorPalette)

# screenWidth = 1600
# screenHeight = 850
screenWidth = 1500
screenHeight = 750
gameMidX = screenWidth/2
gameMidY = screenHeight/2

background_image = p.transform.scale(background_image, (screenWidth, screenHeight))


# General constants and variables defined.
# Space rock variables.
maxRockVelocity = 2
maxRockScaleFactor = 3
maxRockTypes = 3


rock0 = [[[3,0], [0,3], [6,0], [0,-3], [3,0]]]
# rock1 = [[[1,2], [3,1], [3,-1], [1,-2], [-1,-2], 
#          [-3,-1], [-3,1], [-1,2], [1,2]]]
# rock2 = [[[1,1], [1,0], [1,-1], [-2,-1], [-2,1], [1,1]]]

# spaceRocks = rock0 + rock1 + rock2
spaceRocks = rock0 
nRockTypes = len(spaceRocks)
nAsteroids = 20

maxExplodeCount = 30
maxShootingDelay = 20


basicShip = [[3,0], [0,3], [6,0], [0,-3], [3,0]]

# Utility functions.

def orientXY(x0, y0):
    x = x0
    y = screenHeight - y0
    return x, y

def deg2Rad(degrees):
    rad = (math.pi/180.0) * degrees
    return rad

def getDist(x0, y0, x1, y1):
    dist = (x1 - x0)**2 + (y1 - y0)**2
    dist = math.sqrt(dist)
    return dist

def rotatePoint(xc, yc, x, y, deg):
    currentAng = math.atan2(y - yc, x - xc)
    angRad = deg2Rad(deg)
    totalAng = currentAng + angRad
    dist = getDist(xc, yc, x, y)
    xNew = xc + math.cos(totalAng)*dist
    yNew = yc + math.sin(totalAng)*dist
    
    return xNew, yNew

# Objects.

    
class Forcefield:
    def __init__(self, x, y):
        self.x,self.y = orientXY(x,y)
        self.radius = 60  # Adjust the radius as needed
        self.active = True

    def draw(self, screen):
        if self.active:
            x, y = orientXY(self.x, self.y)  # Orient the position
            p.draw.circle(screen, RED, (int(x), int(y)), self.radius, 2)

# Create an instance of the Forcefield at the ship's starting position.
forcefield = Forcefield(gameMidX, gameMidY)

class Vitamin:
    def __init__(self):
        self.x = random.randint(0, screenWidth - 1)
        self.y = random.randint(0, screenHeight - 1)
        self.width = 20  # Adjust the width as needed
        self.height = 20  # Adjust the height as needed
        self.active = False
        self.timer = 0

    def activate(self):
        self.x = random.randint(0, screenWidth - 1)
        self.y = random.randint(0, screenHeight - 1)
        self.active = True

    def draw(self, screen):
        if self.active:
            x, y = orientXY(self.x, self.y)

            p.draw.rect(screen, BLUE, [x, y, self.width, self.height])


    def checkCollision(self, spaceShipX, spaceShipY):
        if self.active:

            vitamin_x, vitamin_y = self.x, self.y
            vitamin_width, vitamin_height = self.width, self.height

            # Calculate the boundaries of the vitamin item
            vitamin_left = vitamin_x
            vitamin_right = vitamin_x + vitamin_width
            vitamin_top = vitamin_y
            vitamin_bottom = vitamin_y + vitamin_height

            # Check if the spaceship's coordinates are within the vitamin's boundaries
            if (spaceShipX >= vitamin_left and spaceShipX <= vitamin_right and
                    spaceShipY >= vitamin_top and spaceShipY <= vitamin_bottom):
                self.active = False  # Deactivate the vitamin item

                return True

        return False


# Create an instance of the Vitamin class
vitamin = Vitamin()
class speedyTriangle:
    def __init__(self):
        self.x = random.randint(0, screenWidth - 1)
        self.y = random.randint(0, screenHeight - 1)
        self.heading = random.randint(0, 359)
        self.xVel = random.randint(-maxRockVelocity, maxRockVelocity)
        self.yVel = random.randint(-maxRockVelocity, maxRockVelocity)
        self.Icollided = False
        
        # self.scaleFactorX = random.randint(1, maxRockScaleFactor)
        # self.myRadius = self.x / 2
        self.myRadius = 20
        self.scaleFactorX = 4
        self.scaleFactorY = 4
        # self.scaleFactorY = random.randint(1, maxRockScaleFactor)
        index = random.randint(0, nRockTypes - 1)
        self.myPoints = spaceRocks[index]
        
        # Find center of rotation.
        xSum = ySum = 0
        for myPoint in self.myPoints:
            xSum = xSum + myPoint[0]
            ySum = ySum + myPoint[1]
        
        self.xc = xSum/len(self.myPoints)
        self.yc = ySum/len(self.myPoints)
        
        # Find a bounding box for this asteroid.
        xs = []
        ys = []
        for myPoint in self.myPoints:
            x = myPoint[0]
            y = myPoint[1]
            # Rotate and scale these points.
            xr, yr = rotatePoint(self.xc, self.yc, x, y, self.heading)
            xScale = xr * self.scaleFactorX
            yScale = yr * self.scaleFactorY
            xs.append(xScale)
            ys.append(yScale)
                      
        self.minX = min(xs)
        self.maxX = max(xs)
        self.minY = min(ys)
        self.maxY = max(ys)
        
        # Find average x and y of the points.
        xav = []
        for x in xs:
            xav.append(abs(x))
            
        yav = []
        for y in ys:
            yav.append(abs(y))
            
        xmean = sum(xav)/len(xav)
        ymean = sum(yav)/len(yav)
        # Find a radius for bounce detection.
        self.bounceRadius = math.sqrt(xmean * xmean + ymean * ymean)
        self.bouncing = False

        index = random.randint(0, nColors - 1)
        self.color = colorPalette[index]

        self.isActive = True

        # index = random.randint(0, nColors - 1)
        # self.color = GREEN
        index = random.randint(0, nColors - 1)
        self.color = colorPalette[index]
        
        self.isActive = True
        
    def moveMe(self, spaceshipX, spaceshipY): 
        # Calculate new positon of space rock based on it's velocity.

        #need to modify this so that the triangles will locate the ship and move to it
        # self.x = spaceShip.getxy(spaceship) + self.xVel
        # self.x = self.x + self.xVel

        # self.y = self.y + self.yVel
         # Calculate angle to player's ship
        angle = math.degrees(math.atan2(spaceshipY- self.y, spaceshipX - self.x))

        # Set the heading angle to chase the player
        self.heading = angle
        # if (self.Icollided == False): 
        #     if self.x < spaceshipX:
        #         self.x = self.x +1
        #     if self.x > spaceshipX:
        #         self.x = self.x -1
        #     if self.y < spaceshipY:
        #         self.y = self.y +1
        #     if self.y > spaceshipY:
        #         self.y = self.y -1
        # if self.Icollided == True:
        #     self.x = self.x+1
        if self.Icollided == False:
            if self.x < spaceshipX:
                self.x = self.x +3
            if self.x > spaceshipX:
                self.x = self.x -3
            if self.y < spaceshipY:
                self.y = self.y +3
            if self.y > spaceshipY:
                self.y = self.y -3
            #find arctan between the two points and thats the heading
        # If rock is outside of game space wrap it to other side.
        if (self.x < 0):
            self.x = screenWidth - 1
        elif (self.x > screenWidth):
            self.x = 0
            
        if (self.y < 0):
            self.y = screenHeight - 1
        elif (self.y > screenHeight):
            self.y = 0
            
        return
    def didAstroidsCollide(self, x1, y1, br1):
            whack = False
            astroidDist = getDist(x1, y1, self.x, self.y)
            whackDist = self.bounceRadius + br1
            if (astroidDist < whackDist):
                whack = True
            
            return whack
    def bounce(self):
        xOrY = random.randint(0, 100)
        if (xOrY < 50):
            self.xVel = -1 * self.xVel
        else:
            self.yVel = -1 * self.yVel
        return

    def didCollideWithOtherTriangles(triangle1x, triangle1y, triangle2x, triangle2y, triangle1Radius, triangle2Radius, triangle1, triangle2):
        distance = (math.sqrt((triangle1x-triangle2x)**2) + (math.sqrt((triangle1y-triangle2y)**2)))
        AddRad = triangle1Radius + triangle2Radius
        if distance < AddRad:
            triangle1.yVel=0
            triangle2.yVel=0
            triangle1.xVel=0
            triangle2.xVel = 0
            # triangle1.y=0
            # triangle2.y=0
            # triangle1.x=0
            # triangle2.x = 0
            
            return True
        
    def drawMe(self, screen):
        if (self.isActive):
            points = []
            for myPoint in self.myPoints:
                # Get coords of point.
                x0 = float(myPoint[0])
                y0 = float(myPoint[1])
                
                # Rotate the point.
                myRadius = getDist(self.xc, self.yc, x0, y0)
                theta = math.atan2(y0 - self.yc, x0 - self.xc)
                radAng = deg2Rad(self.heading)
                xr = self.xc + myRadius*math.cos(radAng + theta)
                yr = self.yc + myRadius*math.sin(radAng + theta)
                
                # Scale.
                xs = xr * self.scaleFactorX
                ys = yr * self.scaleFactorY
                
                # Translate.
                xt = xs  + self.x
                yt = ys  + self.y
                
                # Orient to 0,0 being upper left.
                x, y = orientXY(xt, yt)
                
                # Put point into polygon point list.
                points.append([x, y])
                
            p.draw.polygon(screen, self.color, points, width = 2)
        return
    
    def checkCollision(self, x, y,stayAlive):
        smack = False
        if ((x >= self.minX+self.x) and (x <= self.maxX+self.x)):
            
            if ((y >= self.minY+self.y) and (y <= self.maxY+self.y)):
                smack = True
                self.isActive = stayAlive
                
        return smack

class bullet:
    def __init__(self, x0, y0, heading, radius, velocity):
        self.x = x0
        self.y = y0
        self.heading = heading
        self.radius = radius
        self.velocity = velocity
        self.isActive = True
        self.exploding = False
        self.explodeCount = 20
        
    def drawMe(self, surface, color):
        # Draw active bullets.
        if (self.isActive == True):
            x0 = self.x
            y0 = self.y
            x, y = orientXY(x0, y0)
            center = [x, y]
            
            if (self.exploding):
                p.draw.circle(surface, color, center, self.explodeCount)
                self.explodeCount = self.explodeCount + 1
                if (self.explodeCount == maxExplodeCount):
                    self.isActive = False
            else:
                p.draw.circle(surface, color, center, self.radius, width = 2)
            
            
        
    def moveMe(self):
        if ((self.isActive) and (self.exploding == False)):
            # Calculate new positon of bullet based on it's velocity.
            radAng = deg2Rad(self.heading)
            self.x = self.x + self.velocity*math.cos(radAng)
            self.y = self.y + self.velocity*math.sin(radAng)
            # If bullet is outside of game space set it to inactive.
            if ((self.x < 0) or (self.x > screenWidth)):
                self.isActive = False
            elif ((self.y < 0) or (self.y > screenHeight)):
                self.isActive = False
        return
    
    def setExplosion(self):
        self.exploding = True
        mixer.Sound('asteroid-hitting-something-152511.mp3').play()
        

class spaceShip:
    def __init__(self, x0, y0, heading0, scaleFactor0, points):
        self.x = x0
        self.y = y0
        self.heading = heading0
        self.scaleFactor = scaleFactor0
        
        # Find center of rotation.
        xSum = ySum = 0
        for myPoint in points:
            xSum = xSum + myPoint[0]
            ySum = ySum + myPoint[1]
        
        self.xc = xSum/len(points)
        self.yc = ySum/len(points)
        
    
        self.gunSpot = []
        self.gunX = 0
        self.gunY = 0
        
        return
    
    def getxy(self):
        x = self.x
        y= self.y
        return x,y
    def setGunSpot(self, gunSpot):
        self.gunSpot = gunSpot
        return
    
    def getGunSpot(self):
        return self.gunX, self.gunY
    
    def moveMe(self, inc):
        # Move ship along current course.
        radAng = deg2Rad(self.heading)
        self.x = self.x + inc * math.cos(radAng)
        self.y = self.y + inc * math.sin(radAng)
        # If ship goes out of screen, wrap it other side.
        if (self.x < 0):
            self.x = screenWidth - 1
        elif (self.x > screenWidth):
            self.x = 0
            
        if (self.y < 0):
            self.y = screenHeight - 1
        elif (self.y > screenHeight):
            self.y = 0
        
        return
    
    def drawMe(self, screen, color, myShip):
        points = []
        isTheGunSpot = False
        for myPoint in myShip:
            if (myPoint == self.gunSpot):
                isTheGunSpot = True
                
            # Get coords of point.
            x0 = float(myPoint[0])
            y0 = float(myPoint[1])
            
            # Rotate the point.
            myRadius = getDist(self.xc, self.yc, x0, y0)
            theta = math.atan2(y0 - self.yc, x0 - self.xc)
            radAng = deg2Rad(self.heading)
            xr = self.xc + myRadius*math.cos(radAng + theta)
            yr = self.yc + myRadius*math.sin(radAng + theta)
            
            # Scale.
            xs = xr * self.scaleFactor
            ys = yr * self.scaleFactor
            
            # Translate.
            xt = xs  + self.x
            yt = ys  + self.y
            
            # Save gun position.
            if (isTheGunSpot == True):
                self.gunX = xt
                self.gunY = yt
                isTheGunSpot = False
            
            # Orient to 0,0 being upper left.
            x, y = orientXY(xt, yt)
            
            # Put point into polygon point list.
            points.append([x, y])
            
        p.draw.polygon(screen, color, points, width = 2)
        return
    
    def turn(self, inc):
        self.heading = self.heading + inc
        
        if (self.heading > 359):
            self.heading = 0
        elif (self.heading < 0):
            self.heading = 359
        
            
        return
        
class forceField():
    def __init__(self, spaceShipX, spaceShipY):
        pass
    print("force field activated")       

def asteroidMe():
    # Initialize pygame.
    p.init()

    special = 0

    mixer.init()

    mixer.music.load('Ephixa - Zelda Step - 04 Gerudo Valley Dubstep Remix.mp3')
    mixer.music.play(-1)  # -1 means the music will loop indefinitely

    game_over = False
    # Set the width and height of the screen [width, height]
    size = (screenWidth, screenHeight)
    screen = p.display.set_mode(size)
     
    p.display.set_caption("asteroidMe()")
    
    # Set up random number generator.
    random.seed()
     
    # Loop until the user clicks the close button.
    running = True 
    game_timer = 0
    game_time = 0
    last_spawn_time = 0 
    spawn_rate = 60
    # Used to manage how fast the screen updates
    clock = p.time.Clock()
    
    # Set up some game objects.
    # Space ship stuff.
    initialHeading = 90
    scaleFactor = 6
    ship = spaceShip(gameMidX, gameMidY, initialHeading, scaleFactor, basicShip)
    shipSpeed = 8
    ship.setGunSpot([6,0])
    
    # Bullet stuff
    bullets = []
    bulletSize = int(0.5 * scaleFactor)
    bulletSpeed = 3 * shipSpeed
    shotCount = 0
    
    # Make some asteroids - that is space rocks.
    myAsteroids = []
    for j in range(nAsteroids):
        myAsteroids.append(speedyTriangle())
    
    # Clock/game frame things.
    tickTock = 0
    
    clock = p.time.Clock()
    counter, text = 120, '120'.ljust(5)
    p.time.set_timer(p.USEREVENT, 1000)
    font = p.font.SysFont('Consolas', 30)
    # -------- Main Program Loop -----------
    while running:


        if counter <= 0 or text == 'boom!':  
            game_over = True
        # --- Main event loop
        
        for event in p.event.get():
            if event.type == p.USEREVENT: 
                counter -= 1
                text = str(counter).ljust(15) if counter > 0 else 'boom!'
            if text == 'boom!':
                game_over = True
            if event.type == p.QUIT:
                running = False
        
        """ Check for keyboard presses. """
        key = p.key.get_pressed()
        
        # Handle keypresses.
        if (key[p.K_ESCAPE] == True): 
            running = False
        if (key[p.K_UP] == True): 
            # ship.moveMe(shipSpeed)
            pass
        if (key[p.K_w] == True):
            ship.moveMe(shipSpeed)
        if (key[p.K_DOWN] == True): 
            # ship.moveMe(-1 * shipSpeed)
            pass
        if (key[p.K_s]==True):
            ship.moveMe(-1 * shipSpeed)
            
        if (key[p.K_LEFT] == True):
            # ship.turn(1)
            pass
        if (key[p.K_a]==True):

            ship.turn(1)
        if (key[p.K_RIGHT] == True):
            # ship.turn(-1)
            pass
        if (key[p.K_d]==True):
            ship.turn(-1)
        if (key[p.K_SPACE] == True):
            if (shotCount <= 10):
                gunX, gunY = ship.getGunSpot()
                myBullet = bullet(gunX, gunY, ship.heading, bulletSize, bulletSpeed)
                bullets.append(myBullet)
                mixer.Sound('zap_c_07-82067.mp3').play()

                shotCount = maxShootingDelay
            
        # --- Game logic should go here
        # Move bullets and asteroids.
        for b in bullets:
            b.moveMe()

        # for a in  myAsteroids:
        #     for A in myAsteroids:moveMe
        #         if (a != A) {
        #             # check for collision
        #             # if collision == true, then do not move triangle
        #         }
            
        for a in myAsteroids:
            x,y = spaceShip.getxy(ship)
            a.moveMe(x,y)
            
        for a in myAsteroids:
            triangle1x = a.x
            triangle1y = a.y
            triangle1Rad = a.myRadius
            # triangle1Vel = a.yVel
            
            for b in myAsteroids:
                triangle2x = b.x
                triangle2y = b.y
                triangle2Rad = b.myRadius
                # triangle2Vel = b.yVel
                if (a!=b):
                    #myQuestion = speedyTriangle.didCollideWithOtherTriangles(triangle1x, triangle1y, triangle2x, triangle2y,triangle1Rad, triangle2Rad, a, b)
                    myDist = getDist(a.x, a.y, b.x, b.y)
                    #tooClose = a.myRadius + b.myRadius
                    tooClose = 20
                    if (myDist < tooClose):
                        a.Icollided = True
                        b.Icollided = True
    
    
                    if b.Icollided == True:
                        a.Icollided = False
                        b.x = b.x-0.1
                        b.y = b.y-0.1
                        a.x = a.x+0.1
                        a.y = a.y - 0.1
        game_timer += 1
        vitamin.timer += 1
        game_time += 1
        if game_time - last_spawn_time >= spawn_rate:
            myAsteroids.append(speedyTriangle())
            last_spawn_time = game_time 
        if vitamin.timer >= 1800 and not vitamin.active:
            vitamin.activate()
            vitamin.timer = 0

        # Calculate the oriented position of the circle (Forcefield) centered on the ship.
        if game_timer <= 600:  # 60 frames per second for 10 seconds
            forcefield.x, forcefield.y = orientXY(ship.x, ship.y)   
        # Check to see if a bullet hit an asteroid.
        for a in myAsteroids:
            if a.isActive:
                # Check if the circle (Forcefield) and the green triangle collide with outer edge.
                forcefield_center_x, forcefield_center_y = forcefield.x, forcefield.y
                triangle_x, triangle_y = orientXY(a.x, a.y)
                distance = getDist(forcefield_center_x, forcefield_center_y, triangle_x, triangle_y)
                if game_timer <= 600 and distance < (
                        forcefield.radius + 3):  # 3 is a buffer to prevent touching the ship
                    # Destroy the green triangle.
                    a.isActive = False
            for b in bullets:
                if (a.isActive and b.isActive):
                    smacked = a.checkCollision(b.x, b.y, True)
                    # special+=100
                    if (smacked == True):
                        b.setExplosion()
                        a.isActive = False
                        special+=100
            if vitamin.checkCollision(ship.x, ship.y):
            # Reactivate the forcefield for another ten seconds.
                game_timer = 0
            if game_timer <= 600:
            # Only perform the check for the first 10 seconds
                for a in myAsteroids:
                    if a.isActive:
                        forcefield_center_x, forcefield_center_y = forcefield.x, forcefield.y
                        triangle_x, triangle_y = orientXY(a.x, a.y)
                        distance = getDist(forcefield_center_x, forcefield_center_y, triangle_x, triangle_y)
                        if distance < (forcefield.radius + a.bounceRadius):
                            a.exploding = True  # Set the exploding flag for the asteroid
                            a.isActive = False
        # for a in myAsteroids:
        #     for A in myAsteroids:
        #         if (a != A):
        #             if (a.isActive and A.isActive):
        #                 if (a.bouncing == False) and (A.bouncing == False):
        #                     smacked = a.checkCollision(A.x, A.y, True)
        #                     #whacked = a.didAstroidsCollide(A.x, A.y, A.bounceRadius)
        #                     if (smacked == True):
        #                         a.bounce()
        #                         A.bounce()
        #                         a.bouncing = True
        #                         A.bouncing = True
        # --- Screen-clearing code goes here
     
        # Here, we clear the screen to black. Don't put other drawing commands
        # above this, or they will be erased with this command.
     
        # If you want a background image, replace this clear with blit'ing the
        # background image.

        screen.blit(background_image, (0, 0))
        counter_surface = font.render(text, True, BLACK)

        screen.blit(counter_surface, (screenWidth - 200, 60))
        # --- Drawing code should go here
        # Spaceship
        ship.drawMe(screen, WHITE, basicShip)
        
        # Bullets
        for b in bullets:
            b.drawMe(screen, CYAN)
            
        # Asteroids
        for a in myAsteroids:
            a.drawMe(screen)
        if game_timer <= 600:  # 60 frames per second for 10 seconds
            forcefield.x, forcefield.y = ship.x, ship.y
            forcefield.draw(screen)
        vitamin.draw(screen) 
        if game_over:
            screen.fill(BLACK)  # Clear the screen
            mixer.music.stop()
            mixer.Sound('item-catch.mp3').play()

            game_over_text = font.render("You win!", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            exit_text = font.render("Press Q to Quit", True, WHITE)

            # Display game over message and options on the screen
            screen.blit(game_over_text, (screenWidth // 2 - 70, screenHeight // 2 - 50))
            screen.blit(restart_text, (screenWidth // 2 - 120, screenHeight // 2 + 20))
            screen.blit(exit_text, (screenWidth // 2 - 90, screenHeight // 2 + 60))
            p.display.flip()

            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                if event.type == p.KEYDOWN:
                    if event.key == p.K_q:
                        p.quit()

                    elif event.key == p.K_r:
                        # Reset the game state if the player wants to restart
                        game_over = False
                        asteroidMe()

                        # Reinitialize your game objects like ship, bullets, and asteroids
                        ship = spaceShip(gameMidX, gameMidY, initialHeading, scaleFactor, basicShip)
                        bullets = []
                        myAsteroids = [speedyTriangle() for _ in range(nAsteroids)]
     
        # --- Go ahead and update the screen with what we've drawn.
        font = p.font.SysFont('Consolas', 30)
        points_text = font.render("Points: {}".format(special), True, WHITE)
        screen.blit(points_text, (150, 20))
        p.display.flip()
     
        # --- Limit to 60 frames per second
        clock.tick(60)
        
        # Update frame count.
        tickTock = tickTock + 1
        
        # Implement shooting delay to keep bullet count lower.
        if (shotCount > 0):
            shotCount = shotCount - 1
        # Do some book keeping on arrays.
        # Remove inactive elements of bullets array.
        # Remove inactive elements of asteroids array.
     
    # Close the window and quit.
    p.quit()
    
    return

asteroidMe()