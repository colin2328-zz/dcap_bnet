"""
Classifier Instance Enumeration Scratchpad
Will Drevo
CSAIL LIDS

demotask,./server/tasks/demotask.py,./server/tasks/demotaskdata
c1_1,./server/tasks/runABP.py,./server/tasks/classifierInstances/ci_1
"""

# for matlab serialization and matrix constuction
import numpy as np
import scipy.io as sio

# combinatorics module (Python 2.6 required)
import itertools

# mandatory choices
colors	 	= ['red', 'blue', 'green']
numbers 	= [1, 2, 3]
locations 	= ['indoors', 'outdoors']

COLOR_LABEL 	= 'color'
NUMBER_LABEL 	= 'number'
LOCATION_LABEL	= 'location'

colors_tuples 		= zip([COLOR_LABEL for i in range(len(colors))], colors)
numbers_tuples		= zip([NUMBER_LABEL for i in range(len(numbers))], numbers)
locations_tuples 	= zip([LOCATION_LABEL for i in range(len(locations))], locations)

mandatory_choices = [colors_tuples, numbers_tuples, locations_tuples]

# conditional branching choices
indoor_conditionals = ['bathroom', 'bedroom', 'kitchen']
green_conditionals = ['forest', 'light', 'dark']

INDOOR_TRIGGER = 'indoors'
GREEN_TRIGGER = 'green'

indoor_conditional_tuples = zip([INDOOR_TRIGGER for i in range(len(indoor_conditionals))], indoor_conditionals)
green_conditional_tuples = zip([GREEN_TRIGGER for i in range(len(green_conditionals))], green_conditionals)

# here are the conditional branching choices
conditional_choices = { 
	# if the combination contains the tuple key, 
	# then we'll calculate the combinations with the choices from the list added as well
	(LOCATION_LABEL, INDOOR_TRIGGER): indoor_conditional_tuples, 
	(COLOR_LABEL, GREEN_TRIGGER): green_conditional_tuples 
}

# final list of name value pairs 
combinations = []

# for each combination of the mandatory choices
print "Generating combinations..."
for combination in itertools.product(*mandatory_choices):

	# retrieve all conditionals triggered by this mandatory choice
    conditionals = [conditional_choices[k] for k in combination if k in conditional_choices]
    
    # return the cartesian product of the mandatory and conditional selections
    for r in itertools.product([combination],*conditionals):
    
    	# join the tuple and list into a single list
    	# then add to our total
    	c = list(r[0]) + list(r[1:])
        combinations.append(c)
        print c
        
# now create matrix cells
count = 0
CLASSIFIER_INSTANCE_FILEBASE = "ci_%d.mat"

# for each classifier instance parameter combination
print "Creating matlab serialized classifier instances..."
for c in combinations:

	# unpack tuples into matlab cell array
	cellArr = np.zeros((2, len(c)), dtype=np.object)
	i = 0
	for (name, value) in c:
		cellArr[0,i] = name
		cellArr[1,i] = value
		i += 1
	
	# save to disk
	filename = CLASSIFIER_INSTANCE_FILEBASE % count
	#sio.savemat(filename, {"instance":cellArr})
	count += 1
	
print "Successfully wrote %d classifier instances to disk." % count
        