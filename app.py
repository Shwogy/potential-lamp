from flask import Flask, render_template, request, redirect, url_for
import pdfplumber
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def extract_budget_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        table = page.extract_table()
        df = pd.DataFrame(table[1:], columns=table[0])
        return df

def compare_budgets(df1, df2):
    df1 = df1.rename(columns={df1.columns[0]: 'البند', df1.columns[1]: 'القيمة فترة 1'})
    df2 = df2.rename(columns={df2.columns[0]: 'البند', df2.columns[1]: 'القيمة فترة 2'})
    merged = pd.merge(df1, df2, on='البند', how='outer').fillna(0)
    merged['الفرق'] = merged['القيمة فترة 2'].astype(float) - merged['القيمة فترة 1'].astype(float)
    return merged

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file1 = request.files.get('budget1')
        file2 = request.files.get('budget2')

        if not file1 or not file2:
            return "يرجى رفع كلا الملفين"

        path1 = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        path2 = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
        file1.save(path1)
        file2.save(path2)

        df1 = extract_budget_data(path1)
        df2 = extract_budget_data(path2)

        comparison = compare_budgets(df1, df2)
        table_html = comparison.to_html(index=False)

        return render_template('result.html', table=table_html)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
