try:
    import string
    import pygame
    from pygame.locals import *
except ImportError as e: # most likely a ModuleNotFoundError
    raise Exception('Could not import a module: %s.' % e)

class Button:
    def __init__(self, ctx, text, text_size, position, dimensions, color, alt_color, hover_color, text_color):
        '''
        Create a Button instance.
        
        Args:
            ctx       (__main__.Application) : context of the Application instance required for rendering the button
            text                       (str) : text to be displayed on the button
            text_size                  (int) : text height in pixels
            position                  (list) : two values stating coordinates of the button
            dimensions                (list) : a tuple or list of two values indicating the width and height the rectangular button should be
            color                    (tuple) : the color of the center of the button 
            alt_color                (tuple) : the color of the button border 
            hover_color              (tuple) : the color of the center of the button upon mouse hover
            text_color               (tuple) : the color of the button text
        '''
        self.ctx        = ctx
        self.text       = text
        self.text_size  = text_size
        self.position   = position
        self.dimensions = dimensions
        self.colors     = {'primary':color      ,
                           'alt'    :alt_color  ,
                           'hover'  :hover_color,
                           'text'   :text_color }
        # button coords based off the center of the button using (desired_x - button_width*0.5 , desired_y - button_height*0.5)
        self.rect = pygame.Rect((round(position[0]-(dimensions[0]*0.5)),round(position[1]-(dimensions[1]*0.5))),
                                      (dimensions[0],dimensions[1])) # create button as a Rect object
        self.render(self.colors['primary'])

    def render(self, color):
        '''
        Draw the button onto the display.
        
        Args:
            color (tuple) : the color of the center of the button 
        '''
        pygame.draw.rect(self.ctx.screen, self.colors['alt'], self.rect) # draw the button frame
        pygame.draw.rect(self.ctx.screen, color, pygame.Rect((self.rect.x+5,self.rect.y+5),
                                                             (self.rect.width-10,self.rect.height-10))) # draw the button inside (making a 10 pixel wide frame)
        font  = pygame.font.Font('.\\assets\\font.ttf', self.dimensions[1]-self.text_size) # load the correct font
        label = font.render(self.text, True, self.colors['text'])
        self.ctx.screen.blit(label, (self.position[0]-self.dimensions[0]*.45,self.position[1]-self.dimensions[1]*.45)) # render the text in the middle of the button

    def check(self, mouse_pos):
        '''
        Test whether the button is being hovered over and whether it has been clicked.
        
        Args:
            mouse_pos   (tuple) : mouse coordinates

        Returns:
            True         (bool) : boolean value
            False        (bool) : boolean value
        '''
        if self.rect.collidepoint(mouse_pos): # if the mouse is over the button
            self.render(self.colors['hover'])
            return True
        else:
            self.render(self.colors['primary'])
            return False

    def set_position(self, position):
        '''
        Set the position of a button.

        Args:
            position (list) : two values stating coordinates of the button
        '''
        self.position = position
        self.rect = pygame.Rect((round(position[0]-(self.dimensions[0]*0.5)),round(position[1]-(self.dimensions[1]*0.5))),
                                      (self.dimensions[0],self.dimensions[1]))

