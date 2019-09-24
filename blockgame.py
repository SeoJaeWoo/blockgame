# -*- coding: cp949 -*-
# �ѱ��� ����ϱ� ���ؼ��� ������ ���� coding �κ��� �ֻ����� �����ؾ� �Ѵ�.

import random, time, pygame, sys, copy
from pygame.locals import *

FPS = 10 # ȭ���� ��ȯ�ϴ� �ʴ� ������ �� ����
WINDOWWIDTH = 600  # ���� â�� ���� ����
WINDOWHEIGHT = 600 # ���� â�� ���� ����

BOARDWIDTH = 12 # �������� ���� ��
BOARDHEIGHT = 13 # ���� ���� ���� ��
BLOCKSIZE = 32 # ���� ũ��(���簢��)

NBLOCKIMAGES = 9    # ���� ��ü ����
assert NBLOCKIMAGES >= 5
NITEMIMAGES = 3     # ������ ���� ����

COMBORATE = 1.5     #�޺� ���� ����

PURPLE    = (255, 100, 255)
LIGHTBLUE = (170, 190, 255)
BLUE      = (  0,   0, 255)
RED       = (255,   0,   0)
BLACK     = (  0,   0,   0)
BROWN     = ( 85,  65,   0)
WHITE     = (255, 255, 255)

BGCOLOR = BLACK
GAMEOVERCOLOR = RED # ���� ���� �۾��� ����
SCORECOLOR = PURPLE # ���� �۾��� ����


XMARGIN = int((WINDOWWIDTH - BLOCKSIZE * BOARDWIDTH) / 2)
YMARGIN = int((WINDOWHEIGHT - BLOCKSIZE * BOARDHEIGHT) / 2)

EMPTY_SPACE = -1    # ������� ���ڸ� ����

def main():
    global FPSCLOCK, DISPLAYSURF, BLOCKIMAGES, BOARDRECTS, LINERECTS, SOUNDS

    # ���� �ʱ�ȭ
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('BLOCK')

    BLOCKIMAGES = []
    for i in range(1, NBLOCKIMAGES+1):
        # �̹����� �ҷ��� ����Ʈ�� �����ϴ� �κ�
        blkImage = pygame.image.load('images/b%s.png' % i)
        if blkImage.get_size() != (BLOCKSIZE, BLOCKSIZE):
            blkImage = pygame.transform.smoothscale(blkImage, (BLOCKSIZE, BLOCKSIZE))
        BLOCKIMAGES.append(blkImage)
        
    # �Ҹ��� �ҷ��� ����Ʈ�� �����ϴ� �κ�
    SOUNDS = [pygame.mixer.Sound('sounds/click.wav'),pygame.mixer.Sound('sounds/combo.wav')]

    # ������ ������ ��ġ�� ���� rect ��ü ����
    BOARDRECTS = []
    for x in range(BOARDWIDTH):
        BOARDRECTS.append([])
        for y in range(BOARDHEIGHT):
            r = pygame.Rect((XMARGIN + (x * BLOCKSIZE),
                             YMARGIN + (y * BLOCKSIZE),
                             BLOCKSIZE,
                             BLOCKSIZE))
            BOARDRECTS[x].append(r)

    # ������ ������ ��ġ�� ���� rect ��ü ����
    LINERECTS = []
    for x in range(BOARDWIDTH):
        b = pygame.Rect((XMARGIN + (x * BLOCKSIZE),
                         YMARGIN + (BOARDHEIGHT * BLOCKSIZE + BLOCKSIZE / 2),
                         BLOCKSIZE,
                         BLOCKSIZE))
        LINERECTS.append(b)

    while True:
        showStartScreen()
        DISPLAYSURF.fill(BGCOLOR)   # ȭ���� �������� ä���.
        runGame()
        gameOverScreen()
        DISPLAYSURF.fill(BGCOLOR)

def showStartScreen():
    titleFont = pygame.font.Font('fonts/Wedgie Regular.ttf',50)
    titleSurf = titleFont.render('Block game',True,BLUE)
    titleRect = titleSurf.get_rect()
    titleRect.center = (WINDOWWIDTH/2,WINDOWHEIGHT/3)
    DISPLAYSURF.blit(titleSurf,titleRect)
    a = 1
    color = [(200,200,200),(50,50,50)]
    pressKeyFont = pygame.font.Font('freesansbold.ttf',20)
    pressKeySurf = pressKeyFont.render('press any key to start',True,color[a])
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.center = (WINDOWWIDTH/2,WINDOWHEIGHT*2/3)
    while True:
        # Ű�� �Է��� ������ ��� ������ ����..
        for event in pygame.event.get(): # �̺�Ʈ �ڵ鸵 ����
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                # �ݱ⸦ �����ų� esc�� ������ ������ ����ȴ�.
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                return
            
        # ����ȭ���� ��¦�̴� �� �κ�
        if a == 1:
            a = 0
        else:
            a = 1
        pressKeySurf = pressKeyFont.render('press any key to start',True,color[a])
        pygame.draw.rect(DISPLAYSURF,BGCOLOR,pressKeyRect)
        DISPLAYSURF.blit(pressKeySurf,pressKeyRect)
        pygame.display.update()
        FPSCLOCK.tick(FPS*3)
        

    
