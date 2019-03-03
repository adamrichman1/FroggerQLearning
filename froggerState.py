from copy import deepcopy
from pygame.constants import K_F15, K_w, K_a, K_s, K_d


class FroggerState:
    BLOCK_LENGTH = 32
    GRID_SIZE = 13
    BOTTOM_WALL = 485
    TOP_WALL = 69
    LEFT_WALL = 0
    RIGHT_WALL = 416

    gamma = .2
    inflation_const = 2

    def __init__(self, reward, obs):
        self.q_val = {K_w: 0, K_a: 0, K_s: 0, K_d: 0, None: 0}
        self.cars_list, self.rivers_list, self.homes = self.get_obstacles(obs)
        self.reward = reward
        self.n = {K_w: 0, K_a: 0, K_s: 0, K_d: 0, None: 0}
        self.frog_x = obs['frog_x']
        self.frog_y = obs['frog_y']
        self.dist_from_start = self.calc_dist_from_start()
        self.closest_car_left = self.get_closest_car_left()
        self.closest_car_right = self.get_closest_car_right()
        self.current_space_s = self.current_space_safe()
        self.space_ahead_s = self.space_ahead_safe()
        self.space_behind_s = self.space_behind_safe()
        self.space_left_s = self.space_left_safe()
        self.space_right_s = self.space_right_safe()
        self.dist_to_end = self.calc_dist_to_end()
        self.left_wall_dist = self.calc_left_wall_dist()
        self.right_wall_dist = self.calc_right_wall_dist()
        self.is_empty_home_in_front = self.calc_empty_home_in_front()
        self.against_left_wall = 0 if self.frog_x <= (self.LEFT_WALL + 2) else 1
        self.against_right_wall = 0 if self.frog_x >= (self.RIGHT_WALL - 2) else 1

    def set_n(self, n):
        self.n = n

    def get_n(self):
        return self.n

    def calc_dist_to_end(self):
        return (self.frog_y - self.TOP_WALL) / 32

    def calc_dist_from_start(self):
        return (self.BOTTOM_WALL - self.frog_y) / 32

    def calc_left_wall_dist(self):
        return self.frog_x - self.LEFT_WALL

    def calc_right_wall_dist(self):
        return self.RIGHT_WALL - self.frog_x

    def current_space_safe(self):
        if self.dist_from_start < 7:
            for car in self.cars_list:
                if self.is_same_col(self.frog_x, car[0]) and self.is_same_row(self.frog_y, car[1]):
                    return 0
            return 1
        else:
            for obj in self.rivers_list:
                if self.is_same_col(self.frog_x, obj[0]) and self.is_same_row(self.frog_y, obj[1]):
                    return 1
            return 0

    def space_ahead_safe(self):
        space_ahead = self.frog_y - self.BLOCK_LENGTH
        if self.dist_from_start < 7:
            for car in self.cars_list:
                if self.is_same_col(self.frog_x, car[0]) and self.is_same_row(space_ahead, car[1]):
                    return 0
            return 1
        else:
            for obj in self.rivers_list:
                if self.is_same_col(self.frog_x, obj[0]) and self.is_same_row(space_ahead, obj[1]):
                    return 1
            return 0

    def space_behind_safe(self):
        space_behind = self.frog_y + self.BLOCK_LENGTH
        if self.dist_from_start < 7:
            for car in self.cars_list:
                if self.is_same_col(self.frog_x, car[0]) and self.is_same_row(space_behind, car[1]):
                    return 0
            return 1
        else:
            for obj in self.rivers_list:
                if self.is_same_col(self.frog_x, obj[0]) and self.is_same_row(space_behind, obj[1]):
                    return 1
            return 0

    def space_right_safe(self):
        space_right = self.frog_x + self.BLOCK_LENGTH
        if self.dist_from_start < 7:
            if space_right > self.RIGHT_WALL:
                return 1
            for car in self.cars_list:
                if self.is_same_col(space_right, car[0]) and self.is_same_row(self.frog_y, car[1]):
                    return 0
            return 1
        else:
            if space_right > self.RIGHT_WALL:
                return 0
            for obj in self.rivers_list:
                if self.is_same_col(space_right, obj[0]) and self.is_same_row(self.frog_y, obj[1]):
                    return 1
            return 0

    def space_left_safe(self):
        space_left = self.frog_x - self.BLOCK_LENGTH
        if self.dist_from_start < 7:
            if space_left < self.LEFT_WALL:
                return 1
            for car in self.cars_list:
                if self.is_same_col(space_left, car[0]) and self.is_same_row(self.frog_y, car[1]):
                    return 0
            return 1
        else:
            if space_left < self.LEFT_WALL:
                return 0
            for obj in self.rivers_list:
                if self.is_same_col(space_left, obj[0]) and self.is_same_row(self.frog_y, obj[1]):
                    return 1
            return 0

    def get_closest_car_right(self):
        min_dist = float('inf')
        for car in self.cars_list:
            if self.is_same_row(car[1], self.frog_y) and car[0] > self.frog_x and car[0] - self.frog_x < min_dist:
                min_dist = car[0] - self.frog_x
        return min_dist

    def get_closest_car_left(self):
        min_dist = float('inf')
        for car in self.cars_list:
            if self.is_same_row(car[1], self.frog_y) and self.frog_x > car[0] and self.frog_x - car[0] < min_dist:
                min_dist = self.frog_x - car[0]
        return min_dist

    @staticmethod
    def is_same_row(y1, y2):
        return abs(y1 - y2) <= 33

    @staticmethod
    def is_same_col(x1, x2):
        return abs(x1 - x2) <= 33

    @staticmethod
    def get_obstacles(obs):
        cars_list = []
        cars = obs['cars']
        for rect in cars:
            cars_list.append([rect[0], rect[1]])
            width = rect[2]
            while width > 32:
                cars_list.append([rect[0] + 32, rect[1]])
                width -= 32

        rivers_list = []
        river_objs = obs['rivers']
        for rect in river_objs:
            rivers_list.append([rect[0], rect[1]])
            width = rect[2]
            while width > 32:
                rivers_list.append([rect[0] + 32, rect[1]])
                width -= 32

        homes = []
        home_objs = obs['homeR']
        filled_homes = obs['homes']
        for index, rect in enumerate(home_objs):
            if filled_homes[index] == 0:
                homes.append([rect[0], rect[1]])

        return cars_list, rivers_list, homes

    def get_id(self):
        if self.frog_y > 261:
            return str(int((self.frog_y / 32))) + str(int(self.space_right_s)) + str(int(self.space_ahead_s)) + str(
                int(self.space_behind_s)) + \
                   str(int(self.current_space_s)) + str(self.is_empty_home_in_front) + str(int(self.against_left_wall)) \
                   + str(self.against_right_wall)
        else:
            return str(int((self.frog_y / 32))) + str(int(self.space_right_s)) + str(int(self.space_ahead_s)) + str(
                int(self.space_behind_s)) + \
                   str(int(self.current_space_s)) + str(self.is_empty_home_in_front) + str(int(self.against_left_wall)) \
                   + str(self.against_right_wall)

    def update_q_value(self, reward, future_expected_reward, action):
        self.n[action] += 1
        alpha = 2.0 / self.n[action]
        if self.was_death(reward) or self.was_victory(reward):
            self.q_val[action] = (((1 - alpha) * self.q_val[action]) + (alpha * reward)) + (
                    self.inflation_const / self.n[action])

            print "Updated State: " + self.get_id() + " (" + str(self.frog_x) + ", " + \
                  str(self.frog_y) + "): " + str(self.get_q_value_strings())
            return

        self.q_val[action] = ((1 - alpha) * self.q_val[action] +
                              alpha * (reward + (self.gamma * future_expected_reward))) + (
                                     self.inflation_const / self.n[action])

        print "Updated State: " + self.get_id() + " (" + str(self.frog_x) + ", " + \
              str(self.frog_y) + "): " + str(self.get_q_value_strings())

    def get_frog_y(self):
        return self.frog_y

    def get_frog_x(self):
        return self.frog_x

    def set_q_value(self, action, q_val):
        self.q_val[action] = q_val

    def get_q_values(self):
        return self.q_val

    def get_q_value_strings(self):
        new_dict = {}
        for key, val in self.q_val.iteritems():
            if key == K_a:
                new_dict['LEFT'] = str(round(val, 2))
            elif key == K_s:
                new_dict['DOWN'] = str(round(val, 2))
            elif key == K_d:
                new_dict['RIGHT'] = str(round(val, 2))
            elif key == K_w:
                new_dict['UP'] = str(round(val, 2))
            else:
                new_dict['STAY'] = str(round(val, 2))
        return new_dict

    def set_q_values(self, q_values):
        self.q_val = q_values

    def get_dist_from_start(self):
        return self.dist_from_start

    @staticmethod
    def was_victory(reward):
        return reward == 1.0

    @staticmethod
    def was_death(reward):
        return reward == -1.0

    def get_q_value(self, action):
        return self.q_val[action]

    def check_action(self, action):
        if action == K_s:
            return self.__go_down()
        elif action == K_d:
            return self.__go_right()
        elif action == K_w:
            return self.__go_up()
        elif action == K_a:
            return self.__go_left()
        elif action is None:
            return self
        else:
            print(">>> ERROR: invalid action passed to do_action: " + str(action) + " <<<")
            exit(1)

    def __go_right(self):
        if self.frog_x == self.RIGHT_WALL:
            return self

        copy = deepcopy(self)
        copy.frog_x += self.BLOCK_LENGTH
        return copy

    def __go_left(self):
        if self.frog_x == self.LEFT_WALL:
            return self

        copy = deepcopy(self)
        copy.frog_x -= self.BLOCK_LENGTH
        return copy

    def __go_up(self):
        if self.frog_y == self.TOP_WALL:
            return self

        copy = deepcopy(self)
        copy.frog_y -= self.BLOCK_LENGTH
        return copy

    def __go_down(self):
        if self.frog_y == self.BOTTOM_WALL:
            return self

        copy = deepcopy(self)
        copy.frog_y += self.BLOCK_LENGTH
        return copy

    def calc_empty_home_in_front(self):
        if self.dist_from_start < 12:
            return 1

        space_ahead = self.frog_y - self.BLOCK_LENGTH
        for home in self.homes:
            if self.is_same_col(self.frog_x, home[0]) and self.is_same_row(space_ahead, home[1]):
                return 0
        return 1
