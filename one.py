import random

l=["rock","paper","scissor"]

while True:
  userchoice=int(input('''do you want to play geme?
    1 yes
    2 no '''))
    
  if userchoice==1:
        upoint = 0
        cpoint = 0
        
        for a in range (1,6) :
            userinput=input('''
                         1 rock 
                         2 paper 
                         3 scissor''')
            if  userinput== "1":
                uchoice="rock"
            elif userinput=="2":
               uchoice="paper"
            elif userinput=="3":
               uchoice="scissor"
            else:
                print("Invalid choice! Please enter 1, 2, or 3")
                continue        

            cinput=random.choice(l)
            print(uchoice)
            print(cinput)

            if uchoice==cinput:
                print("your choice:",uchoice)
                print("compter choice:",cinput)
                print("draw")
                upoint+=1
                cpoint+=1
            elif (uchoice=="rock" and  cinput=="scissor") or (uchoice=="paper" and cinput=="rock") or (uchoice=="scissor"and cinput=="paper"):
                print("your choice:",uchoice)
                print("compter choice:",cinput)
                print("you won")
                upoint+=1
            elif  (cinput=="rock" and  uchoice=="scissor") or (cinput=="paper" and uchoice=="rock") or (cinput=="scissor"and uchoice=="paper"):
                print("your choice:",uchoice)
                print("compter choice:",cinput)
                print("computer won")
                cpoint+=1

            if cpoint>upoint :
                print("computer win")
            elif cpoint<upoint :
                print("you won")
            else:
                print("match draw")            
                break
            
            print(f"Final Score - You: {upoint}, Computer: {cpoint}")
  else:
        print("Thanks for playing!")
        break