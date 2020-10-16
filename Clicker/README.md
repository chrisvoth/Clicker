Clicker.py

My take on the clicker type game which generates 'widgets' from clicks, or 
automated parts. The multipliers are slightly randomly variant at each new 
game and game resets. This makes some games harder or easier due to the 
variation.

The window title also shows the prestige multiplier. (Starts at 0, grows when
you restart the game based on widgets created)

There is a quantity to purchase selection above the item buttons. You can
choose from:  x1 x10 x25 x100 or max

The button display is a bit crowded. Here's the breakdown:

+Pencil(5.012223E+10)(^1.085)
 (554, +2,88765E+9/s)(+12)

+ITEM(cost per item based on quantity selected)(growth multiplier)
 (current quantity owned)(rate of widget clicks)(quantity you can buy now)

A savefile is created in the current folder to maintain progress.

-------------------------------------------------------------------------------
Based loosely on info from:
https://blog.kongregate.com/the-math-of-idle-games-part-i/
