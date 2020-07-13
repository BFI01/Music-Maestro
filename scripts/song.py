try:
    import pygame
except ImportError as e: # most likely a ModuleNotFoundError
    raise Exception(f'Could not import a module: {e}.')

class SongParser:
    def __init__(self, song, images):
        '''
        Class to handle the translation of song files into their components.

        Args:
            song   (list) : the song file with all the song data
            images (dict) : contains all the image Surface objects and names the program uses
        '''
        self.song = song[1:-1][::-1] # Remove the metadata at index 1 and blank entry at index -1 and reverse the list
        for i,bar in enumerate(self.song):
            self.song[i] = bar[::-1] # Reverse the notes in each bar
        self.images = images
        self.current_bar = self.song.pop()
        # Creates a list of note names by iterating through ['G','F','E','D','C','B','A'], each iteration of range(7,0,-1) (which counts down from 7 to 1). Then it adds both str values together into the list
        # Finally, the list (['G7', 'F7', 'E7', ... , 'D1', 'C1', 'B1', 'A1']) is iterated through with each value becoming a key in the dictionary with a corresponing y-value
        self.y_pos = {i:int(count*20+60) for count,i in enumerate([y+str(x) for x in range(7,0,-1) for y in ['G','F','E','D','C','B','A']])} # Dictionary of each note and its y-value on screen
        self.tilt = {'#':images['sharp'],
                     'b':images['flat'],
                     'n':None}
        self.durations = {0.25:'sixteenth_',
                          0.5:'eighth_',
                          1.0:'quarter_',
                          2.0:'half_',
                          4.0:'whole_'}

    def _parse(self, note):
        '''
        Translate a string note/rest name and duration into a dictionary of data.

        Args:
            note   (str) : contains information about note/rest name, duration and whether it is sharp or flat or not

        Returns:
            image (dict) : all the data of the note, including loaded image files
        '''
        image = {'pos':1280} # x-coord of where each note should start in the window
        image['note_length'] = float(note[3:-1]) # Append note length 
        image['note_name'] = note[:3] # Append note as string
        image['long_duration_bool'] = 0 # Used to track if a note longer than 1 beat has been spawned for its note duration
        image['played'] = 5 # Number of times microphone detected note must match before the note is successfully played 
        duration = self.durations[image['note_length']] # Lookup the image prefix in the self.durations dict
        y_pos = self.y_pos[note[:2]] 
        tilt = self.tilt[note[2]]
        
        if note[-1] == 'n':
            if y_pos < self.y_pos['B5']: # Any note higher than B5 should have it's stem facing downwards
                image['note_img_offset'] = 18 # Account for height of image file
                image['note_img'] = [pygame.transform.flip(self.images[duration+'note'], True, True),y_pos-image['note_img_offset']] # Flip horizontally and vertically
            else:
                image['note_img_offset'] = 118
                image['note_img'] = [self.images[duration+'note'],y_pos-image['note_img_offset']] # Take 118 from y_pos to account for image height of notes
        elif note[-1] == 'r':
            image['note_img'] = [self.images[duration+'rest'],350] # The image should always be at y=350 if it is a rest

        if tilt:
            image['tilt'] = [tilt,y_pos-115]
        return image
        
    def next_note(self):
        '''
        Get the next note in the song as a dictionary of data.

        Returns:
            self.note     (dict) : all the data of the note, including loaded image files
            None      (NoneType) : special condition returned when self.song is empty
        '''
        self.end_of_bar = len(self.current_bar)==1 # Boolean of whether self.current_bar has length of 1
        if not self.current_bar:
            if self.song: # When the song has no more notes it will evaluate as False
                self.current_bar = self.song.pop()
                if len(self.current_bar) == 1:
                    self.end_of_bar = True
            else:
                return None
        self.note = self._parse(self.current_bar.pop()) # Parse the next note in the song
        return self.note
        
if __name__ == '__main__':
    print('Module not execuatable.')
    raise SystemExit
