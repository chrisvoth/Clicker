# pyClicker IDLE game
# 2020-10-16
import itertools
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import font
import random
import math
import pickle

savefile = 'clickersave.pkl'

class Generator():
    """ Generator() class for clicker game items.
        Create a list of class instances, with supporting functions, to make a complete game.

        >>> items = ['Click', 'Pencil', 'Pen, 'Stick']

        >>> costs = [ (4 * (11 ** x) ) for x in range( len(items) ) ]

        >>> costs.insert(0,0)

        >>> rates = [ (2.5 * (8 ** x) ) for x in range( len(items) ) ]

        >>> rates.insert(0,0)       

        >>> generators = [Generator(name = item, cost_base = cb, rate_base = rb, growth = gr) \
                         for item, cb, rb, gr in zip(items, costs, rates,  \
                         random.choice([1.07, 1.075, 1.08, 1.085, 1.09]) ]

                    """
    
    def __init__(self, name = '', cost_base = 1, rate_base = 1, growth = 1.07, widgets = 0, \
                 lifetime_widgets = 0, owned = 0 ):
        """ Initialize instance variables. multiplier and rate are updated with the self.owned setter.
        Should specify at least name, cost_base and rate_base to start. """

        self.name = name
        self.cost_base = cost_base
        self.rate_base = rate_base
        self.growth = growth
        self.lifetime_widgets = lifetime_widgets 
        self.widgets = widgets         
        self.owned = owned
        self.multiplier = (2**(self.owned // 25))
        self.rate = self.rate_base * self.owned * self.multiplier
        return None

    @property
    def widgets(self):
        return self._widgets
    
    @widgets.setter
    def widgets(self, quantity = 0):
        """ This .setter assumes that if self.widgets is being set, it's either incrementing 
        by a rate, or being reset to 0. self.lifetime widgets gets incremented as well, by self.rate.
        This does create the possibility that setting self.widgets to a non-zero value could 
        incorrectly increment lifetime_widgets. """
        if quantity > 0:
            self.lifetime_widgets += self.rate  
            self._widgets = quantity 
        elif quantity == 0:
            self._widgets = 0

        
    
    def reset(self, growth = 1.07, widgets = 0, owned = 0):
        """ Helper to reset appropriate values to start over."""
        self.growth = growth
        self.widgets = widgets
        self.owned = owned
        self.rate = 0
        self.multiplier = 1
        return None


    def bulk_cost(self, quantity = 1):
        """ Returns the cost of quantity items. Exponential growth on cost. """
        max(quantity,0)
        k = self.owned
        r = self.growth
        b = self.cost_base
        c = b * (((r ** k) * ((r ** quantity) -1)) / (r - 1))
        return c

    def max_buyable(self, amount = 0):
        """returns the maximum widgets which can be bought with amount. 
        (usually some total of widgets available)"""
        maxb = 0
        if amount and self.cost_base > 0:
            c = amount
            k = self.owned
            r = self.growth
            b = self.cost_base
            try: 
                maxb = math.floor(math.log(((c * (r - 1)) / (b * (r ** k))) + 1 ,r))
            except:
                return 0
        return maxb
        
        
    @property
    def owned(self):
        return self._owned

    @owned.setter
    def owned(self,x):
        """ sets the self.owned property and updates self.multipler and self.rate. 
        self.multiplier doubles for every 25 owned."""
        if x <= 0:
            self._owned = 0
        else:
            self._owned = x
            self.multiplier = (2**(self.owned // 25)) 
            self.rate = self.rate_base * self.owned * self.multiplier
        return None
    	
    def __str__(self):
        return f'Name: {self.name},\n  - growth:{self.growth},\n' \
               f'  - owned:{self.owned},\n' \
               f'  - multiplier:{self.multiplier},\n  - rate:{self.rate},\n' \
               f'  - widgets:{self.widgets}\n' \
               f'  - l/t widgets:{self.lifetime_widgets},\n  - cost base:{self.cost_base},\n' \
               f'  - rate base:{self.rate_base}'
    def __repr__(self):
        return f'Generator(name = {self.name}, cost_base = {self.cost_base}, rate_base = {self.rate_base}, ' \
               f'growth = {self.growth}, widgets = {self.widgets}, ' \
               f'lifetime_widgets = {self.lifetime_widgets}, owned = {self.owned})'

    
# ################################
# Balancing with these numbers:
#  - cost_growth: The factor by which each level of item is more expensive than the previous item
#  - rate_growth: the factor by which each rate of production is greater than the previous items's rate
#  - cost_base: the cost of the least expensive item
#  - rate_base: the production rate of starting item
#  
# add new items by simply expanding this list.
items = ['Click', 'Pencil', 
         'Pen', 'Tape', 
         'Stapler', 'Ruler', 
         'Square', 'Divider', 
         'Knife', 'Slide Rule', 
         'Hammer', 'Screwdriver', 
         'Caliper', 'Clamp',
         'Drill', 'Nailgun',
         'Grinder', 'Drill Press' ]
cost_growth = 18.2
cost_base = 11.8
rate_growth = 4.88
rate_base = 3.57
costs = [ (cost_base * (cost_growth ** x) ) for x in range( len(items) ) ]
costs.insert(0,0)
rates = [ (rate_base * (rate_growth ** x) ) for x in range( len(items) ) ]
rates.insert(0,0)
# mapping some tkinter color codes
color = {'nearblack': 'grey2', 
         'deepgrey': 'grey15', 
         'deepblue': 'grey20',
         'brightgreen': 'green2',
         'mainbg': 'grey2',
         'buybuttonbg':'grey15',
         'resetbuttonbg': 'grey15',
         'labelbg': 'grey2',
         'defaultbg': 'grey2',
         'labeltext': 'white',
         'buybuttontext':'white',
         'resetbuttontext': 'orange',
         'statusbg': 'grey15',
         'default': 'grey15'
         }

################################

class Total():
    
    def __init__(self):
        self.widgets = 0
        self.rate = 0
        self.idle_widgets = 0
        self.prestige = 1
        self.spent = 0
        self.ltwidgets = 0
        return None

class Clicker(tk.Frame):
    """ Tkinter app frame to display the clicker game. """
    
    # TODO: Achievements
    # when rate = 1,000,000
    # clicks = 100, 250, 500, 1000
    # each item = 100, 250, 500
    # pencil, tape and square = 20, "basics"
    # etc
    #       
    #producers = dict(zip(items,tuple(zip(costs,rates,itertools.repeat(0)))))
    #items = list(producers.keys())
    



    def __init__(self, master=None):
        
        super().__init__(master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.total = Total()
        self.buy_quantity_selection = []   #will be a list of tk.Radiobuttons later
        self.buy_quantity = tk.IntVar(value = 1)
        self.status_label = tk.StringVar(value = '')
        #self.generators = []

        if not self.load_save():
            self.generators = [Generator(name = item, cost_base = cb, rate_base = rb, growth = gr) \
                              for item, cb, rb, gr in zip(items, costs, rates,  \
                              itertools.repeat(random.choice([1.07, 1.075, 1.08, 1.085, 1.09]))) ]

        #if not self.load_save():
        #    for item, rb, cb in zip(items, rates, costs):
        #        gr = random.choice([1.07, 1.075, 1.08, 1.085, 1.09])
        #        self.generators.append(Generator(name = item, cost_base = cb, rate_base = rb, growth = gr))
    
        self.create_widgets()

    
    def new_prestige(self):
        tl = self.total.ltwidgets
        if tl <= 1000:
            return 1
        try:
            xx = max(150 * (math.sqrt(tl / 1.0E+14)),1.0)
        except:
            return max(self.total.prestige,1)
        return round(xx,2) 
          
    def on_closing(self):
        if tk.messagebox.askokcancel("Quit", "      Do you really want to quit?\n  ( Your progress will be saved and \nwidgets will be made in your absence.)"):
            self.status.after_cancel(self.updateid)
            self.save_progress()
            self.master.destroy()

    def update_totals(self):
        tw = 0
        for g in self.generators:
            g.widgets += g.rate * self.total.prestige
            tw += g.rate * self.total.prestige

        self.total.rate = int(tw) 
        self.total.widgets += int(tw)
        self.total.ltwidgets += int(tw)        
        return None
        
    def get_status_text(self):
        tw = self.total.widgets
        tr = self.total.rate

        return f" Widgets:  {int(tw):>17,.8g}\n" \
               f" Rate: {round(tr,2):>26,.8g} /s"

    def update(self):
        self.update_totals()
        self.status_label.set(self.get_status_text())
        self.update_buy_buttons()
        self.reset_text.set(self.get_reset_button_text())

        # Let's reschedule an update in >= 1 second. No, it's not recursive. 
        self.updateid = self.status.after(1000, self.update)

    def make_buybuttons(self,parent):
        self.buy_button = []
        defaultfont = tk.font.Font(family = 'Candara', size = '10',weight = 'bold')

        for i, x in enumerate(self.generators):
            numitems = len(self.generators)
            col = i // (numitems // 2)
            row = i + 2 if i < (numitems // 2) else (i - (numitems // 2)) + 2
            # c = x.bulk_cost()
            # exp = x.growth
            self.buy_button.append(tk.Button(parent, 
                                             text = "",
                                             fg = color['buybuttontext'], 
                                             bg = color['deepblue'],
                                             font = defaultfont, 
                                             width = 32, 
                                             height = 2,
                                             pady = 5, 
                                             command = lambda y = x: self.buy(item = y, quantity = self.buy_quantity.get())))
            self.update_buy_buttons()
            self.buy_button[i].grid(column = col * 4,
                                    row = row,
                                    columnspan = 4,
                                    )
    def update_buy_buttons(self, value = 0):

        if value == 0:
            value = self.buy_quantity.get()
        for b, g in zip(self.buy_button,self.generators):
            exp = g.growth
            x = g.name
            m = g.max_buyable(self.total.widgets)

            # We want to show the cost (c) of the number of items (value) the
            # user has selected to buy. If user has selected max (value == 1000),
            # and the max buyable (m) is 0, we should display the cost of 1 item.
            c = round(g.bulk_cost(value if value != 1000 else (m if m > 0 else 1)),0) 
            if g == self.generators[0]:
                b["text"] = f"+{g.name}\n({g.owned})"
            else:
                b["text"] = f"+{x} ({c:,.6G}) (^{exp})\n({g.owned}, +{round(g.rate * self.total.prestige,2):,.6G}/s) (+{m})"
            
            if (m >= value or (value == 1000 and m >= 1) or g == self.generators[0]) and value:
                b["bg"] = 'darkgreen'
            else:
                b["bg"] = color['deepblue']
 

    def make_status_label(self,parent):
        labelfont = tk.font.Font(family = 'Candara', size = '14', weight = 'normal')

        self.status = tk.Label(parent, 
                               textvariable = self.status_label,
                               font = labelfont,
                               fg = color['labeltext'], 
                               width = 24, 
                               relief = tk.RIDGE,
                               justify = tk.LEFT, 
                               anchor = tk.W, 
                               height = 3,
                               padx = 4,
                               bg = color['statusbg']
                               )
        self.status.grid(column = 0,
                        row = 0,
                        columnspan = 4,
                        )
# !!!!  # initial call into the self.update() cycle
        self.status.after(1000, self.update)

    
    def make_quantity_buttons(self,parent):
        cols, rows = parent.grid_size()
        qframe = tk.Frame(parent, bg = color['deepgrey'])
        qframe.grid(in_ = parent, column = 0, row = 1, columnspan = cols)
        for i, x in enumerate([1, 10, 25, 100, 1000]):
            if x == 1000:
                txt = 'max'
                val = x
            else:
                txt = f'x{str(x)}'
                val = x

            self.buy_quantity_selection.append( tk.Radiobutton(qframe,
                                            text = txt,
                                            fg = color['brightgreen'],
                                            bg = color['deepgrey'],
                                            activebackground = 'green',
                                            activeforeground = color['nearblack'],
                                            variable = self.buy_quantity,
                                            value = val,
                                            height = 1,
                                            width = 4,
                                            selectcolor = color['deepgrey'],
                                            bd = 2,
                                            justify = tk.CENTER,
                                            disabledforeground = 'grey',
                                            command = lambda x = x: self.update_buy_buttons(val),
                                            ))
            self.buy_quantity_selection[i].grid(column = 0 + i,
                                            row = 1,
                                            )

    def get_reset_button_text(self):
        return f'Leverage Investment and Restart (x{self.new_prestige()})\nLifetime Widgets: {int(self.total.ltwidgets):,}'
    
    def make_reset_button(self, parent):
        self.reset_text = tk.StringVar(value = self.get_reset_button_text())
        cols, rows = parent.grid_size()
        self.reset = tk.Button(parent,
                               #text = 'Leverage Investment and Restart',
                               textvariable = self.reset_text,
                               fg = color['resetbuttontext'],
                               bg = color['resetbuttonbg'],
                               width = 40,
                               pady = 10,
                               command = self.reset,
                               )
        self.reset.grid(column = 0, row = 98, columnspan = cols)

    def reset(self):
    
        def do_reset(reset = False):
            if not reset:
                quityn.grid_forget()
                return -1
            
            # Let's cancel the next update, so we don't get interrupted
            self.status.after_cancel(self.updateid)
            for g in self.generators:
                g.reset(random.choice([1.07, 1.075, 1.08, 1.085, 1.09]))
                
            self.total.widgets = 0
            self.total.rate = 0
            self.total.prestige = self.new_prestige()
            app.master.title(f"PyClicker IDLE game. (x{self.total.prestige})")
            quityn.grid_forget()
            
            # back to work
            self.statusid = self.status.after(100,self.update)
            return None

        quityn = tk.LabelFrame(self.master,
                               text = f"Reset with new Bonus {self.new_prestige()}? Yes or No",
                               width = 200,
                               height = 80,
                               padx = 5,
                               pady = 5, 
                               bg = color['default'], 
                               fg = 'white')
        yesbtn = tk.Button(quityn, 
                           text = "Yes",
                           bg = color['deepblue'] ,
                           fg = "green",
                           width = 12, 
                           command = lambda : do_reset(reset = True),
                           )
        nobtn = tk.Button(quityn, 
                          text = "No",
                          width = 12,
                          bg = color['deepblue'],
                          fg = "red",
                          command = lambda : do_reset(reset = False),
                          )
        
        quityn.grid(column = 5, row = 0, columnspan = 4)
        yesbtn.grid(column = 0, row = 0)
        nobtn.grid(column = 1, row = 0)
        
        
    def idle_popup(self, parent):
    
        idlefont = tk.font.Font(family = 'Candara', size = 12, weight = 'bold')
        ##idle_top = tk.Toplevel(bg =color['deepgrey'], padx = 20, pady = 20)
        #idle_top.geometry('300x200+900+300')
        idle_top = tk.Frame(bg = color['deepgrey'], width = 20, height = 4)

        iframe = tk.LabelFrame(idle_top, 
                      text = "While You were Away",
                      width = 200,
                      height = 80,
                      padx = 5,
                      pady = 5,
                      bg = 'grey15',     
                      fg = 'lightgrey',
                      font = idlefont)
        iframe.grid(column = 0, row = 0)
        tk.Label(iframe, text = f'{int(self.total.idle_widgets):,} widgets created!',
                 font = idlefont,
                 bg = 'lightyellow', 
                 fg = 'black',
                 padx = 10,
                 pady = 10).grid()
        idle_top.grid(column = 5, row = 0, columnspan = 4)
        idle_top.after(5000, lambda : idle_top.destroy())
        #idle_top.lift(aboveThis = self.master)
        

    def create_widgets(self):
        """We create the individual widgets here."""
        top = self.winfo_toplevel()
        top.config(bg = color['deepgrey'], padx = 20, pady = 20)
        self.make_status_label(top)
        #self.make_quit_button(top)
        self.make_buybuttons(top)
        self.make_quantity_buttons(top)
        self.make_reset_button(top)
        if self.total.idle_widgets:
            self.idle_popup(top)

        
    def buy(self, item , quantity = 1):
        
        g = item   #self.generators[items.index(item)]
        tw = self.total.widgets
        
        if quantity == 1000 and g != self.generators[0]:
            quantity = g.max_buyable(self.total.widgets)
        elif g == self.generators[0]:
            quantity = 1
        bulk = g.bulk_cost(quantity)
        
        if g == self.generators[0]:
            g.owned += quantity
            self.total.widgets += quantity
            self.total.ltwidgets += quantity
        elif (bulk <= tw and tw > 0):
            g.owned += quantity
            self.total.widgets -= bulk
            self.total.spent += bulk
        self.update_buy_buttons()
        self.status_label.set(self.get_status_text())



    
    def save_progress(self, overwrite = True):
        savefile = 'clickersave.pkl'
        with open(savefile,'wb') as f:
            pickle.dump(self.generators,f)
            pickle.dump((self.total),f)
            pickle.dump(time.time(), f)
        f.close()
    
    def load_save(self):
        try:
            with open(savefile,'rb') as f:
                self.generators = pickle.load(f)
                self.total = pickle.load(f)
                savetime = pickle.load(f)
        except:
            #print("Ooops no save found")
            return False

        self.total.idle_widgets = round( (time.time() - savetime) * self.total.rate,2)
        self.total.ltwidgets += self.total.idle_widgets
        self.total.widgets += self.total.idle_widgets
        return True



root = tk.Tk()
app = Clicker(master=root)
app.master.title(f"PyClicker IDLE game. (x{app.total.prestige})")
app.mainloop()
