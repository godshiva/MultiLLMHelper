import os
import shutil
import threading

class MyHandlerExampleUpperCase:
    def __init__(self):
        pass

    def ask(self, content):
        return content.upper()

class IdempotentProcessor:
    def __init__(self):
        self.lock = threading.Lock()
        self.processed_files = 0
        self.total_files = 0
        self.errors = []

    def filter_unprocessed(self, files):
        return [(inp, out) for inp, out in files if not self.is_output_exists(out)]

    def is_output_exists(self, output_path):
        with self.lock:
            return os.path.exists(output_path)

    def read_file(self, input_path):
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()
            if not content.strip():
                self.report_empty_file(input_path)
                return None
            return content
        except UnicodeDecodeError:
            self.report_error(input_path, 'File is not in UTF-8 format.')
            return None

    def write_file(self, output_path, content):
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)

    def report_error(self, file_path, message):
        print(f"Error in file {file_path}: {message}")

    def report_empty_file(self, file_path):
        print(f"File {file_path} is empty after stripping.")

    def process_files(self, file_chunk, handler):
        for input_path, output_path in file_chunk:
            self.process(input_path, output_path, handler)
            with self.lock:
                self.processed_files += 1
                if self.processed_files % 100 == 0 or self.processed_files == self.total_files:
                    print(f"Processed {self.processed_files}/{self.total_files} files.")

    def process(self, input_path, output_path, HandlerClassType):
        try:
            if not self.is_output_exists(output_path):
                content = self.read_file(input_path)
                if content is not None:
                    handler_object = HandlerClassType()  # Initialize the handler class
                    processed_content = handler_object.ask(content)  # Call the ask method
                    self.write_file(output_path, processed_content)
        except Exception as e:
            with self.lock:
                self.errors.append(f"Error processing file {input_path}: {e}")


    def process_in_threads(self, files, handler, num_threads=5):
        unprocessed_files = self.filter_unprocessed(files)
        self.total_files = len(unprocessed_files)
        chunk_size = (len(unprocessed_files) + num_threads - 1) // num_threads  # Ceiling division
        threads = []

        for i in range(0, len(unprocessed_files), chunk_size):
            thread = threading.Thread(target=self.process_files, args=(unprocessed_files[i:i + chunk_size], handler))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        if self.errors:
            print("Errors encountered during processing:")
            for error in self.errors:
                print(error)

class IdempotentProcessor_unit_tests:

    def run_process(self, n):
        files_to_process = [
            (f'temp_files/input{i}.txt', f'temp_files/output{i}.txt') for i in range(n)
        ]
        processor = IdempotentProcessor()
        processor.process_in_threads(files_to_process, MyHandlerExampleUpperCase)
        return [processor.total_files, processor.processed_files, len(processor.errors), processor.errors]

    def clean_folder(self, folder_path='./temp_files'):
        if not os.path.exists(folder_path):
            print(f"The folder '{folder_path}' does not exist.")
            return

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    def clean_and_make_files(self, list_of_files):
        self.clean_folder()
        for filename in list_of_files:
            with open(os.path.join(filename), mode='w', encoding='UTF-8') as file:
                file.write(filename)

    def read_file_p(self, input_path):
        try:
            with open(os.path.join(input_path), 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except UnicodeDecodeError:
            return "DID NOT READ FILE"

    def do_tests(self):
        self.clean_and_make_files([])
        results = self.run_process(1)
        assert [1,1,1] == results[0:3] and len(results[-1]) == 1 and results[-1][0] == "Error processing file temp_files/input0.txt: [Errno 2] No such file or directory: 'temp_files/input0.txt'"

        # don't clean this time, we want to make sure nothing appeared

        results = self.run_process(2)
        assert [2, 2, 2] == results[0:3] and len(results[-1]) == 2 and "Error processing file temp_files/input0.txt: [Errno 2] No such file or directory: 'temp_files/input0.txt'" in results[-1]

        self.clean_and_make_files(['./temp_files/input0.txt', './temp_files/input1.txt'])
        results = self.run_process(2)
        assert results == [2, 2, 0, []]
        assert "./temp_files/input1.txt" == self.read_file_p('./temp_files/input1.txt')
        assert self.read_file_p('./temp_files/output1.txt') == "./TEMP_FILES/INPUT1.TXT"

        self.clean_and_make_files(['./temp_files/input0.txt', './temp_files/input1.txt', './temp_files/output1.txt'])
        results = self.run_process(2)
        print(results)
        assert results == [1, 1, 0, []]
        assert "./temp_files/input1.txt" == self.read_file_p('./temp_files/input1.txt')
        assert self.read_file_p('./temp_files/output0.txt') == "./TEMP_FILES/INPUT0.TXT"
        assert self.read_file_p('./temp_files/output1.txt') == "./temp_files/output1.txt"

        for i in range(6,13):
            self.clean_and_make_files([f'./temp_files/input{j}.txt' for j in range(i)])
            results = self.run_process(i)
            assert results == [i, i, 0, []], results


if __name__ == "__main__":
    IdempotentProcessor_unit_tests().do_tests()



