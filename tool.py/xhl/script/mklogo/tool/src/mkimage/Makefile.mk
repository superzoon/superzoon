mkimage: mkimage.c
	gcc -m32  mkimage.c -o mkimage

clean:
	rm ./mkimage
