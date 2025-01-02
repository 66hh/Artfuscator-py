import cv2
from io import StringIO

temp = '''
USE32

global art

section .data
wide: dd 0, 0, 0

section .text

table:
%s

art:
mov eax, 0
jmp [table+eax*4]

%s

end:
ret
'''

labels = StringIO()
codes = StringIO()

# 加载图像
image = cv2.imread('image.jpg')

width = 256
height = 256

# 调整图片大小
resize = cv2.resize(image, (width, height), interpolation = cv2.INTER_CUBIC)

# 二值化
gray = cv2.cvtColor(resize, cv2.COLOR_BGR2GRAY)
retval, gray_image = cv2.threshold(gray, 0, 255,  cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# 拼接代码
for y in range(height + 1):
    for x in range(width + 1):
        label = "pixel_%d_%d" % (x, y)

        if x == 0:
            if y == height:
                codes.write("%s:\nvfmaddsub132ps xmm0,xmm1,[cs:edi+esi*4+wide+4]\njmp end\n" % label)
            else:
                codes.write("%s:\nvfmaddsub132ps xmm0,xmm1,[cs:edi+esi*4+wide+4]\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\njmp pixel_%d_%d\n" % (label, x, y + 1))
            continue
        
        if y == 0:
            labels.write("dd %s\n" % label)

        if y == height:
            codes.write("%s:\nvfmaddsub132ps xmm0,xmm1,[cs:edi+esi*4+wide+4]\njmp end\n" % label)
            continue

        value = gray_image[y, x - 1]
        if value == 255:
            codes.write("%s:\nvfmaddsub132ps xmm0,xmm1,[cs:edi+esi*4+wide+4]\njmp pixel_%d_%d\n" % (label, x, y + 1))
        else:
            codes.write("%s:\nvfmaddsub132ps xmm0,xmm1,[cs:edi+esi*4+wide+4]\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\njmp pixel_%d_%d\n" % (label, x, y + 1))

open("output.asm", "w").write(temp % (labels.getvalue(), codes.getvalue()))

# nasm -f win32 .\output.asm

# 显示图像
cv2.imshow('Black and White Image', gray_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
