from matplotlib import pyplot as plt

colors= '#FF0000', '#FF7F00', '#00FF00', '#0000FF', '#7F00FF'

def plot(field, file_names):
    for file_name, color in zip(file_names, colors):
        file= open(file_name)
        head= file.readline()
        lines= file.readlines()

        value= []
        for line in lines:
            line= line.split('\t')
            value.append(line[field])

        plt.plot(value, color= color)

    plt.show()

file_names= [
    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517212401 test_bed lam20 csLRU100 LCP0.1 .txt',
    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517212576 test_bed lam20 csFIFO100 LCP0.1 .txt',
    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517212627 test_bed lam20 csGEOMETRIC100 LCP0.1 .txt',

    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517212944 test_bed lam20 csLRU100 LCP0.5 .txt',

    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517212737 test_bed lam20 csLRU100 LCP1 .txt',
    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517212792 test_bed lam20 csFIFO100 LCP1 .txt',
    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517212843 test_bed lam20 csGEOMETRIC100 LCP1 .txt',

    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517214670 grid lam20 csLRU20 LCP1 .txt',
    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517214341 grid lam20 csLRU100 LCP1 .txt',
    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517214950 grid lam100 csLRU20 LCP1 .txt',
    # r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517214544 grid lam100 csLRU100 LCP1 .txt',

    r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517734371 grid lam100 csFIFO4 LCP1.0 .txt',
    r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517735754 ba lam100 csFIFO4 LCP1.0 .txt',
    r'C:\Users\bupt632\Desktop\LICNsim\exper_cb\result\1517734844 tree lam100 csFIFO4 LCP1.0 .txt',
]

# Time:0 CSNum:1 Store:2 Evict:3 AskNum:4 StepDist:5 AllDist:6 Disperse:7
plot(1, file_names)
# plot(2, file_names)
# plot(3, file_names)
# plot(6, file_names)
plot(7, file_names)
