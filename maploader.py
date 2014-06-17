import pygame
from pygame.locals import *
from pytmx import *

import  renderer

def init_screen(width, height):
	return pygame.display.set_mode((width, height), pygame.RESIZABLE)

class SimpleTest(object):
	def __init__(self, filename):
		self.renderer = None
		self.running = False
		self.dirty = False
		self.exit_status = 0
		self.load_map(filename)

	def load_map(self, filename):
		self.renderer = renderer.TiledRenderer(filename)

		print "Objects in map:"
		for o in self.renderer.tmx_data.getObjects():
			print o
			for k, v in o.__dict__ .items():
				print "  ", k, v

		print "GID (tile) properties:"
		for k, v in self.renderer.tmx_data.tile_properties.items():
			print "  ", k, v

	def draw(self, surface):
		temp = pygame.Surface(self.renderer.size)
		self.renderer.render(temp)
		pygame.transform.smoothscale(temp, surface.get_size(), surface)
		f = pygame.font.Font(pygame.font.get_default_font(), 20)
		i = f.render('press any key for next map or ESC to quit', 1, (180, 180, 0))
		surface.blit(i, (0, 0))

	def handle_input(self):
		try:
			event = pygame.event.wait()

			if event.type == QUIT:
				self.exit_status = 0
				self.running = False

			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					self.exit_status = 0
					self.running = False
				else:
					self.running = False

			elif event.type == VIDEORESIZE:
				init_screen(event.w, event.h)
				self.dirty = True

		except KeyboardInterrupt:
			self.exit_status = 0
			self.running = False

	def run(self):
		self.dirty = True
		self.running = True
		self.exit_status = 1
		while self.running:
			self.handle_input()
			if self.dirty:
				self.draw(screen)
				self.dirty = False
				pygame.display.flip()

		return self.exit_status

if __name__ == '__main__':
	filename = 'castle.tmx'
	import os.path
	import glob

	pygame.init()
	pygame.font.init()
	screen = init_screen(600, 600)
	pygame.display.set_caption('PyTMX Map Viewer')

	try:
		print "Testing", filename
		SimpleTest(filename).run()
	except:
		pygame.quit()
		raise
