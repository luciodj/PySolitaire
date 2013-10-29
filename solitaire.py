#
# Solitaire
#

import GameView as view
import Model as model
import pygame, sys

#
# Controller
#


Log = []


def animate( dlist, dXY, slist, index, sXY):
    global Adest, Log

    # program animation
    dx, dy = dXY     # get the tip dest coordinates
    sx, sy = sXY     # get source coordinates
    Adest = dlist    # list to append to after animation

    # remove card/tail from source list
    if index == -1:     # single card (tip)
        card = slist.pop()
        # log the move
        Log.append( ( dlist, -1, dXY, slist, sXY))

    else:
        card = slist[ index:]
        Log.append( ( dlist, len( dlist), dXY, slist, sXY))
        while len(slist) > index:
            slist.pop()


    # final point
    Asteps.append( ( card, 0, 0)) # only one step, final
    # 3/4 point
    Asteps.append( ( card, sx+3*(dx-sx)/4, sy+3*(dy-sy)/4))
    # half point
    Asteps.append( ( card, sx+2*(dx-sx)/4, sy+2*(dy-sy)/4))
    # 1/4 point
    Asteps.append( ( card, sx+1*(dx-sx)/4, sy+1*(dy-sy)/4))


def undo():
    global Log
    if Log:
        # animate the reverse of the last move
        dlist, index, dXY, slist, sXY = Log.pop()
        animate( slist, sXY, dlist, index, dXY)
        Log.pop()   # avoid logging the undo action

        # todo
        # 1. unhide
        # 2. refill stack detection

        pass




if __name__ == "__main__":
    Auto = False
    Victory = False

    # init graphics environment
    view.init()

    # intialize the model
    model.init()

    # deal the cards (ramdom)
    model.shuffle()
    model.deal()

    #update display
    view.display()

    # count the steps
    model.countSteps = 0

    Asteps = []      # list of pre-computed steps for animation
    Adest = None     # target list for card at the end of animation

    # main loop
    while( True):
        touch = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONUP:
                touch = view.checkTouch ( pygame.mouse.get_pos())

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    touch = ("basket", 0, (view.basket_x, view.basket_y))

                elif event.key == pygame.K_SPACE:
                    touch = ("stack", 0, (view.stack_x, view.stack_y))


        # check if animation pending
        if Asteps:
            step = Asteps.pop()
            if Asteps:
                # update the view and then add the card in motion
                view.display()
                # check if passed a tail (list of cards)
                if isinstance( step[0], list):
                    x, y = step[1], step[2]
                    for card in step[0]:
                        if card == step[0][-1]: # last in the tail
                            view.printFullCard( card, x, y)
                        else:
                            view.printTopCard( card, x, y)
                        y += view.cardtop_h

                else:   #single card
                    view.printFullCard( *step)

            else:   # end of animation append/extend
                # place card in final position then update view
                if isinstance( step[0], list):
                    Adest.extend( step[0])
                else: # single card append
                    Adest.append( step[0])
                # only now update the view
                view.display()
                # and record the move done
                model.countSteps += 1


        # victory?
        elif Victory:
            choice = view.selectBox(["Victory", "Start a new Game", "Quit"])
            if choice == 0:
                Victory = False
                Auto = False
                model.init()
                model.shuffle()
                model.deal()
                model.countSteps = 0
                Log=[]
                view.display()
            else:
                sys.exit()

        # auto mode activated
        elif Auto:
            # try to use the last card in the basket
            if model.basket:
                card = model.getBasketTip()
                # try to move the card automatically to the first matching row
                top = model.matchTop( card)
                if top >= 0:
                    animate( model.tops[ top],      # dest list
                             view.topXY[ top],      # dest coord
                             model.basket,-1,       # source list
                             (view.basket_x, view.basket_y))  # source coords
                    Victory = model.checkFinished()
                    # update display
                    view.display()
                    continue

            # try with one of the tips
            for i in xrange( 7):
                if model.rows[ i]:
                    card = model.getTip( i)
                    # check if it can go to the top
                    top = model.matchTop( card)
                    if top >= 0:
                        animate( model.tops[ top],          # dest list
                                 view.topXY[ top],          # dest coord
                                 model.rows[ i], -1,        # source list
                                 view.tipXY[ i])            # source coords
                        Victory = model.checkFinished()
                        # update display
                        view.display()
                        break



        # else respond to last user input
        elif touch:

            if touch[0] == "stack":
                card = model.getStackTip()
                # if stack is empty
                if not card:
                    model.refillStack()
                else:   # get the top card out on the basket
                    #model.dropInBasket( st)
                    animate( model.basket,                  # dest list
                             (view.basket_x, view.basket_y),# dest coord
                             model.stack, -1,               # source list
                             touch[2])                      # source coord

            elif touch[0] == "tip":
                card = model.getTip( touch[1])

                # check if it can go to the top
                top = model.matchTop( card)
                if top >= 0:
                    animate( model.tops[ top],          # dest list
                             view.topXY[ top],          # dest coord
                             model.rows[ touch[ 1]], -1,# source list
                             touch[2])                  # source coords
                    model.checkHidden( touch[ 1])

                # or to another row
                else:
                    row = model.matchRow( card)
                    if row >= 0:
                        animate( model.rows[ row],      # dest list
                                 view.tipXY[ row],      # dest coord
                                 model.rows[ touch[ 1]],# source list
                                 -1,
                                 touch[2])              # source coords
                        model.checkHidden( touch[ 1])


            elif touch[0] == "tail":
                row = touch[1]/16
                index = touch[1]%16
                card = model.rows[ row][index]
                drow = model.matchRow( card)
                if drow >= 0:
                    animate( model.rows[ drow],         # dest list
                             view.tipXY[ drow],         # dest coord
                             model.rows[ row],          # source list
                             index,
                             touch[2])                  # source coord
                    model.checkHidden( row)


            elif touch[0] == "top":
                card = model.getTop( touch[1])
                row = model.matchRow( card)
                if row >= 0:
                    animate( model.rows[ row],          # dest list
                             view.tipXY[ row],          # dest coord
                             model.tops[ touch[ 1]],-1, # source list
                             touch[2])                  # source coords

            elif touch[0] == "basket":
                card =  model.getBasketTip()
                # try to move the card automatically to a top
                top = model.matchTop( card)
                if top >= 0:
                    animate( model.tops[ top], # dest list
                             view.topXY[ top], # dest coord
                             model.basket,-1,  # source list
                             touch[2])         # source coords

                else: # move to a tip
                    row = model.matchRow( card)
                    if row >= 0:
                        animate( model.rows[ row], # destination list
                                 view.tipXY[ row], # dest coordinates
                                 model.basket,-1,  # source list
                                 touch[2])         # source coordinates

            elif touch[0] == "button":
                if   touch[ 1] == 0:  # undo
                    undo()

                elif touch[ 1] == 1:  # restart
                    model.restart()
                    model.countSteps = 0
                    Log=[]

                elif touch[ 1] == 2:  # re-shuffle and deal a new one
                    model.init()
                    model.shuffle()
                    model.deal()
                    model.countSteps = 0
                    Log=[]


            # update display
            view.display()
            # check if auto can be activated
            if not Auto:
                Auto = ( model.countHidden() < 1)


        # refresh
        view.wait( 20)

