from global_names import *
from tools import *
#from Sprites import Target


sprites = load_and_resize_sprites('Inky')


class Inky(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, first_gr, second_gr, player, blinky):
        super().__init__(first_gr, second_gr)
        self.frame = 0
        self.action = LEFT
        self.image = sprites[self.action][self.frame]

        self.player = player
        self.blinky = blinky
        #self.target = Target(0, 0, all_sprites)

        self.rect = self.image.get_rect().move(CELL_SIZE * pos_x - CELL_SIZE // 4,
                                               CELL_SIZE * pos_y - CELL_SIZE // 4)

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        find_action(self)

        sprite_changes(self, sprites)

    def choose_path(self, keys, pos):
        target = [(self.player.rect.x + CELL_SIZE // 2) // CELL_SIZE,
                  (self.player.rect.y + CELL_SIZE // 2) // CELL_SIZE]

        act = self.player.action
        if act in VERTICAL:
            target[0] = (-1) ** VERTICAL.index(act) * 2 + target[0]
        else:
            target[0] += - 2 if act == UP else 0   #this is bug in the original game
            target[1] = (-1) ** HORIZONTAL.index(act) * 2 + target[1]

        target[0] = target[0] + (target[0] - self.blinky.rect.x // CELL_SIZE)
        target[1] = target[1] + (target[1] - self.blinky.rect.y // CELL_SIZE)

        #self.target.rect.x = target[0] * CELL_SIZE
        #self.target.rect.y = target[1] * CELL_SIZE

        targeting(self, target, keys, pos)

