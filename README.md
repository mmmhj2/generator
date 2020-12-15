=== 红石音乐生成器 ===

这个 Python 小工具可以将 MIDI 文件转化成在 Minecraft 中可用的数据包。
目前已移动至[Github Repo](https://github.com/mmmhj2/generator)

== 使用方法 ==
1. 下载源代码；
2. 安装依赖；
3. 运行 "python main.py \*.mid" 进行转换（不带参数执行以显示更多说明）；
4. 将生成的 datapack 文件夹拷贝至 Minecraft 存档的 datapacks 文件夹下；  
** 现在你的存档目录树应当类似这样： **
```
(存档文件夹)  
--advancements  
--data  
--datapacks  
----(数据包名)  
------data  
--------...  
------pack.mcmeta  
--DIM1  
--...  
```

5. 进入存档世界。如果数据包没有自动加载，运行 "/datapack enable <你的数据包名\>"。首次执行时运行 "/function std:initialize"，如果画面右侧出现计分板，则一切正常；
6. 执行 "/function std:<你的音乐文件名\>\_result" 生成命令方块；
7. 强充能第一个脉冲命令方块，此后音乐应当正常播放。

== 依赖 ==

Python 3, mido

Minecraft (Java版，版本 >= 1.16)

== 注意事项 ==

* 生成的命令方块可能在某一方向上延伸数千格远，因此建议使用不生成结构的超平坦世界。
* 创建世界时记得开启作弊选项。
