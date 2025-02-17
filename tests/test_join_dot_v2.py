import unittest
from join_dot import open_dot_file_as_text, read_dot_files, combine_dot_files, JoinDotFiles, sample
from gopd_workflow_batch import write_to_file

class MyTest(unittest.TestCase):
    # def test_read_dot_files(self):
    #     result = read_dot_files("./workflow")
    #     print(result)
    #     txt = []
    #     i = 0
    #     for r in result:
    #         with open(r, "r", encoding="utf-8") as f:
    #             txt.append(f.read())
    #             print("Dot file {} : {}".format(i, txt[i]))
    #             i += 1

    # def test_open_dot_file_as_text(self):
    #     path = read_dot_files("./workflow")
    #     print(path)
    #     result = open_dot_file_as_text(path)
    #     print(result)

    # def test_main(self):
    #     dir_path = './workflow/Branch-Operations-Manual-for-Deposit-March-2021-chapter1'
    #     dots = read_dot_files(dir_path)
    #     dots_txt = open_dot_file_as_text(dots)
    #     joinDotFiles = JoinDotFiles(combine_dot_files(dots_txt))
    #     result = joinDotFiles.run()
    #     print(result)

    def test_sample(sefl):
        dir_path = './workflow/HKG_DE_01_Volume_SP_Mar_2021/Branch-Operations-Manual-for-Deposit-March-2021-chapter1'
        dots = read_dot_files(dir_path)
        print("####DOTS: {}".format(dots))
        dots_txt = open_dot_file_as_text(dots)
        print("####DOTS_TXT: {}".format(dots_txt))  
        input = combine_dot_files(dots_txt)
        print("####INPUT: {}".format(input))
        result = sample(input)
        write_to_file(f"joined_graph.dot", result, dir_path)

#    def test_main(self):
#     main()

if __name__ == "__main__":
    unittest.main()


