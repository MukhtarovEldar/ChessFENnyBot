import os
import cv2
import numpy as np
import math

PIECES_DIR = ['pieces/' + file for file in os.listdir('pieces')]

pieceThreshold = {
    'B': 0.5, 'b': 0.95, 'K': 0.2, 'k': 0.5, 'N': 0.2, 'n': 0.8, 'P': 0.15, 'p': 0.65, 'Q': 0.4, 'q': 0.28, 'v': 0.22, 'R': 0.2, 'r': 0.8, '1': 0.01, '2':0.01
}

boardMatrix = [[''] * 8 for _ in range(8)]
pieceImages = {}

pieceSize = 0

def processImages(filePath):
    global pieceSize
    baseName = os.path.basename(filePath)
    boardName = fileName = baseName.split('.')[0]
    boardImage = cv2.imread(filePath)
    pieceSize = int(boardImage.shape[0] / 8)

    for path in PIECES_DIR:
        baseName = os.path.basename(path)
        fileName = baseName.split('.')[0][0]
        pieceImage = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        new_size = int(boardImage.shape[0] / 8)
        pieceImage = cv2.resize(pieceImage, (new_size, new_size))
        pieceImages[fileName] = (pieceImage, pieceThreshold[fileName])

    return boardName, boardImage


def detectPiece(boardName, boardImage):
    for piece in pieceImages:
        pieceImage, pieceThreshold = pieceImages[piece]
        pieceName = piece if piece != 'v' else 'q'

        boardImageGray = cv2.cvtColor(boardImage, cv2.COLOR_BGR2GRAY)
        pieceImageGray = cv2.cvtColor(pieceImage, cv2.COLOR_BGR2GRAY)

        mask = pieceImage[:, :, 3]
        h, w = pieceImageGray.shape

        result = cv2.matchTemplate(boardImageGray, pieceImageGray, cv2.TM_SQDIFF_NORMED, mask=mask)
        min_val, _, min_loc, _ = cv2.minMaxLoc(result)

        while min_val < pieceThreshold:
            top_left = min_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)

            rectangleColor = (0, 200, 50)
            cv2.rectangle(boardImage, top_left, bottom_right, rectangleColor, 2)

            textColor = (255, 0, 0) if pieceName.isupper() else (0, 0, 255)
            textPosition = (top_left[0], top_left[1] + 20)
            cv2.putText(boardImage, pieceName, textPosition, cv2.FONT_HERSHEY_SIMPLEX, 0.7, textColor, 2, cv2.LINE_AA)

            boardMatrix[round(top_left[1] / pieceSize)][round(top_left[0] / pieceSize)] = pieceName

            h1 = top_left[1] - h // 2
            h1 = np.clip(h1, 0, result.shape[0])

            h2 = top_left[1] + h // 2 + 1
            h2 = np.clip(h2, 0, result.shape[0])

            w1 = top_left[0] - w // 2
            w1 = np.clip(w1, 0, result.shape[1])

            w2 = top_left[0] + w // 2 + 1
            w2 = np.clip(w2, 0, result.shape[1])

            result[h1:h2, w1:w2] = 1
            min_val, _, min_loc, _ = cv2.minMaxLoc(result)


def writeFEN():
    fen = ''
    emptyCount = 0

    for row in range(8):
        for col in range(8):
            piece = boardMatrix[row][col]

            if piece.isdigit():
                emptyCount += 1
            else:
                if emptyCount > 0:
                    fen += str(emptyCount)
                    emptyCount = 0
                fen += piece

        if emptyCount > 0:
            fen += str(emptyCount)
            emptyCount = 0

        fen += '/'

    fen = fen[:-1]

    return fen


if __name__ == "__main__":
    path = "boards/1.jpg"
    images = processImages(path)
    detectPiece(images[0], images[1])

    fen = writeFEN()
    print(fen)

    cv2.waitKey(0)    
    cv2.destroyAllWindows()
