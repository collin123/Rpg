#!/usr/bin/env python
import spyral
import pygame

import renderer
import threading
import time
import os

SIZE = (640, 640)
BG_COLOR = (0, 0, 0)
STEP_INTERVAL = 0.25

def load_walking_animation(filename, direction, offset=None, size=None):
	offset = (offset or (0, 0))
	size = (size or (32, 32))
	walking_images = []
	direction_rows = {'down':0, 'left':1, 'right':2, 'up':3}
	assert(direction in direction_rows)
	direction = (direction_rows.get(direction) * size[1])
	img = spyral.Image(filename=filename)
	img.crop(((size[0] * 0) + offset[0], offset[1] + direction), size)
	walking_images.append(img)

	img = spyral.Image(filename=filename)
	img.crop(((size[0] * 1) + offset[0], offset[1] + direction), size)
	walking_images.append(img)

	img = spyral.Image(filename=filename)
	img.crop(((size[0] * 2) + offset[0], offset[1] + direction), size)
	walking_images.append(img)

	img = spyral.Image(filename=filename)
	img.crop(((size[0] * 1) + offset[0], offset[1] + direction), size)
	walking_images.append(img)

	return spyral.Animation('image', spyral.easing.Iterate(walking_images), STEP_INTERVAL, loop=False)

class Game(spyral.Scene):
	"""
	A Scene represents a distinct state of your game. They could be menus,
	different subgames, or any other things which are mostly distinct.
	"""
	sprite_file = 'sprites/player.png'
	sprite_offset = ((32 * 3), 126 + (32 * 4))
	map_file = 'map.tmx'
	def __init__(self):
		spyral.Scene.__init__(self, SIZE)
		# START LOAD RENDERER
		self.renderer = renderer.TiledRenderer(self.map_file)
		background = spyral.Image(size=self.renderer.size)
		self.renderer.render(background._surf)
		background.scale(SIZE)
		self.background = background
		self.scale_height = float(self.background.size.y) / float(self.renderer.size[1])
		self.scale_width = float(self.background.size.x) / float(self.renderer.size[0])
		self.player_animation_lock = threading.Lock()
		# END LOAD RENDERER

		spyral.event.register("system.quit", spyral.director.quit)

		self.player_sprite = spyral.Sprite(self)
		walking_animation = load_walking_animation(self.sprite_file, 'down', self.sprite_offset)
		self.player_sprite.animate(walking_animation)

		# spyral built in events
		spyral.event.register('input.keyboard.down.down', lambda: self.move_player('down'))
		spyral.event.register('input.keyboard.down.up', lambda: self.move_player('up'))
		spyral.event.register('input.keyboard.down.left', lambda: self.move_player('left'))
		spyral.event.register('input.keyboard.down.right', lambda: self.move_player('right'))

		# custom events
		spyral.event.register('rpg.map.collision', self.handle_map_collision)

	def handle_map_collision(self, event):
		pos = event.pos
		new_pos = event.new_pos
		properties = self.get_renderer_tile_properties(new_pos)
		print("Player position {0}, {1}".format(pos[0], pos[1]))

	def position_in_scene(self, position):
		if position.x >= SIZE[0]:
			return False
		elif position.y >= SIZE[1]:
			return False
		elif position.x < 0:
			return False
		elif position.y < 0:
			return False
		return True

	def get_renderer_tile_properties(self, pos):
		properties = self.renderer.get_tile_properties(int(float(pos.x)/self.scale_width), int(float(pos.y)/self.scale_height))
		return properties

	def move_player(self, direction):
		if not self.player_animation_lock.acquire(False):
			return
		#self.player_animation_lock.acquire()
		#self.player_sprite.stop_all_animations()
		pos = self.player_sprite.pos
		tile_height = int(self.renderer.tmx_data.tileheight * self.scale_height)
		tile_width = int(self.renderer.tmx_data.tilewidth * self.scale_width)

		if direction == 'down':
			move_animation = spyral.Animation('y', spyral.easing.Linear(pos.y, pos.y + tile_height), STEP_INTERVAL)
			new_pos = spyral.Vec2D(pos.x, pos.y + tile_height)
		elif direction == 'up':
			move_animation = spyral.Animation('y', spyral.easing.Linear(pos.y, pos.y - tile_height), STEP_INTERVAL)
			new_pos = spyral.Vec2D(pos.x, pos.y - tile_height)
		elif direction == 'left':
			move_animation = spyral.Animation('x', spyral.easing.Linear(pos.x,  pos.x - tile_width), STEP_INTERVAL)
			new_pos = spyral.Vec2D(pos.x - tile_width, pos.y)
		elif direction == 'right':
			move_animation = spyral.Animation('x', spyral.easing.Linear(pos.x,  pos.x + tile_width), STEP_INTERVAL)
			new_pos = spyral.Vec2D(pos.x + tile_width, pos.y)
		try:
			assert(new_pos.x % self.renderer.tmx_data.tilewidth == 0)
			assert(new_pos.y % self.renderer.tmx_data.tileheight == 0)
		except AssertionError:
			import pdb; pdb.set_trace()
		properties = self.get_renderer_tile_properties(new_pos)
		walking_animation = load_walking_animation(self.sprite_file, direction, self.sprite_offset)
		if self.position_in_scene(new_pos):
			if properties.get('collision'):
				collision_event = spyral.Event(pos = pos, new_pos = new_pos)
				spyral.event.handle('rpg.map.collision', event = collision_event)
			else:
				walking_animation = (walking_animation & move_animation)

		event_name = None
		if 'x' in walking_animation.properties:
			event_name = self.player_sprite.__class__.__name__ + '.x.animation.end'
		elif 'y' in walking_animation.properties:
			event_name = self.player_sprite.__class__.__name__ + '.y.animation.end'
		if event_name:
			def test_function(*args, **kwargs):
				self.player_animation_lock.release()
				spyral.event.unregister(event_name, test_function)
			spyral.event.register(event_name, test_function)
		else:
			self.player_animation_lock.release()
		try:
			self.player_sprite.animate(walking_animation)
		except ValueError:
			if event_name:
				self.player_animation_lock.release()
				spyral.event.unregister(event_name, test_function)

if __name__ == "__main__":
	#import pdb; pdb.set_trace()
	directory =  os.path.dirname(__file__)
	if directory:
		os.chdir(directory)
	spyral.director.init(SIZE)
	spyral.director.run(scene=Game())
