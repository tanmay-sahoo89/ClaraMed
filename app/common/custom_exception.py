import sys

class CustomException(Exception):
    def __init__(self, message:str, get_detailed:Exception=None):
        self.error_message = self.get_detailed_error_message(message, get_detailed)
        super().__init__(self.error_message)
        
    @staticmethod
    def get_detailed_error_message(message, get_detailed):
        _, _, exc_tb = sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb else "Unknown file!"
        line_number = exc_tb.tb_lineno if exc_tb else "Unknown line number!"
        return(
            f"{message} | Error: {get_detailed}\n"
            f"File: {file_name} | Line Number: {line_number}"
        )
    def __str__(self):
        return self.error_message