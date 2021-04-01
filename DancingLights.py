"""
DancingLights - Python Arcade
By A.D.Tejpal - 01-Apr-2021

Demonstrates display of animated lights by using the module:
arcade.experimental.lights

There is a soft light object at center of a light wheel, having six
normal light objects at its periphery.

The ligh objects pulsate between max / min size, while the light
wheel as a whole keeps moving all over the screen, at the same
time, rotating around its axis.
"""
import arcade
import arcade.experimental.lights
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 560
SCREEN_TITLE = "Dancing Lights"
FPS = 30   # Frames per sec
VIEWPORT_MARGIN = 200
MOVEMENT_SPEED = 5

# This is the color used for 'ambient light'.
# If you don't want any ambient light, it can be set to black.
AMBIENT_COLOR = (60, 60, 60)

class GamePlay(arcade.Window):
    def __init__(self):
        super().__init__(
            SCREEN_WIDTH, SCREEN_HEIGHT,
            SCREEN_TITLE, update_rate=1/FPS,
            resizable=False)

        # Sprite lists
        self.bakgroundSprites = None

        # --- Light related ---
        # List of all the lights
        self.lightLayer = None

        # This list is used to generate light objects
        # for adding them to self.lightLayer
        self.lightColors = [
            arcade.csscolor.WHITE,
            arcade.csscolor.RED, 
            arcade.csscolor.GREEN,
            arcade.csscolor.BLUE,
            arcade.csscolor.RED,             
            arcade.csscolor.GREEN,
            arcade.csscolor.BLUE]

        # Min Max radius of light objects.
        self.lightRadMin = 60
        self.lightRadMax = 120
        # Current radius of light objects.
        self.lightRad = self.lightRadMin

        # Min Max radius of light wheel
        self.wheelRadMin = 0
        self.wheelRadMax = 120
        # Current radius of light wheel
        self.wheelRad = 0
        # Center position of light wheel
        self.wheelCenterX = SCREEN_WIDTH // 2
        self.wheelCenterY = SCREEN_HEIGHT // 2
        # Rotational angle of light wheel in radians
        self.tiltAngle = 0

        # Incremental change per frame in radius of light wheel
        self.dRadWheel = 0.5
        # Incremental change per frame in radius of light objects
        self.dRadLights = 0.1
        # Incremental movement per frame of light wheel
        # center in x, y directions.
        self.dx = 1
        self.dy = 1
        # Incremental rotation of light wheel in radians per frame
        self.dtilt = 0.01

    def setup(self):
        # Create sprite list
        self.backgroundSprites = arcade.SpriteList()

        # --- Light related ---
        # Lights must shine on something. If there is no background
        # sprite or color, you will just see black. Therefore, we use a
        # loop to create a whole bunch of brick tiles for the background.
        for x in range(-128, SCREEN_WIDTH + 128, 128):
            for y in range(-128, SCREEN_HEIGHT + 128, 128):
                sprite = arcade.Sprite(
                    ":resources:images/tiles/brickTextureWhite.png")
                sprite.position = x, y
                self.backgroundSprites.append(sprite)

        # Create a light layer, used to render things to, then
        # post-process and add lights. This must match the screen size.
        self.lightLayer = arcade.experimental.lights.LightLayer(
            SCREEN_WIDTH, SCREEN_HEIGHT)
        # We can also set the background color that will be lit by lights,
        # but in this instance we just want a black background
        self.lightLayer.set_background_color(arcade.color.BLACK)

        # Create lights as per color list and
        # add the same to self.lightLayer
        x = self.wheelCenterX
        y = self.wheelCenterY
        radius = self.lightRadMin

        # First light in the list (white color) will be
        # soft mode. All others - hard mode
        for color in self.lightColors:
            if color == self.lightColors[0]:
                mode = "soft"
            else:
                mode = "hard"

            light = arcade.experimental.lights.Light(
                x, y, radius, color, mode)
            self.lightLayer.add(light)

    def on_update(self, delta_time):
        """ Movement and game logic """

        # For rotation of light wheel:
        self.tiltAngle = self.tiltAngle + self.dtilt
        # Remove redundant multiples of 2 pi radians
        self.tiltAngle = self.tiltAngle % (2 * math.pi)

        # For movement of light wheel across x axis
        wcX = self.wheelCenterX + self.dx
        if wcX > SCREEN_WIDTH - self.wheelRadMax:
            self.dx = - self.dx
            wcX = SCREEN_WIDTH - self.wheelRadMax

        if wcX < self.wheelRadMax:
            self.dx = - self.dx
            wcX = self.wheelRadMax

        self.wheelCenterX = wcX

        # For movement of light wheel across y axis
        wcY = self.wheelCenterY + self.dy
        if wcY > SCREEN_HEIGHT - self.wheelRadMax:
            self.dy = - self.dy
            wcY = SCREEN_HEIGHT - self.wheelRadMax

        if wcY < self.wheelRadMax:
            self.dy = - self.dy
            wcY = self.wheelRadMax

        self.wheelCenterY = wcY

        # For radial expansion of light wheel at start
        r = self.wheelRad + self.dRadWheel
        if r > self.wheelRadMax:
            r = self.wheelRadMax

        self.wheelRad = r

        # For placing the center light object at updated
        # position resulting from incremental x, y movement
        self.lightLayer[0].position = (
            self.wheelCenterX, self.wheelCenterY)

        # For pushing the other light objects along 
        # expanding radius of light wheel, duly taking
        # into account the incremental rotation per frame
        nc = len(self.lightColors) - 1
        # Equal angular spacing for outer light objects
        stepAngle = 2 * math.pi / nc
        a = 0
        # We start at index 1 so that central light object
        # (with index 0) is not affected by this loop.
        for n in range(1, nc + 1, 1):
            ta = a + self.tiltAngle
            x = self.wheelRad * math.cos(ta)
            y = self.wheelRad * math.sin(ta)

            # For placing the light objects at updated
            # position resulting from all incremental movements
            self.lightLayer[n].position = (
                x + self.wheelCenterX, y + self.wheelCenterY)

            # During initial expansion of light wheel, all light
            # objects too expand at proportionate rate.
            # Thereafter, the light objects are governed by
            # continuing cycle of expansion / contraction
            # within max / min range.
            if self.wheelRad < self.wheelRadMax:
                r = 0.4 * self.wheelRad
                self.lightLayer[0].radius = r
                self.lightLayer[n].radius = r
            else:
                r = self.lightLayer[0].radius + self.dRadLights
                if r > self.lightRadMax:
                    self.dRadLights = - self.dRadLights
                    r = self.lightRadMax

                if r < self.lightRadMin:
                    self.dRadLights = - self.dRadLights
                    r = self.lightRadMin

                self.lightLayer[0].radius = r
                self.lightLayer[n].radius = r
                    
            a = a + stepAngle

    def on_draw(self):
        """ Draw everything. """
        arcade.start_render()

        # Everything that should be affected by lights gets rendered
        # inside this 'with' statement. Nothing is rendered to the screen
        # yet, just the light layer.
        with self.lightLayer:
            self.backgroundSprites.draw()
        
        # Draw the light layer to the screen.
        # This fills the entire screen with the lit version
        # of what we drew into the light layer above.
        self.lightLayer.draw(ambient_color=AMBIENT_COLOR)

#======================
if __name__ == "__main__":
    gp = GamePlay()
    gp.setup()
    arcade.run()
