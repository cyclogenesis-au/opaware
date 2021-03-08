import subprocess
import opaware
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
import time

if __name__ == "__main__":
    HOST = "pi@flashpi"
    # Ports are handled in ~/.ssh/config since we use OpenSSH
    COMMAND = 'tail -n 500 ~/data/testjson.json'

    ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()

    act_data = opaware.ingests.ingest_ambient(result)

    ff = "T = %s" % (act_data.outside_temperature.values[-1])

    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 32
    options.chain_length = 2
    options.hardware_mapping = "adafruit-hat"
    mymat = RGBMatrix(options = options)

    offscreen_canvas = mymat.CreateFrameCanvas()
    font = graphics.Font()
    font.LoadFont("/home/ubuntu/7x13.bdf")
    textColor = graphics.Color(255, 255, 0)
    pos = offscreen_canvas.width
    my_text = ff

    while True:
        offscreen_canvas.Clear()
        len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, my_text)
        pos -= 1
        if (pos + len < 0):
            pos = offscreen_canvas.width

        time.sleep(0.05)
        offscreen_canvas = mymat.SwapOnVSync(offscreen_canvas)

