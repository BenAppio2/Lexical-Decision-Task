import pandas as pd
from psychopy.gui import DlgFromDict
from psychopy.visual import Window, TextStim, ImageStim, ShapeStim, Circle
from psychopy.core import Clock, quit, wait
from psychopy.event import Mouse
from psychopy.hardware.keyboard import Keyboard

exp_info = {'participant_nr': '', 'age': ''}
dlg = DlgFromDict(exp_info)

# If pressed Cancel, abort!
if not dlg.OK:
    quit()
else:
    # Quit when either the participant nr or age is not filled in
    if not exp_info['participant_nr'] or not exp_info['age']:
        quit()
        
    # Also quit in case of invalid participant nr or age
    if int(exp_info['participant_nr']) > 99 or int(exp_info['age']) < 18:
        quit()
    else:  # let's star the experiment!
        print(f"Started experiment for participant {exp_info['participant_nr']} "
                 f"with age {exp_info['age']}.")

# Initialize a fullscreen window with my monitor (HD format) size
# and my monitor specification called "samsung" from the monitor center
win = Window(size=(1920, 1080), fullscr=False, monitor='samsung')

# Also initialize a mouse, although we're not going to use it
mouse = Mouse(visible=True)

# Initialize a (global) clock
clock = Clock()

# Initialize Keyboard
kb = Keyboard()
kb.clearEvents()

### START BODY OF EXPERIMENT ###


### WELCOME ROUTINE ###
# Create a welcome screen and show for 3 seconds
welcome_txt_stim = TextStim(win, text="Welcome to this experiment!", color=(1, 0, -1), font='Calibri')
welcome_txt_stim.draw()
win.flip()
wait(3)

### INSTRUCTION ROUTINE ###
instruct_txt = """ 
In this experiment, you will see a string of words and you have decide if they are words or not.

Use the left and right arrow keys on your keyboard to answer

    CORRECT Word = Left
    INCORRECT Word = Right
    
(Press ‘return’ to start the experiment!)
 """
 
 # Show instructions and wait until response (return)
instruct_txt = TextStim(win, instruct_txt, alignText='left', height=0.085)
instruct_txt.draw()
win.flip()

# Initialize keyboard and wait for response
kb = Keyboard()
while True:
    keys = kb.getKeys()
    if 'return' in keys:
        # The for loop was optional
        for key in keys:
            print(f"The {key.name} key was pressed within {key.rt:.3f} seconds for a total of {key.duration:.3f} seconds.")
        break  # break out of the loop!

### TRIAL LOOP ROUTINE ###
# Read in conditions file
cond_df = pd.read_excel('word_conditions.xlsx')
cond_df = cond_df.sample(frac=1)

# Create fixation target (a plus sign)
fix_target = TextStim(win, '+')
trial_clock = Clock()

# START exp clock
clock.reset()

# Show initial fixation
fix_target.draw()
win.flip()
wait(1)

for idx, row in cond_df.iterrows():
    # Extract current stim and word
    curr_stim = row['stim']
    curr_word = row['word']

    # Create and draw text/img
    stim_txt = TextStim(win, curr_stim, pos=(0, 0.3))

    # Initially, onset is undefined
    cond_df.loc[idx, 'onset'] = -1

    trial_clock.reset()
    kb.clock.reset()
    while trial_clock.getTime() < 2:
        # Draw stuff
        
        if trial_clock.getTime() < 0.5:
            stim_txt.draw()
        else:
            fix_target.draw()
            
        win.flip()
        if cond_df.loc[idx, 'onset'] == -1:
            cond_df.loc[idx, 'onset'] = clock.getTime()
        
        # Get responses
        resp = kb.getKeys()
        if resp:
            # Stop the experiment when 'q' is pressed
            if 'q' in resp:
                quit()

            # Log reaction time and response
            cond_df.loc[idx, 'rt'] = resp[-1].rt
            cond_df.loc[idx, 'resp'] = resp[-1].name

            # Log correct/incorrect
            if resp[-1].name == 'left' and curr_word == 'yes':
               cond_df.loc[idx, 'correct'] = 1
            elif resp[-1].name ==  'right' and curr_word == 'no':
                cond_df.loc[idx, 'correct'] = 1
            else:
                cond_df.loc[idx, 'correct'] = 0
        
effect = cond_df.groupby('word').mean(numeric_only=True)
rt_con = effect.loc['yes', 'rt']
rt_incon = effect.loc['no', 'rt']
acc = cond_df['correct'].mean()

txt = f"""
Your reaction times are as follows:

    Real Word: {rt_con:.3f}
    Not a Word: {rt_incon:.3f}

Overall accuracy: {acc:.3f}
"""
result = TextStim(win, txt)
result.draw()
win.flip()
wait(5)

cond_df.to_csv(f"sub-{exp_info['participant_nr']}_results.csv")

# Thank you screen
thankyou_txt_stim = TextStim(win, text="Thank you for taking this experiment! Please select the green circle if you enjoyed it, and select the red if you did not", color=(1, 0, -1), font='Calibri',height=0.1)
thankyou_txt_stim.draw()
win.flip()
wait(6)

red_circle = Circle(win=win, units="pix", radius=50, fillColor=[1, 0, 0], lineColor=[1, 0, 0],pos=(-50,0)) # Change radius and color as desired

green_circle = Circle(win=win, units="pix", radius=50, fillColor=[0, 1, 0], lineColor=[0, 1, 0],pos=(50,0)) # Change radius and color as desired

green_circle.draw()
red_circle.draw()
win.flip()

while True:
    if mouse.isPressedIn(green_circle):
        print("green")
        break
    if mouse.isPressedIn(red_circle):
        print("red")
        break  # This stops the routine from continuing

# Finish experiment by closing window and quitting
win.close()
quit()  