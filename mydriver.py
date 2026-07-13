"""
This driver does not do any action.
"""

from rose.common import obstacles, actions  # NOQA

driver_name = "MyDriver8"


MAX_DEPTH = 2
PATH_SCORE_IDX = 0
PATH_ACTION_IDX = 1

#default rewards when the driver interacts with the objects listed below
REWARDS = {
    obstacles.NONE: 0,
    obstacles.CRACK: 5,
    obstacles.TRASH: -10,
    obstacles.PENGUIN: 10,
    obstacles.BIKE: -10,
    obstacles.WATER: 4,
    obstacles.BARRIER: -10,
}
PUNISH = -10
NEUTRAL = 0

#dictionary of special actions required to acquire when reaching special objects
SPECIAL_ACTIONS = {
    obstacles.PENGUIN: actions.PICKUP,
    obstacles.CRACK: actions.JUMP,
    obstacles.WATER: actions.BRAKE,
}


class DriveEngine:
    def __init__(self, world):
        self.__world = world
        self.__car_x = world.car.x
        self.__car_y = world.car.y
        
        self.__possible_paths = []

    def get_obj(self, x: int, y: int) -> str:
        try:
            obj = self.__world.get((x, y))
            return obj
        except IndexError:
            return None
    
    def get_object_reward(self, x: int, y: int) -> str:
        obj = self.get_obj(x, y)
        prev_obj = self.get_obj(x, y+1)
        
        # #it doesn't matter what's infront of the object if the object is already harmful so we skip all the code below and return the original value
        # if obj in (obstacles.BIKE, obstacles.TRASH, obstacles.BARRIER):
        #     return REWARDS[obj]
        
        if obj in (obstacles.PENGUIN, obstacles.CRACK, obstacles.WATER) and prev_obj in (obstacles.PENGUIN, obstacles.NONE):
            if self.__car_x != x and self.__car_y - y == 1: #checking if the item is even reachable to be picked/jumped/breaked       (the car cannot go diagonal and perform a special action if the object is found in the diagonal cell. the car needs to be 1 cell behind and on the same lane in order to perform a special action.)     
                if obj == obstacles.PENGUIN:#moving on a penguin doesnt reduct any points so NEUTRAL is returned
                    return NEUTRAL
                return PUNISH#moving on other special objects without performing action reducts 10 points so PUNISH is returned.
            return REWARDS[obj]
        
        if obj in (obstacles.PENGUIN, obstacles.CRACK, obstacles.WATER) and prev_obj not in (obstacles.PENGUIN, obstacles.NONE):
            return PUNISH
        
        return REWARDS[obj]
    
    def get_best_action(self):
        self.__possible_paths = []
        self.__scan_tree(self.__car_x, 0, 0, actions.NONE)
        
        self.__possible_paths.sort(key=lambda path_tuple: path_tuple[PATH_SCORE_IDX], reverse=True)
        
        best_action = self.__possible_paths[0][PATH_ACTION_IDX]
        return best_action

    def __scan_tree(self, current_x, current_depth, current_score, first_step_action):
        if current_depth == MAX_DEPTH:
            self.__possible_paths.append((current_score, first_step_action))
            return
        
        next_y = self.__car_y - 1 - current_depth
        
        possible_moves = [(current_x, actions.NONE)]
        if current_x > 0:
            possible_moves.append((current_x - 1, actions.LEFT))
            
        if current_x < 2:
            possible_moves.append((current_x + 1, actions.RIGHT))
            
        for next_x, next_action in possible_moves:
             # Считаем очки в клетке, куда наступит машина на этом шаге
            cell_reward = self.get_object_reward(next_x, next_y)
            
            step_action = first_step_action
            if current_depth == 0:
                curr_obj = self.get_obj(next_x, next_y)
                step_action = SPECIAL_ACTIONS.get(curr_obj, next_action)
            
            
            self.__scan_tree(
                current_x=next_x,
                current_depth=current_depth + 1,
                current_score=current_score + cell_reward,
                first_step_action=step_action
            )

            
def drive(world):
    engine = DriveEngine(world)
    return engine.get_best_action()
