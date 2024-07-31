# Written by Jian Zhang(jian_zhang@cug.edu.cn)
# Last modified: 2024-Jul-29
# Version: 1.1

from os import path
import numpy as np
import re
import matplotlib.pyplot as plt
from matplotlib import _rc_params_in_file # type: ignore
from matplotlib import rcParams
from pathlib import Path
from matplotlib import rcParamsDefault


################### 相关提取字符串的正则表达式 ###################
re_title = r'@\s+title\s+\"(.+)\"'
re_legend = r'@\s+s[0-9]+\s+legend\s+\"(.+)\"'

################### 横纵坐标坐标标签 ###################
x_label = r'$\mathit{r}$'+'(nm)'
rdf_label = r'$\mathit{g}$'+'('+r'$\mathit{r}$'+')'
coor_label = 'Coordination Number'

################### 相关的类 ###################
class FileUtils:
    """
    文件工具类
    输入值:
    * file_path: 文件路径,类型为str
    其包括以下的几个方法:
    * filename: 获取文件名(含后缀名)
    * file_no_ext: 获取文件名(不含后缀名)
    * is_file: 判断文件是否存在
    """
    def __init__(self, 
                 file_path: str):
        self.file_path = file_path    # 文件路径

    @property
    def filename(self) -> str:
        return path.basename(self.file_path)   # 返回文件名(含后缀)
    
    @property
    def file_no_ext(self) -> str:
        return path.splitext(self.filename)[0]  # 返回文件名(不含后缀)
    
    @property
    def is_exit(self) -> bool:
        return path.isfile(self.file_path)   # 判断文件是否存在
    
class RDF_XVG(FileUtils):
    """
    单个径向分布函数或配位数曲线的XVG文件类
    输入值:
    * file_path: XVG文件路径,类型为str
    * color: XVG文件作图时的曲线颜色,默认是"black",类型为str,是关键词参数
    * legend: XVG文件的图例,类型为list,默认为[],即该值从XVG文件中提取,是关键词参数
    其在继承FileUtils类的基础上,由以下的几个方法:
    * title: XVG文件的标题,从title 'XXXX'中提取,类型为str
    * data: XVG文件的数据,类型为numpy.ndarray
    其有如下的几个属性:
    * color: XVG文件作图时的曲线颜色
    * legend: XVG文件的图例
    """
    def __init__(self, 
                 file_path: str,
                 *,
                 color: str = "black",
                 legend: str = ""):
        super().__init__(file_path)
        self.__title = None
        self.__data = None
        self.legend = legend
        if legend == "":
            self.extract_data()
        self.color = color

    @property
    def title(self) -> str:         # 获取xvg文件标题
        if self.__title is None:
            self.extract_data()
        return self.__title # type: ignore
    
    @property
    def data(self) -> np.ndarray:   # 获取xvg文件数据
        if self.__data is None:
            self.extract_data()
        return self.__data # type: ignore

    def extract_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            line = f.readline()
            while line.strip().startswith('#') or line.strip().startswith('@'):
                if line.strip().startswith('@'):
                    line = line.strip()
                    if (content := re.search(re_title, line)):     # 使用海象运算符实现判断的同时进行赋值操作,提取title后的内容
                        self.__title = content.group(1)
                    elif (content := re.search(re_legend, line)) and self.legend == "":  # 提取图例
                        self.legend = content.group(1)
                line = f.readline()
        self.__data = np.loadtxt(self.file_path, comments=["#", "@"])

