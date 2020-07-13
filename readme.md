# Name
Music Maestro by BFI01

## Description
Music Maestro is a music tutor application designed in assisting in the practice
and development of musical performance. It uses a microphone input to recognise
notes played and records how accurately you play one of the pieces of music
included.

Things that took a while:
- The scroll bar;
- The metronome;
- Note detection (duh);
- min_distance_from_target (line 150 in audio.py (it is very sexy though; see "Coding conversion of frequency to note name" in the write-up, page 33 to 38)).

Sorry for the inconsistent commenting ¯\\_(ツ)_/¯

## Installation
### Dependancies
- [Python 3.7](https://www.python.org/downloads/)
- [pygame](https://pypi.org/project/pygame/)
- [numpy](https://pypi.org/project/numpy/)
- [scipy](https://pypi.org/project/scipy/)
- [pyaudio](https://pypi.org/project/PyAudio/)

## MIT License
Copyright (c) 2019 BFI01

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