class ScrollBar:
    def __init__(self, ctx, dimensions, position, scroll_length, color, alt_color, clicked_color, scroll_position=0):
        '''
        Create a scroll bar instance.
        
        Args:
            ctx             (__main__.Application) : context of the Application instance required for rendering the scroll bar
            dimensions                      (list) : width and height of the scroll bar
            position                        (list) : two values stating the coordinates of the scroll bar
            scroll_length                    (int) : number of pixels needed to be scrolled
            color                          (tuple) : slider track color  
            alt_color                      (tuple) : slider thumb when not clicked color
            clicked_color                  (tuple) : slider thumb when clicked color
            scroll_position                  (int) : how far along the scroll bar notch is (assumed to never be larger than the scroll length)
                                                     default: 0 
        '''
        self.ctx        = ctx
        self.dimensions = dimensions
        self.position   = position
        if scroll_length <= dimensions[0]: # if the scrollable area is less than the width of the scroll bar track, set to the scroll bar track width (no scrolling needed)
            self.scroll_length = dimensions[0] + 1 # add 1 to avoid a division by 0 error
        else:
            self.scroll_length = scroll_length
        self.scroll_position = scroll_position
        self.colors = {'primary':color        ,
                       'alt'    :alt_color    ,
                       'clicked':clicked_color}
        self.scroll_bar_track = pygame.draw.rect(ctx.screen, color, pygame.Rect((round(position[0]-(dimensions[0]*0.5)),round(position[1]-(dimensions[1]*0.5))), # adjust from coords based on middle of object to top left
                                                                                (dimensions[0],dimensions[1])))
        # the size of the scroll notch is: (size of scroll bar) / ( (scrolling length) * (size of scroll bar) )
        self.scroll_bar_thumb = pygame.draw.rect(ctx.screen, alt_color, pygame.Rect((self.scroll_bar_track.x+scroll_position,self.scroll_bar_track.y),
                                                                                    (self.scroll_bar_track.width/(scroll_length+1000)*self.scroll_bar_track.width,self.scroll_bar_track.height)))
        self.was_scroll_bar_clicked = False # track whether the thumb was clicked last cycle
        # scroll amount per pixel change in thumb: (scrolling length) / ( ( (x coord of the right most wall of the scroll bar track)-(thumb width) )-(x position of scroll bar track) )
        # or, the scrolling length divided by the number of pixels the scroll bar can travel
        try:
            self.scroll_amount = scroll_length/((self.scroll_bar_track.right-self.scroll_bar_thumb.width)-self.scroll_bar_track.x)
        except ZeroDivisionError:
            self.scroll_amount = 0

    def render(self, thumb_color):
        '''
        Draw the scroll bar and notch onto the display.
        
        Args:
            thumb_color (tuple) : the color of the thumb
        '''
        pygame.draw.rect(self.ctx.screen, self.colors['primary'], self.scroll_bar_track)
        pygame.draw.rect(self.ctx.screen, thumb_color, self.scroll_bar_thumb)

    def check(self, mouse_pos, mouse_clicked):
        '''
        
        '''
        if self.was_scroll_bar_clicked:
            if mouse_clicked:
                self.scroll_bar_thumb = self.scroll_bar_thumb.move(mouse_pos[0]-self.last_mouse_pos[0], 0) # move the thumb by the change in mouse x-axis position
                self.scroll_position -= self.scroll_amount*(mouse_pos[0]-self.last_mouse_pos[0]) # change the scroll position by the scroll amount times the same change
                if self.scroll_bar_track.contains(self.scroll_bar_thumb):
                    self.render(self.colors['clicked'])
                else:
                    self.scroll_bar_thumb = self.scroll_bar_thumb.move(-(mouse_pos[0]-self.last_mouse_pos[0]), 0) # undo the above thumb and scroll position changes
                    self.scroll_position += self.scroll_amount*(mouse_pos[0]-self.last_mouse_pos[0])
            else:
                self.render(self.colors['alt'])
                self.was_scroll_bar_clicked = False
        elif self.scroll_bar_thumb.collidepoint(mouse_pos) and mouse_clicked: # if the scroll bar thumb has been clicked
            self.was_scroll_bar_clicked = True
        self.last_mouse_pos = mouse_pos # keep track of the mouse position of the last cycle
        
    def get_notch_position(self):
        return self.scroll_position

