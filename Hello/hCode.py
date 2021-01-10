
def covariance(l1, l2, size):
    l1_avg = sum(l1)/size
    l2_avg = sum(l2)/size
    return sum([(l1[i] - l1_avg)*(l2[i] - l2_avg) for i in range(0, size)])

def get_result(image, pix):
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
