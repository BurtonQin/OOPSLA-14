import sys
import os

def find_files(dir, givenName):
    ans = []
    for dirpath, dirnames, filenames in os.walk(dir):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if cmp(filename, givenName) != 0:
                continue
            ans.append(os.path.join(dirpath, filename))

    return ans

if __name__ == '__main__':
    delete_files = find_files(sys.argv[1], 'report.txt')

    for fileName in delete_files:
        print fileName
        os.unlink(fileName)
