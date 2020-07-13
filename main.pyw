#!/usr/bin/env python3
try:
    import os
    import threading
    import pygame
    from random import choice
    from string import ascii_letters, digits
    from numpy import ceil
    from pygame.locals import *
    from scripts.song import SongParser
    from scripts.audio import SoundData
    from scripts.ui_elements import Button, ScrollBar, SongTab, TextInput
    from scripts.user import User
except ImportError as e: # most likely a ModuleNotFoundError
    raise Exception(f'Could not import a module: {e}.')

class Application:
    def __init__(self):
        '''
        Initialize an Application instance.
        '''
        pygame.init() # initialize all imported pygame modules
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        
        self.images = {}
        images = self._loadFiles()
        for image in images:
            self.images[image[1]] = pygame.image.load(image[0]) # load the image onto a new Surface object into a dictionary
        self.backgrounds = [self.images['menu_background_a'],
                            self.images['menu_background_b'],
                            self.images['menu_background_c'],
                            self.images['menu_background_d'],
                            self.images['menu_background_e']]
        self.overlay = pygame.Surface((1280,720))
        self.overlay.set_alpha(50)
        self.overlay.fill((255,255,255))

        self.user = User()
        
        self.screen = pygame.display.set_mode((1280, 720)) # initialize a window 

        pygame.display.set_caption('Music Maestro') # set the text in the window caption (top left)
        pygame.display.set_icon(self.images['icon'])

        self.clock = pygame.time.Clock()
        self.audio = SoundData()

        self.notes = {'A'    :[440],
                      'A#/Bb':[466],
                      'B'    :[493],
                      'C'    :[523],
                      'C#/Db':[554],
                      'D'    :[587],
                      'D#/Eb':[622],
                      'E'    :[659],
                      'F'    :[698],
                      'F#/Gb':[739],
                      'G'    :[783],
                      'G#/Ab':[830]}

        self.font = {str(i):pygame.font.Font('.\\assets\\font.ttf', i) for i in range(10,510,10)} # Load various font sizes
        return

    def _loadFiles(self, t=['png','jpg']):
        '''
        Load files from the directory the program is run from and all child directories.
        
        Args:
            t        (list) : list of all file extensions to whitelist during the directory walk
                              default: ['png','jpg']
        Returns:
            location (list) : contains all file names and addresses of files that have the whitelisted extensions
        '''
        dir_contents = [[files,root] for root, dirs, files in os.walk('.')] # os.walk() will traverse all child directories from the argument returning a generator
                                                                            # dir_contents is a 2D array of all files (and their root suffix, e.g: .png) in all child directories 
        location = []
        for x,dirs in enumerate(dir_contents): # enumerate allows for iteration over an object with an automatic counter (in this case variable x)
                                               # for each child directory in dir_contents
            for y,file in enumerate(dirs[0]): # for each file in each child directory 
                file = file.split('.') # split a string file name at each '.' into a list: 'picture.jpg' --> ['picture' , 'jpg']
                if file[1] in t:
                    path = dirs[1] + '\\' + dir_contents[x][0][y]
                    location.append([path,file[0]]) # add location details of a found file to location var where file[0]=name of file
        return location

    def _menuScreen(self):
        '''
        Handle the main menu screen including the event loop and button functionality.
        '''            
        # clear screen and set background color
        self.screen.fill((255,255,255))

        # set background image
        background_image = self.images['menu_background']
        self.screen.blit(background_image, (0,40))

        # create ui elements
        song_select_button = Button(self, text='Song Select', text_size=22, position=[768,288], dimensions=[300,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
        options_button     = Button(self, text='Options'    , text_size=22, position=[768,378], dimensions=[300,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
        buttons = [[song_select_button, self._songSelectScreen], # add button and the corresponding function to a list
                   [options_button    , self._optionsScreen   ]]
        if self.user.get_username(): # if the user is signed in there is no need to have a login button
            text = self.font['30'].render(f'Logged in as: {self.user.get_username()}', True, (0,0,0)) # show logged in as text
            self.screen.blit(text, (15, 675))
            quit_button = Button(self, text='Quit', text_size=22, position=[768,468], dimensions=[300,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
            buttons.append([quit_button, self.quit])
        else:
            login_button = Button(self, text='Log In', text_size=22, position=[698,468], dimensions=[160,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
            quit_button  = Button(self, text='Quit'  , text_size=22, position=[856,468], dimensions=[125,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
            buttons.append([login_button, self._logInScreen])
            buttons.append([quit_button , self.quit        ])

        # render title text
        title = self.font['70'].render('Music Maestro', True, (0,0,0))
        self.screen.blit(title, (190, 135))
            
        # event loop
        while True:
            mouse_pos = pygame.mouse.get_pos() # get mouse position as a tuple
            for event in pygame.event.get(): # iterate through all current pygame events 
                if event.type == QUIT:
                    return self.quit() # end the program if the quit event is performed

                if event.type == MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button[0].check(mouse_pos):
                            button[1]()
                            return
                    
            for button in buttons:
                button[0].check(mouse_pos)
                
            pygame.display.flip() # update screen
        return

    def _songSelectScreen(self):
        '''
        Handle the song select screen including the event loop, buttons and scroll bar functionality.
        '''
        # background color
        self.screen.fill((255,255,255))

        # background image
        background_image = self.images['menu_background_f']
        self.screen.blit(background_image, (round(640-(background_image.get_size()[0]*.5)),round(360-(background_image.get_size()[1]*.5))))
        self.screen.blit(self.overlay, (0,0))
        
        # title text
        title = self.font['50'].render('Song select', True, (0,0,0))
        self.screen.blit(title, (490,36))

        songs = self._loadFiles(t=['txt'])
        for song in songs:
            song[1] = song[1].split(' - ')
        del songs[-1] # remove pseudocode.txt
        
        # ui elements
        song_tabs = []
        for place,song in enumerate(songs,start=1):
            if self.user.get_username():
                user_data = self.user.get_data()
                try:
                    song_tabs.append(SongTab(self, start_pos=round(place*(250+25))-135, song=[songs[place-1][1][0],songs[place-1][1][1],songs[place-1][0]], highscore=user_data[songs[place-1][1][0]]))
                except KeyError:
                    song_tabs.append(SongTab(self, start_pos=round(place*(250+25))-135, song=[songs[place-1][1][0],songs[place-1][1][1],songs[place-1][0]], highscore=0))
            else:
                song_tabs.append(SongTab(self, start_pos=round(place*(250+25))-135, song=[songs[place-1][1][0],songs[place-1][1][1],songs[place-1][0]]))
        back_button = Button(self, text='Back', text_size=22, position=[128,648], dimensions=[160,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
        scroll_bar = ScrollBar(self, dimensions=[1000,20], position=[640,504], scroll_length=round(275*len(song_tabs))-1025, color=(153,217,234), alt_color=(0,162,232), clicked_color=(0,131,187))
        
        # event loop
        while True:
            mouse_pos     = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]
            pygame.draw.rect(self.screen, (255,255,255), (0,92,1280,400))
            
            scroll_bar.check(mouse_pos, mouse_clicked)               
            back_button.check(mouse_pos)
            for tab in song_tabs:
                tab.set_x(scroll_bar.get_notch_position())
                if -275 < tab.get_x() < 1280:
                    tab.render()
                    tab.button.check(mouse_pos)
                      
            for event in pygame.event.get():
                if event.type == QUIT:
                    return self.quit()
                if event.type == MOUSEBUTTONDOWN:
                    if back_button.check(mouse_pos):
                        return self._menuScreen()
                    for tab in song_tabs:
                        if tab.button.check(mouse_pos):
                            return self._performanceScreen(tab.song)
                        
            pygame.draw.rect(self.screen, (255,255,255,255), (0,115,140,365))
            pygame.draw.rect(self.screen, (255,255,255,255), (1140,115,1280,365))
            pygame.display.flip()  
        return

    def _optionsScreen(self):
        '''
        Handle the main menu screen including the event loop, buttons and slider functionality.
        '''
        def render_screen():
            # background color
            self.screen.fill((255,255,255))

            # background image
            self.screen.blit(background_image, (round(640-(background_image.get_size()[0]*.5)),round(360-(background_image.get_size()[1]*.5))))
            self.screen.blit(self.overlay, (0,0))
            
            # title text
            title = self.font['50'].render('Options', True, (0,0,0))
            self.screen.blit(title, (490,36))

            title = self.font['40'].render('Calibrate Microphone', True, (0,0,0))
            self.screen.blit(title, (100,100))

            title = self.font['40'].render('User Account', True, (0,0,0))
            self.screen.blit(title, (750,100))

            # ui elements
            back_button = Button(self, text='Back', text_size=22, position=[128,648], dimensions=[160,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
            calibration_button = Button(self, text='Calibrate', text_size=20, position=[300,200], dimensions=[200,60], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
            buttons = [[back_button,self._menuScreen],
                       [calibration_button, calibrate_microphone]]
            if self.user.get_username():
                logout_button = Button(self, text='Log Out', text_size=20, position=[875,200], dimensions=[180,60], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
                delete_account_button = Button(self, text='Delete Account', text_size=26, position=[875,275], dimensions=[250,60], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
                buttons.append([logout_button        , user_logout   ])
                buttons.append([delete_account_button, delete_account])
            else:
                login_button = Button(self, text='Log In', text_size=22, position=[875,200], dimensions=[160,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
                buttons.append([login_button, self._logInScreen])
            return buttons
            
        def calibrate_microphone():             
            for note in self.notes.keys():
                title_text = self.font['40'].render('Please play the following note once:', True, (0,0,0))
                note_text = self.font['400'].render(note, True, (0,0,0))

                self.screen.fill((255,255,255))
                self.screen.blit(title_text, (490,36))
                self.screen.blit(note_text, (0,25))
                pygame.display.flip()

                tick = 0
                buffering = True
                buffer = {}
                while buffering:
                    self.clock.tick(60)
                    tick += 1

                    if tick < 40:
                        self.audio.stream()
                        for frequency in self.audio.get_dominant_frequencies().tolist():
                            buffer[str(frequency)] = buffer.get(str(frequency),0) + 1 # Creates a dictionary of how many times each dominant frequency appears in the timeframe
                    else:
                        buffering = False
                        try:
                            del buffer['1.0'] # Erroneous value that should be removed
                        except KeyError:
                            pass # Ignore error raised if the value is not found
                        buffer_mode = sorted(zip(buffer.values(),buffer.keys()),reverse=True)[:3] # zip([A,B,C],[x,y,z])=[(A,x),(B,y),(C,z)] , sorted([2,87,1,9,2,4,56,8,0])=[0,1,2,2,4,8,9,56,87] --> Extract top 3 most frequent frequencies
                        self.notes[note] = [int(float(freq[1])) for freq in buffer_mode]
                        
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            return self.quit()
            self._optionsScreen()
            
        def user_logout():
            self.user = User()
            buttons = render_screen()
            return buttons

        def delete_account():
            self.user.remove()
            return user_logout()
        
        background_image = choice(self.backgrounds)
        buttons = render_screen()            
        
        # event loop
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == QUIT:
                    return self.quit()
                if event.type == MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button[0].check(mouse_pos):
                            buttons = button[1]()
                            break
        
            for button in buttons:
                button[0].check(mouse_pos)
            
            pygame.display.flip()
        return


    def _logInScreen(self):
        '''
        Handle the log in screen including the event loop, buttons and text box functionality.

        Returns:
            self._menuScreen (bound method) : returns to the main menu
        '''
        def render_screen():
            # background color
            self.screen.fill((255,255,255))

            # background image
            self.screen.blit(background_image, (round(640-(background_image.get_size()[0]*.5)),round(360-(background_image.get_size()[1]*.5))))
            self.screen.blit(self.overlay, (0,0))
            
            # title text
            title = self.font['50'].render('Log in', True, (0,0,0))
            self.screen.blit(title, (565,36))

            username_text = self.font['40'].render('Username', True, (0,0,0))
            self.screen.blit(username_text, (340,125))
            
            username_text = self.font['40'].render('Password', True, (0,0,0))
            self.screen.blit(username_text, (340,235))
        
        def login(username, password):
            error = self.user.validate(username, password)
            if not error:
                return self._menuScreen()
            else:
                render_screen()
                error_text = self.font['30'].render(error, True, (0,0,0))
                self.screen.blit(error_text, (340,325))
            return

        def create_account(username, password):
            error = self.user.create(username, password)
            if not error:
                return self._menuScreen()
            else:
                render_screen()
                error_text = self.font['30'].render(error, True, (0,0,0))
                self.screen.blit(error_text, (340,325))
            return
        
        background_image = choice(self.backgrounds)
        render_screen()
        
        # ui elements
        username_input        = TextInput(self, dimensions=(575, 40), position=(340,175), character_limit=16, allowed_characters=ascii_letters+digits+'_', color=(153,217,234), active_color=(113,203,225))
        password_input        = TextInput(self, dimensions=(225, 40), position=(340,285), character_limit=16, allowed_characters=ascii_letters+digits+' ', input_hidden=True, color=(153,217,234), active_color=(113,203,225))
        login_button          = Button(self, text='Log in', text_size=22, position=[640,395], dimensions=[160,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
        create_account_button = Button(self, text='Create account', text_size=35, position=[640,475], dimensions=[320,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))
        back_button           = Button(self, text='Back', text_size=22, position=[128,648], dimensions=[160,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))

        # event loop
        while True:
            mouse_pos     = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]
            for event in pygame.event.get():
                if event.type == QUIT:
                    return self.quit()
                if event.type == MOUSEBUTTONDOWN:
                    if login_button.check(mouse_pos):
                        login(username_input.get_value(), password_input.get_value())
                    if create_account_button.check(mouse_pos):
                        create_account(username_input.get_value(), password_input.get_value())
                    if back_button.check(mouse_pos):
                        return self._menuScreen()
                if event.type == KEYDOWN:
                    if event.unicode:
                        username_input.key_press(event.unicode, key_type='char')
                        password_input.key_press(event.unicode, key_type='char')
                    else:
                        username_input.key_press(event.key, key_type='action')
                        password_input.key_press(event.key, key_type='action')

            login_button.check(mouse_pos)
            create_account_button.check(mouse_pos)
            back_button.check(mouse_pos)
            username_input.check(mouse_pos,mouse_clicked)
            password_input.check(mouse_pos,mouse_clicked)
            
            pygame.display.flip()
        
        return self._menuScreen()


    def _performanceScreen(self,song):
        '''
        Run the song performance of a selected song.

        Args:
            song (list) : details of the song to be run, consisting of song name, difficulty, and file address
        '''
        # Declare global variables, used in the sub-routines 
        global Song, score, tempo, cleff, time_signature, key, song_length
        global metronome, current_note, current_mic_note, tick, event, beats, note_buffer, note_played_data
        global hitbox, metronome_offset
        
        def get_song_vars(song):
            global Song, score, tempo, cleff, time_signature, key, song_length
            global metronome, current_note, current_mic_note, tick, event, beats, note_buffer, note_played_data
            # Variables from song file
            with open(song[2], mode='r') as File:
                song_contents = File.read().split('|') # Read the song file into a list
            for i,bar in enumerate(song_contents):
                song_contents[i] = bar.strip('\n').split(',') # Strip all newlines and split into individual notes
            Song = SongParser(song_contents, self.images) # Load SongParser object  
            tempo = int(song_contents[0][0].split('=')[1]) # Identify song variables
            cleff = self.images[song_contents[0][1].split('=')[1]+'_cleff']
            time_signature = song_contents[0][2].split('=')[1].split('/')
            key = song_contents[0][3].split('=')[1]
            if key not in ['C','Am']: # The key of C and Am have no special notation, so only load the key image if it is not C or Am
                key = self.images[key+'_key_signature']
            song_length = int(song_contents[0][4].split('=')[1])

            # Miscellaneous variables
            metronome = 'left'
            current_mic_note = 'X'
            current_note = 'Y'
            score = 0
            tick = 0
            event = None
            beats = 0
            note_buffer = [Song.next_note()]
            note_played_data = []
            return

        def fade_from_white():
            for i in range(200):
                draw_background()

                overlay = pygame.Surface((1280,720))
                overlay.set_alpha(round(255-(255/200)*i))
                overlay.fill((255,255,255))
                self.screen.blit(overlay, (0,0))

                for event in pygame.event.get():
                    if event.type == QUIT:
                        return self.quit()
                    
                pygame.display.flip()
            return
        
        def draw_background():
            global hitbox, metronome_offset

            # Draw note fadeout gradient 
            fadeout_steps = 50
            fadeout_gradient = [pygame.Surface((int(275/fadeout_steps),720)) for i in range(fadeout_steps)] # 275 is the distance between left of screen to left of hitbox
            for i,part in enumerate(fadeout_gradient):
                part.set_alpha(260-int((255/len(fadeout_gradient))*(i+1)))
                part.fill((255,255,255))
                self.screen.blit(part, (part.get_rect().width*i,0))

            # Draw text
            title = self.font['30'].render('Now playing - {}'.format(song[0]), True, (0,0,0)) # Render the "Now playing" text 
            score_text = self.font['60'].render('Score: {}'.format(score), True, (0,0,0)) # Render the score text
            self.screen.blit(title, (0,0)) # Display the "Now playing" and score text
            self.screen.blit(score_text, (0,40))

            # Draw metronome
            self.screen.blit(self.images['metronome_'+metronome], (50,150)) # Draw the metronome

            # Draw stationary music components
            cleff_rect = self.screen.blit(cleff, (0,310)) # Display the cleff
            beats_text = self.font['80'].render(time_signature[0], True, (0,0,0)) # Display the time signature 
            per_bar = self.font['80'].render(time_signature[1], True, (0,0,0))
            if key not in ['C','Am']: # Display the key signature (the key of C and Am do not have any special notation so only do this if it is any other key signature)
                key_rect = self.screen.blit(key,(cleff_rect.right-75,300))
                time_signature_rect = self.screen.blit(beats_text, (key_rect.right,350))
                self.screen.blit(per_bar, (key_rect.right,430))
            else:
                time_signature_rect = self.screen.blit(beats_text, (cleff_rect.right-50,350))
                self.screen.blit(per_bar, (cleff_rect.right-50,430))
            for i in range(0,200,40): # Draw the stave
                pygame.draw.line(self.screen, (0,0,0), (100,360+i), (1280,360+i), 5)
                
            hitbox = pygame.Surface((50,200)) # Create the hitbox for note detection
            hitbox.set_alpha(200)
            hitbox.fill((153,217,234))
            hitbox = self.screen.blit(hitbox, (time_signature_rect.right+25,340))
            metronome_offset = round(((self.screen.get_width()-hitbox.left)/(tempo/20))/(60**2/tempo))
            return

        def run_audio_stream():
            while True:
                self.audio.stream()
                if event != 'playing':
                    break
            return                

        get_song_vars(song)
        fade_from_white()
        while True:
            self.clock.tick(60)
            self.screen.fill((255,255,255)) # Fill the screen completely white
            tick += 1
            if event != 'playing' and tick % 60 == 0:
                event = self.font['500'].render(str(4-(tick//60)), True, (0,0,0)) # Render countdown text
                if not 4-(tick//60):
                    tick = 0
                    event = 'playing'
                    stream_thread = threading.Thread(target=run_audio_stream)
                    stream_thread.start()
                    
            if event and event != 'playing':
                self.screen.blit(event, (500,10))
            elif event == 'playing':

                if tick % (60**2/tempo) == 0:
                    note_buffer[-1]['long_duration_bool'] += 1

                if (tick-(3*metronome_offset)) % (60**2/tempo) == 0:
                    beats += 1
                    if metronome == 'left':
                        metronome = 'right'
                    else:
                        metronome = 'left'
                
                if tick:
                    if tick % round((60**2/tempo)*note_buffer[-1]['note_length']) == 0 and note_buffer[0]:
                        if Song.end_of_bar:
                            note_buffer.append({'pos': 1280,
                                                'note_length': note_buffer[-1]['note_length'],
                                                'note_name': 'X',
                                                'long_duration_bool': 0,
                                                'played': 5,
                                                'note_img_offset':0,
                                                'note_img': [None, 0]})
                            Song.end_of_bar = False
                        else:
                            if note_buffer[-1]['note_length'] > 1:
                                if note_buffer[-1]['long_duration_bool'] == note_buffer[-1]['note_length']:
                                    note_buffer.append(Song.next_note())
                                else:
                                    tick += 60**2/tempo
                            else:
                                note_buffer.append(Song.next_note())

                        if Song.end_of_bar:
                            note_buffer[-1]['note_length'] /= 2
                            
                        if note_buffer[-1] == None: # End of the song is reached
                            del note_buffer[-1]
                            note_buffer.insert(0,None)
                            
                    if tick > 10:
                        current_mic_frequencies = self.audio.get_dominant_frequencies()
                        current_mic_note = self.audio.get_note_from_frequency(self.notes, current_mic_frequencies)
                        note = self.font['30'].render(f'Detected note: {current_mic_note}', True, (0,0,0))
                        self.screen.blit(note, (975,675))

                if current_note in current_mic_note.split('/'):
                    for note in note_buffer:
                        if note:
                            if note['note_name'][-1] == 'n':
                                note_name = note['note_name'][0]
                            else:
                                note_name = note['note_name'][0] + note['note_name'][-1]
                                
                            if note_name == current_note:
                                note['played'] -= 1
                                break
                        
                for i,note in enumerate(note_buffer):
                    if note:
                        note['pos'] -= tempo/20                        
                        if hitbox.left < note['pos'] < hitbox.right:
                            if note['note_name'][-1] == 'n':
                                current_note = note['note_name'][0]
                            else:
                                current_note = note['note_name'][0] + note['note_name'][-1]
                        elif note['pos'] < hitbox.left-40:
                            note['played'] = 2**40
                            
                        if note['played'] <= 0:
                            note['pos'] = -40
                            current_note = 'X'
                            score += 1            
                            
                        for j,part in enumerate(list(note.keys())[6:]):
                            if j:
                                self.screen.blit(note[part][0], (note['pos']-25,note[part][1]))
                            else:
                                if note[part][0]:
                                    self.screen.blit(note[part][0], (note['pos'],note[part][1]))
                                    if note[part][1]+note['note_img_offset'] > 540:
                                        for k in range(((note[part][1]+note['note_img_offset'])-520)//40):
                                            pygame.draw.line(self.screen, (0,0,0), (note['pos']-10,560+(40*k)), (note['pos']+60,560+(40*k)), 5)
                                    elif note[part][1] < 340:
                                        for k in range(((360-(note[part][1]+note['note_img_offset']))//40)):
                                            pygame.draw.line(self.screen, (0,0,0), (note['pos']-10,320-(40*k)), (note['pos']+60,320-(40*k)), 5)
                                else:
                                    pygame.draw.line(self.screen, (0,0,0), (note['pos'],360), (note['pos'],520), 4)
                            
                        if note['pos'] <= -40:
                            del note_buffer[i] # Delete the note when it's x-position is off screen
                            if note['note_name'] != 'X':
                                note_played_data.append(round(100*(score/(len(note_played_data)+1)))) # Percent of notes played correctly out of all the notes so far
                        else:
                            note_buffer[i] = note
                
                if note_buffer == [None]:
                    event = 'complete'
                    stream_thread.join()
                    return self._analysisScreen([song[0], score, round(100*(score/song_length)), song_length, note_played_data])
              
            for e in pygame.event.get():
                if e.type == QUIT:
                    return self.quit()
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        if event == 'playing':
                            event = 'complete'
                            stream_thread.join()
                            return self._menuScreen()
                    
            draw_background()
            pygame.display.flip()

        # As each note collides with the hitbox, set "current note" to the note value, or None if a rest
        # If some function current_note_being_played() == current_note, then they successfully played it
        # else, they did not
        # could be an analogue thing to allow for more precise timings (based on how close the note is to the center of the hitbox)
        # current_note_being_played() should also have a None value if no note is detected
        return

    def _analysisScreen(self, score):
        '''
        Display song performance scores, and graph to show where the errors in the performance occurred.

        Args:
            score (list) : 
        '''
        def graph(total_notes, percents):
            # Draw graph details
            pygame.draw.line(self.screen, (0,0,0), (640,125), (640,625), 4) # Draw y-axis
            pygame.draw.line(self.screen, (0,0,0), (640,625), (1140,625), 4) # Draw x-axis
            graph_underlay = pygame.Surface((498,499)) # Create a translucent underlay under the graph area to obscure potentially distracting background image
            graph_underlay.set_alpha(200)
            graph_underlay.fill((255,255,255))
            self.screen.blit(graph_underlay, (643,125))

            # Convert x and y value to x and y on-screen coordinates
            y = lambda k: int(ceil((625-10)-(((500/(100-min_percent))*(k-min_percent))))) # Ceiling of: (origin_y-offset) - ((length of axis/range of percents)*i)
            x = lambda k: int(ceil((640-5)+(((500/(total_notes-1))*k)))) # Ceiling of: (origin_x) + ((total length of axis - text height/range of percents)*i)

            min_percent = int(min(percents)*.1)*10
            if min_percent == 100: # Prevent axis from having only one value on it
                min_percent = 90 
            for i in range(0,(100-min_percent)+10,10): # Calculate positions of and display graph y-axis label text
                text = self.font['20'].render(f'{i+min_percent}%', True, (0,0,0))
                self.screen.blit(text, (590,y(i+min_percent))) 

            x_positions = []
            for i in range(total_notes): # Calculate positions of and display graph x-axis label text
                if total_notes <= 20 or i==0 or i==total_notes-1: 
                    text = self.font['20'].render(str(i+1), True, (0,0,0))
                    self.screen.blit(text, (x(i),640))
                x_positions.append(x(i)+6)

            y_label = self.font['30'].render('Accuracy', True, (0,0,0)) # Label text for y-axis
            self.screen.blit(y_label, (450,350))
            x_label = self.font['30'].render('Note count', True, (0,0,0)) # Label text for x-axis
            self.screen.blit(x_label, (830,660))

            # Plot points
            percents = [y(percent)+10 for percent in percents]   
            for point in zip(x_positions,percents):
                try:
                    pygame.draw.aaline(self.screen, (0,0,0), point, last_point, 4)
                except UnboundLocalError: # On the first iteration of the loop, catch the error caused by last_point not yet being defined
                    pass
                last_point = point

            for point in zip(x_positions,percents):
                pygame.draw.circle(self.screen, (255,0,0), point, 4)
                
        # background color
        self.screen.fill((255,255,255))

        # background image
        background_image = choice(self.backgrounds)
        self.screen.blit(background_image, (round(640-(background_image.get_size()[0]*.5)),round(360-(background_image.get_size()[1]*.5))))
        self.screen.blit(self.overlay, (0,0))
        
        # title text
        title = self.font['50'].render('Song Performance', True, (0,0,0))
        song_name_text = self.font['40'].render(f'Song name: {score[0]}', True, (0,0,0))
        score_text = self.font['40'].render(f'Score: {score[1]}', True, (0,0,0))
        percent_text  = self.font['40'].render(f'Percent: {score[2]}%', True, (0,0,0))
        self.screen.blit(title, (490,36))
        self.screen.blit(song_name_text, (25,86))
        self.screen.blit(score_text, (25,126))
        self.screen.blit(percent_text, (25,170))
        
        # ui elements
        back_button = Button(self, text='Back', text_size=22, position=[128,648], dimensions=[160,75], color=(153,217,234), alt_color=(0,162,232), hover_color=(113,203,225), text_color=(255,255,255))

        # update user data
        if self.user.get_username():
            user_data = self.user.get_data()
            try:
                if score[2] > user_data[score[0]]: # score > high score (%)
                    user_data[score[0]] = score[2] # high score = score (%)
            except KeyError:
                user_data[score[0]] = score[2]
            finally:
                self.user.save(user_data)
                highscore_text = self.font['40'].render('High score: {0}%'.format(user_data[score[0]]), True, (0,0,0))
                self.screen.blit(highscore_text, (25,210))
                
        if score[2] > 1: # Only show graph if song contains more than one note to avoid division by zero error
            graph(score[3],score[4])
        # event loop
        while True:
            mouse_pos     = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]
            for event in pygame.event.get():
                if event.type == QUIT:
                    return self.quit()
                if event.type == MOUSEBUTTONDOWN:
                    if back_button.check(mouse_pos):
                        return self._menuScreen()
                    
            back_button.check(mouse_pos)
            
            pygame.display.flip()
        return
    
    def run(self):
        '''
        Higher level initilization of the program.
        '''
        self._menuScreen()
        return

    def quit(self):
        '''
        End all PyGame processes and close the PyGame window.
        '''
        pygame.font.quit()
        pygame.quit()
        return

if __name__ == '__main__':
    MusicMaestro = Application()
    MusicMaestro.run()
    raise SystemExit
