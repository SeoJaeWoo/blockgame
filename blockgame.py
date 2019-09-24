# -*- coding: cp949 -*-
# 한글을 사용하기 위해서는 다음과 같이 coding 부분을 최상위에 선언해야 한다.

import random, time, pygame, sys, copy
from pygame.locals import *

FPS = 10 # 화면을 전환하는 초당 프레임 수 설정
WINDOWWIDTH = 600  # 게임 창의 가로 길이
WINDOWHEIGHT = 600 # 게임 창의 세로 길이

BOARDWIDTH = 12 # 게임판의 가로 수
BOARDHEIGHT = 13 # 게임 판의 세로 수
BLOCKSIZE = 32 # 블럭의 크기(정사각형)

NBLOCKIMAGES = 9    # 블럭의 전체 개수
assert NBLOCKIMAGES >= 5
NITEMIMAGES = 3     # 아이템 블럭의 개수

COMBORATE = 1.5     #콤보 점수 비율

PURPLE    = (255, 100, 255)
LIGHTBLUE = (170, 190, 255)
BLUE      = (  0,   0, 255)
RED       = (255,   0,   0)
BLACK     = (  0,   0,   0)
BROWN     = ( 85,  65,   0)
WHITE     = (255, 255, 255)

BGCOLOR = BLACK
GAMEOVERCOLOR = RED # 게임 오버 글씨의 색상
SCORECOLOR = PURPLE # 점수 글씨의 색상


XMARGIN = int((WINDOWWIDTH - BLOCKSIZE * BOARDWIDTH) / 2)
YMARGIN = int((WINDOWHEIGHT - BLOCKSIZE * BOARDHEIGHT) / 2)

EMPTY_SPACE = -1    # 빈공간의 숫자를 정의

def main():
    global FPSCLOCK, DISPLAYSURF, BLOCKIMAGES, BOARDRECTS, LINERECTS, SOUNDS

    # 게임 초기화
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('BLOCK')

    BLOCKIMAGES = []
    for i in range(1, NBLOCKIMAGES+1):
        # 이미지를 불러와 리스트에 저장하는 부분
        blkImage = pygame.image.load('images/b%s.png' % i)
        if blkImage.get_size() != (BLOCKSIZE, BLOCKSIZE):
            blkImage = pygame.transform.smoothscale(blkImage, (BLOCKSIZE, BLOCKSIZE))
        BLOCKIMAGES.append(blkImage)
        
    # 소리를 불러와 리스트에 저장하는 부분
    SOUNDS = [pygame.mixer.Sound('sounds/click.wav'),pygame.mixer.Sound('sounds/combo.wav')]

    # 보드의 블럭들의 위치에 대한 rect 객체 생성
    BOARDRECTS = []
    for x in range(BOARDWIDTH):
        BOARDRECTS.append([])
        for y in range(BOARDHEIGHT):
            r = pygame.Rect((XMARGIN + (x * BLOCKSIZE),
                             YMARGIN + (y * BLOCKSIZE),
                             BLOCKSIZE,
                             BLOCKSIZE))
            BOARDRECTS[x].append(r)

    # 라인의 블럭들의 위치에 대한 rect 객체 생성
    LINERECTS = []
    for x in range(BOARDWIDTH):
        b = pygame.Rect((XMARGIN + (x * BLOCKSIZE),
                         YMARGIN + (BOARDHEIGHT * BLOCKSIZE + BLOCKSIZE / 2),
                         BLOCKSIZE,
                         BLOCKSIZE))
        LINERECTS.append(b)

    while True:
        showStartScreen()
        DISPLAYSURF.fill(BGCOLOR)   # 화면을 배경색으로 채운다.
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
        # 키를 입력할 때까지 계속 루프를 돈다..
        for event in pygame.event.get(): # 이벤트 핸들링 루프
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                # 닫기를 누르거나 esc를 누르면 게임이 종료된다.
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                return
            
        # 메인화면의 반짝이는 글 부분
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
    
    while True: # 메인 게임 루프
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
            # 만약 게임판의 블럭이 제일 꼭대기까지 올라갈 경우 게임을 종료한다.
            if gameBoard[i][0] != EMPTY_SPACE:
                return
        
        while clickedSpace == None: # 클릭한 곳이 블럭일 때까지 루프를 돈다.
            for event in pygame.event.get(): # 이벤트 핸들링 루프
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                
                elif event.type == MOUSEBUTTONUP:
                    if event.pos == (lastMouseDownX, lastMouseDownY):
                    # 클릭했을 때의 조건(눌렀다 뗐을 때)
                        clickedSpace = checkClick(gameBoard,event.pos)
                    
                elif event.type == MOUSEBUTTONDOWN:
                    # 클릭하기 시작할 때의 조건
                    lastMouseDownX, lastMouseDownY = event.pos
                    SOUNDS[0].play()


        blockNumber = gameBoard[clickedSpace[0]][clickedSpace[1]]
        if blockNumber < NITEMIMAGES:
            # 클릭한 블럭이 아이템 블럭일 경우
            deleting_blocks = useItem(gameBoard,nextLine,blockNumber,clickedSpace)
        else:
            deleting_blocks = findSameBlocks(gameBoard,clickedSpace)

        for a in deleting_blocks:
            # 제거할 블럭들을 제거 후에 각 블럭당 10점씩 준다.
            gameBoard[a[0]][a[1]] = EMPTY_SPACE
            score+=10
            
        FPSCLOCK.tick(FPS)
        
        displayReset(gameBoard,nextLine,score)
        
        pullDownAllBlocks(gameBoard)
        FPSCLOCK.tick(FPS)
        
        displayReset(gameBoard,nextLine,score)

        
        FPSCLOCK.tick(FPS/2)
        
        matchedBlocks = findMatchingBlocks(gameBoard)
        # 3개 이상 맞는 블럭의 위치를 저장한 투플의 리스트를 구한다.
        
        combo = COMBORATE
        while matchedBlocks != []:

            for blockSet in matchedBlocks:
                for block in blockSet:
                    gameBoard[block[0]][block[1]] = EMPTY_SPACE
                    score+=int(10*combo)
                    # 구한 블럭의 리스트에 있는 블럭들을 모두 빈 공간으로 만든다.
            
            SOUNDS[1].play()
            displayReset(gameBoard,nextLine,score)

            
            FPSCLOCK.tick(FPS/2)
            pullDownAllBlocks(gameBoard)
            
            displayReset(gameBoard,nextLine,score)
            FPSCLOCK.tick(FPS/2)
            
            matchedBlocks = findMatchingBlocks(gameBoard)
            combo += COMBORATE  # 여러번 터질수록 콤보의 비율이 올라간다.
            
        FPSCLOCK.tick(FPS)
        
        nextLine = upNext(gameBoard,nextLine,score)
        
        DISPLAYSURF.fill(BGCOLOR)

