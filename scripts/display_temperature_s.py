import subprocess
import opaware
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
import time
import getpass
import paramiko
import os

hostname = 'flashpi'
iport = 22
username = 'pi'
password = 'R!de45ice'

def do_it():
    s = paramiko.SSHClient()
    #client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #s.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    s.load_system_host_keys()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(hostname, iport, username, password)
    command = 'tail -n 500 ~/data/testjson.json'
    (stdin, stdout, stderr) = s.exec_command(command)
    lines = stdout.readlines()
    s.close()
    print(lines[-1])
    return lines

def do_it_different():
    s = paramiko.SSHClient()
    s.load_host_keys(os.path.expanduser('/home/ubuntu/.ssh/known_hosts'))
    s.load_system_host_keys()
    s.connect(hostname, iport, username)
    command = 'tail -n 500 ~/data/testjson.json'
    (stdin, stdout, stderr) = s.exec_command(command)
    lines = stdout.readlines()
    s.close()
    print(lines[-1])
    return lines


if __name__ == "__main__":
    print(getpass.getuser())
    HOST = "pi@flashpi"
    # Ports are handled in ~/.ssh/config since we use OpenSSH
    COMMAND = 'tail -n 500 ~/data/testjson.json'

    #ssh = subprocess.Popen(["ssh", "-i /root/.ssh/id_rsa.pub", "%s" % HOST, COMMAND],
    #                       shell=False,
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.PIPE)
    #result = ssh.stdout.readlines()
    result = do_it()
    act_data = opaware.ingests.ingest_ambient(result)

    ff = "T:%s" % (act_data.outside_temperature.values[-1])

    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 32
    options.chain_length = 2
    options.hardware_mapping = "adafruit-hat"
    mymat = RGBMatrix(options = options)
    options.drop_privileges=False


    offscreen_canvas = mymat.CreateFrameCanvas()
    font = graphics.Font()
    font.LoadFont("/home/ubuntu/5x8.bdf")
    textColor = graphics.Color(255, 255, 0)
    textColor_dp =  graphics.Color(0, 255, 0)
    pos = 0 #offscreen_canvas.width
    my_text = ff
    print('enetering loop')
    my_dp =  "Td:{:.1f}".format(act_data.outside_dewpoint.values[-1])
    print(getpass.getuser())
    print('do it again before loop')
    #ssh = subprocess.Popen(["ssh", "-i /root/.ssh/id_rsa.pub", "%s" % HOST, COMMAND],
    #                       shell=False,
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.PIPE)
    #result = ssh.stdout.readlines()
    #result = do_it()
    #act_data = opaware.ingests.ingest_ambient(result)

    #ff = "T = %s" % (act_data.outside_temperature.values[-1])



    while True:
        print(pos)
        offscreen_canvas.Clear()
        len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, my_text)
        len = graphics.DrawText(offscreen_canvas, font, pos, 20, textColor_dp, my_dp)

        #pos -= 1
        #if (pos + len < 0):
        #    pos = offscreen_canvas.width
        #
        #time.sleep(160
        print('fetcjing data')
        offscreen_canvas = mymat.SwapOnVSync(offscreen_canvas)
        time.sleep(16)
        print(getpass.getuser())
        # ssh = subprocess.Popen(["ssh", "-i /home/ubunt/.ssh/id_rsa.pub", "%s" % HOST, COMMAND],
        #                    shell=False,
        #                   stdout=subprocess.PIPE,
        #                   stderr=subprocess.PIPE)
        #result = ssh.stdout.readlines()
        print(getpass.getuser())
        result =  do_it()
        act_data = opaware.ingests.ingest_ambient(result)
        my_text = "T:%s" % (act_data.outside_temperature.values[-1])
        my_dp =  "Td:{:.1f}".format (act_data.outside_dewpoint.values[-1])
        print(my_text)
