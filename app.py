from flask import Flask, render_template
from services.student.score_analysis import get_student_score_analysis

app = Flask(__name__)

@app.route('/score_analysis/<stuno>')
def score_analysis(stuno):
    analysis = get_student_score_analysis(stuno)
    return render_template('analysis_result.html', analysis=analysis)

if __name__ == '__main__':
    app.run(debug=True)