def runGame():
    gameBoard = initBoard()
    score = 0
    nextLine = createLine(gameBoard,score)
    nextLine = upNext(gameBoard,nextLine,score)
    lastMouseDownX = None
    lastMouseDownY = None
    gameIsOver = False
    
    while True: # ���� ���� ����
        clickedSpace = None

        drawScore(score)
        drawBoard(gameBoard,nextLine)
        pygame.display.update()
        FPSCLOCK.tick(FPS/2)

        matchedBlocks = findMatchingBlocks(gameBoard)
        
        combo = COMBORATE
        while matchedBlocks != []:

            for blockSet in matchedBlocks:
                for block in blockSet:
                    gameBoard[block[0]][block[1]] = EMPTY_SPACE
                    score+=int(10*combo)

            SOUNDS[1].play()

            
            displayReset(gameBoard,nextLine,score)
            FPSCLOCK.tick(FPS/2)
            pullDownAllBlocks(gameBoard)

            displayReset(gameBoard,nextLine,score)
            FPSCLOCK.tick(FPS/2)
            
            matchedBlocks = findMatchingBlocks(gameBoard)
            combo += COMBORATE
        
        for i in range(BOARDWIDTH):
            # ���� �������� ���� ���� �������� �ö� ��� ������ �����Ѵ�.
            if gameBoard[i][0] != EMPTY_SPACE:
                return
        
        while clickedSpace == None: # Ŭ���� ���� ���� ������ ������ ����.
            for event in pygame.event.get(): # �̺�Ʈ �ڵ鸵 ����
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                
                elif event.type == MOUSEBUTTONUP:
                    if event.pos == (lastMouseDownX, lastMouseDownY):
                    # Ŭ������ ���� ����(������ ���� ��)
                        clickedSpace = checkClick(gameBoard,event.pos)
                    
                elif event.type == MOUSEBUTTONDOWN:
                    # Ŭ���ϱ� ������ ���� ����
                    lastMouseDownX, lastMouseDownY = event.pos
                    SOUNDS[0].play()


        blockNumber = gameBoard[clickedSpace[0]][clickedSpace[1]]
        if blockNumber < NITEMIMAGES:
            # Ŭ���� ���� ������ ���� ���
            deleting_blocks = useItem(gameBoard,nextLine,blockNumber,clickedSpace)
        else:
            deleting_blocks = findSameBlocks(gameBoard,clickedSpace)

        for a in deleting_blocks:
            # ������ ������ ���� �Ŀ� �� ���� 10���� �ش�.
            gameBoard[a[0]][a[1]] = EMPTY_SPACE
            score+=10
            
        FPSCLOCK.tick(FPS)
        
        displayReset(gameBoard,nextLine,score)
        
        pullDownAllBlocks(gameBoard)
        FPSCLOCK.tick(FPS)
        
        displayReset(gameBoard,nextLine,score)

        
        FPSCLOCK.tick(FPS/2)
        
        matchedBlocks = findMatchingBlocks(gameBoard)
        # 3�� �̻� �´� ���� ��ġ�� ������ ������ ����Ʈ�� ���Ѵ�.
        
        combo = COMBORATE
        while matchedBlocks != []:

            for blockSet in matchedBlocks:
                for block in blockSet:
                    gameBoard[block[0]][block[1]] = EMPTY_SPACE
                    score+=int(10*combo)
                    # ���� ���� ����Ʈ�� �ִ� ������ ��� �� �������� �����.
            
            SOUNDS[1].play()
            displayReset(gameBoard,nextLine,score)

            
            FPSCLOCK.tick(FPS/2)
            pullDownAllBlocks(gameBoard)
            
            displayReset(gameBoard,nextLine,score)
            FPSCLOCK.tick(FPS/2)
            
            matchedBlocks = findMatchingBlocks(gameBoard)
            combo += COMBORATE  # ������ �������� �޺��� ������ �ö󰣴�.
            
        FPSCLOCK.tick(FPS)
        
        nextLine = upNext(gameBoard,nextLine,score)
        
        DISPLAYSURF.fill(BGCOLOR)

