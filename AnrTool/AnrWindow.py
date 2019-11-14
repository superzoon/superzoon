
import tkinter as tk
if __name__ == '__main__':
    window = tk.Tk()
    window.title('Anr 工具')
    window.geometry('560x340')
    var = tk.StringVar()
    var.set('你好！今天的ANR你努力了吗')
    l = tk.Label(window, textvariable=var, bg='green', font=('Arial', 12), width=30, height=2)
    l.pack() #pack()自动 place() grid
    on_hit = False

    def hit_me():
        global on_hit
        if on_hit == False:
            on_hit = True
            var.set('you hit me')
        else:
            on_hit = False
            var.set('')


    b = tk.Button(window, text='hit me', font=('Arial', 12), width=10, height=1, command=hit_me)
    b.pack()

    e1 = tk.Entry(window, show='*', font=('Arial', 14))  # 显示成密文形式
    e2 = tk.Entry(window, show=None, font=('Arial', 14))  # 显示成明文形式
    e1.pack()
    e2.pack()

    e = tk.Entry(window, show=None)  # 显示成明文形式
    e.pack()

    t = tk.Text(window, height=3)
    t.pack()

    def insert_point():  # 在鼠标焦点处插入输入内容
        var = e.get()
        t.insert('insert', var)


    def insert_end():  # 在文本框内容最后接着插入输入内容
        var = e.get()
        t.insert('end', var)


    b1 = tk.Button(window, text='insert point', width=10,
                   height=2, command=insert_point)
    b1.pack()
    b2 = tk.Button(window, text='insert end', width=10,
                   height=2, command=insert_end)
    b2.pack()

    window.mainloop()