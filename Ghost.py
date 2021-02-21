from global_names import *
from tools import *
from Sprites import Target


class Ghost(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, first_gr, second_gr, name):
        super().__init__(first_gr, second_gr)

        self.frame = 0
        self.action = UP
        self.alive = True
        self.at_home = True
        self.frightened = False
        self.newborn = {
            'status': True,
            'action': UP
        }
        self.points_to_leave = 0      #ghosts can leave only with a certain number of points per round

        self.name = name
        self.sprites = SPRITES[name]
        self.image = self.sprites[game_parameters['mod']][self.action][self.frame]
        self.mask = pygame.mask.from_surface(self.image)

        self.last_cell_action = [0, 0]

        self.target = Target(0, 0, all_sprites)

        self.rect = self.image.get_rect().move(CELL_SIZE * pos_x + CELL_SIZE // 4,
                                               CELL_SIZE * pos_y + CELL_SIZE // 4)

        self.real_rect_x = self.rect.x
        self.real_rect_y = self.rect.y

    def update(self):
        if self.newborn['status'] is True:
            pos = position(self)
            if pygame.sprite.collide_mask(self, game_obj['Border']):
                if self.points_to_leave - game_parameters['score per round'] > 0:
                    self.action = opposite_keys[self.action]
                else:
                    if pos[0] != 13:
                        self.action = self.newborn['action']
                    else:
                        self.action = UP

            if pos not in HOME_WITH_DOORS and cell_center(self)[-1] == MIDDLE:
                self.newborn['status'] = False
                self.action = LEFT
        else:
            self.is_ghost_at_home()
            keys = self.find_action()

            if len(keys) == 1:
                self.action = keys[0]
            else:
                if self.frightened and self.alive:
                    self.action = random(keys)
                else:
                    self.action = self.targeting(self.choose_target(), keys)

        if game_parameters['mod'] != STOP:
            self.sprite_changes()

    def choose_target(self):
        if self.at_home:
            return [12, 11]
        elif self.alive is False:
            return HOME_TAR
        elif game_parameters['mod'] == SCATTER:
            return target_in_scatter_mod[self.name]
        return self.choose_path()

    def is_ghost_at_home(self):
        pos = position(self)
        mod = game_parameters['mod']
        if pos in HOME and self.alive is False:
            self.alive = True
            self.at_home = True
            self.action = opposite_keys[self.action]
            self.frightened = False
        elif mod != FRIGHTENED and mod != H_FRIGHTENED and self.at_home \
                and pos not in HOME_WITH_DOORS:  # when the ghost leaves the house, its mod can be chase or scatter
            self.at_home = False

    def dead(self):
        self.alive = False
        self.frame = 0
        self.image = self.sprites['points'][game_parameters['ate ghosts']]
        self.mask = pygame.mask.from_surface(self.image)

    def sprite_changes(self):
        if self.at_home:
            mod = CHASE
        elif self.alive is True:
            mod = game_parameters['mod']
        else:
            mod = DEAD

        if (mod != FRIGHTENED and mod != H_FRIGHTENED and
                self.frightened is False or self.alive is False) or self.at_home:
            path = self.sprites[mod][self.action]
            frame_speed = 0.2
        else:
            path = self.sprites[mod]
            frame_speed = 0.1

        self.frame = (self.frame + frame_speed) % len(path)
        self.image = path[int(self.frame)]
        self.mask = pygame.mask.from_surface(self.image)

        move_x, move_y = correct_move(self, self.ghost_speed_change())

        self.real_rect_x = (self.real_rect_x + move_x) % LEN_X
        self.real_rect_y = (self.real_rect_y + move_y)

        self.rect.x = int(self.real_rect_x)
        self.rect.y = int(self.real_rect_y)

    def ghost_speed_change(self):
        mod = game_parameters['mod']
        if self.at_home:
            mod = CHASE
        if self.alive is False:
            speed = MODS_SPEED[DEAD]
        elif mod == FRIGHTENED or mod == H_FRIGHTENED:
            speed = MODS_SPEED[FRIGHTENED]
        elif position(self) in TUNNEL_CELLS:
            speed = MODS_SPEED['tunnel']
        elif mod == CHASE or mod == SCATTER:
            speed = self.default_speed()
        else:
            speed = 3
        return {
            RIGHT: [0, speed],
            LEFT: [0, -speed],
            DOWN: [speed, 0],
            UP: [-speed, 0],
        }

    def default_speed(self):
        return MODS_SPEED[CHASE]

    def choose_path(self):
        target = [(game_obj['Pac-Man'].rect.x + CELL_SIZE // 2) // CELL_SIZE,
                  (game_obj['Pac-Man'].rect.y + CELL_SIZE // 2) // CELL_SIZE]

        return self.new_target(target)

    def new_target(self, target):
        return target

    def find_action(self):
        if self.at_home or self.alive is False:
            point = '_'
        else:
            point = None
        keys = possible_keys(self, point)

        if len(keys) == 1:
            return keys

        #ghosts can't turn around
        if opposite_keys[self.action] in keys:
            keys.remove(opposite_keys[self.action])

        #ghosts on these cells cannot turn up
        if position(self) in BLOCK_CELLS:
            if UP in keys:
                keys.remove(UP)

        return keys

    def targeting(self, target, keys):
        pos = position(self)

        ans = list()

        for i in keys:
            if i in VERTICAL:
                x = (-1) ** VERTICAL.index(i) + pos[0]
                y = pos[1]
            else:
                x = pos[0]
                y = (-1) ** HORIZONTAL.index(i) + pos[1]
            #distance from the center of the next turn to the target
            first = abs(target[0] * CELL_SIZE - x * CELL_SIZE)
            second = abs(target[1] * CELL_SIZE - y * CELL_SIZE)
            line = (first ** 2 + second ** 2) ** 0.5
            ans.append((i, (x, y), line))

        ans = sorted(ans, key=lambda z: z[-1])

        if ans[0][-1] == ans[-1][-1] and len(ans) != 1:
            #if all ways have the same length, the way will be chosen by priority
            priority = [UP, LEFT, DOWN]
            ans = sorted(ans, key=lambda z: priority.index(z[0]) if z[0] in priority else 10)

        return ans[0][0]

