import base64
import time

from selenium import webdriver
from selenium.webdriver.common import actions
from selenium.webdriver.common.keys import Keys
import cv2
import numpy as np


def get_driver_image(driver):
    str = """
    try {
        console.log('start'); // TODO put this on init so I don't have to set it every time I want something
        console.log(arguments[0]);
        arguments[0].setAttribute('crossOrigin', 'Anonymous');
        let img = arguments[0].toDataURL('image/png').substring(21);
        return img;
        console.log(img);
        document.write('<img id=\"img\" src=\"'+img+'\"/>');
    }
    catch(e) {
        console.log(e);
    }
    """
    canvas_base64 = driver.execute_script(
        str,
        canvas
    )

    cap = base64.b64decode(canvas_base64)
    image = cv2.imdecode(np.frombuffer(cap, np.uint8), 1)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image
    # Now what do we do with this image?
    # We detect objects inside of it and keep a list of them and their positions on the screen
    # And we draw that list on the screen


def prepare_image(gray_image):
    binary_image = cv2.Laplacian(gray_image, cv2.CV_8UC1)

    dilated_image = cv2.dilate(binary_image, np.ones((6, 6)))

    _, thresh = cv2.threshold(dilated_image, 32, 255, cv2.THRESH_BINARY)
    cv2.imwrite('./test.png', thresh)
    _, _, stats, centers = cv2.connectedComponentsWithStats(thresh, CONNECTIVITY, cv2.CV_32S)
    # centers = components[3]
    print(stats)
    print(centers)
    print(thresh.shape)
    drawCentroidShapes(driver, canvas, centers, stats, [])

def drawCentroidShapes(driver, canvas , centroids, stats, previousEls):
    canvasx = canvas.location['x']
    canvasy = canvas.location['y']
    canvaswidth = canvas.size['width']
    canvasheight = canvas.size['height']
    # Remove all the old ones
    for previousEl in previousEls:
        driver.execute_script("""
        document.getElementById(arguments[0]).remove();
        """, previousEl)
    # place the new ones
    elIds = []
    for index, centroid in enumerate(centroids):
        stat = stats[index]
        # Get the current centroid width/height
        if stat[cv2.CC_STAT_AREA] < 20:
            continue

        cent__index = 'cent_' + str(index)
        elIds.append(cent__index)
        driver.execute_script("""
            debugger;
            const [index, canvasx, canvasy, canvaswidth, canvasheight, centx, centy] = arguments;
            const el = document.createElement('div');
            el.style.position = 'absolute';
            el.style.left = `${canvasx + centx}px`;
            el.style.top = `${canvasy + centy}px`;
            el.style.zIndex = 100;
            el.style.backgroundColor = '6a0dad';
            el.style.opacity = 0.5;
            el.style.width = '50px';
            el.style.height = '50px';
            el.style.borderRadius = '20px';
            el.style.backgroundColor = 'green';
            el.style.border = '2px solid #ccc';
            document.body.appendChild(el);
        """, cent__index, canvasx, canvasy, canvaswidth, canvasheight, centroid[0], centroid[1])
    time.sleep(20)
    return elIds







user_name = "YOUR EMAILID"
password = "YOUR PASSWORD"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-web-security')
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://diep.io")
# Wait 4 seconds for diep to load
time.sleep(4)
# Get the canvas element
canvas = driver.find_element_by_id('canvas')
# Now get its bits

BINARY_THRESHOLD = 128
CONNECTIVITY = 4
webdriver.ActionChains(driver).click(canvas).key_down(Keys.ENTER).perform()
time.sleep(2)


prepare_image(get_driver_image(driver))

driver.close()
