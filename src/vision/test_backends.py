import cv2

# backends = cv2.videoio_registry.getBackends()
# for backend in backends:
#     print(cv2.videoio_registry.getBackendName(backend))

# capture_api = cv2.VideoCaptureAPIs

properties = [
    "CAP_PROP_POS_MSEC",
    "CAP_PROP_POS_FRAMES",
    "CAP_PROP_POS_AVI_RATIO",
    "CAP_PROP_FRAME_WIDTH",
    "CAP_PROP_FRAME_HEIGHT",
    "CAP_PROP_FPS",
    "CAP_PROP_FOURCC",
    "CAP_PROP_FRAME_COUNT",
    "CAP_PROP_FORMAT",
    "CAP_PROP_MODE",
    "CAP_PROP_BRIGHTNESS",
    "CAP_PROP_CONTRAST",
    "CAP_PROP_SATURATION",
    "CAP_PROP_HUE",
    "CAP_PROP_GAIN",
    "CAP_PROP_EXPOSURE",
    "CAP_PROP_CONVERT_RGB",
    "CAP_PROP_WHITE_BALANCE_BLUE_U",
    "CAP_PROP_RECTIFICATION",
    "CAP_PROP_MONOCHROME",
    "CAP_PROP_SHARPNESS",
    "CAP_PROP_AUTO_EXPOSURE",
    "CAP_PROP_GAMMA",
    "CAP_PROP_TEMPERATURE",
    "CAP_PROP_TRIGGER",
    "CAP_PROP_TRIGGER_DELAY",
    "CAP_PROP_WHITE_BALANCE_RED_V",
    "CAP_PROP_ZOOM",
    "CAP_PROP_FOCUS",
    "CAP_PROP_GUID",
    "CAP_PROP_ISO_SPEED",
    "CAP_PROP_BACKLIGHT",
    "CAP_PROP_PAN",
    "CAP_PROP_TILT",
    "CAP_PROP_ROLL",
    "CAP_PROP_IRIS",
    "CAP_PROP_SETTINGS",
    "CAP_PROP_BUFFERSIZE",
    "CAP_PROP_AUTOFOCUS",
]

cap = cv2.VideoCapture(0, cv2.CAP_V4L2, [cv2.CAP_PROP_BUFFERSIZE, 1, cv2.CAP_PROP_FRAME_WIDTH, 1280, cv2.CAP_PROP_FRAME_HEIGHT, 720])
# cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

for i in range(39):
    print(properties[i], cap.get(i))

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("image", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Appuyez sur la touche Esc pour quitter
        break