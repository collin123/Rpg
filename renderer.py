import pygame
import pytmx

class TiledRenderer(object):
	"""
	Renders tiled tmx files.
	"""
	def __init__(self, filename):
		"""
		:param str filename: The name of the file you want to renderer.
		"""
		tm = pytmx.load_pygame(filename, pixelalpha=True)
		self.size = tm.width * tm.tilewidth, tm.height * tm.tileheight
		self.tmx_data = tm
		self.tmx_layers = tm.all_layers

	def get_objects_for_position(self, x, y):
		"""
		Finds objects in the position the player will move to
		"""
		pass

	def get_tile_properties(self, x, y, layer=0):
		x = x / self.tmx_data.tilewidth
		y = y / self.tmx_data.tileheight
		return self.tmx_data.getTileProperties((x, y, layer)) or {}

	def render(self, surface):
		"""
		Renders a tmx file type into a image. It expects the surface to
		be the size of the renderer

		:param pygame.Surface surface: The surface you want to be loaded.
		"""
		tw = self.tmx_data.tilewidth
		th = self.tmx_data.tileheight
		if self.tmx_data.background_color:
			surface.fill(self.tmx_data.background_color)
		for layer in self.tmx_data.visibleLayers:
			if isinstance(layer, pytmx.TiledLayer):
				for x, y, gid in layer:
					tile = self.tmx_data.getTileImageByGid(gid)
					if tile:
						surface.blit(tile, (x * tw, y * th))
			elif isinstance(layer, pytmx.TiledImageLayer):
				image = self.tmx_data.getTileImageByGid(layer.gid)
				if image:
					surface.blit(image, (0, 0))
		for o in self.tmx_data.getObjects():
			if hasattr(o, 'points'):
				pygame.draw.lines(surface, (255, 128, 128), o.closed, o.points, 2)
			elif o.gid:
				tile = self.tmx_data.getTileImageByGid(o.gid)
				if tile:
					surface.blit(tile, (o.x, o.y))
			else:
				pygame.draw.rect(surface, (255, 128, 128), (o.x, o.y, o.width, o.height), 2)
