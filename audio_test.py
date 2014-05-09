#!/usr/bin/env python

from pygame import mixer # Load the required library
from time import sleep

mixer.init()
mixer.music.load('./song.mp3')
mixer.music.play()
sleep(10)