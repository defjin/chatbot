import cv2 
import numpy as np
import imutils
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

def setLabel(image, str, contour):
    (text_width, text_height), baseline = cv2.getTextSize(str, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)
    x,y,width,height = cv2.boundingRect(contour)
    pt_x = x+int((width-text_width)/2)
    pt_y = y+int((height + text_height)/2)
    cv2.rectangle(image, (pt_x, pt_y+baseline), (pt_x+text_width, pt_y-text_height), (200,200,200), cv2.FILLED)
    cv2.putText(image, str, (pt_x, pt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 1, 8)


def changeGrayColorAndBlur(address) : 
    ########### 이미지 전처리 과정 ##########
    # https://webnautes.tistory.com/1296
    # https://sosal.kr/1067
    # https://076923.github.io/posts/Python-opencv-9/#top
    print("이미지 전처리 - 흑백화")
    img_origin = cv2.imread(address+ r"\menu.png", cv2.IMREAD_COLOR)
    img_copy = img_origin.copy() 
    img_gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('Show Image', img_gray)
    # cv2.waitKey(0)
    cv2.imwrite(address+r"\menu_gray.jpg", img_gray)
    # 가우시안을 이용해서 이미지를 조금 더 명확하게 구분할 수 있게 된다고 한다.
    ##블러가 필요한가?
    img_blurred = cv2.GaussianBlur(img_gray,(5,5), 0)
    # cv2.imshow('Show Image', img_blurred)
    # cv2.waitKey(0)
    cv2.imwrite(address+r"\menu_blurred.jpg", img_blurred)
    # cv2.destroyAllWindows()
    print("이미지 전처리 - 흑백화 및 블러 완료")
    
# 이 함수를 통해 그림에서 필요한 부분만을 잘라낸다.     
# 목표는 선을 명확히해서 주변 둘레 선을 확인하는 것이다.
# https://webnautes.tistory.com/1097

def saveBoxImage(address) : 

    img = cv2.imread(address+ r"\menu.png", cv2.IMREAD_GRAYSCALE)

    ret,img_binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)
    cv2.imshow('result', img_binary)
    cv2.waitKey(0)

    contours, hierarchy = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rectlist = []
    for cnt in contours:
        size = len(cnt)
        print(size)

        epsilon = 0.005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        size = len(approx)
        print(size)

        cv2.line(img, tuple(approx[0][0]), tuple(approx[size-1][0]), (0, 255, 0), 3)
        for k in range(size-1):
            cv2.line(img, tuple(approx[k][0]), tuple(approx[k+1][0]), (0, 255, 0), 3)

        if cv2.isContourConvex(approx):
            if size == 3:
                setLabel(img, "triangle", cnt)
            elif size == 4:
                #setLabel(img, "rectangle", cnt)
                rectlist.append(cnt)
            elif size == 5:
                setLabel(img, "pentagon", cnt)
            elif size == 6:
                setLabel(img, "hexagon", cnt)
            elif size == 8:
                setLabel(img, "octagon", cnt)
            elif size == 10:
                setLabel(img, "decagon", cnt)
            else:
                setLabel(img, str(size), cnt)
        else:
            setLabel(img, str(size), cnt)

    cv2.imshow('result', img)
    cv2.waitKey(0)

    # rentangle 2가지 찾음 -> 2을 각각을 이미지로 저장하자
    count = 0
    for rect in rectlist : 
        rect = rect.astype("float")
        rect = rect.astype("int")
        x,y,w,h = cv2.boundingRect(rect)

        if w < 200: 
            continue
        count += 1
        cv2.imwrite(address+r"/menuBox"+str(count)+".jpg", img[y: y + h, x: x + w])

    