class SongTab:
    def __init__(self, ctx, start_pos, song=['name','difficulty','location'], highscore=-1):
        self.ctx       = ctx
        self.start_pos = start_pos
        self.position  = start_pos
        self.song      = song
        self.button    = Button(self.ctx, text='play', text_size=22, position=[self.position+125,400], dimensions=[160,75], color=(213,240,247), alt_color=(0,162,232), hover_color=(58,186,218), text_color=(0,0,0))
        self.highscore = highscore

    def render(self):
        pygame.draw.rect(self.ctx.screen, (0,162,232), (self.position, 115, 250, 350))
        pygame.draw.rect(self.ctx.screen, (153,217,234), (self.position+5, 120, 240, 340)) # 5 pixels smaller to create a border

        font_40  = pygame.font.Font('.\\assets\\font.ttf', 40) # size 40 text
        font_20  = pygame.font.Font('.\\assets\\font.ttf', 20) # size 20 text
        name = font_40.render(self.song[0], True, (0,0,0)) # create the song name text
        diff = font_20.render(self.song[1], True, (0,0,0)) # create the song difficulty text
        self.ctx.screen.blit(name, (self.position+10,120)) # render all the text
        self.ctx.screen.blit(diff, (self.position+10,170))

        if self.highscore >= 0:
            highscore = font_20.render(f'Highscore: {self.highscore}%', True, (0,0,0))
            self.ctx.screen.blit(highscore, (self.position+10,200))

    def set_x(self, x):
        self.button.set_position([self.start_pos+125+x,400])
        self.position = self.start_pos + x

    def get_x(self):
        return self.position

class TextInput:
    def __init__(self, ctx, dimensions, position, character_limit, allowed_characters, color, active_color, input_hidden=False):
        self.ctx             = ctx
        self.dimensions      = dimensions
        self.position        = position
        self.character_limit = character_limit
        self.colors          = {'inactive':color       ,
                                'active'  :active_color}
        self.rect            = pygame.Rect(position, dimensions)
        self.allowed_characters = allowed_characters
        self.input_hidden = input_hidden
        self.is_active = False
        self.cursor = None
        self.value = []
        self.cursor_position = 0

    def render(self):
        if self.is_active:
            pygame.draw.rect(self.ctx.screen, self.colors['active'], self.rect)
        else:
            pygame.draw.rect(self.ctx.screen, self.colors['inactive'], self.rect)
        font = pygame.font.Font('.\\assets\\font.ttf', self.dimensions[1])
        if self.input_hidden:
            text = font.render('•'*len(self.value), True, (0,0,0))
        else:
            text = font.render(''.join(self.value), True, (0,0,0))
        self.ctx.screen.blit(text, (self.rect.left,self.rect.top-(.2*self.dimensions[1])))

    def check(self, mouse_pos, mouse_clicked):
        if self.rect.collidepoint(mouse_pos):
            self.cursor = pygame.cursors.compile(pygame.cursors.textmarker_strings)
            pygame.mouse.set_cursor((8,16),(0,0),*self.cursor)
            if mouse_clicked:
                self.is_active = True
        else:
            if self.cursor:
                pygame.mouse.set_cursor(*pygame.cursors.arrow)
                self.cursor = None
            if mouse_clicked:
                self.is_active = False
        self.render()

    def key_press(self, key, key_type='char'):
        if self.is_active:
            if key_type == 'char':
                if key == '\x08': # Backspace
                    try: # If value is empty an index error will be raised if a del is performed on it
                        del self.value[self.cursor_position-1]
                        self.cursor_position -= 1
                    except IndexError: # Catch redundant error
                        pass
                elif len(self.value) < self.character_limit: # Only continue if the current length of the input is less than the maximum allowed length
                    if key in self.allowed_characters: # Make sure the character is valid for the input 
                        self.value.insert(self.cursor_position, key) # Insert the character at the cursor position
                        self.cursor_position += 1
                    
            if key_type == 'action':
                if key == 276 and self.cursor_position > 0: # Left arrow
                    self.cursor_position -= 1
                elif key == 275 and self.cursor_position < len(self.value): # Right arrow
                    self.cursor_position += 1
                elif key == 127: # Del key
                    try: # If value is empty an index error will be raised if a del is performed on it
                        del self.value[self.cursor_position]
                    except IndexError: # Catch redundant error
                        pass
        return

    def get_value(self):
        return ''.join(self.value)
    
if __name__ == '__main__':
    print('Module not execuatable.')
    raise SystemExit