def useItem(board,line,num,space):
    removeSet = set()   #�� ������ ������� ���� ���� ��ġ�� �ʰ� �ϱ� ���� ������ ����Ѵ�.
    brdtmp = copy.deepcopy(board)
    x,y = space

    #��ź ������
    if num == 0:
        for a in range(x-1,x+2):    # �ֺ��� 3*3�� ������ ��� �����Ѵ�.
            for b in range(y-1,y+2):
                if getBlock(brdtmp,a,b) != None and getBlock(brdtmp,a,b) != EMPTY_SPACE:
                    removeSet.add((a,b))
                    if brdtmp[a][b] < NITEMIMAGES and space != (a,b):
                        # ���ŵǴ� �� �߿� ������ ���� �� ���� �ÿ� ����Լ��� ������ ���� �����Ų��.
                        
                        brdtmp[x][y] = NITEMIMAGES  # �̹� ���� ������ ������ ���� ������ �Ϲ� ������ �ٲ۴�.
                        
                        removeSet = removeSet | useItem(brdtmp,line,brdtmp[a][b],(a,b)) # �������� ���� ������ ���� �������Ѵ�.

    #���� ������
    elif num == 1:
        for a in range(BOARDWIDTH): # ���� ���� ��ġ�� �ִ� ������ ��� �����Ѵ�.
            if getBlock(brdtmp,a,y) != EMPTY_SPACE:
                removeSet.add((a,y))
                if brdtmp[a][y] < NITEMIMAGES and space != (a,y):
                    brdtmp[x][y] = NITEMIMAGES
                    removeSet = removeSet | useItem(brdtmp,line,brdtmp[a][y],(a,y))

    #sero
    elif num == 2:
        for a in range(BOARDHEIGHT):    # ���� ���� ��ġ�� �ִ� ������ ��� �����Ѵ�.
            if getBlock(brdtmp,x,a) != EMPTY_SPACE:
                removeSet.add((x,a))
                if brdtmp[x][a] < NITEMIMAGES and space != (x,a):
                    brdtmp[x][y] = NITEMIMAGES
                    removeSet = removeSet | useItem(brdtmp,line,brdtmp[x][a],(x,a))

    return removeSet
        
def displayReset(board, line, score):
    # ����� ���ھ �ٽ� �׸��� �Լ�
    DISPLAYSURF.fill(BGCOLOR)
    drawScore(score)
    drawBoard(board, line)
    pygame.display.update()
 
def gameOverScreen():
    #���� ���� ȭ��
    gameOverFont = pygame.font.Font('freesansbold.ttf',70)
    gameOverSurf = gameOverFont.render('GAME OVER',True,RED)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (WINDOWWIDTH/2,WINDOWHEIGHT/2)
    DISPLAYSURF.blit(gameOverSurf,gameOverRect)
    pygame.display.update()
    while True:
        for event in pygame.event.get(): # �̺�Ʈ �ڵ鸵 ����
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                return
            
def drawScore(score):
    scoreImg = pygame.font.Font('fonts/Open 24 Display St.ttf', 25).render("score : %s" % score, 1, SCORECOLOR)
    scoreRect = scoreImg.get_rect()
    scoreRect.bottomleft = (10, WINDOWHEIGHT - 6)
    DISPLAYSURF.blit(scoreImg, scoreRect)



def initBoard():
    # �������� ��������� �ʱ�ȭ�ϴ� �Լ�
    board = []
    for x in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)
    return board

def createLine(board,score):
    # ���ο� ������ ����� �Լ�
    line = []
    n = NITEMIMAGES
    m = NBLOCKIMAGES - 1
    itemCount = 0

    if countItem(board) < 3 and score > 300 :
        # ������ 300�� �̻��̰�, �����ǿ� ������ ���� 3�� �̸����� ���� ��� ������ ���� �������� �����Ѵ�.
        n = 0
        
    if score < 1000:
        # 1000�� �̸��� ��쿡�� ���� ������ 2�� ���δ�.
        m = NBLOCKIMAGES - 3
        
    elif score < 1500:
        # 1000�� �̻� 1500�� �̸��� ��쿡�� ���� ������ 1�� ���δ�.
        m = NBLOCKIMAGES - 2
    
    for i in range(BOARDWIDTH):
        a = random.randint(n,m)
        if itemCount > 1:
            
            # �������� ������ �� �߿� ������ ���� 2�� �̻� ���� ��� �Ϲ� ������ �ٲ۴�.
            while a < NITEMIMAGES:
                a = random.randint(n,m)
        elif a < NITEMIMAGES:
            itemCount += 1
        elif i > 1 and line[i-2] == line[i-1] == a:
            
            # ���� ���� ���� �������� 3���� ���� ��� �ٸ� ������ ������ �ٲ۴�.
            while a == line[i-1]:
                a = random.randint(n,m)
        line.append(a)
    return line


