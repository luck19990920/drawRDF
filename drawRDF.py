print('Loading drawRDF...\n')
import os
import logging
import contextlib, collections
import numpy as np

logger = logging.getLogger('drawRDF.py')  # 实例化一个logging对象

mplstyle = ['./style/no-latex.mplstyle', './style/my.mplstyle']

print(f'Draw radial distribution function or coordination number curve from xvg file produced by gromacs\n'
      f'Version 1.0, release date: 2024-Jun-22\n'
      f'Programmed by Jian Zhang (jian_zhang@cug.edu.cn)\n'
)

# 使用上下文装饰器
@contextlib.contextmanager
def openany(filename: str):
    with open(file=filename, encoding='utf-8') as fp:
        lines = fp.readlines()
    yield lines

# 所有关于文件的类的最上层的类
class FileUtils(object):
    def _init_filename(self, filename: str):
    # 初始化文件路径
        self.real_filename = os.path.realpath(filename)  # os.path.realpath(path, strict=False)若strict为True,文件不存在会返回OSError

    def filename(self, filename: str, *, my_ext: None|str = None) -> str:
    # 提取文件名(不含后缀名), 若给了my_ext则返回换了文件后缀名的文件名
        filename, ext = os.path.splitext(filename)
        if my_ext:
            filename = filename + os.extsep + my_ext.strip(os.extsep)
        return filename
    

# 目前只针对于只有2列的xvg文件,针对一个xvg文件(一条曲线)
class XVG(FileUtils):
    # 初始化
    def __init__(
            self, filename: str, label: str|None = None, **kwargs
    ):
    # filename: xvg文件名
    # kwargs: stride: 每隔多少行读取一个数据
        self._init_filename(filename)    # 在这里给实例增加了一个real_filename属性
        self._array = None               # 存储xvg文件中的数据,用.array属性获得其值
        self.names = label               # 曲线的label,若提供则以提供的label为准,否则从文件中读取
        self.stride = kwargs.get('stride', 1)    # 提取数据的间隔
        self.type = None                        # 判断xvg文件的种类
        self.parse()     

    # 实际上读取xvg文件
    def parse(self):
        rows = []    # 存储数据
        with openany(self.real_filename) as xvg:
            for linenum, line in enumerate(xvg, start=1):
                
                # 获得曲线的label
                if line.startswith('@ s') and 'subtitle' not in line and self.names is None:
                    name = line.split('legend ')[-1].replace('"','').strip().split()[-1]
                    self.names = name
                
                # 判断曲线的种类
                if line.startswith('@    title'):
                    title_dict = {
                        'Cumulative Number RDF': 'Coor',
                        'Radial distribution': 'RDF'
                    }
                    titile = line.split('title ')[-1].replace('"','').strip()
                    self.type = title_dict.get(titile)
                    if self.type is None:
                        msg = f'{self.real_filename} is neuther radial distribution function nor coordination number curve'
                        logger.error(msg)
                        raise ValueError

                # 采集数据  
                if not (line.startswith('#') or line.startswith('@')):
                    try:
                        row = [float(el) for el in line.split()]
                    except:
                        logger.error(f'Cannot parse line {linenum}: {line.strip()}.')
                        raise
                    rows.append(row)

        try:
            self._array = np.array(rows).transpose()[:,::self.stride]    # 第一个数组为x坐标, 第二个数组为y坐标
        except:
            logger.error(f'Failed reading XVG file, possibly data corrupted.')
            raise
        finally:
            del rows
    
    @property
    def array(self):
        return self._array

