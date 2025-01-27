
import warnings
warnings.filterwarnings('ignore') # ignore warnings

from .markers import markers

from numpy import nan
class State:
    markers = markers
    

    def __init__(self, story_state):
        # list story keys
        self.name = story_state.get('name','') # string
        self.title = story_state.get('title','') # string
        self.stages = {k:v.get('state',{}) for k,v in story_state['stages'].items()} #  dict_keys(['0', '1', '2', '3', '4', '5', '6'])
        class_room_keys = ['id', 'code', 'name', 'active', 'created', 'updated', 'educator_id', 'asynchronous']
        self.classroom = story_state.get('classroom',{k:None for k in class_room_keys})# dict_keys(['id', 'code', 'name', 'active', 'created', 'updated', 'educator_id', 'asynchronous'])
        self.responses = story_state.get('responses',{})
        self.mc_scoring = story_state.get('mc_scoring',{}) # dict_keys(['1', '3', '4', '5', '6'])
        self.stage_index = story_state.get('stage_index',nan) # int
        self.total_score = story_state.get('total_score',nan) #int
        self.student_user = story_state.get('student_user',{}) # dict_keys(['id', 'ip', 'age', 'lat', 'lon', 'seed', 'dummy', 'email', 'gender', 'visits', 'password', 'username', 'verified', 'last_visit', 'institution', 'team_member', 'last_visit_ip', 'profile_created', 'verification_code'])
        self.teacher_user = story_state.get('teacher_user',None) # None
        self.max_stage_index = story_state.get('max_stage_index',0) # int
        self.has_best_fit_galaxy = story_state.get('has_best_fit_galaxy',False) # bool
        
        
    
    def get_possible_score(self):
        possible_score = 0
        for key, value in self.mc_scoring.items():
            for v in value.values():
                possible_score += 10
        return possible_score
    
    def stage_score(self, stage):
        score = 0
        possible_score = 0
        for key, value in self.mc_scoring[str(stage)].items():
            score += value['score']
            possible_score += 10
        return score, possible_score
    

    @property
    def how_far(self):
        stage_index = self.max_stage_index
        if stage_index is nan:
            return {'string': 'No stage index', 'value':0.0}
        stage_markers = self.markers.get(str(stage_index),None)
        
        frac = self.stage_fraction_completed(stage_index)
        # are we in slideshow stage
        if stage_markers is None:
            string_fmt =  "In Stage {} slideshow".format(stage_index)
        else:
            string_fmt = f"{frac:.0%} through Stage {stage_index}"
            
        return {'string': string_fmt, 'value':frac}
    
    def stage_fraction_completed(self, stage):
        if stage is None:
            return 1.0
        markers = self.markers[str(stage)]
        
        if markers is None:
            return 1.0
        current_stage_marker = self.stages[str(stage)]['marker']
        total = len(markers)
        if current_stage_marker not in markers:
            return nan
        current = markers.index(current_stage_marker) + 1
        frac = float(current) / float(total)
        return frac
    
    def total_fraction_completed(self):
        total = []
        current = []
        for key, stage in self.stages.items():
            markers = self.markers.get(key,None)
            if markers is not None:
                total.append(len(markers))
                if self.stage_index == int(key):
                    if self.current_marker in markers:
                        val = markers.index(self.current_marker) + 1
                    else:
                        val = nan
                elif self.max_stage_index > int(key):
                    # if true, then stage key is complete
                    val = len(markers)
                elif self.stage_index < int(key):
                    # if false, then stage key is not complete
                    val = 0 #markers.index(stage['marker']) + 1
                else:
                    val = 0

                current.append(val)
        # print(total, current)
        if nan in current:
            frac = nan
        else:
            frac = int(100 * float(sum(current)) / float(sum(total)))
        return {'percent':frac, 'total':sum(total), 'current':sum(current)}
    
    @property
    def possible_score(self):
        return self.get_possible_score()
    
    @property
    def score(self):
        return self.total_score / self.possible_score
    
    
    @property
    def current_marker(self):
        return self.stages.get(str(self.stage_index),{}).get('marker','none')
    
    @property
    def max_marker(self):
        return self.stages.get(str(self.max_stage_index),{}).get('marker','none')
    
    @property
    def percent_completion(self):
        return self.total_fraction_completed()['percent']
    
    
# create a wrapper class StateList that can be used to create a list of State objects
# and getattr to get the attributes of the State object
class StateList():
    
    def __init__(self, list_of_states):
        self.states = [State(state) for state in list_of_states]
    
    def __getattribute__(self, __name):
        try:
            return object.__getattribute__(self, __name)
        except AttributeError:
            if __name == 'student_id' or __name == 'id':
                return [state.student_user['id'] for state in self.states]
            return [getattr(state, __name) for state in self.states]

