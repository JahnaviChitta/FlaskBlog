from PIL import Image


'''
def estimate_coef(x, y):
    n = np.size(x)
    m_x, m_y = np.mean(x), np.mean(y) 
    SS_xy = np.sum(y*x) - n*m_y*m_x 
    SS_xx = np.sum(x*x) - n*m_x*m_x 
    b_1 = SS_xy / SS_xx 
    b_0 = m_y - b_1*m_x   
    return(b_0, b_1)

def build():
    global rootdir
    global x
    global y
    for subdir,dir,files in os.walk(rootdir):
        for file in files:
            if "subject" in file:
                indexer = file.split("_")
                if len(indexer)>1:
                    im = cv2.imread(os.path.join(subdir,file))
                    x.append(get_result(im))
                    y.append(float(indexer[1].replace(".jpeg","")))
build()
x = np.array(x)
y = np.array(y)
b = estimate_coef(x,y)
print('coefficients:\n',b)
'''

def covariance(l1, l2, size):
    l1_avg = sum(l1)/size
    l2_avg = sum(l2)/size
    return sum([(l1[i] - l1_avg)*(l2[i] - l2_avg) for i in range(0, size)])

def get_result(image):
    size = image.size
    red = []
    green = []
    blue = []
    for i in range(size[0]):
        for j in range(size[1]):
            rgb = pix[i, j] #(255, 255, 255)
            red.append(rgb[0])
            green.append(rgb[1])
            blue.append(rgb[2])
    k = covariance(red,green,len(red))
    l = covariance(red,blue,len(red))
    return round(k+l)


input_image = input("Welcome to 'Anegoo - No pain Only gain'\nChoose your palm's picture to check haemoglobin level : ")

i = input_image + '.jpeg'
im = Image.open(i)
pix = im.load()
print('Size of the Original image', im.size) #width and height of original image
#print(pix[50, 50]) #RGBA value
#im.show()
resized_image = im.resize((400, 400))
resized_image.show()
pix = resized_image.load()
print('Size of image', resized_image.size) #Width and height of resized image
result = get_result(resized_image)
a = (14.639534353807022 + (result*(1.1083761675274781e-08)))
print("\nYour Hemoglobin level is : " + str(a))
if a < 9 :
    print("Results show you might have ANEMIA!!!\nEat plenty of iron-rich foods, such as tofu, green and leafy vegetables, lean red meat, lentils, beans and iron-fortified cereals and breads.\nEat and drink vitamin C-rich foods and drinks.\n Avoid drinking tea or coffee with your meals, as they can affect iron absorption. ")
elif a > 9 and a < 12 :
    print("Low levels of hemoglobin.\nIncreasing the intake of iron-rich foods (eggs, spinach, artichokes, beans, lean meats, and seafood) and foods rich in cofactors (such as vitamin B6, folic acid, vitamin B12, and vitamin C) are important for maintaining normal hemoglobin levels.")
elif a > 12 :
    print("You are perfectly alright :) ")


