# Invoice PDF Creator

This project is a lightweight Streamlit app for turning an Excel workbook into one PDF per row using the invoice template stored in the templates folder.

## What it does

- Lets the user upload their own Excel workbook each time
- Reads spreadsheet rows into a simple invoice layout
- Generates one PDF per row with the stored template
- Uses a browser-based interface so the app stays easy for non-technical users

## Recommended spreadsheet columns

Use column names similar to:

- Invoice Number
- Customer Name
- Invoice Date
- Amount Due
- Description

The app normalizes those names automatically and maps common variants.

## Windows launch for non-technical users

1. Double-click `launch_app.bat` in this project folder.
2. The app will open in the browser for you.
3. Upload the Excel workbook for that week.
4. Choose an output folder.
5. Click `Generate PDFs`.

The user should never need to know about UV or Python. The launcher handles the setup automatically and keeps the technical details hidden.

> The sample workbook in the `data` folder is only for demo purposes. The end user should upload their own workbook every time they run the app.

## Manual launch

If you want to launch it from a terminal:

1. Open a terminal in this project folder.
2. Run:

   py -3 -m pip install -e .

3. Start the app:

   py -3 -m streamlit run main.py
