import win32gui
import win32ui 
import win32con
import time
import threading
import ctypes
import os
import pickle
from press_release_keyboard import PressKey, ReleaseKey
from scipy import misc
#import numpy as np
#import random


class screenshot(object):
    
    def init_screenshot(self, fps = 2, filter_length = 200, y = [], y_dir = 'y.txt', ss_dir = 'screenshot', model_dir = '', left = 0x41, right = 0x44, forward = 0x41, back = 0x5A, run = 0x4F, pause = 0x50, kill = 0x4C, w = 1920, h = 1080, zfillnum = 5, debugMode = True, obMode = True):
        self.y_pred = [0, 0]
        self.w = w
        self.h = h
        self.windowname = 'None'
        self.zfillnum = zfillnum
        self.gap = 1/fps
        self.filter_length = filter_length
        self.minigap = self.gap/filter_length
        self.left = left
        self.right = right
        self.forward = forward
        self.back = back
        self.run = run
        self.pause = pause
        self.kill = kill
        self.screenshot_enable = False
        self.thread_enable = True
        self.debugMode = debugMode
        self.obMode = obMode
        self.y = y
        self.y_dir = y_dir
        self.index = len(self.y)
        self.index_image_processing = self.index
        self.directionname = ss_dir
        self.model_dir = model_dir
        print('\n--------------------------\nMachine Learning Project:\nRacing Car AI!\nby Jiadong Chen and Ke Yang\n--------------------------\n\nPress O to start, P to pause, L to quit\n')
        

        
    def IsKeyPressed(self, VK_KEYCODE):
        return ctypes.windll.user32.GetKeyState(ctypes.c_int(VK_KEYCODE)) & 0x8000 != 0
    
    def LeftMiddleRight(self):
        l = self.IsKeyPressed(self.left)
        r = self.IsKeyPressed(self.right)
        f = self.IsKeyPressed(self.forward)
        b = self.IsKeyPressed(self.back)
        
        lmr = 0
        fmb = 0
        
        if l and not r:
            lmr = -1
        elif not l and r:
            lmr = 1
            
        if f and not b:
            fmb = 1
        elif not f and b:
            fmb = -1
        
        return lmr, fmb
    
    def threadscreenshot(self):
        dir_exists = os.path.isdir(self.directionname)
        if not dir_exists:
            os.mkdir(self.directionname)
            print("Making directory %s" %self.directionname)
        else:
            print("Will store images in directory %s" %self.directionname)
        while self.screenshot_enable: 
            if self.index%50 == 0:
                pickle.dump(self.y, open(self.y_dir, 'wb'))
                print('save y at index =', self.index)
            time0 = time.time()
            fn = './' + self.directionname + '/' + str(self.index).zfill(self.zfillnum) + '.bmp'
            
            hwnd = win32gui.FindWindow(None, self.windowname)
            wDC = win32gui.GetWindowDC(hwnd)
            dcObj=win32ui.CreateDCFromHandle(wDC)
            cDC=dcObj.CreateCompatibleDC()
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
            cDC.SelectObject(dataBitMap)
            cDC.BitBlt((0,0),(self.w, self.h) , dcObj, (0,0), win32con.SRCCOPY)
            time1 = time.time()
            #add filter here
            num = [0, 0]
            for i in range(self.filter_length):
                lmr, fmb = self.LeftMiddleRight()
                num[0] += lmr
                num[1] += fmb
                time.sleep(0.00001)
            num[0] = num[0]/self.filter_length
            num[1] = num[1]/self.filter_length
            time2 = time.time()
            
            self.index += 1
            dataBitMap.SaveBitmapFile(cDC, fn)
            
            
            self.y.append(num)
            print('save screenshot', fn, ' regression num =', num)
            # Free Resources
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())
            time3 = time.time()
            print(time1-time0, time2-time1, time3-time2)
            
    def image_process(self, temp):
        cut = int(self.h*0.2)
        cut2 = int(self.h*0.35)
        temp = temp[cut2:-cut, :, :]#slice
        self.ts = temp.shape
        temp = misc.imresize(temp, (self.ts[0]//3, self.ts[1]//3))
        #temp = misc.imresize(temp, (307, 840))
        #temp = np.sum(temp*self.rgb2gray_filter, axis=2)#rgb
        return temp
    
    def y_adjust(self, y_pred):
        #you may try something like
        #return [0.3*y_pred[0], 0.3]
        #this random number is only for debug
        return y_pred
    
    def image_processing_thread(self):

        self.rgb2gray_filter = [[[0.2989, 0.5870, 0.1140]]]
        while self.screenshot_enable or self.index_image_processing < self.index:
            try:
                fn = './screenshot/' + str(self.index_image_processing).zfill(self.zfillnum) + '.bmp'
                temp = misc.imread(fn)
                temp = self.image_process(temp)
                os.remove(fn)
                print('remove', fn)
                misc.imsave(fn, temp)
                print('save processed image', fn)
                self.index_image_processing += 1
                #temp = misc.imresize(, (nrow, ncol))##imageio.imread, skimage.transform.resize
            except:
                print(fn + ' not processed yet')
            time.sleep(0.13)
    
    def ss_and_predict_thread(self):
        
        self.temp_dir = 'ss_and_predict_temp.bmp'
        #load model
        try:
            self.model
        except:
            import keras.backend as K
            K.clear_session()
            from keras.models import load_model
            print('loading model ', self.model_dir)
            try:
                self.model = load_model(self.model_dir)
                print('load model finish')
            except:
                print('load model failed, prepare to exit()')
                time.sleep(10)
                exit()
        
        if not self.obMode:
            self.born_asyn_press_thread()
        self.born_thread_www()
        
        while self.screenshot_enable:
            #time.sleep(0.1)
            hwnd = win32gui.FindWindow(None, self.windowname)
            wDC = win32gui.GetWindowDC(hwnd)
            dcObj=win32ui.CreateDCFromHandle(wDC)
            cDC=dcObj.CreateCompatibleDC()
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
            cDC.SelectObject(dataBitMap)
            cDC.BitBlt((0,0),(self.w, self.h) , dcObj, (0,0), win32con.SRCCOPY)
            dataBitMap.SaveBitmapFile(cDC, self.temp_dir)
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())
            
            temp = [self.model.predict(self.image_process(misc.imread(self.temp_dir))[None, :])[0][0], 0.35]#random for debug only
            print('y_pred =', temp)
            self.y_pred = self.y_adjust(temp)
            if self.debugMode:
                print('y_pred_adjusted =', self.y_pred)
            
    def asyn_press_thread(self):
        y_in = [float(0), float(0)]
        y_ifright_ifforward = [True, True]
        y_press_ratio = [float(0), float(0)]
        y_pressed_history = [[1, 0], [1, 0]]#first for not pressed, second for pressed
        y_pressed_ratio = [(y_pressed_history[0][1])/(y_pressed_history[0][0]+y_pressed_history[0][1]), (y_pressed_history[1][1])/(y_pressed_history[1][0]+y_pressed_history[1][1])]
        time0 = time.time()
        while self.screenshot_enable:
            time.sleep(0.0001)
            if self.y_pred != y_in:#update status of keyboard press, clear history
                y_in = self.y_pred
                time1 = time.time()
                if self.debugMode:
                    print('asyn_press_period =', time1-time0, 's')
                time0 = time1
                if self.debugMode:
                    print('y_pressed_history =', y_pressed_history)
                    print('y_ifright_ifforward =', y_ifright_ifforward)
                y_pressed_history = [[1, 0], [1, 0]]
                y_ifright_ifforward = [y_in[0] >= 0, y_in[1] >= 0]
                y_press_ratio = [abs(y_in[0]), abs(y_in[1])]
                '''
                ReleaseKey(self.right)
                ReleaseKey(self.left)
                ReleaseKey(self.forward)
                ReleaseKey(self.back)
                '''
            
            y_pressed_ratio = [(y_pressed_history[0][1])/(y_pressed_history[0][0]+y_pressed_history[0][1]), (y_pressed_history[1][1])/(y_pressed_history[1][0]+y_pressed_history[1][1])]
            
            if y_press_ratio[0] <= y_pressed_ratio[0]:
                y_pressed_history[0][0] += 1
                if y_ifright_ifforward[0]:
                    ReleaseKey(self.right)
                else:
                    ReleaseKey(self.left)
            else:
                y_pressed_history[0][1] += 1
                if y_ifright_ifforward[0]:
                    PressKey(self.right)
                else:
                    PressKey(self.left)
            '''
            if y_press_ratio[1] <= y_pressed_ratio[1]:
                y_pressed_history[1][0] += 1
                if y_ifright_ifforward[1]:
                    ReleaseKey(self.forward)
                else:
                    ReleaseKey(self.back)
            else:
                y_pressed_history[1][1] += 1
                if y_ifright_ifforward[1]:
                    PressKey(self.forward)
                else:
                    PressKey(self.back)
            '''
    
    def thread_www(self):
        www = self.forward
        while self.screenshot_enable:
            PressKey(www)
            time.sleep(0.3)
            ReleaseKey(www)
            time.sleep(0.1)
            for i in range(3):
                PressKey(www)
                time.sleep(0.05)
                ReleaseKey(www)
                time.sleep(0.35)
        ReleaseKey(www)
    
    def threadcontroller(self):
        print('now collecting data set\nwill create file', self.y_dir, 'and folder', self.directionname, 'in working directory')
        while self.thread_enable:
            if self.IsKeyPressed(self.run) and not self.screenshot_enable:
                self.screenshot_enable = True
                self.born_screenshot_thread()
                self.born_image_processing_thread()
                self.born_thread_www()
            if self.IsKeyPressed(self.pause):
                self.end()
            if self.IsKeyPressed(self.kill):
                self.end()
                self.thread_enable = False
            time.sleep(0.02)
            
    def playthreadcontroller(self):
        print('now predict and play')

        while self.thread_enable:
            if self.IsKeyPressed(self.run) and not self.screenshot_enable:
                self.screenshot_enable = True
                self.born_ss_and_predict_thread()
            if self.IsKeyPressed(self.pause):
                self.end()
            if self.IsKeyPressed(self.kill):
                self.end()
                self.thread_enable = False
            time.sleep(0.02)
    

    
    def born_screenshot_thread(self):
        self.threadss = threading.Thread(target = self.threadscreenshot)
        self.threadss.start()
        
    def born_image_processing_thread(self):
        self.threadip = threading.Thread(target = self.image_processing_thread)
        self.threadip.start()
        
    def born_asyn_press_thread(self):
        self.threadap = threading.Thread(target = self.asyn_press_thread)
        self.threadap.start()
        
    def born_ss_and_predict_thread(self):
        self.threadap = threading.Thread(target = self.ss_and_predict_thread)
        self.threadap.start()
    
    def born_thread_www(self):
        self.threadw = threading.Thread(target = self.thread_www)
        self.threadw.start()
    
    def born_controller_thread(self):
        self.threadc = threading.Thread(target = self.threadcontroller)
        self.threadc.start()
        
    def born_playcontroller_thread(self):
        self.threadpc = threading.Thread(target = self.playthreadcontroller)
        self.threadpc.start()
    

    
    def end(self):
        try:
            pickle.dump(self.y, open(self.y_dir, 'wb'))
        except:
            pass
        self.screenshot_enable = False
        try:
            os.remove(self.temp_dir)
        except:
            pass














#VKStr[0x01] = "LEFT_MOUSEE"
#VKStr[0x02] = "RIGHT_MOUSE"
#VKStr[0x03] = "MIDDLE_MOUSE"
#VKStr[0x08] = "BACKSPACE"
#VKStr[0x09] = "TAB"
#VKStr[0x0D] = "ENTER"
#VKStr[0x10] = "SHIFT"
#VKStr[0x11] = "CTRL"
#VKStr[0x12] = "ALT"
#VKStr[0x14] = "CAPSLOCK"
#VKStr[0x18] = "ESCAPE"
#VKStr[0x20] = " "
#VKStr[0x25] = "LEFT_ARROW"
#VKStr[0x26] = "UP_ARROW"
#VKStr[0x27] = "RIGHT_ARROW"
#VKStr[0x28] = "DOWN_ARROW"
#VKStr[0x2C] = "PRINT_SCREEN"
#VKStr[0x30] = "0"
#VKStr[0x31] = "1"
#VKStr[0x32] = "2"
#VKStr[0x33] = "3"
#VKStr[0x34] = "4"
#VKStr[0x35] = "5"
#VKStr[0x36] = "6"
#VKStr[0x37] = "7"
#VKStr[0x38] = "8"
#VKStr[0x39] = "9"
#VKStr[0x41] = "a"
#VKStr[0x42] = "b"
#VKStr[0x43] = "c"
#VKStr[0x44] = "d"
#VKStr[0x45] = "e"
#VKStr[0x46] = "f"
#VKStr[0x47] = "g"
#VKStr[0x48] = "h"
#VKStr[0x49] = "i"
#VKStr[0x4A] = "j"
#VKStr[0x4B] = "k"
#VKStr[0x4C] = "l"
#VKStr[0x4D] = "m"
#VKStr[0x4E] = "n"
#VKStr[0x4F] = "o"
#VKStr[0x50] = "p"
#VKStr[0x51] = "q"
#VKStr[0x52] = "r"
#VKStr[0x53] = "s"
#VKStr[0x54] = "t"
#VKStr[0x55] = "u"
#VKStr[0x56] = "v"
#VKStr[0x57] = "w"
#VKStr[0x58] = "x"
#VKStr[0x59] = "y"
#VKStr[0x5A] = "z"


#
#y_dir = 'y.txt'
#model_dir = 'model_20171213_dirt4.h5'
#
#debugMode = False
#obMode = True
#collectNotPredict = False
#
##for keyboard
#left = 0x25
#right = 0x27
#forward = 0x26
#back = 0x28
##for control thread
#run = 0x4F
#pause = 0x50
#kill = 0x4C
##for w and h
#w = 1920-400
#h = 1080
#
#
#ss = screenshot()
#try:
#    y = pickle.load(open(y_dir, "rb"))
#    ss.init_screenshot(left = left, right = right, forward = forward, back = back, run = run, pause = pause, kill = kill, w = w, h = h, model_dir = model_dir, debugMode = debugMode, obMode = obMode, y = y)
#except:
#    ss.init_screenshot(left = left, right = right, forward = forward, back = back, run = run, pause = pause, kill = kill, w = w, h = h, model_dir = model_dir, debugMode = debugMode, obMode = obMode)
#
#
#if collectNotPredict:
#    ss.born_controller_thread()
#else:
#    ss.born_playcontroller_thread()










