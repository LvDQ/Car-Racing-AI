from Car_Racing_AI import screenshot
import pickle

y_dir = 'y.txt'
model_dir = 'model_20171213_dirt4.h5'

debugMode = False
collectNotPredict = True

#for keyboard
left = 0x25
right = 0x27
forward = 0x26
back = 0x28
#for control thread
run = 0x4F
pause = 0x50
kill = 0x4C
#for w and h
w = 1920-400
h = 1080

ss = screenshot()
try:
    y = pickle.load(open(y_dir, "rb"))
    ss.init_screenshot(left = left, right = right, forward = forward, back = back, run = run, pause = pause, kill = kill, w = w, h = h, model_dir = model_dir, debugMode = debugMode, y = y)
except:
    ss.init_screenshot(left = left, right = right, forward = forward, back = back, run = run, pause = pause, kill = kill, w = w, h = h, model_dir = model_dir, debugMode = debugMode)


if collectNotPredict:
    ss.born_controller_thread()
else:
    ss.born_playcontroller_thread()