def cutImagesToGetInfo(address) : 
    # http://www.gisdeveloper.co.kr/?p=6714
    # 먼저 Box1 : 식단표
    # Box2 : 반시간표
    # 혹시 형태가 바뀐다면 크기에 따라서 바꿔주는 것이 맞을 듯하다. 큰 것이 식단표. 위의 함수에서 저장해줄 때 처리해주면 됨.

    img = cv2.imread(address+ r"\menuBox1.jpg", cv2.IMREAD_GRAYSCALE)
    

    #ret,img_binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)
    #cv2.imshow('result', img)
    #cv2.waitKey(0)

    edges = cv2.Canny(img,50,150,apertureSize = 3)
    
    lines = cv2.HoughLines(edges,1,np.pi/180,150)
    for line in lines:
        rho,theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
    
        cv2.line(img,(x1,y1),(x2,y2),(255,0,255),1)
    
    cv2.imshow('edges', edges)
    cv2.imshow('result', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()





def makeMenuItems(address) : 
    print("메뉴만들기")
    changeGrayColorAndBlur(address)
    saveBoxImage(address) 
    
    #날짜를 찾아서
    #필요한 만큼 잘라야 할 것 같다.   
    cutImagesToGetInfo(address)    

    

    # 격자감지 https://codeday.me/ko/qa/20190619/823855.html
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html

    # img = cv2.imread(address + '\Img1.jpg')
    # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) 
    
    # # Apply edge detection method on the image 
    # edges = cv2.Canny(gray,50,150,apertureSize = 3) 
    
    # # This returns an array of r and theta values 
    # lines = cv2.HoughLines(edges,1,np.pi/180, 200) 

    # # The below for loop runs till r and theta values  
    # # are in the range of the 2d array 
    # for r,theta in lines[0]: 
        
    #     print(lines[1])
    #     # Stores the value of cos(theta) in a 
    #     a = np.cos(theta) 
    #     # Stores the value of sin(theta) in b 
    #     b = np.sin(theta) 
    #     # x0 stores the value rcos(theta) 
    #     x0 = a*r 
    #     # y0 stores the value rsin(theta) 
    #     y0 = b*r 
    #     # x1 stores the rounded off value of (rcos(theta)-1000sin(theta)) 
    #     x1 = int(x0 + 1000*(-b))    
    #     # y1 stores the rounded off value of (rsin(theta)+1000cos(theta)) 
    #     y1 = int(y0 + 1000*(a)) 
    #     # x2 stores the rounded off value of (rcos(theta)+1000sin(theta)) 
    #     x2 = int(x0 - 1000*(-b)) 
    #     # y2 stores the rounded off value of (rsin(theta)-1000cos(theta)) 
    #     y2 = int(y0 - 1000*(a)) 
    #     # cv2.line draws a line in img from the point(x1,y1) to (x2,y2). 
    #     # (0,0,255) denotes the colour of the line to be  
    #     #drawn. In this case, it is red.  
    #     cv2.line(img,(x1,y1), (x2,y2), (0,0,255),2) 
        
    # # All the changes made in the input image are finally 
    # # written on a new image houghlines.jpg 
    # cv2.imwrite(address + '\houghlines3.jpg',img)

    ## pytesseract 사용


    # If you don't have tesseract executable in your PATH, include the following:
    #full path 
    #pytesseract.pytesseract.tesseract_cmd = r'C:\Users\student\python\myself\menusender'
    # Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

    # Simple image to string : basic english
    #print(pytesseract.image_to_string(Image.open(address +'\savedimage.jpg')))

    # korean text image to string -> 전체 이미지 대상
    totalstr = pytesseract.image_to_string(Image.open(address + '\menuBox1.jpg'), lang='kor')
    print(totalstr)
    totalstrlist = totalstr.split(' ')
    strlist = list(filter(None, totalstrlist))
    print(strlist)
    #print(pytesseract.image_to_string(Image.open(address + '\Img2.jpg'), lang='kor'))

    # In order to bypass the image conversions of pytesseract, just use relative or absolute image path
    # NOTE: In this case you should provide tesseract supported images or tesseract will return error
    # print(pytesseract.image_to_string('test.png'))

    # # Batch processing with a single file containing the list of multiple image file paths
    # print(pytesseract.image_to_string('images.txt'))

    # # Get bounding box estimates
    # print(pytesseract.image_to_boxes(Image.open('test.png')))

    # # Get verbose data including boxes, confidences, line and page numbers
    # print(pytesseract.image_to_data(Image.open('test.png')))

    # # Get information about orientation and script detection
    # print(pytesseract.image_to_osd(Image.open('test.png')))