class draw:
    """
    绘图的类
    输入值:
    data: 键为XVG文件的title属性,值为XVG文件对象的实例的元组,类型为dict
    legend_bool: 是否显示图例,默认为True,即显示,类型为bool,是关键词参数
    legend_loc: 图例摆放位置,默认为"best",类型为str,是关键词参数
    style_path: 自定义样式文件路径,类型为list,默认为空,即使用matplotlib默认样式,是关键词参数
    x_min: 横坐标的最小值,类型为float,是关键词参数
    x_max: 横坐标的最大值,类型为float,是关键词参数
    其包括以下的几个方法:
    * show: 绘制图表并展现在屏幕上
    * save: 保存图表到指定路径
    """
    def __init__(self,
                 data: dict[str, list[RDF_XVG]],
                 *,
                 legend_bool: bool = True,
                 legend_loc: str = "best",
                 style_path: list[str,] | None = None,
                 x_min: float,
                 x_max: float):
        self.__data = data
        self.__legend_bool = legend_bool
        self.__legend_loc = legend_loc
        self.__style_path = style_path
        self.__fig = None                   # 存储绘图的fig对象
        self.__ax = None                    # 存储绘图的ax对象
        self.x_min = x_min
        self.x_max = x_max

        if self.__style_path is not None:
            rcParams.update(rcParamsDefault)   # 为防止多个draw对象绘图时,样式表更改相互干扰,故现对绘图细节初始化,将plt.rcParams恢复到默认值
            styles = {}
            for path in self.__style_path:
                path = Path(path)
                if path.is_file():
                    styles[path.stem] = _rc_params_in_file(path)
                    plt.style.core.update_nested_dict(plt.style.library, styles) # type: ignore
                    plt.style.core.available[:] = sorted(plt.style.library.keys())
            plt.style.use(list(styles.keys()))
        
        if len(self.__data) == 1:     # 绘制单y轴坐标的图表
            self.__draw_single_y()
        elif len(self.__data) == 2:   # 绘制双y轴坐标的图表
            self.__draw_double_y()
        else:
            raise ValueError(f"The number of types of xvg files can only be less than or equal to 2, but there are {len(self.__data)} types.")
        
        
        
    def __draw_single_y(self):
        ############################################################################################
        # 通过plt.subplots()获取fig对象和ax对象。此外，还可通过plt.gca()获得ax对象,plt.gcf()获得fig对象 #
        #              gcf是Get Current Figure的缩写，gca是Get Current Axes的缩写                    #
        ############################################################################################ 
        self.__fig, self.__ax = plt.subplots()   
        for i in list(self.__data.values())[0]:
            # 对于rdf与配位数曲线的xvg文件数据只有两列
            # plt.plot()的本质是plt.gca().plot()
            self.__ax.plot(i.data[:,0], i.data[:,1], label=i.legend, color=i.color) # type: ignore
            self.__ax.set_xlabel(x_label) # type: ignore
            if list(self.__data.keys())[0] == "Radial distribution":
                self.__ax.set_ylabel(r'$\mathit{g}$'+'('+r'$\mathit{r}$'+')') 
            else:
                self.__ax.set_ylabel(coor_label)
            if self.__legend_bool:
                self.__ax.legend(loc=self.__legend_loc)
        self.__ax.set_xlim(self.x_min, self.x_max) 

##################################################################################
#     注意: 利用plt.legend()函数中的handles参数,可以将多个曲线的图例放在同一张图上    #
#  详见:https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html  #
##################################################################################
    def __draw_double_y(self):
        # 获得径向分布函数的数据
        tuple_rdf = self.__data['Radial distribution']
        self.__fig, self.__ax = plt.subplots()
        ls = []
        for val in tuple_rdf:
            line, = self.__ax.plot(val.data[:,0], val.data[:,1], label=val.legend, color=val.color) # type: ignore
            ls.append(line)
            self.__ax.set_xlabel(x_label) 
            self.__ax.set_ylabel(rdf_label)

        ax2 = self.__ax.twinx()

        # 获得配位数曲线的数据
        tuple_coor = self.__data['Cumulative Number RDF']
        for val in tuple_coor:
            line, = ax2.plot(val.data[:,0], val.data[:,1], label=val.legend, color=val.color, linestyle="dashed") # type: ignore
            ls.append(line)
            ax2.set_ylabel(coor_label)

        if self.__legend_bool:
            self.__ax.legend(handles = ls, loc=self.__legend_loc)

        self.__ax.set_xlim(self.x_min, self.x_max)
    
    @ property
    def show(self):
        self.__fig.show() # type: ignore
        # plt.cla()
        # plt.clf()

    def save(self, 
             *,
             path: str,
             dpi: int):
        # plt.savefig的本质是plt.gcf().savefig()
        ###########################################################################################################################
        ##          一旦调用了plt.show()后,当前的fig和ax就被释放了,因此我们使用self.__fig和self.__ax保存fig对象和ax对象               ##
        ## 详见https://stackoverflow.com/questions/21875356/saving-a-figure-after-invoking-pyplot-show-results-in-an-empty-file  ##
        ###########################################################################################################################
        self.__fig.savefig(path, dpi=dpi) # type: ignore

###################################################### 主程序 #####################################################
intro_inf = f"Draw radial distribution function or coordination number curve from xvg file produced by gromacs\n"\
            f"Version 1.1, release date: 2024-Jul-29\n"\
            f"Programmed by Jian Zhang (jian_zhang@cug.edu.cn)\n"
print(intro_inf)

############# 读入文件 ##########
file_list = []      # 存储xvg文件路径的列表
input_file = input("Please input the path of xvg file and enter 'q' to perform the next step.\n")
while input_file != "q" or len(input_file) == 0:
    if path.isfile(input_file):
        file_list.append(input_file)
    else:
        print(f"{input_file} is not a file\nPlease enter the path of file again.")
    input_file = input("Please input the path of xvg file and enter 'q' to perform the next step.\n")