# 针对多条曲线，多个xvg文件
class multiXVG:
    def __init__(self, filename: list[str,], label: list[str,]|None = None):
        self._filelist = filename     # 存储xvg文件路径的列表,可以传入多个,已去重
        if label is None:
            self.curve_label = ['curve'+str(i+1) for i in range(len(self._filelist))]   # label要么为None,要么和文件的个数吻合
        else:
            self.curve_label = label
        self._dict = self._data_dict  # 存储xvg文件信息的字典,键为文件的路径,值为该文件对应的XVG对象

    # 修改self._dict,键为文件名,值为该文件名对应的XVG对象
    @property
    def _data_dict(self):
        _dict = dict()
        for file in self._filelist:
            _dict[file] = XVG(file)
        return _dict
    
    def plot(self, **kwargs):
        color = kwargs.get('color')
        if len(color) != len(self._filelist): # type: ignore
            raise ValueError("The number of color doesn't match with the number curve.")
        linestyle = kwargs.get('linestyle', 'dashed')   # 仅针对于RDF和配位数曲线均绘制,对配位数曲线的线形控制
        if linestyle  not in ['solid', 'dashed']:
            raise ValueError("The linestyle is wrong. Please choice 'solid' or 'dashed'.")
        label_bool = kwargs.get('label_bool', True)
        output_format = kwargs.get('output_format', 'png')
        output_dpi = kwargs.get('output_dpi', 300)
        label_position = kwargs.get('label_position', 'best')

        import matplotlib.pyplot as plt
        from matplotlib import _rc_params_in_file # type: ignore
        from pathlib import Path
        styles = {}
        for path in mplstyle:
            path = Path(path)
            if path.is_file():
                styles[path.stem] = _rc_params_in_file(path)
                plt.style.core.update_nested_dict(plt.style.library, styles) # type: ignore
                plt.style.core.available[:] = sorted(plt.style.library.keys())
        plt.style.use(list(styles.keys()))

        ax = plt.gca()
        
        # 绘制全部都为同一种类型的曲线
        def single_draw(xvgobject_list: list):
            ls = []
            for num, xvgobject in enumerate(xvgobject_list):
                line, = ax.plot(xvgobject.array[0], xvgobject.array[1], label=self.curve_label[num], color=color[num]) # type: ignore
                ls.append(line)
            return ls

        # 绘制不同类型的曲线
        def multi_draw(xvgobject_list: list):
            ls = []
            for num, xvgobject in enumerate(xvgobject_list):
                if xvgobject.type == 'RDF':
                    line, = ax.plot(xvgobject.array[0], xvgobject.array[1], label=self.curve_label[num], color=color[num]) # type: ignore
                if xvgobject.type == 'Coor':
                    line, = ax2.plot(xvgobject.array[0], xvgobject.array[1], label=self.curve_label[num], color=color[num], linestyle=linestyle) # type: ignore
                ls.append(line)
            return ls

        curve_type_list = [XVG.type for XVG in list(self._dict.values())]
        if len(set(curve_type_list)) == 1: # type: ignore   # 所绘制的全部为同种曲线
            if curve_type_list[0] == 'RDF': # type: ignore
                ax.set_ylabel(r'$\mathit{g}$'+'('+r'$\mathit{r}$'+')')
            else:
                ax.set_ylabel('Coordination Number')
            if label_bool:
                plt.legend(handles = single_draw(list(self._dict.values())), loc=label_position)
            else:
                _ = single_draw(list(self._dict.values()))
            
        else:
            ax.set_ylabel(r'$\mathit{g}$'+'('+r'$\mathit{r}$'+')')
            ax2 = ax.twinx()
            ax2.set_ylabel('Coordination Number')
            if label_bool:
                plt.legend(handles = multi_draw(list(self._dict.values())), loc=label_position)
            else:
                _ = multi_draw(list(self._dict.values()))
        #ax.legend()
        ax.set_xlabel(r'$\mathit{r}$'+'(nm)')

        min_max_value = [(np.min(XVG.array[0]), np.max(XVG.array[0])) for XVG in list(self._dict.values())]
        min_value = min([min_value_tuple for min_value_tuple, _ in min_max_value])
        max_value = min([max_value_tuple for _, max_value_tuple in min_max_value])
        # plt.legend(loc='upper right')
        ax.set_xlim(min_value, max_value)
        plt.savefig('./draw.' + output_format, dpi=output_dpi)
        plt.show()


while True:
    file_list = []
    legend_bool = False
    output_format = 'png'
    output_dpi = 300
    while True:
        input_file = input("Please input the path of xvg file and enter 'q' to perform the next step.\n")
        if input_file == 'q' and len(file_list) !=0:
            break
        if not os.path.isfile(input_file):
            print(f'{input_file} is not a file\nPlease enter the path of file again.')
            continue
        if input_file not in file_list:
            file_list.append(input_file)

    color = ['#0C5DA5', '#00B945', '#FF9500', '#FF2C00', '#845B97', '#474747', '#9e9e9e']
    user_color = [color[int(i%7)] for i in range(len(file_list))]
    label = [f'curve {i+1}' for i in range((len(file_list)))]
    label_position = 'best'
    label_position_list = ['best', 'upper right', 'upper left', 'lower left', 'lower right']
    
    while True:
        print(f'0  Whether to turn on the legend: {str(legend_bool)}')
        print(f'1  Format of output picture: {output_format}')
        print(f'2  The dpi of output picture: {str(output_dpi)}')
        print(f'3  The color of curve in output picture: {', '.join(user_color)}')
        print(f'4  The paths of style sheets: {', '.join(mplstyle)}')
        print(f'5  The label of curves: {str(None) if label == [] else ', '.join(label)}')
        print(f'6  The position of label: {label_position}')
        print(f'd  Start to draw picture')
        match input():
            case '0':
                legend_bool = not legend_bool
            case '1':
                format_pic = input('Format of picture: png, tiff, jpg. Please enter one of them.\n')
                if format_pic in ['png', 'tiff', 'jpg']:
                    output_format = format_pic
                else:
                    print('Invalid input. Use default format: png.')
                    output_format = 'png'
            case '2':
                try:
                    output_dpi = int(input('The dpi of picture.\n'))
                except:
                    print('Invalid input. Use default value.')
                    output_dpi = 300
            case '3':
                print(f'You need to enter the hexadecimal color codes for all {len(file_list)} colors')
                print(f'For example: #23BAC5')
                print(f'Enter one color per line.')
                user_color = collections.deque(maxlen=len(file_list))
                for i in range(len(file_list)):
                    user_color.append(input())
            case '4':
                mplstyle.append(input(f'Enter one path of style sheets\n'))
            case '5':
                print(f'Enter the number of labels: {len(file_list)}')
                print('For example: x${_2}$')
                user_label = []
                for _ in range(len(file_list)):
                    user_label.append(input())
                label = user_label
            case '6':
                print('Please enter the position of legend, you can enter the following values.')
                s = input(', '.join(label_position_list)+'\n')
                label_position = s if s in label_position_list else 'best' 
            case 'd':
                break
            case _:
                print('Invalid input.')


    print('Analyzing data...')
    picture = multiXVG(file_list, label=label)
    picture.plot(label_bool=legend_bool, color=user_color, output_format=output_format, output_dpi=output_dpi, label_position=label_position)
    if input("Enter 'qq' to exit this program.\nPress Enter directly to redraw.\n") == 'qq':
        break
    







