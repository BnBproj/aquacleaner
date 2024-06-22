import pymurapi as mur
from nicegui import ui
import asyncio
import time    
import sys
import pigpio      
import threading
import cv2                   #импорт библиотек 
pi = pigpio.pi()             
h = pi.i2c_open(1, 0x18)     #создание порта обмена данных по I2C
auv = mur.mur_init()

cap = cv2.VideoCapture(0)
fps = 24.0
image_size = (640,480)
video_file = 'res.avi'       #создание камеры и ее настроек

i = 0
curs=[]
timee=[]
timee1=[]                    #создание списков и переменных

# -скорость то вперед
# +скорость то назад

@ui.page('/')    
async def index():           #создание страницы
    ar1 = ui.input(label='Домашняя долгота в формате ГГмм.мм')    
    ar2 = ui.input(label='Домашняя широта в формате ГГмм.мм')
    ar3 = ui.input(label='Конечная долгота в формате ГГмм.мм')
    ar4 = ui.input(label='Конечная широта в формате ГГмм.мм')
    ar1 = ui.input(label='Курс', on_change=lambda a: curs.insert(0, a.value)) 
    ar1 = ui.input(label='Время движения', on_change=lambda b: timee.insert(0, b.value)) 
    ar4 = ui.input(label='Время работы на точке', on_change=lambda c: timee1.insert(0, c.value))
    st = ui.button('Установить координаты дома автоматически') 
    st1 = ui.button('Начать работу', on_click=lambda: comport())

def cam():                                                                                                 #функция записи видео
    out = cv2.VideoWriter(video_file, cv2.VideoWriter_fourcc(*'XVID'), fps, image_size)   
    for i in range(0, 4000):
        ret, frame = cap.read()
        out.write(frame)
        time.sleep(0.02)
        i = i + 1        
    cap.release()
    
def swim():                                                 #функция управления робота
    yaw = round(auv.get_yaw()) 
    napr = int(curs[0])   
    e = 0
    eold = 0
    tim = int(timee[0]) 
    tim1 = int(timee1[0]) 
    timer = time.time()
        
    while (timer + tim > time.time()):                      #ПД-регулятор удерживающий заданное направление
        yaw = round(auv.get_yaw())
        e = napr - yaw       
        u = (0.2 * e) + (0.3 * (e-eold))    
        print(u)    
        m1 = 50 + u
        m2 = 50 - u
        auv.set_motor_power(0, 0)
        auv.set_motor_power(1, 0)   
        eold = e

    auv.set_motor_power(0, 0)
    auv.set_motor_power(1, 0)   
    print("доплыл")
    pi.i2c_write_byte(h, 1)
    timer = time.time()
    while time.time() < timer + tim1:           #цикл движения по спирали
        auv.set_motor_power(0, 0)
        auv.set_motor_power(1, 0)  
        time.sleep(0.2)   
        inf = pi.i2c_read_byte(h) 
        print(inf)
        if inf == 8:
            print("ok")       
        if inf == 2:
            print("Фильтр забит!")
            break;
        if inf == 3:
            print("Устройство разряжено!")
            break;
        
    auv.set_motor_power(0, 0)
    auv.set_motor_power(1, 0)       
    print("по спирали проплыл")    
    pi.i2c_write_byte(h, 4) 
    timer = time.time()
    
#    while (timer + tim + 10 > time.time()):                  #ПД-регулятор удерживающий направление для вохвращения на базу
#        yaw = round(auv.get_yaw())
#        if napr > 0:
#            e = abs(napr - yaw) - 180
#            print("-180")
#        if napr < 0:
#            e = -abs(napr - yaw) + 180
#            print("+180")
#        u = (0.2 * e) + (0.3 * (e-eold))    
#        print(u)    
#        m1 = 50 - u
#        m2 = 50 + u
#        auv.set_motor_power(0, m1)
#        auv.set_motor_power(1, m2)   
#        eold = e
        
    sys.exit(1)


def comport():                                                #функция, запускающая в параллельные потоки запись видео и движение
#    thread1 = threading.Thread(target=cam)
#    thread2 = threading.Thread(target=swim)
#    thread1.start()
#    thread2.start()
    swim()    
ui.run(reload = False)
