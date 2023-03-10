import glob
import os
import shutil
import json
import argparse

# x : in the direction of width(not opencv coordinate)
# y : in the direction of height(not opencv coordinate )
# imgsz : (width,height)

def xyxy2xywh(x1,y1,x2,y2, imgsz):
    x = (x1+x2)/2/imgsz[0]
    y = (y1+y2)/2/imgsz[1]
    w = abs(x2-x1)/imgsz[0]
    h = abs(y2-y1)/imgsz[1]

    return x,y,w,h

def json2yolotxt(jdir, tdir, fname):
    jsonpath = os.path.join(jdir, fname)

    with open(jsonpath, 'r') as jf:
        data = json.load(jf)
        res = []
        imgsz = tuple(map(int, data["image"]["imsize"]))

        for id, it in enumerate(data['annotation']):
            x1,y1,x2,y2 = it["box"]
            x,y,w,h = xyxy2xywh(x1,y1,x2,y2,imgsz)
            clsid = 20

            if it["attribute"][0]["green"] == "on":
                clsid += 1
            if it["attribute"][0]["left_arrow"] == "on":
                clsid += 2
            if it["attribute"][0]["yellow"] == "on":
                clsid += 4
            if it["attribute"][0]["red"] == "on":
                clsid += 8

            res.append((clsid, id, x,y,w,h))

        if len(res)>0:
            tpath = os.path.join(tdir, os.path.splitext(fname)[0])+'.txt'
            
            with open(tpath, 'w') as tf:
                for d in res:
                    txt = "{} {} {:.8f} {:.8f} {:.8f} {:.8f}\n".format(*d)
                    tf.write(txt)
    return res

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument('--inroot', '-inroot', nargs='?', default = './tlc', help="Input root directory")
    parser.add_argument('--dataset', '-dataset', nargs='?', default = 'val', help="Train, or Validation dataset")

    args = parser.parse_args()

    indataroot = os.path.join(args.inroot, args.dataset)

    if os.path.exists(indataroot) == False:
        print("Not valid input data path")
        return

    subdirs = [x for x in os.listdir(indataroot) 
                if os.path.isdir(os.path.join(indataroot, x))]

    for sub in subdirs:
        dir = os.path.join(indataroot, sub)
        jsondir = os.path.join(dir,'json')

        jsons = [x for x in os.listdir(jsondir) 
                    if os.path.isdir(os.path.join(jsondir, x)) == False]

        txtdir = os.path.join(dir, 'image')

        for j in jsons:
            json2yolotxt(jsondir, txtdir, j)

if __name__ == "__main__":
    main()