def upNext(board,line,score):
    # �����ǿ� ���� ���� �ø��� �Լ�
    for x in range(BOARDWIDTH):
        board[x] = board[x][1:]
        board[x].append(line[x])
    return createLine(board,score)

def checkClick(board,pos):
    # Ŭ���� �κ��� Ȯ���ϴ� �Լ���, ���� ���� �κ��� �� ������ �ƴ� ��쿡�� ��ġ�� ���÷� ��ȯ�Ѵ�.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if BOARDRECTS[x][y].collidepoint(pos[0], pos[1]):
                if board[x][y] == EMPTY_SPACE:
                    return None
                return (x,y)
    return None

def getBlock(board, x, y):
    # �������� �ε����� ������ ����� �ʵ��� �ϱ����� �Լ�
    if x < 0 or y < 0 or x >= BOARDWIDTH or y >= BOARDHEIGHT:
        return None
    else:
        return board[x][y]

def countItem(board):
    # �������� ���� ���� Ȯ���ϴ� �Լ�
    n = 0
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] < NITEMIMAGES and board[x][y] != EMPTY_SPACE:
                n += 1
    return n

def findMatchingBlocks(board):
    blocksToRemove = []
    boardCopy = copy.deepcopy(board)

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            # ���η� �´� �� �˻�
            if getBlock(boardCopy,x,y) >= NITEMIMAGES and getBlock(boardCopy, x, y) == getBlock(boardCopy, x + 1, y) == getBlock(boardCopy, x + 2, y):
                targetBlock = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getBlock(boardCopy, x + offset, y) == targetBlock:
                    # 3�� �̻��� �̾��� ���� �ִ� �� �˻�
                    removeSet.append((x + offset, y))
                    offset += 1
                blocksToRemove.append(removeSet)

            # ���η� �´� �� �˻�
            if getBlock(boardCopy,x,y) >= NITEMIMAGES and getBlock(boardCopy, x, y) == getBlock(boardCopy, x, y + 1) == getBlock(boardCopy, x, y + 2) and getBlock(boardCopy, x, y) != EMPTY_SPACE:
                targetBlock = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getBlock(boardCopy, x, y + offset) == targetBlock:
                    # 3�� �̻��� �̾��� ���� �ִ� �� �˻�
                    removeSet.append((x, y + offset))
                    offset += 1
                blocksToRemove.append(removeSet)

    return blocksToRemove


def findSameBlocks(board,space):
    sameBlockList = []
    brdtmp = copy.deepcopy(board)
    x,y = space

    sameBlockList.append((x,y))
    for i in range(BOARDHEIGHT):
        if brdtmp[x][i] == brdtmp[x][y] and i != y:
            sameBlockList.append((x,i))

    for i in range(BOARDWIDTH):
        if brdtmp[i][y] == brdtmp[x][y] and i != x:
            sameBlockList.append((i,y))

    return sameBlockList

def drawBoard(board,line):

    # �����ǿ� �簢���� �׸���.
    pygame.draw.rect(DISPLAYSURF,BROWN,(XMARGIN, YMARGIN + BLOCKSIZE,
                                        WINDOWWIDTH - XMARGIN*2,
                                        WINDOWHEIGHT - YMARGIN*2 - BLOCKSIZE),3)

    # �����ǰ� ������ ���� ������ ��輱�� �׸���.
    pygame.draw.line(DISPLAYSURF,WHITE,(XMARGIN,WINDOWHEIGHT - YMARGIN + BLOCKSIZE/4),
                     (WINDOWWIDTH-XMARGIN,WINDOWHEIGHT - YMARGIN + BLOCKSIZE/4),3)
    
    # �������� �׸���.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            blockToDraw = board[x][y]
            if blockToDraw != EMPTY_SPACE:
                DISPLAYSURF.blit(BLOCKIMAGES[blockToDraw], BOARDRECTS[x][y])

    # ������ ���� ������ �׸���.
    for i in range(BOARDWIDTH):
        lineToDraw = line[i]
        if lineToDraw != EMPTY_SPACE:
            DISPLAYSURF.blit(BLOCKIMAGES[lineToDraw], LINERECTS[i])

def pullDownAllBlocks(board):
    # �ؿ� �� ���� ���� ���� ��� ������ ����
    for x in range(BOARDWIDTH):
        blocksInColumn = []
        for y in range(BOARDHEIGHT):
            if board[x][y] != EMPTY_SPACE:
                blocksInColumn.append(board[x][y])
        board[x] = ([EMPTY_SPACE] * (BOARDHEIGHT - len(blocksInColumn))) + blocksInColumn



if __name__ == "__main__":  # ������ ���� ���� �ÿ��� main�Լ� ����
    main()
