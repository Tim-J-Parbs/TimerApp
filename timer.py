import tkinter as tk
import threading
import datetime
import time
import numpy as np
import random
import string
class Application(tk.Tk):
    def __init__(self,  master=None):
        tk.Tk.__init__(self, master)
        #self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.geometry('600x800')
        self.resizable(True, True)
        self.title('Timer')
        self.mainframe()
        self.timer_running = threading.Event()
        self.timer_stopped = threading.Event()
        self.timer_time = 0.0
        self.timer_interval = 0.01
        self.stopwatch = self.Stopwatch(self.timer_interval, self.update_time, self.timer_stopped)
        self.update_time(0)
        self.slidecounter  = 1
    def mainframe(self):
        # Define interface
        self.columnconfigure(6, weight=1)
        self.rowconfigure(20, weight=2)

        self.timerbox = tk.Label(master=self, text='0')
        self.timerbox.grid(column=0, columnspan=2,
                      row=0, rowspan=1)
        self.eventlist = tk.StringVar(value=())
        self.eventlistbox = tk.Listbox(self,listvariable=self.eventlist, width=38)
        self.scrollbar = tk.Scrollbar(master=self, orient=tk.VERTICAL)
        self.eventlistbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.eventlistbox.yview)

        self.run = tk.Button(self, text="run", command=self.timer_start)
        self.stop = tk.Button(self, text="stop", command=self.timer_stop)
        self.clear = tk.Button(self, text="clear", command=self.timer_clear)
        self.newevent_slide_done = tk.Button(self, text="Slide Done", command=self.Slide_done)
        self.newevent_interrupt = tk.Button(self, text="Interruption", command=self.Interrupt)
        self.export = tk.Button(self, text="Export Log", command=self.logexport)
        self.eventlistbox.grid(row=1, column=0, rowspan=20, columnspan=2,
                    sticky='nswe')
        self.scrollbar.grid(row=1, column=3, rowspan=20,  sticky='nsw')
       # self.eventlistbox.columnconfigure(0, weight=1)

        self.run.grid(row=1, column=4, sticky='nswe')
        self.stop.grid(row=1, column=5, sticky='nswe')
        self.newevent_slide_done.grid(row=2, column=4, sticky='nswe')
        self.newevent_interrupt.grid(row=2, column=5, sticky='nswe')
        self.export.grid(row=3, column=4, sticky='nswe')
        self.clear.grid(row=1, column=6, sticky='nswe')
        self.text_eventlist = []
        # Start main loop
    def msg_update(self, time, msg):
        if self.stopwatch.running:
            msglen = 10
            timestr = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(time), "%H:%M:%S")
            if (msglen-len(msg)) <0:
                msg = msg[:msglen-2]+'...'
            interr = ' ' *(msglen-len(msg))
            tolist = timestr + ' - ' + interr + msg
            self.text_eventlist.append(tolist)
            self.eventlist.set(self.text_eventlist)

    def timer_start(self):
        if not self.stopwatch.running:
            print("Starting thread")
            self.timer_stopped.clear()
            self.timer_running.set()
            self.stopwatch.run()
        else:
            print('Already running!')


    class Stopwatch(threading.Thread):
        def __init__(self, interval, timefn, stopevent):
            threading.Thread.__init__(self)
            self.stopped = stopevent
            self.interval = interval
            self.timer_time = 0.0
            self.fn = timefn
            self.running = False
            self.starttime = 0
            self.stoptime = 0
            self.paused = False
        def run(self):
            self.running = True
            self.starttime = time.time()-self.stoptime
            while not self.stopped.wait(self.interval):
                self.update()
            self.stoptime = time.time()-self.starttime
            self.running = False
        def get_time(self):
            return time.time()-self.starttime
        def update(self):
            self.fn(time.time()-self.starttime)
        def clear(self):
            self.starttime = time.time()
            self.fn(0.0)
            self.stoptime = 0.0
        def calibrate(self):
            then = time.time()
            for i in range(1000):
                self.timer_time += self.interval
                self.fn(self.timer_time)
            now = time.time()
            self.clear()
            return (now-then)/1000

    def update_time(self, thistime):
        timestr = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(thistime), "%H:%M:%S:%f")
        # self.timer_time = np.floor(self.timer_time/interval)*interval
        self.timerbox.config(text=timestr)
        self.update()
    def timer_stop(self):
        self.timer_stopped.set()
        print("Attempting to end")
    def timer_clear(self):
        self.stopwatch.clear()

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    def Slide_done(self):
        if self.stopwatch.running:
            self.slidecounter  +=1
            msg = 'Folie ' + str(self.slidecounter)
            self.msg_update(self.stopwatch.get_time(),msg)

    def Interrupt(self):
        msg = 'Störung'
        self.msg_update(self.stopwatch.get_time(), msg)
    def logexport(self):
        timestr = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(time.time()), "%M:%D:%H:%M:%S:%f")
        with open('./run.txt', 'w+')as f:
            f.write('-----------' + timestr + '-----------\n')
            for n in self.text_eventlist:
                f.write(n+'\n')
        print('Done exporting')

a = Application()
a.mainframe()
a.mainloop()

