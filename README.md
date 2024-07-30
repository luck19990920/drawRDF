# drawRDF
`drawRDF`是一款开源的绘图软件，旨在从gromacs (https://www.gromacs.org/) 的`gmx rdf`命令获得的xvg文件直接绘制径向分布函数图像与配位数图像。

### 使用方法
目录下`drawRDF.py`为`drawRDF`软件的python源代码，`drawRDF.exe`为其的可执行文件。双击`drawRDF.exe`就可以运行该软件。运行该软件后，首先会看到以下的内容：
```
Loading drawRDF...

Draw radial distribution function or coordination number curve from xvg file produced by gromacs
Version 1.0, release date: 2024-Jun-22
Programmed by Jian Zhang (jian_zhang@cug.edu.cn)

Please input the path of xvg file and enter 'q' to perform the next step.
```
随后，逐个拉进需要绘图的xvg文件，按`q`回车即可结束文件载入，如下图所示。
```
Loading drawRDF...

Draw radial distribution function or coordination number curve from xvg file produced by gromacs
Version 1.0, release date: 2024-Jun-22
Programmed by Jian Zhang (jian_zhang@cug.edu.cn)

Please input the path of xvg file and enter 'q' to perform the next step.
C:\Users\89732\Desktop\office-automation\ts\rdf-1.xvg
Please input the path of xvg file and enter 'q' to perform the next step.
C:\Users\89732\Desktop\office-automation\ts\rdf_cn-1.xvg
Please input the path of xvg file and enter 'q' to perform the next step.
q
```
随后，出现下面的菜单选项：
```
0  Whether to turn on the legend: False
1  Format of output picture: png
2  The dpi of output picture: 300
3  The color of curve in output picture: #0C5DA5, #00B945
4  The paths of style sheets: ./style/no-latex.mplstyle, ./style/my.mplstyle
5  The label of curves: curve 1, curve 2
6  The position of label: best
d  Start to draw picture
```
* 按`0`: 选择是否开启每一条曲线的图例，默认不开启
* 按`1`: 选择图片的格式，这里可以选择`png`， `jpg`和`tiff`三者之一，默认为`png`格式
* 按`2`: 选择输出图片的分辨率，默认300
* 按`3`: 设置每一条曲线颜色的十六进制码，默认的颜色有`#0C5DA5`，`#00B945`，`#FF9500`，`#FF2C00`，`#845B97`，`#474747`和`#9e9e9e`
* 按`4`: 设置作图格式文件路径，默认为`./style/no-latex.mplstyle`和`./style/my.mplstyle`
* 按`5`: 设置每一条曲线的图例，只有当`0`选项为`True`时，该设置才起作用
* 按`6`: 设置图例的位置，可选的位置有`best`，`upper right`，`upper left`，`lower left`和`lower right`，默认为`best`
* 按`7`: 开始作图

### 绘图效果
##### 实例1：绘制单独的一条径向分布函数曲线
<table align='center'>
    <tr>
        <th style="text-align: center;">不使用图例</th>
        <th style="text-align: center;">使用图例</th>
    </tr>
    <tr>
        <th><img src='./example/draw-1.png'></th>
        <th><img src='./example/draw-2.png'></th>
    </tr>
</table>

##### 实例2：绘制单独的一条配位数曲线
<table align='center'>
    <tr>
        <th style="text-align: center;">不使用图例</th>
        <th style="text-align: center;">使用图例</th>
    </tr>
    <tr>
        <th><img src='./example/draw-3.png'></th>
        <th><img src='./example/draw-4.png'></th>
    </tr>
</table>

##### 实例3：同时绘制多条曲线
<table align='center'>
    <tr>
        <th><img src='./example/draw-5.png'></th>
        <th><img src='./example/draw-6.png'></th>
    </tr>
</table>

##### 实例4：采用不同的风格样式
<table align='center'>
    <tr>
        <th style="text-align: center;">Solarize_Light2风格</th>
    </tr>
    <tr>
        <th><img src='./example/draw-7.png'></th>
    </tr>
</table>

<table align='center'>
    <tr>
        <th style="text-align: center;">ggplot风格</th>
    </tr>
    <tr>
        <th><img src='./example/draw-8.png'></th>
    </tr>
</table>

### 更新日志
* [2024-Jul-18] 修改选项`0`与选项`5`之间的逻辑关系，修复了某些bug。


### 鸣谢
在开发`drawRDF`的过程中，主要使用到了以下的Python开源模组
* NumPy, https://numpy.org/ 
* Matplotlib, https://matplotlib.org/ 
* PyInstaller, https://pyinstaller.org/en/stable/ 

此外，还参考了以下Python开源模组的处理方式
* GromacsWrapper, https://gromacswrapper.readthedocs.io/en/latest/ 
* SciencePlots, https://github.com/garrettj403/SciencePlots 

在此对上述模组的开发者表示感谢。

### 许可证
`drawRDF`基于MIT许可证开源。这意味着您可以自由地使用，修改和分发代码。
