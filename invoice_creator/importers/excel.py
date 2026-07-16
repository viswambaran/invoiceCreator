import pandas as pd


class ExcelImporter:


    def __init__(self, file_path):

        self.file_path = file_path



    def load_rows(self):

        df = pd.read_excel(
            self.file_path
        )

        ## Clean the headers remove trailing spaces 
        df.columns = (
            df.columns
            .astype(str).
            str.strip()
        )


        return df.to_dict(
            orient="records"
        )