dict_RDF_XVG = {}        # 用于后续传入draw类的字典
for file in file_list:
    RDF_XVG_obj = RDF_XVG(file)
    if RDF_XVG_obj.title in dict_RDF_XVG:
        dict_RDF_XVG[RDF_XVG_obj.title].append(RDF_XVG_obj)
    else:
        dict_RDF_XVG[RDF_XVG_obj.title] = [RDF_XVG_obj]

print("\n")
num_file_inf = [f"The number of {key} curve: {len(value)}" for key, value in dict_RDF_XVG.items()]
print("\n".join(num_file_inf))

############# 绘图相关默认参数设定 ##########
legend_bool = False                                             # 是否显示图例,默认不显示
output_dpi = 300                                                # 输出图片的分辨率,默认300
color = ['#0C5DA5', '#00B945', '#FF9500', '#FF2C00',
         '#845B97', '#474747', '#9e9e9e']                       # 曲线颜色(曲线颜色不从mplstyle文件中读取)
mplstyle = ['./style/no-latex.mplstyle', './style/my.mplstyle'] # 默认的mplstyle文件文件路径
user_color = [color[int(i%7)] for i in range(len(file_list))]   # 默认颜色  
label_position_list = ['best', 'upper right', 'upper left', 
                       'lower left', 'lower right']             # 可以输入的图例位置
label_position = "best"                                         # 默认的图例位置
save_path = "./draw.png"                                        # 默认的保存路径
x_min = 0                                                       # 默认的x轴最小值
x_max = 1                                                       # 默认的x轴最大值
label = []                                                      # 从xvg文件中直接提取得到的曲线图例
for _, value in dict_RDF_XVG.items():
    for i in value:
        label.append(i.legend)
        i.color = user_color[file_list.index(i.file_path)]

############# 菜单设定 ##########
while True:
    print(f'0  Whether to turn on the legend: {str(legend_bool)}')
    print(f'1  The dpi of output picture: {str(output_dpi)}')
    print(f'2  The color of curve in output picture: {', '.join(user_color)}')
    print(f'3  The path of style sheets: {', '.join(mplstyle)}')
    print(f'4  The label of curves: {" \\ ".join(label)}')
    print(f'5  The position of label: {label_position}')
    print(f'6  The range of x-axis: ({x_min},{x_max})')
    print(f'd  Start to draw picture')
    print(f's  Save the picture')
    print(f'q  Exit program')
    match input():
        case '0':
            legend_bool = not legend_bool
        case '1':
            try:
                output_dpi = int(input('The dpi of picture.\n'))
            except:
                print('Invalid input. Use default value.')
                output_dpi = 300
        case "2":
            user_color = []
            for _, value in dict_RDF_XVG.items():
                for i in value:
                    i.color = input(f'Please enter the hexadecimal color codes for {i.filename}\nFor example: #0C5DA5\n')
                    user_color.append(i.color)
        case "3":
            mplstyle_input = input(f'Enter one path of style sheets\nIf input del, delete the last style sheet\n')
            if mplstyle_input == "del" and len(mplstyle) != 0:
                mplstyle.pop()
            elif mplstyle_input == "del" and len(mplstyle) == 0:
                print("There is no style sheet to delete.")
            elif mplstyle_input != "del" and mplstyle_input != "":
                mplstyle.append(mplstyle_input)
        case "4":
            legend_bool = True
            label = []
            for _, value in dict_RDF_XVG.items():
                for i in value:
                    i.legend = input(f'Please enter the label for {i.filename}\n')
                    label.append(str(None) if i.legend == "" else i.legend)
        case "5":
            label_position = input('Please enter the position of legend, you can enter the following values.\n'+', '.join(label_position_list)+'\n')
        case "6":
            x_range_input = input("Please enter the range of x-axis separated by spaces.\nFor example 0 10\n").split()
            if len(x_range_input) == 2:
                x_min = float(x_range_input[0])
                x_max = float(x_range_input[1])
            else:
                print("Invalid input. Default values will be used.")
        case "d":
            draw_obj = draw(dict_RDF_XVG, legend_bool=legend_bool, legend_loc=label_position, style_path=mplstyle, x_min=x_min, x_max=x_max)
            draw_obj.show    
        case "s":
            input_save_path = input(f"Please enter the path of output picture.\n"\
                                    f"if you want to use the default path({save_path}), just press enter.\n"\
                                    f"Picture formats: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff\n"\
                                    f"For example: D:\\for-calculation\\python_case\\drawRDF\\1.png\n")
            if input_save_path:
                save_path = input_save_path
            draw_obj = draw(dict_RDF_XVG, legend_bool=legend_bool, legend_loc=label_position, style_path=mplstyle, x_min=x_min, x_max=x_max)
            draw_obj.save(path=save_path, dpi=output_dpi)
        case "q":
            break
        case _:
            print("Wrong input, please enter again.")



    

