from utils.common import loadobj

def pyobj_compare_worker(file_range, dir1, dir2):
        print("Starting worker on: " + str(file_range))
        fail_list = []
        for _file_num in file_range:  #First doc starts at '1'
                _obj1 = loadobj(dir1+'/'+str(_file_num)+'.pyobj')
                _obj2 = loadobj(dir2+'/'+str(_file_num)+'.pyobj')
                if (_obj1['source'] != _obj2['source'] or
                    _obj1['add'] != _obj2['add'] or
                    _obj1['delete'] != _obj2['delete'] or
                    _obj1['update'] != _obj2['update']):
                        fail_list.append(_file_num)
        print("Finished worker on: " + str(file_range))
        return (file_range, fail_list)

def pyobj_compare_parallel(dir1, dir2):
        import os
        import multiprocessing
        from functools import partial
        print("Starting compare")
        partial_function = partial(pyobj_compare_worker, dir1=dir1, dir2=dir2)
        _doc_num = len(os.listdir(dir1))
        if len(os.listdir(dir2)) != _doc_num:
                print("File count does not match")
                return False
        # step = int(_doc_num/multiprocessing.cpu_count())
        step = int(_doc_num/4)
        filename_list = range(_doc_num+1)
        task_list = [filename_list[i:i+step] for i in range(1, _doc_num, step)]
        pool = multiprocessing.Pool(4)
        results = pool.map(partial_function, task_list)
        pool.close()
        pool.join()
        for result in results:
                print("Files " + str(result[0][0]) + "-" + str(result[0][len(result[0])-1]) + ":"
                                  + str(len(result[1])) + " mismatches")

def main():
        import sys
        if len(sys.argv) != 3:
                print("Usage: compare_pyobj directory1 directory2")
                return
        pyobj_compare_parallel(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
        main()