#I want a ashtroid game that is similar to that one xbox game
#shapes follow the player
# player has 3 lives
# each shape when defeated gives points
# circle //red
# triangle //green // faster than the other shapes
# squares // yellow or blue
# sheild for 10 seconds
# when hit bigger ashtroid, it splits into two smaller ones and if smaller one, it deletes
# the amount of ashtroids increases for how long you play.
# player has 3 lives
#game keeps going until timer runs out or player runs out of lives

# -*- coding: utf-8 -*-


import pygame as p
import random
import math

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

colorPalette = [WHITE, GREEN, RED, ORANGE, YELLOW, CYAN, MAGENTA]
nColors = len(colorPalette)

screenWidth = 1600
screenHeight = 850

gameMidX = screenWidth/2
gameMidY = screenHeight/2

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
maxShootingDelay = 30


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
# Modify the Forcefield class to correctly orient its position.
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

    def checkCollision(self, x, y):
        if self.active:
            x1, y1 = self.x, self.y
            x2, y2 = x1 + self.width, y1 + self.height
            if x >= x1 and x <= x2 and y >= y1 and y <= y2:
                self.active = False
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
        self.exploding = False  # Add an exploding flag
        self.explodeCount = 20  # Explosion effect count
        # self.scaleFactorX = random.randint(1, maxRockScaleFactor)
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

        index = random.randint(0, nColors - 1)
        self.color = GREEN
        # Find average x and y of the points.
        xav = []
        for x in xs:
            xav.append(abs(x))

        yav = []
        for y in ys:
            yav.append(abs(y))

        xmean = sum(xav) / len(xav)
        ymean = sum(yav) / len(yav)

        # Find a radius for bounce detection.
        self.bounceRadius = math.sqrt(xmean * xmean + ymean * ymean)
        self.bouncing = False



        self.isActive = True

    def moveMe(self):
        # Calculate new positon of space rock based on it's velocity.
        self.x = self.x + self.xVel
        self.y = self.y + self.yVel

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
                xt = xs + self.x
                yt = ys + self.y

                # Orient to 0,0 being upper left.
                x, y = orientXY(xt, yt)

                # Put point into polygon point list.
                points.append([x, y])

            p.draw.polygon(screen, self.color, points, width=2)

        return

    def checkCollision(self, x, y, stayAlive):
        smack = False
        if ((x >= self.minX + self.x) and (x <= self.maxX + self.x)):

            if ((y >= self.minY + self.y) and (y <= self.maxY + self.y)):
                smack = True
                self.isActive = stayAlive
        return smack

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
                p.draw.circle(surface, color, center, self.radius, width=1)

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



def asteroidMe():
    # Initialize pygame.
    p.init()

    # Set the width and height of the screen [width, height]
    size = (screenWidth, screenHeight)
    screen = p.display.set_mode(size)

    p.display.set_caption("asteroidMe()")

    # Set up random number generator.
    random.seed()

    # Loop until the user clicks the close button.
    running = True
    game_timer = 0
    # Used to manage how fast the screen updates
    clock = p.time.Clock()

    # Set up some game objects.
    # Space ship stuff.
    initialHeading = 90
    scaleFactor = 6
    ship = spaceShip(gameMidX, gameMidY, initialHeading, scaleFactor, basicShip)
    shipSpeed = 3
    ship.setGunSpot([6,0])

    # Bullet stuff
    bullets = []
    bulletSize = int(0.5 * scaleFactor)
    bulletSpeed = 3 * shipSpeed
    shotCount = 0
    proximityCount = 0

    # Make some asteroids - that is space rocks.
    myAsteroids = []
    for j in range(nAsteroids):
        myAsteroids.append(speedyTriangle())

    # Clock/game frame things.
    tickTock = 0

    # -------- Main Program Loop -----------
    while running:
        # --- Main event loop
        for event in p.event.get():
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
                shotCount = maxShootingDelay

        # --- Game logic should go here
        # Move bullets and asteroids.
        for b in bullets:
            b.moveMe()

        for a in myAsteroids:
            a.moveMe()
            a.bouncing = False

            # Check for astroid to astroid collisions.
        for a in myAsteroids:
            for A in myAsteroids:
                if (a != A):
                    if (a.isActive and A.isActive):
                        if (a.bouncing == False) and (A.bouncing == False):
                            smacked = a.checkCollision(A.x, A.y, True)
                            # whacked = a.didAstroidsCollide(A.x, A.y, A.bounceRadius)
                            if (smacked == True):
                                a.bounce()
                                A.bounce()
                                a.bouncing = True
                                A.bouncing = True

        # Inside the game loop, update the game_timer.
        game_timer += 1
        vitamin.timer += 1

        # Check if 30 seconds have passed, and the vitamin is not active
        if vitamin.timer >= 1800 and not vitamin.active:
            vitamin.activate()
            vitamin.timer = 0

        # Calculate the oriented position of the circle (Forcefield) centered on the ship.
        if game_timer <= 600:  # 60 frames per second for 10 seconds
            forcefield.x, forcefield.y = orientXY(ship.x, ship.y)

        # Check for collisions between green triangles and the circle (Forcefield).
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

        for a in myAsteroids:
            for b in bullets:
                if (a.isActive and b.isActive):
                    smacked = a.checkCollision(b.x, b.y, False)
                    if (smacked == True):
                        b.setExplosion()

        # Check for collisions between the ship and the vitamin.
        if vitamin.checkCollision(ship.x, ship.y):
            # Reactivate the forcefield for another ten seconds.
            game_timer = 0

        # Check for collisions between asteroids and the forcefield.
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

        # --- Screen-clearing code goes here

        # Here, we clear the screen to black. Don't put other drawing commands
        # above this, or they will be erased with this command.

        # If you want a background image, replace this clear with blit'ing the
        # background image.
        screen.fill(BLACK)

        # --- Drawing code should go here

        # Spaceship
        ship.drawMe(screen, WHITE, basicShip)

        # Bullets
        for b in bullets:
            b.drawMe(screen, RED)

        # Asteroids
        for a in myAsteroids:
            a.drawMe(screen)

        # Draw the circle (Forcefield) around the player's ship for the first ten seconds.
        if game_timer <= 600:  # 60 frames per second for 10 seconds
            forcefield.x, forcefield.y = ship.x, ship.y
            forcefield.draw(screen)

        # Draw the vitamin
        vitamin.draw(screen)

        # --- Go ahead and update the screen with what we've drawn.
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
