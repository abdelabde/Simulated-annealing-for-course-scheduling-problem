#Importing libraries:
import random
import numpy
#Building room,instructor,course as objects with attributes as follows:
#room is an object with name and capacity as attributes
class Room:
    def __init__(self,name, cap):
        self.name =name
        self.capacity = cap

    def __str__(self):
        return " {}".format(self.name)
#instructor is an object with names and taught courses (list of courses) as attributes
class Instructor:
    def __init__(self, name):
        self.name = name
        self.courses = []

    def add_course(self, course):
        self.courses.append(course)
    def __str__(self):
        return "{}".format(self.name)
#course is an object with name and capacity as attributes    
class Course:
    def __init__(self, name, cap):
        self.name = name
        self.capacity = cap

    def __str__(self):
        return "{}".format(self.name)
    
#Data of the problem as lists:
Courses=[[1,20],[2,25],[3,30],[4,20],[5,30],[6,30]]
Rooms=[['r1',25],['r2',25],['r3',30],['r4',30]]
Instructors=[['X',[1,2,3]],['Y',[1,2,3]],['Z',[4,5,6]],['R',[4,5,6]],]
#Building the problem as objects with (list of class,list of rooms,list of instructors,list of times lots) as attributes and a function to load data to the object
class Problem:

    def __init__(self):
        self.class_list = []
        self.room_list = []
        self.instructor_list = []
        self.time_slots = ['T1','T2','T3','T4']

    def load_data(self):
        for i in Courses:
            temp_class =Course(i[0],i[1])
            self.class_list.append(temp_class)
        for j in Rooms:
            temp_room =Room(j[0], j[1])
            self.room_list.append(temp_room)
        for k in Instructors:
            temp_instructor = Instructor(k[0])
            for n in k[1]:
                temp_instructor.add_course(n)
                self.instructor_list.append(temp_instructor)
# Object ScheduleBlock:is a block in the schedule including all final info for a session like this (course_name, time, room,instructor)    
class ScheduleBlock:

    def __init__(self, name):
        self.course_name = name
        self.time = 0
        self.instructor = "TBD"
        self.room = "TBD"

    def assign_time(self, time):
        self.time = time

    def assign_instructor(self, inst):
        self.instructor = inst

    def assign_room(self, loc):
        self.room = loc

    def __str__(self):
        return "CS {} at {} in {} with {}.".format(self.course_name, self.time, self.room, self.instructor)
#Fonction to find a random solution to start 
def random_solution(problem):
    schedule = []
    for item in problem.class_list:
        # Create block
        temp_block = ScheduleBlock(item)
        # assign instructor
        while True:
            temp_pr = random.choice(problem.instructor_list)
            if item.name in temp_pr.courses:
                temp_block.assign_instructor(temp_pr)
                break
        # assign room
        while True:
            temp_rm = random.choice(problem.room_list)
            if item.capacity <= temp_rm.capacity:
                temp_block.assign_room(temp_rm)
                break
        # assign time
        while True:
            temp_tm = random.choice(problem.time_slots)
            if len(schedule) == 0:
                temp_block.assign_time(temp_tm)
                break
            cnt = 0
            for prior in schedule:
                if prior.time == temp_tm and prior.instructor == temp_block.instructor:
                    cnt += 1
            if cnt == 0:
                temp_block.assign_time(temp_tm)
                break

        schedule.append(temp_block)

    return schedule
'''Example of a random solution to start'''
problem = Problem()
problem.load_data()
L= random_solution(problem)
for i in L :
    print(i.course_name)
    print(i.instructor)
    print(i.room)
    print(i.time)
    
#The probability function known fo a simulated annealing problem    
def probability(fit_c, fit_new, tem):
    if fit_new > fit_c:
        return 1
    return numpy.exp(10000000 * (fit_new - fit_c) / tem)
#Bulding the fitness function based on a cost to schedule with no conflicts.
def fitness_function(state):
    cost = 0
    for block in state:
        #Conflict1:Different courses occupied the same room at the same time
        class_time_room = 0
        for other_block in state:
            if block.time == other_block.time and block.room == other_block.room:
                class_time_room += 1
        if class_time_room > 1:
            cost += 5

        # Conflict 2:A course the assign to be taught in a room that is smaller than the maximum number of students
        if block.course_name.capacity>= block.room.capacity:
            cost += 5
        # Conflict3: An instructor assigned to teach more the one course at the same time
        class_time_instructor = 0
        for other_block in state:
            if not (other_block.time == block.time and other_block.instructor == block.instructor):
                class_time_instructor +=1
        if class_time_instructor > 1:
            cost += 5

    return cost

#Generate a solution that is close to the prior solution
def neighbor(problem, previous):
    new_state = previous
    ran_block = random.choice(new_state)
    item_selector = random.randint(1, 3)
    if item_selector == 1:
        ran_block.assign_time(random.choice(problem.time_slots))
    if item_selector == 2:
        ran_block.assign_room(random.choice(problem.room_list))
    if item_selector == 3:
        while True:
            temp_pr = random.choice(problem.instructor_list)
            temp_pr.courses=[str(i) for i in temp_pr.courses ]
            if str(ran_block.course_name) in temp_pr.courses:
                ran_block.assign_instructor(temp_pr)
                break

    return new_state

#Function for the simulated annealing algorithm            
def simulated_annealing(problem):
    random.seed()
    # Setup temp variables
    temp = 1.0
    temp_min = 0.0001
    temp_drop = 0.98

    attempts = 0
    better_attempts = 0

    # Initialize current and best state and fitness
    current_state = random_solution(problem)
    best_state = current_state
    current_fitness = fitness_function(current_state)
    best_fit = current_fitness
    while temp > temp_min:
        # Generate a new neighbor state
        new_state = neighbor(problem, current_state)
        new_fitness = fitness_function(new_state)
        # New fit is recorded if best fit yet
        if new_fitness < best_fit:
            best_state = current_state
            best_fit = new_fitness
            better_attempts += 1
        else:
            # Assign new current state if within probability
            prob = probability(current_fitness, best_fit, temp)
            if prob > random.random():
                current_state = new_state
                current_fitness = new_fitness
            # Drop temp and reset counters
        if attempts > 4000 or better_attempts > 400:
            temp=temp*temp_drop
            attempts = 0
            better_attempts = 0
        attempts += 1
        #To see results of each iteration
        print("Result for iteration {} :fit:{} ,and block:{}".format(attempts,best_fit,best_state))
    return(best_state, best_fit)


#Function to see the final results:
def main():
    problem = Problem()
    problem.load_data()

    best_state, best_fit = simulated_annealing(problem)
    for block in best_state:
        print(str(block))
#Run to see the result:        
if __name__ == "__main__":
    main()
    