def useItem(board,line,num,space):
    removeSet = set()   #블럭 순서에 상관없이 같은 블럭이 겹치지 않게 하기 위해 집합을 사용한다.
    brdtmp = copy.deepcopy(board)
    x,y = space

    #폭탄 아이템
    if num == 0:
        for a in range(x-1,x+2):    # 주변의 3*3의 블럭들을 모두 제거한다.
            for b in range(y-1,y+2):
                if getBlock(brdtmp,a,b) != None and getBlock(brdtmp,a,b) != EMPTY_SPACE:
                    removeSet.add((a,b))
                    if brdtmp[a][b] < NITEMIMAGES and space != (a,b):
                        # 제거되는 블럭 중에 아이템 블럭이 더 있을 시에 재귀함수로 아이템 블럭을 실행시킨다.
                        
                        brdtmp[x][y] = NITEMIMAGES  # 이미 터진 현재의 아이템 블럭을 임의의 일반 블럭으로 바꾼다.
                        
                        removeSet = removeSet | useItem(brdtmp,line,brdtmp[a][b],(a,b)) # 연속으로 터진 아이템 블럭을 합집합한다.

    #가로 아이템
    elif num == 1:
        for a in range(BOARDWIDTH): # 같은 가로 위치에 있는 블럭들을 모두 제거한다.
            if getBlock(brdtmp,a,y) != EMPTY_SPACE:
                removeSet.add((a,y))
                if brdtmp[a][y] < NITEMIMAGES and space != (a,y):
                    brdtmp[x][y] = NITEMIMAGES
                    removeSet = removeSet | useItem(brdtmp,line,brdtmp[a][y],(a,y))

    #sero
    elif num == 2:
        for a in range(BOARDHEIGHT):    # 같은 세로 위치에 있는 블럭들을 모두 제거한다.
            if getBlock(brdtmp,x,a) != EMPTY_SPACE:
                removeSet.add((x,a))
                if brdtmp[x][a] < NITEMIMAGES and space != (x,a):
                    brdtmp[x][y] = NITEMIMAGES
                    removeSet = removeSet | useItem(brdtmp,line,brdtmp[x][a],(x,a))

    return removeSet
        
def displayReset(board, line, score):
    # 보드와 스코어를 다시 그리는 함수
    DISPLAYSURF.fill(BGCOLOR)
    drawScore(score)
    drawBoard(board, line)
    pygame.display.update()
 
def gameOverScreen():
    #게임 오버 화면
    gameOverFont = pygame.font.Font('freesansbold.ttf',70)
    gameOverSurf = gameOverFont.render('GAME OVER',True,RED)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (WINDOWWIDTH/2,WINDOWHEIGHT/2)
    DISPLAYSURF.blit(gameOverSurf,gameOverRect)
    pygame.display.update()
    while True:
        for event in pygame.event.get(): # 이벤트 핸들링 루프
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
    # 게임판을 빈공간으로 초기화하는 함수
    board = []
    for x in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)
    return board

