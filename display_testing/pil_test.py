from PIL import Image, ImageDraw, ImageTk
import tkinter

im = Image.new("RGB", (400, 400), (0, 0, 0))


draw = ImageDraw.Draw(im)
draw.line((00, 00, 150, 300), fill=128)
#print(list(im.getdata()))

window = tkinter.Tk()
window.tkIm = ImageTk.PhotoImage(im)
window.label = tkinter.Label(window, image=window.tkIm)
window.label.pack()
window.update()

while True:
    pass
