import glob
import os
import shutil
import tarfile
import json
import argparse

def filterlabel(f, outdir):
    with open(f, 'r') as jf:
        data = json.load(jf)
        imgname = data["image"]["filename"]

        lightdict = {"annotation": [], 
                     "image" : {"filename" : imgname, 
                                "imsize":data["image"]["imsize"]}}

        for it in data['annotation']:
            try:
                if it['class'] == "traffic_light" and it['light_count'] == "4":
                    lightdict["annotation"].append(it)
            except:
                return None

        if len(lightdict["annotation"])>0:
            jname = os.path.basename(f)
            jsonout = os.path.join(outdir, jname)

            with open(jsonout, 'w') as ojf:
                json.dump(lightdict, ojf)
            
            return imgname

    return None

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument('--inroot', '-inroot', nargs='?', default = './org', help="Input root directory")
    parser.add_argument('--outroot', '-outroot',nargs='?', default = './tlc', help="Output root directory")
    parser.add_argument('--dataset', '-dataset', nargs='?', default = 'val', help="Train, or Validation dataset")

    args = parser.parse_args()

    indataroot = os.path.join(args.inroot, args.dataset)

    if os.path.exists(indataroot) == False:
        print("Not valid input data path")
        return

    jsondir = 'json'
    imgdir = 'image'

    labelsuffix = "라벨"
    datasuffix = "원천"

    outdataroot = os.path.join(args.outroot, args.dataset)
    os.makedirs(outdataroot, exist_ok=True)

    tarlist = glob.glob(indataroot+'/*.tar')

    for tfile in tarlist:
        fname = os.path.basename(tfile)
        suffix = fname[1:3]
        subdir = os.path.splitext(fname[4:])[0]

        outjsondir = None
        imgnames = []
        print(subdir + " is processed.")

        if suffix == labelsuffix:
            basedir = os.path.join(outdataroot, subdir)
            outjsondir = os.path.join(basedir,jsondir)
            os.makedirs(outjsondir, exist_ok=True)

            jsontar = tarfile.open(tfile)
            jsontar.extractall(indataroot)
            jsontar.close()
            jsonlist = glob.glob(os.path.join(os.path.join(indataroot, subdir),'*.json'))

            print('Total : {}'.format(len(jsonlist)))

            for j in jsonlist:
                name = filterlabel(j, outjsondir)
                if name:
                    imgnames.append(name)

            injsondir = os.path.dirname(jsonlist[0])

            if len(imgnames) == 0:
                shutil.rmtree(outjsondir,ignore_errors=True)
                shutil.rmtree(injsondir,ignore_errors=True)
                imgnames = []
                continue

            itarname = fname.replace(labelsuffix, datasuffix)
            itarpath = os.path.join(indataroot, itarname)

            print('TLC : {}'.format(len(imgnames)))

            if os.path.exists(itarpath):
                imgtar = tarfile.open(itarpath)
                outimgdir = os.path.join(basedir,imgdir)

                imgtar.extractall(injsondir)
                imgtar.close()
                os.makedirs(outimgdir, exist_ok=True)

                for name in imgnames:
                    imgpath = os.path.join(outimgdir, name)
                    shutil.move(os.path.join(injsondir, name), imgpath)

            shutil.rmtree(injsondir,ignore_errors=True)

if __name__ == "__main__":
    main()