def createLine(board,score):
    # 새로운 라인을 만드는 함수
    line = []
    n = NITEMIMAGES
    m = NBLOCKIMAGES - 1
    itemCount = 0

    if countItem(board) < 3 and score > 300 :
        # 점수가 300점 이상이고, 게임판에 아이템 블럭이 3개 미만으로 있을 경우 아이템 블럭도 랜덤으로 생성한다.
        n = 0
        
    if score < 1000:
        # 1000점 미만일 경우에는 블럭의 개수를 2개 줄인다.
        m = NBLOCKIMAGES - 3
        
    elif score < 1500:
        # 1000점 이상 1500점 미만의 경우에는 블럭의 개수를 1개 줄인다.
        m = NBLOCKIMAGES - 2
    
    for i in range(BOARDWIDTH):
        a = random.randint(n,m)
        if itemCount > 1:
            
            # 랜덤으로 생성한 블럭 중에 아이템 블럭이 2개 이상 있을 경우 일반 블럭으로 바꾼다.
            while a < NITEMIMAGES:
                a = random.randint(n,m)
        elif a < NITEMIMAGES:
            itemCount += 1
        elif i > 1 and line[i-2] == line[i-1] == a:
            
            # 같은 색의 블럭이 연속으로 3개가 나올 경우 다른 색상의 블럭으로 바꾼다.
            while a == line[i-1]:
                a = random.randint(n,m)
        line.append(a)
    return line


def upNext(board,line,score):
    # 게임판에 블럭을 한줄 늘리는 함수
    for x in range(BOARDWIDTH):
        board[x] = board[x][1:]
        board[x].append(line[x])
    return createLine(board,score)

def checkClick(board,pos):
    # 클릭한 부분을 확인하는 함수로, 만약 누른 부분이 빈 공간이 아닐 경우에만 위치를 투플로 반환한다.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if BOARDRECTS[x][y].collidepoint(pos[0], pos[1]):
                if board[x][y] == EMPTY_SPACE:
                    return None
                return (x,y)
    return None

def getBlock(board, x, y):
    # 게임판의 인덱스가 범위를 벗어나지 않도록 하기위한 함수
    if x < 0 or y < 0 or x >= BOARDWIDTH or y >= BOARDHEIGHT:
        return None
    else:
        return board[x][y]

def countItem(board):
    # 게임판의 블럭의 수를 확인하는 함수
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
            # 가로로 맞는 블럭 검사
            if getBlock(boardCopy,x,y) >= NITEMIMAGES and getBlock(boardCopy, x, y) == getBlock(boardCopy, x + 1, y) == getBlock(boardCopy, x + 2, y):
                targetBlock = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getBlock(boardCopy, x + offset, y) == targetBlock:
                    # 3개 이상의 이어진 블럭이 있는 지 검사
                    removeSet.append((x + offset, y))
                    offset += 1
                blocksToRemove.append(removeSet)

            # 세로로 맞는 블럭 검사
            if getBlock(boardCopy,x,y) >= NITEMIMAGES and getBlock(boardCopy, x, y) == getBlock(boardCopy, x, y + 1) == getBlock(boardCopy, x, y + 2) and getBlock(boardCopy, x, y) != EMPTY_SPACE:
                targetBlock = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getBlock(boardCopy, x, y + offset) == targetBlock:
                    # 3개 이상의 이어진 블럭이 있는 지 검사
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

    # 게임판에 사각형을 그린다.
    pygame.draw.rect(DISPLAYSURF,BROWN,(XMARGIN, YMARGIN + BLOCKSIZE,
                                        WINDOWWIDTH - XMARGIN*2,
                                        WINDOWHEIGHT - YMARGIN*2 - BLOCKSIZE),3)

    # 게임판과 다음에 나올 라인의 경계선을 그린다.
    pygame.draw.line(DISPLAYSURF,WHITE,(XMARGIN,WINDOWHEIGHT - YMARGIN + BLOCKSIZE/4),
                     (WINDOWWIDTH-XMARGIN,WINDOWHEIGHT - YMARGIN + BLOCKSIZE/4),3)
    
    # 게임판을 그린다.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            blockToDraw = board[x][y]
            if blockToDraw != EMPTY_SPACE:
                DISPLAYSURF.blit(BLOCKIMAGES[blockToDraw], BOARDRECTS[x][y])

    # 다음에 나올 라인을 그린다.
    for i in range(BOARDWIDTH):
        lineToDraw = line[i]
        if lineToDraw != EMPTY_SPACE:
            DISPLAYSURF.blit(BLOCKIMAGES[lineToDraw], LINERECTS[i])

def pullDownAllBlocks(board):
    # 밑에 빈 공간 없이 블럭을 모두 밑으로 내림
    for x in range(BOARDWIDTH):
        blocksInColumn = []
        for y in range(BOARDHEIGHT):
            if board[x][y] != EMPTY_SPACE:
                blocksInColumn.append(board[x][y])
        board[x] = ([EMPTY_SPACE] * (BOARDHEIGHT - len(blocksInColumn))) + blocksInColumn



if __name__ == "__main__":  # 게임을 직접 실행 시에만 main함수 실행
    main()
