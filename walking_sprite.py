#!/usr/bin/env python
import spyral
import pygame

import renderer

SIZE = (640, 480)
BG_COLOR = (0, 0, 0)

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

	return spyral.Animation('image', spyral.easing.Iterate(walking_images), 0.5, loop=False)

class Game(spyral.Scene):
	"""
	A Scene represents a distinct state of your game. They could be menus,
	different subgames, or any other things which are mostly distinct.
	"""
	sprite_file = 'EchFF.png'
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
		# END LOAD RENDERER

		spyral.event.register("system.quit", spyral.director.quit)

		self.player_sprite = spyral.Sprite(self)
		walking_animation = load_walking_animation(self.sprite_file, 'down', self.sprite_offset)
		self.player_sprite.animate(walking_animation)

		spyral.event.register('input.keyboard.down.down', lambda: self.move_player('down'))
		spyral.event.register('input.keyboard.down.up', lambda: self.move_player('up'))
		spyral.event.register('input.keyboard.down.left', lambda: self.move_player('left'))
		spyral.event.register('input.keyboard.down.right', lambda: self.move_player('right'))

	def move_player(self, direction):
		self.player_sprite.stop_all_animations()
		walking_animation = load_walking_animation(self.sprite_file, direction, self.sprite_offset)

		pos = self.player_sprite.pos
		if direction == 'down':
			move_animation = spyral.Animation('y', spyral.easing.Linear(pos.y, pos.y + 32), 0.5)
		elif direction == 'up':
			move_animation = spyral.Animation('y', spyral.easing.Linear(pos.y, pos.y - 32), 0.5)
		elif direction == 'left':
			move_animation = spyral.Animation('x', spyral.easing.Linear(pos.x,  pos.x - 32), 0.5)
		elif direction == 'right':
			move_animation = spyral.Animation('x', spyral.easing.Linear(pos.x,  pos.x + 32), 0.5)
		self.player_sprite.animate(walking_animation & move_animation)

if __name__ == "__main__":
	spyral.director.init(SIZE)
	spyral.director.run(scene=Game())
